#! /usr/bin/env bash

rsync -vazrh . azure-api-auohealth:~/workspace/ --exclude .mypy_cache/ --exclude __pycache__/ --exclude .pytest_cache/ --exclude .git --exclude auohealth-cert/ --exclude /etc
