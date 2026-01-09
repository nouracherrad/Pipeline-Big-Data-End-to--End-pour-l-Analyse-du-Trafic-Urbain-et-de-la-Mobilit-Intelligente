from kafka import KafkaConsumer
import requests
from datetime import datetime
import json
import time
import sys
from prometheus_client import start_http_server, Counter, Gauge, Histogram
from kafka.errors import NoBrokersAvailable

KAFKA_BROKER = 'kafka:9092'
TOPIC_NAME = 'traffic-events'
NAMENODE_HOST = 'namenode'
NAMENODE_PORT = 9870
HDFS_USER = 'root'
RAW_PATH = '/data/raw/traffic'

def wait_for_kafka(max_retries=30, delay=2):
    """Attendre que Kafka soit disponible"""
    for i in range(max_retries):
        try:
            print(f"⏳ Tentative de connexion à Kafka ({i+1}/{max_retries})...")
            test_consumer = KafkaConsumer(
                bootstrap_servers=[KAFKA_BROKER],
                api_version=(0, 10, 1),
                group_id='test-connection',
                consumer_timeout_ms=1000
            )
            test_consumer.close()
            print("✅ Kafka est disponible !")
            return True
        except NoBrokersAvailable:
            print(f"⏳ Kafka n'est pas encore prêt, nouvelle tentative dans {delay} secondes...")
            time.sleep(delay)
        except Exception as e:
            print(f"⚠️ Erreur: {e}")
            time.sleep(delay)
    return False

def wait_for_hdfs(max_retries=30, delay=2):
    """Attendre que HDFS soit disponible"""
    for i in range(max_retries):
        try:
            print(f"⏳ Tentative de connexion à HDFS ({i+1}/{max_retries})...")
            url = f"http://{NAMENODE_HOST}:{NAMENODE_PORT}/webhdfs/v1/?op=GETFILESTATUS&user.name={HDFS_USER}"
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print("✅ HDFS est disponible !")
                return True
        except Exception as e:
            print(f"⏳ HDFS n'est pas encore prêt, nouvelle tentative dans {delay} secondes...")
            time.sleep(delay)
    return False

def hdfs_mkdir(path):
    """Créer un dossier HDFS via l'API WebHDFS"""
    url = f"http://{NAMENODE_HOST}:{NAMENODE_PORT}/webhdfs/v1{path}?op=MKDIRS&user.name={HDFS_USER}"
    try:
        response = requests.put(url, timeout=10)
        return response.status_code in [200, 201]
    except Exception as e:
        print(f"⚠️ Erreur création dossier {path}: {e}")
        return False

def hdfs_append(path, data):
    """Écrire dans un fichier HDFS via l'API WebHDFS"""
    # D'abord vérifier si le fichier existe
    check_url = f"http://{NAMENODE_HOST}:{NAMENODE_PORT}/webhdfs/v1{path}?op=GETFILESTATUS&user.name={HDFS_USER}"
    
    try:
        check_response = requests.get(check_url, timeout=5)
        
        if check_response.status_code == 200:
            # Fichier existe, utiliser APPEND
            url = f"http://{NAMENODE_HOST}:{NAMENODE_PORT}/webhdfs/v1{path}?op=APPEND&user.name={HDFS_USER}"
            response = requests.post(url, allow_redirects=False, timeout=10)
            
            if response.status_code == 307:
                redirect_url = response.headers['Location']
                write_response = requests.post(redirect_url, data=data.encode('utf-8'), timeout=10)
                return write_response.status_code == 200
        else:
            # Fichier n'existe pas, utiliser CREATE
            url = f"http://{NAMENODE_HOST}:{NAMENODE_PORT}/webhdfs/v1{path}?op=CREATE&user.name={HDFS_USER}&overwrite=false"
            response = requests.put(url, allow_redirects=False, timeout=10)
            
            if response.status_code == 307:
                redirect_url = response.headers['Location']
                write_response = requests.put(redirect_url, data=data.encode('utf-8'), timeout=10)
                return write_response.status_code in [200, 201]
        
        return False
    except Exception as e:
        print(f"⚠️ Erreur écriture {path}: {e}")
        return False

# Métriques Prometheus
start_http_server(8000)
EVENTS_COUNTER = Counter("traffic_events_total", "Nombre total d'événements traités")
VEHICLE_COUNT_GAUGE = Gauge("traffic_vehicle_count", "Nombre de véhicules par zone", ["zone"])
AVERAGE_SPEED_GAUGE = Gauge("traffic_average_speed", "Vitesse moyenne par zone", ["zone"])
OCCUPANCY_GAUGE = Gauge("traffic_occupancy_rate", "Taux d'occupation par zone", ["zone"])
CONGESTION_GAUGE = Gauge("traffic_congestion_level", "Niveau de congestion (0-100)", ["zone"])
PROCESSING_TIME = Histogram("traffic_processing_seconds", "Temps de traitement des messages")
BYTES_WRITTEN = Counter("hdfs_bytes_written", "Nombre total d'octets écrits dans HDFS")

def calculate_congestion_level(vehicle_count, average_speed, occupancy_rate):
    """Calculer le niveau de congestion (0-100)"""
    # Score normalisé pour chaque métrique
    vehicle_score = min(vehicle_count / 200 * 100, 100)
    speed_score = max((110 - average_speed) / 110 * 100, 0)
    occupancy_score = occupancy_rate
    
    # Pondération
    congestion = (vehicle_score * 0.4 + speed_score * 0.4 + occupancy_score * 0.2)
    return round(congestion, 2)

# Attendre que Kafka et HDFS soient prêts
print("🚀 Kafka Consumer → HDFS démarrage...")
print(f"📡 Kafka: {KAFKA_BROKER}")
print(f"📊 HDFS: {NAMENODE_HOST}:{NAMENODE_PORT}")
print("=" * 50)

if not wait_for_kafka():
    print("❌ Impossible de se connecter à Kafka")
    sys.exit(1)

if not wait_for_hdfs():
    print("❌ Impossible de se connecter à HDFS")
    sys.exit(1)

# Créer la structure HDFS de base
print("📁 Création de la structure HDFS...")
hdfs_mkdir('/data')
hdfs_mkdir('/data/raw')
hdfs_mkdir('/data/raw/traffic')
print("✅ Structure HDFS créée")

# Configurer le consumer
consumer = KafkaConsumer(
    TOPIC_NAME,
    bootstrap_servers=[KAFKA_BROKER],
    auto_offset_reset='earliest',
    value_deserializer=lambda x: json.loads(x.decode('utf-8')),
    enable_auto_commit=True,
    group_id='hdfs-consumer-group',
    api_version=(0, 10, 1)
)

print("✅ Kafka Consumer → HDFS démarré et prêt !")
print("=" * 50)

# Variables pour le buffer
buffer = {}
created_dirs = set()
zone_metrics = {}
message_count = 0

def flush_buffer():
    """Écrire le buffer dans HDFS"""
    total_written = 0
    for key, events in buffer.items():
        if not events:
            continue
        
        hdfs_path = f"{RAW_PATH}/{key}/traffic.json"
        data = '\n'.join([json.dumps(e) for e in events]) + '\n'
        
        if hdfs_append(hdfs_path, data):
            bytes_written = len(data.encode('utf-8'))
            BYTES_WRITTEN.inc(bytes_written)
            total_written += len(events)
            print(f"💾 Écrit {len(events)} événements dans {key} ({bytes_written} octets)")
        else:
            print(f"❌ Échec écriture {key}")
    
    buffer.clear()
    return total_written

try:
    last_flush = time.time()
    last_metric_update = time.time()
    last_status = time.time()
    
    for message in consumer:
        start_time = time.time()
        try:
            event = message.value
            event_time = datetime.fromisoformat(event['event_time'])
            date_str = event_time.strftime('%Y-%m-%d')
            hour_str = event_time.strftime('%H')
            zone = event['zone']
            
            # Structure de dossiers: date=YYYY-MM-DD/hour=HH/zone=zone
            dir_key = f"date={date_str}/hour={hour_str}/zone={zone}"
            hdfs_dir = f"{RAW_PATH}/{dir_key}"
            
            # Créer les dossiers si nécessaire
            if dir_key not in created_dirs:
                hdfs_mkdir(f"{RAW_PATH}/date={date_str}")
                hdfs_mkdir(f"{RAW_PATH}/date={date_str}/hour={hour_str}")
                hdfs_mkdir(hdfs_dir)
                created_dirs.add(dir_key)
                print(f"📁 Dossier créé: {hdfs_dir}")
            
            # Ajouter au buffer
            if dir_key not in buffer:
                buffer[dir_key] = []
            buffer[dir_key].append(event)
            
            # Mettre à jour les métriques par zone
            if zone not in zone_metrics:
                zone_metrics[zone] = {
                    'count': 0,
                    'total_vehicles': 0,
                    'total_speed': 0,
                    'total_occupancy': 0
                }
            
            zone_metrics[zone]['count'] += 1
            zone_metrics[zone]['total_vehicles'] += event['vehicle_count']
            zone_metrics[zone]['total_speed'] += event['average_speed']
            zone_metrics[zone]['total_occupancy'] += event['occupancy_rate']
            
            message_count += 1
            EVENTS_COUNTER.inc()
            
            # Enregistrer le temps de traitement
            processing_time = time.time() - start_time
            PROCESSING_TIME.observe(processing_time)
            
            # Afficher un statut toutes les 20 messages
            current_time = time.time()
            if current_time - last_status > 10:
                print(f"📊 Statut: {message_count:04d} événements traités | "
                      f"Buffer: {sum(len(v) for v in buffer.values())} | "
                      f"Zones actives: {len(zone_metrics)}")
                last_status = current_time
            
            # Flush toutes les 10 secondes ou tous les 100 messages
            if current_time - last_flush > 10 or sum(len(v) for v in buffer.values()) >= 100:
                written = flush_buffer()
                if written > 0:
                    print(f"📤 Flush: {written} événements écrits dans HDFS")
                last_flush = current_time
            
            # Mettre à jour les métriques Prometheus toutes les 15 secondes
            if current_time - last_metric_update > 15:
                for zone, metrics in zone_metrics.items():
                    if metrics['count'] > 0:
                        avg_vehicles = metrics['total_vehicles'] / metrics['count']
                        avg_speed = metrics['total_speed'] / metrics['count']
                        avg_occupancy = metrics['total_occupancy'] / metrics['count']
                        congestion = calculate_congestion_level(avg_vehicles, avg_speed, avg_occupancy)
                        
                        VEHICLE_COUNT_GAUGE.labels(zone=zone).set(avg_vehicles)
                        AVERAGE_SPEED_GAUGE.labels(zone=zone).set(avg_speed)
                        OCCUPANCY_GAUGE.labels(zone=zone).set(avg_occupancy)
                        CONGESTION_GAUGE.labels(zone=zone).set(congestion)
                
                last_metric_update = current_time
        
        except json.JSONDecodeError as e:
            print(f"❌ Erreur JSON: {e}")
        except KeyError as e:
            print(f"❌ Champ manquant: {e}")
        except Exception as e:
            print(f"❌ Erreur traitement message: {e}")

except KeyboardInterrupt:
    print("\n🛑 Consumer arrêté par l'utilisateur")
    written = flush_buffer()
    print(f"📤 Dernier flush: {written} événements écrits")
except Exception as e:
    print(f"❌ Erreur fatale: {e}")
    import traceback
    traceback.print_exc()
    written = flush_buffer()
finally:
    consumer.close()
    print(f"👋 Consumer fermé. Total: {message_count} événements traités")