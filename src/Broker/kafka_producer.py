import json
from datetime import datetime
from kafka import KafkaProducer

# Создание продюсера
def get_kafka_producer():
    return KafkaProducer(
        bootstrap_servers=['kafka:29092'],  # Для сервисов внутри Docker-сети
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )


producer = get_kafka_producer()

# Функции отправки событий
def send_registration_event(client_id):
    event = {
        'client_id': client_id,
        'timestamp': datetime.now().isoformat()
    }
    producer.send('registration_events', event)
    producer.flush()

def send_like_event(client_id, post_id):
    event = {
        'client_id': client_id,
        'post_id': post_id,
        'event_type': 'like',
        'timestamp': datetime.now().isoformat()
    }
    producer.send('like_click_events', event)
    producer.flush()

def send_view_event(client_id, post_id):
    event = {
        'client_id': client_id,
        'post_id': post_id,
        'event_type': 'view',
        'timestamp': datetime.now().isoformat()
    }
    producer.send('view_events', event)
    producer.flush()

def send_comment_event(client_id, post_id, comment_id):
    event = {
        'client_id': client_id,
        'post_id': post_id,
        'event_type': 'comment',
        'comment_id': comment_id,
        'timestamp': datetime.now().isoformat()
    }
    producer.send('comment_events', event)
    producer.flush()
