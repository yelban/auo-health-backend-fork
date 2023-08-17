#!/bin/bash
# cd ~/workspace && docker run -it --rm --env-file .env --network=workspace_default postgres:13.6-bullseye bash
export PGPASSWORD=$DATABASE_PASSWORD

DB_NAME=${DATABASE_NAME}
BACKUP_DB_NAME=${DATABASE_NAME}_bak_$(date +"%Y%m%d%H")
db_dump_file=${DATABASE_NAME}.dump

pg_dump -h $DATABASE_HOST -U $DATABASE_USER -F custom $DB_NAME > "$db_dump_file"
dropdb -h $DATABASE_HOST -U $DATABASE_USER --if-exists $BACKUP_DB_NAME
createdb -h $DATABASE_HOST -U $DATABASE_USER -T template0 $BACKUP_DB_NAME
pg_restore -h $DATABASE_HOST -U $DATABASE_USER -d $BACKUP_DB_NAME "$db_dump_file"
