#! /usr/bin/env bash
set -e

celery -A auo_project.services.celery.tasks beat -l debug
