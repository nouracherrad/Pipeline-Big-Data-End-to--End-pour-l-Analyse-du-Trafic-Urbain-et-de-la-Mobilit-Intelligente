import json, time, random
from datetime import datetime
from kafka import KafkaProducer

SENSORS = [f"sensor_{i:03d}" for i in range(1, 51)]
ROADS = [f"road_{i:02d}" for i in range(1, 21)]
ROAD_TYPES = ["autoroute", "avenue", "rue"]
ZONES = ["Centre", "Nord", "Sud", "Est", "Ouest"]

KAFKA_BROKER = 'kafka:9092'
TOPIC_NAME = 'traffic-events'

producer = KafkaProducer(
    bootstrap_servers=[KAFKA_BROKER],
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

def generate_event():
    now = datetime.now()
    hour = now.hour
    if 7 <= hour <= 9 or 17 <= hour <= 20:
        vehicle_count = random.randint(100, 200)
        average_speed = random.uniform(15, 40)
        occupancy_rate = random.uniform(60, 90)
    elif hour >= 22 or hour <= 6:
        vehicle_count = random.randint(5, 30)
        average_speed = random.uniform(70, 110)
        occupancy_rate = random.uniform(5, 25)
    else:
        vehicle_count = random.randint(50, 100)
        average_speed = random.uniform(40, 70)
        occupancy_rate = random.uniform(30, 60)

    return {
        "sensor_id": random.choice(SENSORS),
        "road_id": random.choice(ROADS),
        "road_type": random.choice(ROAD_TYPES),
        "zone": random.choice(ZONES),
        "vehicle_count": vehicle_count,
        "average_speed": round(average_speed, 2),
        "occupancy_rate": round(occupancy_rate, 2),
        "event_time": now.isoformat()
    }

if __name__ == "__main__":
    print("🚀 Kafka Producer démarré...")
    while True:
        event = generate_event()
        producer.send(TOPIC_NAME, value=event)
        producer.flush()
        print(f"Envoyé : {event}")
        time.sleep(1)
