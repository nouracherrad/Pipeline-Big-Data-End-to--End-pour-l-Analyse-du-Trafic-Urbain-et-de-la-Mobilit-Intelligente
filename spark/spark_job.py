from pyspark.sql import SparkSession
from pyspark.sql.functions import avg, count, col

spark = SparkSession.builder \
    .appName("TrafficProcessing") \
    .config("spark.hadoop.fs.defaultFS", "hdfs://namenode:9000") \
    .config("spark.sql.shuffle.partitions", "4") \
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN")

print("🚀 Spark Job - Traitement des données de trafic")

try:
    # CHEMIN CORRIGÉ avec la vraie structure
    input_path = "hdfs://namenode:9000/data/raw/traffic/date=*/hour=*/zone=*/traffic.json"
    print(f"📖 Lecture des données depuis: {input_path}")
    
    df = spark.read.json(input_path)
    row_count = df.count()
    print(f"📊 Nombre total d'événements: {row_count}")
    
    if row_count == 0:
        print("⚠️ Aucune donnée trouvée")
    else:
        print("\n📄 Aperçu des données:")
        df.show(5, truncate=False)
        
        # Statistiques par zone
        print("\n📈 Calcul des statistiques par zone...")
        traffic_stats = df.groupBy("zone").agg(
            count("*").alias("total_events"),
            avg("vehicle_count").alias("avg_vehicle_count"),
            avg("average_speed").alias("avg_speed"),
            avg("occupancy_rate").alias("avg_occupancy")
        ).orderBy(col("total_events").desc())
        
        print("\n✅ Statistiques de trafic par zone:")
        traffic_stats.show(truncate=False)
        
        # Statistiques par type de route
        print("\n📈 Calcul des statistiques par type de route...")
        road_stats = df.groupBy("road_type").agg(
            count("*").alias("total_events"),
            avg("vehicle_count").alias("avg_vehicle_count"),
            avg("average_speed").alias("avg_speed")
        ).orderBy(col("total_events").desc())
        
        print("\n✅ Statistiques par type de route:")
        road_stats.show(truncate=False)
        
        # Zones congestionnées
        print("\n🚦 Zones congestionnées:")
        congested = df.groupBy("zone").agg(
            avg("vehicle_count").alias("avg_vehicles"),
            avg("average_speed").alias("avg_speed"),
            avg("occupancy_rate").alias("avg_occupancy")
        ).filter((col("avg_speed") < 40) & (col("avg_occupancy") > 60))
        congested.show(truncate=False)
        
        # Sauvegarder les résultats
        print("\n💾 Sauvegarde des résultats...")
        traffic_stats.write.mode("overwrite").parquet("hdfs://namenode:9000/data/analytics/traffic/by_zone")
        road_stats.write.mode("overwrite").parquet("hdfs://namenode:9000/data/analytics/traffic/by_road_type")
        congested.write.mode("overwrite").parquet("hdfs://namenode:9000/data/analytics/traffic/congested_zones")
        
        print("\n✅ Job Spark terminé avec succès!")

except Exception as e:
    print(f"\n❌ Erreur: {e}")
    import traceback
    traceback.print_exc()
finally:
    spark.stop()
    print("👋 SparkSession fermée")