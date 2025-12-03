import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Any
import os
from celery import Celery

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


SMTP_HOST = os.getenv("SMTP_HOST", "localhost")
SMTP_PORT = int(os.getenv("SMTP_PORT", 1025))
EMAIL_FROM = os.getenv("EMAIL_FROM", "noreply@marketplace-blog.com")


try:
    from worker.celery_app import celery_app
except ImportError:
    celery_app = Celery("marketplace_blog")
    celery_app.config_from_object("worker.celery_config")


@celery_app.task(bind=True, max_retries=3)
def send_welcome_email(self, user_data: Dict[str, Any]) -> bool:
    """
    Отправка приветственного email новому пользователю
    """
    try:
        email = user_data.get("email")
        name = user_data.get("name", "Пользователь")

        logger.info(f"Начинаем отправку приветственного письма для {email}")

        msg = MIMEMultipart("alternative")
        msg["Subject"] = "Добро пожаловать в Marketplace Blog!"
        msg["From"] = EMAIL_FROM
        msg["To"] = email

        text = f"""Добро пожаловать, {name}!

Вы успешно зарегистрировались в Marketplace Blog.
Ваш email для входа: {email}

Спасибо за регистрацию!
---
Это письмо отправлено автоматически."""

        html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: #4CAF50; color: white; padding: 20px; text-align: center; }}
        .content {{ padding: 20px; background: #f9f9f9; }}
        .footer {{ padding: 20px; text-align: center; font-size: 12px; color: #666; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Добро пожаловать, {name}!</h1>
        </div>
        <div class="content">
            <p>Вы успешно зарегистрировались в <strong>Marketplace Blog</strong>.</p>
            <p>Ваш email для входа: <strong>{email}</strong></p>
            <p>Теперь вы можете создавать статьи, комментировать и многое другое!</p>
        </div>
        <div class="footer">
            <p>Это письмо отправлено автоматически, пожалуйста, не отвечайте на него.</p>
        </div>
    </div>
</body>
</html>"""

        msg.attach(MIMEText(text, "plain"))
        msg.attach(MIMEText(html, "html"))

        logger.info(f"Пытаемся отправить письмо через {SMTP_HOST}:{SMTP_PORT}")

        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.send_message(msg)
            logger.info(f"Письмо успешно отправлено пользователю {email}")

        return True

    except Exception as e:
        logger.error(f"Ошибка отправки письма для {user_data.get('email')}: {str(e)}")
        logger.exception(e)

        raise self.retry(exc=e, countdown=30)


@celery_app.task
def test_email_task(email: str) -> bool:
    """
    Тестовая задача для проверки Celery
    """
    logger.info(f"Тестовая задача выполнена для email: {email}")
    return True
