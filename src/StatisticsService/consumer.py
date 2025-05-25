import json
import logging
import threading
from kafka import KafkaConsumer
from db import get_clickhouse_client, parse_timestamp

logger = logging.getLogger('consumer')

KAFKA_BOOTSTRAP_SERVERS = ['kafka:29092']
TOPICS = [
    ('view_events', 'view'),
    ('like_click_events', 'like'),
    ('comment_events', 'comment')
]

def process_message(message, event_type, clickhouse_client):
    try:
        data = message.value

        client_id = data.get('client_id', '')
        post_id = int(data.get('post_id', 0))
        comment_id = data.get('comment_id', None)

        timestamp_str = data.get('timestamp', '')
        timestamp = parse_timestamp(timestamp_str)
        logger.info("ok1")

        row = {
            'event_type': event_type,
            'client_id': client_id,
            'post_id': post_id,
            'comment_id': comment_id,
            'timestamp': timestamp
        }
        logger.info("ok2")
        logger.info(type(row['post_id']))

        clickhouse_client.execute(
            '''INSERT INTO events 
               (event_type, client_id, post_id, comment_id, timestamp) VALUES''',
            [
                (
                    row['event_type'],
                    row['client_id'],
                    row['post_id'],
                    row['comment_id'],
                    row['timestamp']
                )
            ]
        )
        logger.info("ok3")
        logger.info(f"Saved {event_type} event for post {post_id} from user {client_id}")
    except Exception as e:
        logger.error(f"Error processing message: {e}")

def kafka_topic_listener(topic, event_type):
    clickhouse_client = get_clickhouse_client()
    logger.info(f"Starting to listen topic: {topic}")

    consumer = KafkaConsumer(
        topic,
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        group_id=f"statistics-{topic}-group",
        auto_offset_reset='earliest',
        value_deserializer=lambda m: json.loads(m.decode('utf-8')),
        enable_auto_commit=True
    )

    for message in consumer:
        process_message(message, event_type, clickhouse_client)

def start_kafka_consumers():
    for topic, event_type in TOPICS:
        thread = threading.Thread(
            target=kafka_topic_listener,
            args=(topic, event_type),
            daemon=True
        )
        thread.start()
    logger.info("Kafka consumers started for all topics")
