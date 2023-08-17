#! /usr/bin/env bash

cp .env.prod .env
docker compose -f deploy/docker-compose.yml -f deploy/docker-compose.prd.yml --project-directory . up -d
