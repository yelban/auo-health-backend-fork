"""Celery service."""

from auo_project.services.celery.lifetime import init_celery

celery_app = init_celery()
