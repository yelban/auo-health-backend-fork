#! /usr/bin/env bash

docker compose -f deploy/docker-compose.yml -f deploy/docker-compose.prd.yml --project-directory . build streamlit
docker compose -f deploy/docker-compose.yml -f deploy/docker-compose.prd.yml --project-directory . up streamlit -d
