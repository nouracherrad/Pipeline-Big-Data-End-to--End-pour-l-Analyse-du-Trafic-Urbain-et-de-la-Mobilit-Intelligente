# 🚦 Pipeline Big Data - Analyse du Trafic Urbain et Mobilité Intelligente

## 📋 Table des matières
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

## 🎯 Vue d'ensemble

Ce projet implémente un **pipeline Big Data end-to-end** pour l'analyse du trafic urbain dans le cadre d'une Smart City. Il permet de :

- ✅ **Collecter** des données de trafic en temps réel depuis des capteurs simulés
- ✅ **Ingérer** les données via Apache Kafka
- ✅ **Stocker** dans un Data Lake HDFS
- ✅ **Traiter** avec Apache Spark
- ✅ **Visualiser** avec Grafana
- ✅ **Orchestrer** avec Apache Airflow
- ✅ **Monitorer** avec Prometheus

### 🎓 Contexte du projet

Dans le cadre d'une Smart City, les villes modernes déploient des capteurs urbains (caméras, boucles magnétiques, capteurs IoT, applications mobiles) pour collecter en continu des données de trafic routier. Ce projet répond à la problématique suivante :

> **Comment concevoir et implémenter un pipeline Big Data capable de collecter des données de trafic urbain en temps réel, de les stocker dans un Data Lake, de les traiter efficacement, puis de produire des indicateurs exploitables pour la gestion intelligente de la mobilité ?**

---

## 🏗️ Architecture du système

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

### 🔄 Flux de données

1. **Génération** : Le producer Python simule 50 capteurs générant des événements JSON
2. **Streaming** : Les événements sont publiés dans Kafka (topic `traffic-events`)
3. **Ingestion** : Le consumer Kafka lit les messages et les écrit dans HDFS
4. **Stockage Raw** : Organisation hiérarchique par `date`/`heure`/`zone`
5. **Traitement** : Spark lit les données raw et calcule les agrégations
6. **Stockage Analytics** : Résultats sauvegardés en Parquet pour l'analyse
7. **Visualisation** : Grafana affiche les métriques en temps réel
8. **Orchestration** : Airflow automatise l'exécution du pipeline toutes les heures

---

## 📦 Prérequis

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

### Configuration système recommandée

- **CPU** : 4 cœurs minimum
- **RAM** : 8 GB minimum (12 GB recommandé)
- **Disque** : 20 GB d'espace libre
- **OS** : Linux, macOS, ou Windows avec WSL2

---

## 🚀 Installation et démarrage

### 1. Cloner le projet

```bash
git clone <votre-repo>
cd traffic-big-data-pipeline
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

**⏱️ Temps de démarrage estimé : 2-3 minutes**

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

## 📁 Structure du projet

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

## 🎮 Guide d'utilisation

### Étape 1 : Démarrer le pipeline

```bash
# 1. Démarrer tous les services
docker-compose up -d

# 2. Vérifier que tous les conteneurs sont UP
docker-compose ps

# 3. Suivre les logs généraux
docker-compose logs -f
```

**📸 À capturer en screenshot** :
- Résultat de `docker-compose ps` montrant tous les services en "Up"
- Logs du producer montrant la génération d'événements

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

**📸 À capturer en screenshot** :
- Liste des topics montrant `traffic-events`
- Quelques messages JSON affichés par le consumer

**Exemple de sortie attendue** :

```json
{"sensor_id":"sensor_003","road_id":"road_12","road_type":"avenue","zone":"Nord","vehicle_count":85,"average_speed":45.2,"occupancy_rate":52.1,"event_time":"2026-01-10T14:30:00"}
```

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

**📸 À capturer en screenshot** :
- Structure hiérarchique montrant date → hour → zone
- Contenu d'un fichier `traffic.json`
- Taille totale des données stockées

#### Via interface web HDFS

1. Ouvrir dans un navigateur : http://localhost:9870
2. Cliquer sur **Utilities** dans le menu
3. Sélectionner **Browse the file system**
4. Naviguer vers `/data/raw/traffic/`
5. Explorer la structure date/hour/zone

**📸 À capturer en screenshot** :
- Page d'accueil HDFS montrant le cluster
- Navigation dans `/data/raw/traffic/`
- Détails d'un fichier JSON

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

**📸 À capturer en screenshot** :
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

**📸 À capturer en screenshot** :
- Liste des dossiers analytics
- Contenu d'une table (by_zone, by_road_type, ou congested_zones)

---

### Étape 5 : Utiliser Airflow

#### Accéder à l'interface Airflow

1. Ouvrir dans un navigateur : http://localhost:8080
2. Se connecter avec :
   - **Username** : `admin`
   - **Password** : `admin`

**📸 À capturer en screenshot** :
- Page de connexion Airflow
- Page d'accueil avec la liste des DAGs

#### Activer le DAG

1. Dans la liste des DAGs, trouver `traffic_pipeline_big_data`
2. Cliquer sur le bouton **Toggle** (interrupteur) à gauche pour l'activer
3. Le DAG devient actif et s'exécutera automatiquement toutes les heures

**📸 À capturer en screenshot** :
- DAG activé (interrupteur en bleu/vert)
- Description du DAG : "Pipeline Big Data pour analyse du trafic urbain"

#### Lancer manuellement le DAG

1. Cliquer sur le nom du DAG `traffic_pipeline_big_data`
2. Cliquer sur le bouton **▶️ (Play)** en haut à droite
3. Sélectionner **Trigger DAG**
4. Confirmer le lancement

**📸 À capturer en screenshot** :
- Bouton "Trigger DAG"
- Fenêtre de confirmation

#### Observer l'exécution

1. Cliquer sur le DAG pour voir les détails
2. Choisir la vue **Graph** pour voir le workflow
3. Observer les tâches qui s'exécutent :
   - 🟡 Jaune : En cours
   - 🟢 Vert : Réussi
   - 🔴 Rouge : Échoué

**📸 À capturer en screenshot** :
- Vue Graph montrant toutes les tâches
- Tâches en cours d'exécution (jaune)
- Toutes les tâches réussies (vert)

#### Vue détaillée des logs

1. Cliquer sur une tâche (ex: `spark_processing`)
2. Sélectionner **Log**
3. Observer les logs détaillés de la tâche

**📸 À capturer en screenshot** :
- Logs de la tâche `check_hdfs_data` montrant les fichiers trouvés
- Logs de la tâche `spark_processing` montrant le succès du job
- Logs de la tâche `generate_report` montrant le rapport final

**Exemple de log attendu pour `spark_processing`** :

```
[2026-01-10, 14:35:00] {bash.py:123} INFO - 🔥 Lancement du job Spark...
[2026-01-10, 14:35:05] {bash.py:123} INFO - 📊 Nombre total d'événements: 5432
[2026-01-10, 14:35:10] {bash.py:123} INFO - ✅ Job Spark terminé avec succès
```

#### Vue du calendrier

1. Cliquer sur l'onglet **Calendar**
2. Observer l'historique des exécutions
3. Chaque case colorée représente une exécution :
   - Vert : Succès
   - Rouge : Échec
   - Blanc : Pas d'exécution

**📸 À capturer en screenshot** :
- Vue calendrier montrant plusieurs exécutions réussies

---

### Étape 6 : Visualiser avec Grafana

#### Accéder à Grafana

1. Ouvrir dans un navigateur : http://localhost:3000
2. Se connecter avec :
   - **Username** : `admin`
   - **Password** : `admin`
3. (Optionnel) Changer le mot de passe ou cliquer sur "Skip"

**📸 À capturer en screenshot** :
- Page de connexion Grafana
- Page d'accueil de Grafana

#### Accéder au dashboard

1. Cliquer sur le menu hamburger (☰) en haut à gauche
2. Sélectionner **Dashboards**
3. Cliquer sur **Traffic Analytics - Smart City**

**📸 À capturer en screenshot** :
- Liste des dashboards
- Dashboard complet "Traffic Analytics - Smart City"

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
- Panel montrant le compteur total (ex: 8532 événements)

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

**📸 À capturer en screenshot** :
- Graphique avec les 5 courbes de zones
- Légende montrant les couleurs de chaque zone
- Pic visible pendant les heures de pointe

---

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

**📸 À capturer en screenshot** :
- Ensemble des jauges pour toutes les zones
- Au moins une zone en rouge (congestion)
- Au moins une zone en vert (fluide)

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

**📸 À capturer en screenshot** :
- Graphique montrant l'évolution temporelle
- Courbes de différentes couleurs pour chaque zone
- Variation visible selon les heures

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

**📸 À capturer en screenshot** :
- Jauges de congestion pour toutes les zones
- Au moins une zone en état critique (rouge)

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

**📸 À capturer en screenshot** :
- Menu de sélection temporelle
- Dashboard mis à jour avec une période différente

##### Rafraîchissement automatique

1. En haut à droite, cliquer sur l'icône de rafraîchissement
2. Sélectionner "5s" pour un rafraîchissement toutes les 5 secondes
3. Observer les graphiques se mettre à jour en temps réel

**📸 À capturer en screenshot** (optionnel) :
- Indicateur de rafraîchissement automatique actif

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

**📸 À capturer en screenshot** :
- Page d'accueil de Prometheus

#### Vérifier les targets

1. Cliquer sur **Status** dans le menu
2. Sélectionner **Targets**
3. Vérifier que `kafka_consumer_metrics` est en **UP**

**📸 À capturer en screenshot** :
- Liste des targets
- Target `kafka_consumer_metrics` avec état "UP" et endpoint `kafka-consumer:8000`

#### Exécuter des requêtes PromQL

##### Requête 1 : Taux d'événements par seconde

```promql
rate(traffic_events_total[1m])
```

1. Copier la requête dans la barre de recherche
2. Cliquer sur **Execute**
3. Sélectionner l'onglet **Graph** pour voir l'évolution

**📸 À capturer en screenshot** :
- Graphique montrant le taux d'événements/seconde

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

**📸 À capturer en screenshot** :
- Table montrant les valeurs par
