import os
from kombu import Connection


def check_rabbitmq_connection():
    broker_url = os.getenv("CELERY_BROKER_URL", "amqp://guest:guest@localhost:5672//")

    try:
        with Connection(broker_url) as conn:
            conn.connect()
            print("✅ RabbitMQ connection successful")
            print(f"URL: {broker_url}")
            return True
    except Exception as e:
        print(f"❌ RabbitMQ connection failed: {e}")
        print(f"URL: {broker_url}")
        return False


if __name__ == "__main__":
    check_rabbitmq_connection()
