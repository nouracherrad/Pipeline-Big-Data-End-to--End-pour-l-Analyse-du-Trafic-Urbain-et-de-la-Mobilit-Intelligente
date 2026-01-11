#  Pipeline Big Data - Analyse du Trafic Urbain et Mobilité Intelligente

##  Table des matières
1. [Vue d'ensemble](#-vue-densemble)
2. [Architecture du système](#️-architecture-du-système)
3. [Prérequis](#-prérequis)
4. [Installation et démarrage](#-installation-et-démarrage)
5. [Structure du projet](#-structure-du-projet)
6. [Guide d'utilisation](#-guide-dutilisation)
7. [Vérification du pipeline](#-vérification-du-pipeline)
8. [Dashboards et visualisation](#-dashboards-et-visualisation)
9. [Troubleshooting](#-troubleshooting)
10. [Métriques et KPIs](#-métriques-et-kpis)

---

##  Vue d'ensemble

Ce projet implémente un **pipeline Big Data end-to-end** pour l'analyse du trafic urbain dans le cadre d'une Smart City. Il permet de :

- ✅ **Collecter** des données de trafic en temps réel depuis des capteurs simulés
- ✅ **Ingérer** les données via Apache Kafka
- ✅ **Stocker** dans un Data Lake HDFS
- ✅ **Traiter** avec Apache Spark
- ✅ **Visualiser** avec Grafana
- ✅ **Orchestrer** avec Apache Airflow
- ✅ **Monitorer** avec Prometheus

###  Contexte du projet

Dans le cadre d'une Smart City, les villes modernes déploient des capteurs urbains (caméras, boucles magnétiques, capteurs IoT, applications mobiles) pour collecter en continu des données de trafic routier. Ce projet répond à la problématique suivante :

> **Comment concevoir et implémenter un pipeline Big Data capable de collecter des données de trafic urbain en temps réel, de les stocker dans un Data Lake, de les traiter efficacement, puis de produire des indicateurs exploitables pour la gestion intelligente de la mobilité ?**

---

##  Architecture du système

```
┌─────────────────────────────────────────────────────────────────┐
│                      ARCHITECTURE PIPELINE                       │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────┐
│  Capteurs IoT   │ ◄── Simulation de 50 capteurs urbains
│   (Producer)    │     Génère des événements toutes les secondes
└────────┬────────┘
         │ JSON events
         ▼
┌─────────────────┐
│  Apache Kafka   │ ◄── Streaming temps réel
│  Topic: traffic │     Gestion des flux IoT
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Kafka Consumer │ ◄── Ingestion et organisation des données
│   + Prometheus  │     Métriques exposées pour monitoring
└────────┬────────┘
         │ Écriture HDFS
         ▼
┌─────────────────┐
│   HDFS (Raw)    │ ◄── Data Lake - Zone Raw
│ /data/raw/traffic│    Structure partitionnée par date/heure/zone
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Apache Spark   │ ◄── Traitement distribué et agrégation
│  Batch Process  │     Calcul des statistiques et KPIs
└────────┬────────┘
         │ Parquet format
         ▼
┌─────────────────┐
│ HDFS (Analytics)│ ◄── Zone Analytics - Format optimisé
│ /data/analytics │     Résultats prêts pour l'analyse
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│    Grafana      │ ◄── Dashboards interactifs
│  + Prometheus   │     Visualisation temps réel des KPIs
└─────────────────┘
         ▲
         │ Orchestration
┌─────────────────┐
│ Apache Airflow  │ ◄── Automatisation du pipeline
│   DAG hourly    │     Workflow complet toutes les heures
└─────────────────┘
```

###  Flux de données

1. **Génération** : Le producer Python simule 50 capteurs générant des événements JSON
2. **Streaming** : Les événements sont publiés dans Kafka (topic `traffic-events`)
3. **Ingestion** : Le consumer Kafka lit les messages et les écrit dans HDFS
4. **Stockage Raw** : Organisation hiérarchique par `date`/`heure`/`zone`
5. **Traitement** : Spark lit les données raw et calcule les agrégations
6. **Stockage Analytics** : Résultats sauvegardés en Parquet pour l'analyse
7. **Visualisation** : Grafana affiche les métriques en temps réel
8. **Orchestration** : Airflow automatise l'exécution du pipeline toutes les heures

---

##  Prérequis

### Logiciels requis

- **Docker** (version 20.10+)
- **Docker Compose** (version 2.0+)
- **Git**
- **Au moins 8 GB de RAM disponible**
- **20 GB d'espace disque**

### Vérifier les versions

```bash
docker --version
# Docker version 20.10.x ou supérieur

docker-compose --version
# Docker Compose version 2.x.x ou supérieur
```

### 2. Structure des dossiers

Créez la structure suivante si elle n'existe pas :

```
traffic-big-data-pipeline/
├── producer/
│   ├── Dockerfile
│   ├── traffic_producer.py
│   └── requirements.txt
├── consumer/
│   ├── Dockerfile
│   ├── kafka_to_hdfs.py
│   └── requirements.txt
├── spark/
│   ├── Dockerfile
│   ├── spark_job.py
│   └── requirements.txt
├── airflow/
│   └── dags/
│       └── traffic_pipeline.py
├── grafana/
│   └── provisioning/
│       ├── datasources/
│       │   └── datasources.yml
│       └── dashboards/
│           ├── dashboard.yml
│           └── traffic_analytics.json
├── prometheus/
│   └── prometheus.yml
├── docker-compose.yml
└── README.md
```

### 3. Démarrer les services

```bash
# Démarrer tous les services en arrière-plan
docker-compose up -d

# Vérifier que tous les conteneurs sont actifs
docker-compose ps
```

** Temps de démarrage estimé : 2-3 minutes**

Vous devriez voir une sortie similaire à :

```
NAME                  STATUS
airflow-postgres      Up (healthy)
airflow-scheduler     Up
airflow-webserver     Up
datanode              Up
grafana               Up
kafka                 Up (healthy)
kafka-consumer        Up
kafka-producer        Up
namenode              Up (healthy)
prometheus            Up
spark                 Up
zookeeper             Up (healthy)
```

### 4. Accéder aux interfaces web

| Service | URL | Identifiants | Description |
|---------|-----|--------------|-------------|
| **Airflow** | http://localhost:8080 | admin / admin | Orchestration du pipeline |
| **Grafana** | http://localhost:3000 | admin / admin | Dashboards et visualisation |
| **Prometheus** | http://localhost:9090 | - | Métriques et monitoring |
| **HDFS NameNode** | http://localhost:9870 | - | Interface web HDFS |
| **Kafka** | localhost:9092 | - | Broker Kafka (CLI uniquement) |

---

##  Structure du projet

### Producer (Générateur de données)

**Fichier** : `producer/traffic_producer.py`

**Rôle** : Simuler des capteurs urbains IoT générant des événements de trafic

**Caractéristiques** :
- 50 capteurs simulés (`sensor_001` à `sensor_050`)
- 20 routes différentes (`road_01` à `road_20`)
- 5 zones géographiques (Centre, Nord, Sud, Est, Ouest)
- 3 types de routes (autoroute, avenue, rue)
- Génération adaptative selon l'heure :
  - **Heures de pointe** (7h-9h, 17h-20h) : Trafic dense
  - **Heures creuses** (22h-6h) : Trafic faible
  - **Heures normales** : Trafic modéré

**Exemple d'événement généré** :

```json
{
  "sensor_id": "sensor_042",
  "road_id": "road_15",
  "road_type": "avenue",
  "zone": "Centre",
  "vehicle_count": 150,
  "average_speed": 25.8,
  "occupancy_rate": 75.4,
  "event_time": "2026-01-10T14:30:45.123456"
}
```

**Commande pour voir les logs** :

```bash
docker-compose logs -f kafka-producer
```

---

### Consumer (HDFS Writer)

**Fichier** : `consumer/kafka_to_hdfs.py`

**Rôle** : Consommer les messages Kafka et les écrire dans HDFS

**Fonctionnalités** :
- Consommation temps réel depuis Kafka
- Organisation hiérarchique des données :
  ```
  /data/raw/traffic/
    date=2026-01-10/
      hour=14/
        zone=Centre/
          traffic.json
        zone=Nord/
          traffic.json
  ```
- Buffering pour optimiser les écritures HDFS
- Exposition de métriques Prometheus sur le port 8000
- Gestion des erreurs et reconnexion automatique

**Métriques exposées** :
- `traffic_events_total` : Nombre total d'événements traités
- `traffic_vehicle_count` : Nombre de véhicules par zone
- `traffic_average_speed` : Vitesse moyenne par zone
- `traffic_occupancy_rate` : Taux d'occupation par zone
- `traffic_congestion_level` : Niveau de congestion calculé
- `hdfs_bytes_written` : Octets écrits dans HDFS

**Commande pour voir les logs** :

```bash
docker-compose logs -f kafka-consumer
```

---

### Spark Job (Traitement)

**Fichier** : `spark/spark_job.py`

**Rôle** : Traiter les données raw et produire des analytics

**Traitements effectués** :

1. **Statistiques par zone** :
   - Nombre total d'événements
   - Nombre moyen de véhicules
   - Vitesse moyenne
   - Taux d'occupation moyen

2. **Statistiques par type de route** :
   - Trafic moyen par type (autoroute, avenue, rue)
   - Vitesse moyenne par type

3. **Détection des zones congestionnées** :
   - Critères : vitesse < 40 km/h ET occupation > 60%
   - Liste des zones nécessitant une intervention

**Résultats sauvegardés** :
- `/data/analytics/traffic/by_zone/` (format Parquet)
- `/data/analytics/traffic/by_road_type/` (format Parquet)
- `/data/analytics/traffic/congested_zones/` (format Parquet)

**Commande pour exécuter manuellement** :

```bash
docker exec spark spark-submit \
  --master local[*] \
  --driver-memory 2g \
  /app/spark_job.py
```

---

### Airflow DAG (Orchestration)

**Fichier** : `airflow/dags/traffic_pipeline.py`

**Rôle** : Automatiser l'exécution du pipeline complet

**Workflow du DAG** :

```
check_services → wait_for_data → check_hdfs_data → 
spark_processing → validate_results → generate_report
```

**Tâches** :

1. **check_services** : Vérifier que tous les conteneurs sont actifs
2. **wait_for_data** : Attendre 60 secondes pour accumuler des données
3. **check_hdfs_data** : Vérifier la présence de données dans HDFS
4. **spark_processing** : Lancer le job Spark
5. **validate_results** : Vérifier que les analytics ont été générés
6. **generate_report** : Produire un rapport d'exécution

**Configuration** :
- **Fréquence** : Toutes les heures (`@hourly`)
- **Propriétaire** : noura
- **Retries** : 2 tentatives en cas d'échec
- **Timeout** : 30 minutes par tâche

**Accès** : http://localhost:8080

---

##  Guide d'utilisation

### Étape 1 : Démarrer le pipeline

```bash
# 1. Démarrer tous les services
docker-compose up -d

# 2. Vérifier que tous les conteneurs sont UP
docker-compose ps

# 3. Suivre les logs généraux
docker-compose logs -f
```
<img width="955" height="447" alt="image" src="https://github.com/user-attachments/assets/c24bcac0-db9e-48fe-afc2-78765454d7b7" />

**Indicateurs de succès** :
- ✅ Tous les services affichent "Up" ou "Up (healthy)"
- ✅ Le producer affiche : `Envoyé : {...}`
- ✅ Le consumer affiche : `💾 Écrit X événements`

---

### Étape 2 : Vérifier Kafka

```bash
# Lister les topics Kafka
docker exec kafka kafka-topics --list --bootstrap-server localhost:9092

# Vous devriez voir : traffic-events

# Consommer quelques messages pour vérifier
docker exec kafka kafka-console-consumer \
  --bootstrap-server localhost:9092 \
  --topic traffic-events \
  --from-beginning \
  --max-messages 5
```


**Exemple de sortie attendue** :

```json
{"sensor_id":"sensor_003","road_id":"road_12","road_type":"avenue","zone":"Nord","vehicle_count":85,"average_speed":45.2,"occupancy_rate":52.1,"event_time":"2026-01-10T14:30:00"}
```
#### kafka-producer
<img width="936" height="466" alt="image" src="https://github.com/user-attachments/assets/caff4336-b6a8-467b-9211-4d37204bad77" />


#### kafka-consumer
<img width="960" height="746" alt="image" src="https://github.com/user-attachments/assets/096833fd-8a38-4f4d-90cd-1ddae15dbc60" />


**Vérifier le lag du consumer** :

```bash
docker exec kafka kafka-consumer-groups \
  --bootstrap-server localhost:9092 \
  --describe --group hdfs-consumer-group
```

---

### Étape 3 : Vérifier HDFS

#### Via ligne de commande

```bash
# 1. Lister la structure principale
docker exec namenode hdfs dfs -ls /data/raw/traffic/

# Sortie attendue :
# drwxr-xr-x   - root supergroup  date=2026-01-10

# 2. Voir les dossiers par date
docker exec namenode hdfs dfs -ls /data/raw/traffic/date=2026-01-10/

# 3. Voir les heures
docker exec namenode hdfs dfs -ls /data/raw/traffic/date=2026-01-10/hour=14/

# 4. Voir les zones
docker exec namenode hdfs dfs -ls /data/raw/traffic/date=2026-01-10/hour=14/

# 5. Lire le contenu d'un fichier (premières lignes)
docker exec namenode hdfs dfs -cat \
  /data/raw/traffic/date=2026-01-10/hour=14/zone=Centre/traffic.json | head -5

# 6. Voir la taille totale des données
docker exec namenode hdfs dfs -du -s -h /data/raw/traffic/
```
- Structure hiérarchique montrant date → hour → zone
- Contenu d'un fichier `traffic.json`
- Taille totale des données stockées
<img width="1592" height="653" alt="image" src="https://github.com/user-attachments/assets/894a7c43-53ef-43d8-ac2d-a546d16700c4" />

#### Via interface web HDFS

1. Ouvrir dans un navigateur : http://localhost:9870
2. Cliquer sur **Utilities** dans le menu
3. Sélectionner **Browse the file system**
4. Naviguer vers `/data/raw/traffic/`
5. Explorer la structure date/hour/zone

** screenshot** :
- Page d'accueil HDFS montrant le cluster
- Navigation dans `/data/raw/traffic/`
- Détails d'un fichier JSON
<img width="1885" height="827" alt="image" src="https://github.com/user-attachments/assets/7e6a2862-6d21-49eb-bd34-cabd987c3a49" />

---

### Étape 4 : Exécuter le job Spark

#### Méthode 1 : Exécution manuelle

```bash
docker exec spark spark-submit \
  --master local[*] \
  --driver-memory 2g \
  --executor-memory 2g \
  /app/spark_job.py
```

** À capturer en screenshot** :
- Logs Spark montrant :
  - `📊 Nombre total d'événements: X`
  - `✅ Statistiques de trafic par zone:`
  - Tableau avec les statistiques
  - `✅ Job Spark terminé avec succès!`

**Sortie attendue** :

```
🚀 Spark Job - Traitement des données de trafic
📖 Lecture des données depuis: hdfs://namenode:9000/data/raw/traffic/...
📊 Nombre total d'événements: 5432

✅ Statistiques de trafic par zone:
+------+------------+------------------+---------+--------------+
|zone  |total_events|avg_vehicle_count |avg_speed|avg_occupancy |
+------+------------+------------------+---------+--------------+
|Centre|1234        |125.5             |32.4     |68.2          |
|Nord  |1100        |95.3              |45.7     |52.1          |
...
```
<img width="1641" height="742" alt="image" src="https://github.com/user-attachments/assets/a6b5b4d0-c638-4b9a-9d13-c07e1e56af37" />


#### Méthode 2 : Via Airflow (recommandé)

Cette méthode sera détaillée à l'étape 5.

#### Vérifier les résultats analytics

```bash
# Lister les dossiers analytics
docker exec namenode hdfs dfs -ls /data/analytics/traffic/

# Vous devriez voir :
# /data/analytics/traffic/by_zone/
# /data/analytics/traffic/by_road_type/
# /data/analytics/traffic/congested_zones/

# Voir la taille des résultats
docker exec namenode hdfs dfs -du -s -h /data/analytics/traffic/by_zone/

# Lire quelques résultats (format Parquet)
docker exec spark spark-shell --master local[*] <<EOF
val df = spark.read.parquet("hdfs://namenode:9000/data/analytics/traffic/by_zone")
df.show()
EOF
```

**📸Liste des dossiers analytics** :
- Contenu d'une table (by_zone, by_road_type, ou congested_zones)
---
<img width="1197" height="167" alt="image" src="https://github.com/user-attachments/assets/ec62cb40-f9c2-41c1-b685-a0d65799b59c" />


### Étape 5 : Utiliser Airflow

#### Accéder à l'interface Airflow

1. Ouvrir dans un navigateur : http://localhost:8080
2. Se connecter avec :
   - **Username** : `admin`
   - **Password** : `admin`


#### Activer le DAG

1. Dans la liste des DAGs, trouver `traffic_pipeline_big_data`
2. Cliquer sur le bouton **Toggle** (interrupteur) à gauche pour l'activer
3. Le DAG devient actif et s'exécutera automatiquement toutes les heures

**📸 screenshot** :
<img width="1902" height="635" alt="image" src="https://github.com/user-attachments/assets/484f9de4-12f7-4767-b982-695b77d63e03" />


#### Lancer manuellement le DAG

1. Cliquer sur le nom du DAG `traffic_pipeline_big_data`
2. Cliquer sur le bouton **▶️ (Play)** en haut à droite
3. Sélectionner **Trigger DAG**
4. Confirmer le lancement

**📸  screenshot** :
- Vue Graph montrant toutes les tâches
- Tâches en cours d'exécution (jaune)
- Toutes les tâches réussies (vert)
<img width="1891" height="966" alt="image" src="https://github.com/user-attachments/assets/68da0ff1-990f-4661-aa36-44ab152dc017" />

#### Observer l'exécution

1. Cliquer sur le DAG pour voir les détails
2. Choisir la vue **Graph** pour voir le workflow
3. Observer les tâches qui s'exécutent :
   - 🟡 Jaune : En cours
   - 🟢 Vert : Réussi
   - 🔴 Rouge : Échoué


#### Vue détaillée des logs

1. Cliquer sur une tâche (ex: `spark_processing`)
2. Sélectionner **Log**
3. Observer les logs détaillés de la tâche

**📸 À capturer en screenshot** :
- Logs de la tâche `check_hdfs_data` montrant les fichiers trouvés
- Logs de la tâche `spark_processing` montrant le succès du job
- Logs de la tâche `generate_report` montrant le rapport final
<img width="1887" height="955" alt="image" src="https://github.com/user-attachments/assets/e000137d-e717-4141-add8-5fb4fe4996aa" />


### Étape 6 : Visualiser avec Grafana

#### Accéder à Grafana

1. Ouvrir dans un navigateur : http://localhost:3000
2. Se connecter avec :
   - **Username** : `admin`
   - **Password** : `admin`
3. (Optionnel) Changer le mot de passe ou cliquer sur "Skip"

** Page d'accueil de Grafana** :
<img width="1918" height="965" alt="image" src="https://github.com/user-attachments/assets/cbb52b11-28c3-4d4f-948f-44479497aa52" />


#### Accéder au dashboard

1. Cliquer sur le menu hamburger (☰) en haut à gauche
2. Sélectionner **Dashboards**
3. Cliquer sur **Traffic Analytics - Smart City**

** Liste des dashboards** :
- Dashboard complet "Traffic Analytics - Smart City"
<img width="967" height="447" alt="image" src="https://github.com/user-attachments/assets/8d813daf-044a-4a8a-9103-581eecaeed63" />

#### Panels du dashboard

Le dashboard contient 5 panels principaux :

##### 1. Total Événements (Stat Panel)

**Description** : Affiche le nombre total d'événements traités depuis le démarrage

**Métriques** :
- Compteur : `traffic_events_total`
- Seuils de couleur :
  - 🟢 Vert : < 1000 événements
  - 🟡 Jaune : 1000-5000 événements
  - 🔴 Rouge : > 5000 événements

**📸 À capturer en screenshot** :
- Panel montrant le compteur total
  <img width="1423" height="381" alt="image" src="https://github.com/user-attachments/assets/4728ee9d-8f8b-45e8-bc7e-cb481f058bb4" />

---

##### 2. Véhicules par Zone (Time Series)

**Description** : Graphique temporel montrant l'évolution du nombre de véhicules par zone

**Métriques** :
- Série temporelle : `traffic_vehicle_count`
- Une courbe par zone (Centre, Nord, Sud, Est, Ouest)

**Interprétation** :
- Pics visibles pendant les heures de pointe
- Tendances différentes selon les zones
- Identification rapide des zones les plus fréquentées

**screenshot** :
<img width="640" height="352" alt="image" src="https://github.com/user-attachments/assets/dc6a1e9b-409b-4f5a-b4b2-8da6b00ee70e" />


##### 3. Vitesse Moyenne (Gauge)

**Description** : Jauges circulaires montrant la vitesse moyenne par zone

**Métriques** :
- Gauge : `traffic_average_speed`
- Une jauge par zone
- Unité : km/h

**Seuils de couleur** :
- 🔴 Rouge : < 30 km/h (congestion)
- 🟡 Jaune : 30-50 km/h (ralentissement)
- 🟢 Vert : > 50 km/h (fluide)

**screenshot** :
- Ensemble des jauges pour toutes les zones
- Au moins une zone en rouge (congestion)
- Au moins une zone en vert (fluide)
<img width="630" height="377" alt="image" src="https://github.com/user-attachments/assets/40af6d4a-8c48-4d48-a0d5-9778c7165b0d" />

---

##### 4. Taux d'Occupation (Time Series)

**Description** : Évolution du taux d'occupation de la route (0-100%)

**Métriques** :
- Série temporelle : `traffic_occupancy_rate`
- Une courbe par zone
- Échelle : 0-100%

**Interprétation** :
- Occupation élevée (>70%) = risque de congestion
- Occupation faible (<30%) = trafic fluide

**screenshot** :
- Graphique montrant l'évolution temporelle
- Courbes de différentes couleurs pour chaque zone
- Variation visible selon les heures
<img width="618" height="388" alt="image" src="https://github.com/user-attachments/assets/b639427d-38b1-4895-90a1-827c6bb1afd6" />

---

##### 5. Niveau de Congestion (Gauge)

**Description** : Score composite de congestion calculé (0-100)

**Formule de calcul** :
```
Congestion = 0.4 × (vehicle_count/200×100) 
           + 0.4 × ((110-speed)/110×100) 
           + 0.2 × occupancy_rate
```

**Métriques** :
- Gauge : `traffic_congestion_level`
- Score de 0 à 100

**Seuils d'interprétation** :
- 🟢 Vert : 0-40 (fluide)
- 🟡 Jaune : 40-70 (modéré)
- 🔴 Rouge : 70-100 (congestionné)

**screenshot** :
- Jauges de congestion pour toutes les zones
- Au moins une zone en état critique (rouge)
<img width="1913" height="592" alt="image" src="https://github.com/user-attachments/assets/eab5462a-3de9-4a39-b7cb-b994f154a935" />

---

#### Fonctionnalités avancées de Grafana

##### Filtrage temporel

En haut à droite du dashboard :
1. Cliquer sur la sélection de temps (ex: "Last 1 hour")
2. Choisir une période :
   - Last 5 minutes
   - Last 15 minutes
   - Last 1 hour
   - Last 3 hours
   - Custom range

##### Rafraîchissement automatique

1. En haut à droite, cliquer sur l'icône de rafraîchissement
2. Sélectionner "5s" pour un rafraîchissement toutes les 5 secondes
3. Observer les graphiques se mettre à jour en temps réel


##### Zoom sur un graphique

1. Cliquer et glisser sur un graphique pour sélectionner une période
2. Le graphique zoome automatiquement
3. Cliquer sur "Zoom out" pour revenir

##### Export de dashboard

1. Cliquer sur l'icône de partage en haut du dashboard
2. Sélectionner "Export"
3. Télécharger le fichier JSON

---

### Étape 7 : Vérifier Prometheus

#### Accéder à Prometheus

1. Ouvrir dans un navigateur : http://localhost:9090
2. Aucune authentification requise


#### Vérifier les targets

1. Cliquer sur **Status** dans le menu
2. Sélectionner **Targets**
3. Vérifier que `kafka_consumer_metrics` est en **UP**

**Liste des targets** :

- Target `kafka_consumer_metrics` avec état "UP" et endpoint `kafka-consumer:8000`
 ![Uploading image.png…]()


#### Exécuter des requêtes PromQL

##### Requête 1 : Taux d'événements par seconde

```promql
rate(traffic_events_total[1m])
```

1. Copier la requête dans la barre de recherche
2. Cliquer sur **Execute**
3. Sélectionner l'onglet **Graph** pour voir l'évolution

---

##### Requête 2 : Véhicules moyens par zone

```promql
avg(traffic_vehicle_count) by (zone)
```

**Résultat attendu** :
```
{zone="Centre"}    125.5
{zone="Nord"}      95.3
{zone="Sud"}       87.2
{zone="Est"}       102.1
{zone="Ouest"}     78.9
```
## Conclusion

Ce projet démontre la mise en place complète d'un **pipeline Big Data end-to-end** pour l'analyse du trafic urbain dans le contexte d'une Smart City. L'architecture implémentée couvre l'ensemble des étapes essentielles d'un système de traitement de données massives en temps réel.

### Objectifs atteints

#### 1. Collecte de données en temps réel
- Simulation de 50 capteurs IoT urbains
- Génération continue d'événements de trafic
- Adaptation du trafic selon les heures (pointe, creuse, normale)
- Format JSON standardisé et structuré

#### 2. Ingestion streaming
- Apache Kafka pour la gestion des flux temps réel
- Producer capable de générer des milliers d'événements
- Consumer avec gestion des erreurs et reconnexion automatique
- Exposition de métriques pour le monitoring

#### 3. Stockage distribué (Data Lake)
- HDFS comme système de stockage distribué
- Organisation hiérarchique par date/heure/zone
- Zone Raw pour les données brutes
- Zone Analytics pour les résultats traités

#### 4. Traitement Big Data
- Apache Spark pour le traitement distribué
- Calculs d'agrégations et statistiques complexes
- Détection des zones congestionnées
- Format Parquet optimisé pour l'analyse

#### 5. Visualisation et dashboards
- Grafana avec dashboards interactifs
- 5 panels couvrant tous les KPIs métier
- Rafraîchissement temps réel (5 secondes)
- Alertes visuelles par seuils de couleur

#### 6. Orchestration et automatisation
- Apache Airflow pour l'automatisation du pipeline
- DAG avec 6 tâches interdépendantes
- Exécution automatique toutes les heures
- Gestion des erreurs et retry automatique

#### 7. Monitoring et observabilité
- Prometheus pour la collecte de métriques
- 7 métriques exposées par le consumer
- Supervision de la santé des services
- Requêtes PromQL pour l'analyse avancée

### Compétences démontrées

Ce projet illustre la maîtrise des technologies et concepts suivants :

| Domaine | Technologies | Compétences |
|---------|-------------|-------------|
| **Streaming** | Kafka, Producer/Consumer | Traitement temps réel, gestion des flux IoT |
| **Stockage** | HDFS, Parquet | Data Lake, partitionnement, formats optimisés |
| **Traitement** | Apache Spark, PySpark | Calculs distribués, agrégations, transformations |
| **Orchestration** | Apache Airflow | Workflows, DAGs, automatisation, scheduling |
| **Visualisation** | Grafana, Prometheus | Dashboards, métriques, KPIs, monitoring |
| **Infrastructure** | Docker, Docker Compose | Conteneurisation, orchestration, microservices |
| **DevOps** | CI/CD concepts | Automatisation, logging, healthchecks |

### Résultats métier

Le pipeline produit des insights exploitables pour la gestion urbaine :

1. **Identification des zones critiques** en temps réel
2. **Prédiction des congestions** basée sur des patterns historiques
3. **Optimisation du trafic** grâce aux statistiques par type de route
4. **Aide à la décision** pour la planification urbaine
5. **Alertes automatiques** pour les interventions urgentes

### Scalabilité et évolutions possibles

Le système est conçu pour évoluer :

**Court terme** :
- Augmentation du nombre de capteurs (scalabilité horizontale)
- Ajout de nouvelles zones géographiques
- Intégration de données météo pour corrélation

**Moyen terme** :
- Machine Learning pour la prédiction de congestion
- API REST pour exposer les analytics
- Système de recommandation d'itinéraires

**Long terme** :
- Déploiement sur Kubernetes pour haute disponibilité
- Intégration avec systèmes de feux intelligents
- Extension à d'autres villes (multi-tenant)

### Valeur ajoutée pour une Smart City

Ce pipeline répond aux enjeux majeurs de la mobilité urbaine :

- **Réactivité** : Détection des problèmes en quelques secondes
- **Prévention** : Anticipation des congestions avant qu'elles ne surviennent
- **Optimisation** : Meilleure allocation des ressources municipales
- **Durabilité** : Réduction des émissions par fluidification du trafic
- **Transparence** : Données accessibles via dashboards publics

### Apprentissages clés

1. **Architecture Lambda** : Combinaison de traitement batch (Spark) et streaming (Kafka)
2. **Data Lake moderne** : Organisation en zones (Raw, Processed, Analytics)
3. **Observabilité** : L'importance du monitoring dès la conception
4. **Résilience** : Gestion des pannes et reprise automatique
5. **Performance** : Optimisations (partitionnement, formats, buffering)

### Conclusion finale

Ce projet démontre qu'un **pipeline Big Data robuste et scalable** peut être mis en place avec des technologies open-source modernes. L'approche end-to-end, de la collecte à la visualisation en passant par le traitement distribué, illustre parfaitement les défis et solutions d'un système Big Data en production.

La combinaison de **Kafka, HDFS, Spark, Airflow, et Grafana** forme une stack technologique éprouvée, capable de gérer des volumes massifs de données tout en fournissant des insights exploitables en temps réel.

Ce système est **prêt pour la production** et pourrait être déployé dans une véritable Smart City avec des ajustements mineurs pour s'adapter aux spécificités locales.



## Références

- [Apache Kafka Documentation](https://kafka.apache.org/documentation/)
- [Apache Spark Documentation](https://spark.apache.org/docs/latest/)
- [Apache Airflow Documentation](https://airflow.apache.org/docs/)
- [Hadoop HDFS Guide](https://hadoop.apache.org/docs/stable/hadoop-project-dist/hadoop-hdfs/HdfsUserGuide.html)
- [Grafana Documentation](https://grafana.com/docs/)
- [Prometheus Documentation](https://prometheus.io/docs/)

---

## Auteur

**Noura cherrad** - Projet Big Data : Analyse du Trafic Urbain et Mobilité Intelligente



**nissrine el fijaoui** - Projet Big Data : Analyse du Trafic Urbain et Mobilité Intelligente

---
