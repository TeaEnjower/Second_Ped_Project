from typing import Dict, Any
from worker.tasks import send_welcome_email
import logging

logger = logging.getLogger(__name__)


class EmailService:
    @staticmethod
    async def send_welcome_email_async(user_data: Dict[str, Any]):
        """Асинхронная отправка приветственного email"""
        try:
            task = send_welcome_email.delay(user_data)
            logger.info(f"Email задача поставлена в очередь, ID: {task.id}")
            return task.id
        except Exception as e:
            logger.error(f"Ошибка постановки email задачи: {str(e)}")
            raise

    @staticmethod
    def send_welcome_email_sync(user_data: Dict[str, Any]):
        """Синхронная отправка (для тестов)"""
        return send_welcome_email.apply(args=[user_data])
