#! /usr/bin/env bash

rsync -vazrh . azure-api-auohealth:~/workspace_dev/ --exclude .mypy_cache/ --exclude __pycache__/ --exclude .pytest_cache/ --exclude .git --exclude auohealth-cert/ --exclude /etc
