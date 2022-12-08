from celery import Celery

from auo_project.core.config import settings


def init_celery():
    celery_app = Celery(
        "worker",
        broker=f"amqp://{settings.RABBITMQ_DEFAULT_USER}:{settings.RABBITMQ_DEFAULT_PASS}@{settings.RABBITMQ_HOSTNAME}/{settings.RABBITMQ_DEFAULT_VHOST}",
    )
    celery_app.conf.task_default_queue = "main-queue"
    return celery_app


def shutdown_celery():
    # TODO
    pass
