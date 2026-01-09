# Pipeline Big Data pour l'Analyse du Trafic Urbain

##  Introduction
Ce projet implémente un pipeline Big Data complet pour l'analyse du trafic urbain dans le cadre d'une Smart City. Le système collecte, traite et analyse des données de trafic en temps réel pour fournir des insights exploitables pour la gestion intelligente de la mobilité.

##  Objectifs
- **Collecter** des données de trafic en temps réel via des capteurs simulés
- **Ingérer** les données via Apache Kafka
- **Stocker** les données brutes dans un Data Lake HDFS
- **Traiter** les données avec Apache Spark
- **Visualiser** les résultats avec Grafana
- **Orchestrer** le pipeline avec Apache Airflow

##  Architecture du Pipeline

```
Capteurs Simulés (Python) → Kafka → HDFS (Raw) → Spark (Processing) → HDFS (Analytics) → Grafana (Visualisation)
                              ↑
                          Apache Airflow (Orchestration)
```

##  Structure du Projet

```
smart-city-traffic/
├── docker-compose.yml          # Configuration des services Docker
├── airflow/
│   └── dags/
│       └── traffic_pipeline.py # DAG Airflow pour l'orchestration
├── producer/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── traffic_producer.py     # Générateur de données Kafka
├── consumer/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── kafka_to_hdfs.py        # Consumer Kafka → HDFS
├── spark/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── spark_job.py           # Job Spark de traitement
├── prometheus/
│   └── prometheus.yml         # Configuration Prometheus
├── grafana/
│   └── provisioning/
│       ├── datasources/
│       │   └── datasource.yml # Source de données Grafana
│       └── dashboards/
│           └── dashboard.json # Dashboard Grafana
└── README.md                  # Documentation
```

##  Services Déployés

| Service | Port | Description |
|---------|------|-------------|
| Kafka | 9092 | Broker de messages |
| Zookeeper | 2181 | Coordination Kafka |
| HDFS NameNode | 9870/9000 | Interface web/API HDFS |
| Spark | - | Traitement distribué |
| Prometheus | 9090 | Monitoring des métriques |
| Grafana | 3000 | Visualisation des données |
| Airflow | 8080 | Orchestration du pipeline |
| Postgres | 5432 | Base de données Airflow |

##  Prérequis

- Docker 20.10+
- Docker Compose 2.0+
- 8GB RAM minimum
- 10GB d'espace disque libre

##  Installation et Démarrage

1. **Cloner le projet**
```bash
git clone [URL_DU_PROJET]
cd smart-city-traffic
```

2. **Démarrer les services**
```bash
docker-compose up -d
```

3. **Vérifier l'état des services**
```bash
docker-compose ps
```

##  Étapes du Pipeline

### 1. Génération des Données
- **Script**: `producer/traffic_producer.py`
- **Format JSON**: Événements de trafic avec capteur, route, zone, comptage véhicules
- **Fréquence**: 1 événement/seconde
- **Simulation**: 50 capteurs, 20 routes, 5 zones géographiques

### 2. Ingestion Kafka
- **Topic**: `traffic-events`
- **Producer**: Envoi continu des événements
- **Partitionnement**: Par défaut (1 partition)
- **Volume estimé**: ~86,400 événements/jour

### 3. Stockage HDFS
- **Consumer**: `consumer/kafka_to_hdfs.py`
- **Structure**: `/data/raw/traffic/date=YYYY-MM-DD/hour=HH/zone=ZONE/`
- **Format**: JSON brut
- **Métriques**: Exposition Prometheus sur le port 8000

### 4. Traitement Spark
- **Script**: `spark/spark_job.py`
- **Calculs**:
  - Trafic moyen par zone
  - Vitesse moyenne par route
  - Taux de congestion
  - Identification des zones critiques
- **Sortie**: Parquet dans `/data/analytics/traffic/`

### 5. Visualisation Grafana
- **Dashboard**: "Traffic Analytics - Smart City"
- **Métriques**:
  - Total des événements
  - Véhicules par zone
  - Vitesse moyenne
  - Taux d'occupation
  - Niveau de congestion
- **Rafraîchissement**: 5 secondes

### 6. Orchestration Airflow
- **DAG**: `traffic_pipeline_big_data`
- **Fréquence**: Horaire
- **Tâches**:
  1. Vérification des services
  2. Attente génération données
  3. Vérification HDFS
  4. Traitement Spark
  5. Validation résultats
  6. Génération rapport

##  KPI (Indicateurs Clés de Performance)

1. **Trafic par Zone**: Nombre moyen de véhicules
2. **Vitesse Moyenne**: km/h par zone/route
3. **Taux d'Occupation**: % d'utilisation des voies
4. **Niveau de Congestion**: Score 0-100 (basé sur véhicules, vitesse, occupation)
5. **Zones Critiques**: Zones avec vitesse < 40km/h ET occupation > 60%

##  Accès aux Interfaces

1. **Grafana**: http://localhost:3000
   - Utilisateur: `admin`
   - Mot de passe: `admin`

2. **Airflow**: http://localhost:8080
   - Utilisateur: `admin`
   - Mot de passe: `admin`

3. **HDFS NameNode**: http://localhost:9870

4. **Prometheus**: http://localhost:9090

##  Tests et Validation

### Vérification du Flux de Données
```bash
# Vérifier les services
docker-compose ps

# Voir les logs du producer
docker logs kafka-producer -f

# Vérifier les données dans HDFS
docker exec namenode hdfs dfs -ls -R /data/raw/traffic/

# Tester le consumer Kafka
docker exec kafka kafka-console-consumer --bootstrap-server localhost:9092 --topic traffic-events --from-beginning
```

### Exécution Manuelle du Pipeline
```bash
# Lancer le traitement Spark
docker exec spark spark-submit /app/spark_job.py

# Déclencher le DAG Airflow
curl -X POST http://localhost:8080/api/v1/dags/traffic_pipeline_big_data/dagRuns \
  -H "Content-Type: application/json" \
  -d '{"conf": {}}'
```

##  Format des Données

### Événement de Trafic (JSON)
```json
{
  "sensor_id": "sensor_001",
  "road_id": "road_01",
  "road_type": "avenue",
  "zone": "Centre",
  "vehicle_count": 125,
  "average_speed": 45.5,
  "occupancy_rate": 72.3,
  "event_time": "2024-01-10T08:30:15.123456"
}
```

### Structure HDFS
```
/data/raw/traffic/
├── date=2024-01-10/
│   ├── hour=08/
│   │   ├── zone=Centre/
│   │   │   └── traffic.json
│   │   └── zone=Nord/
│   │       └── traffic.json
│   └── hour=09/
│       └── ...

/data/analytics/traffic/
├── by_zone/              # Parquet
├── by_road_type/         # Parquet
└── congested_zones/      # Parquet
```

##  Dashboard Grafana

Le dashboard comprend 5 panneaux principaux:

1. **Total Événements**: Compteur total des événements traités
2. **Véhicules par Zone**: Séries temporelles par zone géographique
3. **Vitesse Moyenne**: Jauge avec seuils (vert > 50km/h, jaune 30-50km/h, rouge < 30km/h)
4. **Taux d'Occupation**: Graphique en ligne 0-100%
5. **Niveau de Congestion**: Jauge avec seuils critiques

##  Dépannage

### Problèmes Courants

1. **Kafka non disponible**
```bash
docker-compose restart kafka
docker logs kafka
```

2. **HDFS non accessible**
```bash
docker-compose restart namenode datanode
docker exec namenode hdfs dfsadmin -report
```

3. **Airflow DAG non déclenché**
```bash
docker-compose restart airflow-scheduler
docker logs airflow-scheduler
```

4. **Grafana sans données**
   - Vérifier la connexion Prometheus
   - Vérifier que le consumer expose les métriques (port 8000)

### Nettoyage
```bash
# Arrêter tous les services
docker-compose down -v

# Supprimer les volumes
docker volume prune -f
```

##  Métriques de Performance

- **Latence end-to-end**: < 2 secondes
- **Débit Kafka**: ~1 événement/seconde
- **Stockage quotidien**: ~10MB/jour (JSON brut)
- **Temps traitement Spark**: ~30 secondes pour 1000 événements
- **Disponibilité dashboard**: Temps réel (rafraîchissement 5s)

##  Apprentissage

Ce projet couvre:
- **Data Engineering**: Pipeline ETL temps réel
- **Big Data**: Kafka, Spark, HDFS
- **DevOps**: Docker, orchestration, monitoring
- **Data Visualization**: Grafana, dashboards temps réel
- **Orchestration**: Airflow DAGs

##  Ressources

- [Documentation Apache Kafka](https://kafka.apache.org/documentation/)
- [Guide Apache Spark](https://spark.apache.org/docs/latest/)
- [Tutoriel HDFS](https://hadoop.apache.org/docs/stable/hadoop-project-dist/hadoop-hdfs/HdfsUserGuide.html)
- [Grafana Documentation](https://grafana.com/docs/)
- [Airflow Documentation](https://airflow.apache.org/docs/)


