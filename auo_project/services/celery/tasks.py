from asgiref.sync import async_to_sync
from celery.schedules import crontab

from auo_project.core.measure import (
    update_measure_cn_means,
    update_measure_cn_means_by_human,
)
from auo_project.core.recipe import remove_inactive_recipes
from auo_project.core.upload import post_finish, update_uploading_upload_status
from auo_project.services.celery import celery_app


@celery_app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    # Call every 10 minutes
    sender.add_periodic_task(
        crontab(minute="*/5"),
        task_update_uploading_upload_status.s(),
        expire=60,
    )

    # Call everyday
    sender.add_periodic_task(
        crontab(
            minute=30,
            hour=16,
        ),
        task_update_measure_cn_means.s(),
        expire=60 * 60,
    )

    # Call everyday
    sender.add_periodic_task(
        crontab(minute=10, hour=16),
        task_cleanup_inactive_recipes.s(),
        expire=60 * 60,
    )


@celery_app.task(acks_late=True)
def test_celery(word: str) -> str:
    return f"test task return {word}"


@celery_app.task()
def tusd_post_finish(arbitrary_json):
    async_to_sync(post_finish)(arbitrary_json)


@celery_app.task()
def task_update_measure_cn_means():
    async_to_sync(update_measure_cn_means)()
    async_to_sync(update_measure_cn_means_by_human)()


@celery_app.task()
def task_cleanup_inactive_recipes():
    async_to_sync(remove_inactive_recipes)()


@celery_app.task()
def task_update_uploading_upload_status():
    async_to_sync(update_uploading_upload_status)()
