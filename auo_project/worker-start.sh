#! /usr/bin/env bash
set -e

# TODO
# python /app/app/celeryworker_pre_start.py

celery -A auo_project.services.celery.tasks worker -l info -Q main-queue --autoscale=10,5
