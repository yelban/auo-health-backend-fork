from asgiref.sync import async_to_sync

from auo_project.core.upload import post_finish
from auo_project.services.celery import celery_app


@celery_app.task(acks_late=True)
def test_celery(word: str) -> str:
    return f"test task return {word}"


@celery_app.task()
def tusd_post_finish(arbitrary_json):
    async_to_sync(post_finish)(arbitrary_json)
