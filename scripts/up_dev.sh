#! /usr/bin/env bash

cp .env.dev .env
docker compose -f deploy/docker-compose.yml -f deploy/docker-compose.dev.yml --project-directory . up -d
