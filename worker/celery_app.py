import os
from celery import Celery
from kombu import Exchange, Queue
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

broker_url = os.getenv("CELERY_BROKER_URL", "amqp://guest:guest@rabbitmq:5672//")

celery_app = Celery("marketplace_blog", broker=broker_url, include=["worker.tasks"])


celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_queues=[
        Queue("default", Exchange("default"), routing_key="default"),
        Queue("emails", Exchange("emails"), routing_key="email"),
    ],
    task_default_queue="default",
    task_default_exchange="default",
    task_default_routing_key="default",
)

if __name__ == "__main__":
    celery_app.start()
