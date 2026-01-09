from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import time

default_args = {
    'owner': 'noura',
    'start_date': datetime(2026, 1, 5),
    'retries': 2,
    'retry_delay': timedelta(minutes=2),
    'execution_timeout': timedelta(minutes=30)
}

dag = DAG(
    'traffic_pipeline_big_data',
    default_args=default_args,
    schedule_interval='@hourly',
    catchup=False,
    description='Pipeline Big Data pour analyse du trafic urbain'
)

def wait_for_data():
    """Attendre que des données soient disponibles"""
    print("⏳ Attente de génération de données (60 secondes)...")
    time.sleep(60)
    print("✅ Données générées")

# Tâche 1 : Vérifier que les services sont prêts
check_services = BashOperator(
    task_id='check_services',
    bash_command='''
    echo "🔍 Vérification des services..."
    docker ps | grep kafka-producer || exit 1
    docker ps | grep kafka-consumer || exit 1
    docker ps | grep spark || exit 1
    echo "✅ Tous les services sont actifs"
    ''',
    dag=dag
)

# Tâche 2 : Attendre la génération de données
wait_data = PythonOperator(
    task_id='wait_for_data_generation',
    python_callable=wait_for_data,
    dag=dag
)

# Tâche 3 : Vérifier les données dans HDFS
check_hdfs_data = BashOperator(
    task_id='check_hdfs_data',
    bash_command='''
    echo "📊 Vérification des données dans HDFS..."
    docker exec namenode hdfs dfs -ls /data/raw/traffic/ || exit 1
    COUNT=$(docker exec namenode hdfs dfs -ls -R /data/raw/traffic/ | grep -c "traffic.json" || echo "0")
    echo "✅ Fichiers trouvés : $COUNT"
    if [ "$COUNT" -eq "0" ]; then
        echo "❌ Aucune donnée trouvée"
        exit 1
    fi
    ''',
    dag=dag
)

# Tâche 4 : Traitement Spark
spark_processing = BashOperator(
    task_id='spark_processing',
    bash_command='''
    echo "🔥 Lancement du job Spark..."
    docker exec spark spark-submit \
        --master local[*] \
        --driver-memory 2g \
        --executor-memory 2g \
        /app/spark_job.py
    
    if [ $? -eq 0 ]; then
        echo "✅ Job Spark terminé avec succès"
    else
        echo "❌ Échec du job Spark"
        exit 1
    fi
    ''',
    dag=dag
)

# Tâche 5 : Vérifier les résultats analytics
validate_results = BashOperator(
    task_id='validate_analytics',
    bash_command='''
    echo "🔍 Vérification des résultats analytics..."
    docker exec namenode hdfs dfs -ls /data/analytics/traffic/by_zone || exit 1
    docker exec namenode hdfs dfs -ls /data/analytics/traffic/by_road_type || exit 1
    echo "✅ Résultats analytics disponibles"
    ''',
    dag=dag
)

# Tâche 6 : Générer un rapport
generate_report = BashOperator(
    task_id='generate_report',
    bash_command='''
    echo "📄 Génération du rapport..."
    TIMESTAMP=$(date +"%Y-%m-%d %H:%M:%S")
    echo "==================================="
    echo "RAPPORT PIPELINE TRAFIC URBAIN"
    echo "Date: $TIMESTAMP"
    echo "==================================="
    
    echo "📊 Statistiques HDFS:"
    docker exec namenode hdfs dfs -du -s -h /data/raw/traffic/
    docker exec namenode hdfs dfs -du -s -h /data/analytics/traffic/
    
    echo ""
    echo "✅ Pipeline exécuté avec succès"
    ''',
    dag=dag
)

# Définir les dépendances
check_services >> wait_data >> check_hdfs_data >> spark_processing >> validate_results >> generate_report