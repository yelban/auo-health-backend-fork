# auo-health-backend

This project was generated using fastapi_template.

## Poetry

This project uses poetry. It's a modern dependency management
tool.

To run the project use this set of commands:

```bash
poetry install
poetry run python -m auo_project
```

This will start the server on the configured host.

You can find swagger documentation at `/api/docs`.

You can read more about poetry here: https://python-poetry.org/

## Project structure

```bash
$ tree "auo_project"
auo_project
├── conftest.py  # Fixtures for all tests.
├── db  # module contains db configurations
│   ├── dao  # Data Access Objects. Contains different classes to inteact with database.
│   └── models  # Package contains different models for ORMs.
├── __main__.py  # Startup script. Starts uvicorn.
├── services  # Package for different external services such as rabbit or redis etc.
├── settings.py  # Main configuration settings for project.
├── static  # Static content.
├── tests  # Tests for project.
└── web  # Package contains web server. Handlers, startup config.
    ├── api  # Package with all handlers.
    │   └── router.py  # Main router.
    ├── application.py  # FastAPI application configuration.
    └── lifetime.py  # Contains actions to perform on startup and shutdown.
```

## Configuration

This application can be configured with environment variables.

You can create `.env` file in the root directory and place all
environment variables here.

All environment variabels should start with "" prefix.

For example if you see in your "auo_project/settings.py" a variable named like
`random_parameter`, you should provide the "RANDOM_PARAMETER"
variable to configure the value. This behaviour can be changed by overriding `env_prefix` property
in `auo_project.core.config.Settings.Config`.

An exmaple of .env file:
```bash
RELOAD="True"
PORT="8000"
ENVIRONMENT="dev"
```

You can read more about BaseSettings class here: https://pydantic-docs.helpmanual.io/usage/settings/

## Pre-commit

To install pre-commit simply run inside the shell:
```bash
pre-commit install
```

pre-commit is very useful to check your code before publishing it.
It's configured using .pre-commit-config.yaml file.

By default it runs:
* black (formats your code);
* mypy (validates types);
* isort (sorts imports in all files);
* flake8 (spots possibe bugs);
* yesqa (removes useless `# noqa` comments).


You can read more about pre-commit here: https://pre-commit.com/

## Deploy code to VM

* dev env
```bash
# rsync code to vm $HOME/workspace_dev
./scripts/rsync_dev.sh
# Build image and recreate docker container and would cause short downtime. Recommend deploy to kubernetes or azure container service
ssh azure-api-auohealth -t '$HOME/workspace_dev/scripts/up_dev.sh'
```

* prd env
```bash
# rsync code to vm $HOME/workspace
./scripts/rsync_prd.sh
# Build image and recreate docker container and would cause short downtime. Recommend deploy to kubernetes or azure container service
ssh azure-api-auohealth -t '$HOME/workspace/scripts/up_prd.sh'
```

## Migrations
If you want to migrate your database, you should run following commands:
```bash
# To run all migrations untill the migration with revision_id.
alembic upgrade "<revision_id>"
```

### Reverting migrations

If you want to revert migrations, you should run:
```bash
# revert all migrations up to: revision_id.
alembic downgrade <revision_id>

# Revert everything.
alembic downgrade base
```

### Migration generation

To generate migrations you should run:
```bash
# For automatic change detection.
alembic revision --autogenerate

# For empty file generation.
alembic revision
```

## Running tests

If you want to run it in docker, simply run:

```bash
docker compose -f deploy/docker-compose.yml --project-directory . run --rm api pytest -vv .
docker compose -f deploy/docker-compose.yml --project-directory . down
```

For running tests on your local machine.
1. you need to start a database.

I prefer doing it with docker:
```
docker run -p "5432:5432" -e "POSTGRES_PASSWORD=auo_project" -e "POSTGRES_USER=auo_project" -e "POSTGRES_DB=auo_project" postgres:13.6-bullseye
```


2. Run the pytest.
```bash
pytest -vv .
```

```bash
pytest --cov-report term --cov=auo_project auo_project/tests/
```

## Shell
```bash
poetry run python -m auo_project.cli shell
```

## Streamlit
```bash
PYTHONPATH=$PWD poetry run streamlit run auo_project/streamlit/web_app.py
```

## rewrite_file
```
await rewrite_file("d0332b96-21e3-49cb-9da8-d4f6e4798892")
```


## zip files
```
find . -d 1 -type dir -exec zip -r {}.zip {} \;
```


資料庫關閉 ssl
move to azure db
CREATE ROLE auo_project with login password 'password';
pg_restore -h auohealth-app.postgres.database.azure.com -U auo_admin -d auo_project --no-owner --role=auo_admin "$db_dump_file"

# 搬資料 prd -> dev

-- org id: 9514ea88-b530-4887-ac1e-598d300eaaa8
-- user id: 89cab69c-d789-4aae-865f-3f97024fe781
select '89cab69c-d789-4aae-865f-3f97024fe781' as owner_id, upload_status, file_number, start_from, end_to, is_active, created_at, updated_at, id, display_file_number
from app.uploads
where owner_id in (select id from app.auth_users where org_id = (select id
from app.auth_orgs
where name = 'nricm'))
;

select name, '89cab69c-d789-4aae-865f-3f97024fe781' as owner_id, upload_id, file_status, size, location, is_dup, is_valid, memo, created_at, updated_at, id
from app.upload_files
where owner_id in (select id from app.auth_users where org_id = (select id
from app.auth_orgs
where name = 'nricm'))
;

select sid, name, birth_date, sex, memo, standard_measure_id, is_active, created_at, updated_at, id, last_measure_time, number, proj_num, '9514ea88-b530-4887-ac1e-598d300eaaa8' as org_id
from measure.subjects
where org_id = (select id
from app.auth_orgs
where name = 'nricm')

;

select subject_id, file_id, '9514ea88-b530-4887-ac1e-598d300eaaa8' as org_id, uid, number, has_measure, has_bcq, has_tongue, has_memo, has_low_pass_rate, measure_time, measure_operator, mean_prop_range_1_l_cu, mean_prop_range_2_l_cu, mean_prop_range_3_l_cu, mean_prop_range_1_l_qu, mean_prop_range_2_l_qu, mean_prop_range_3_l_qu, mean_prop_range_1_l_ch, mean_prop_range_2_l_ch, mean_prop_range_3_l_ch, mean_prop_range_1_r_cu, mean_prop_range_2_r_cu, mean_prop_range_3_r_cu, mean_prop_range_1_r_qu, mean_prop_range_2_r_qu, mean_prop_range_3_r_qu, mean_prop_range_1_r_ch, mean_prop_range_2_r_ch, mean_prop_range_3_r_ch, mean_prop_range_max_l_cu, mean_prop_range_max_l_qu, mean_prop_range_max_l_ch, mean_prop_range_max_r_cu, mean_prop_range_max_r_qu, mean_prop_range_max_r_ch, max_amp_depth_of_range_l_cu, max_amp_depth_of_range_l_qu, max_amp_depth_of_range_l_ch, max_amp_depth_of_range_r_cu, max_amp_depth_of_range_r_qu, max_amp_depth_of_range_r_ch, max_amp_value_l_cu, max_amp_value_l_qu, max_amp_value_l_ch, max_amp_value_r_cu, max_amp_value_r_qu, max_amp_value_r_ch, irregular_hr_l_cu, irregular_hr_l_qu, irregular_hr_l_ch, irregular_hr_r_cu, irregular_hr_r_qu, irregular_hr_r_ch, irregular_hr_l, irregular_hr_type_l, irregular_hr_r, irregular_hr_type_r, irregular_hr, max_slope_value_l_cu, max_slope_value_l_qu, max_slope_value_l_ch, max_slope_value_r_cu, max_slope_value_r_qu, max_slope_value_r_ch, strength_l_cu, strength_l_qu, strength_l_ch, strength_r_cu, strength_r_qu, strength_r_ch, width_l_cu, width_l_qu, width_l_ch, width_r_cu, width_r_qu, width_r_ch, sex, age, height, weight, bmi, sbp, dbp, judge_time, judge_dr, hr_l, hr_r, special_l, special_r, comment, memo, proj_num, is_active, created_at, updated_at, id, ver, static_max_amp_l_cu, static_max_amp_l_qu, static_max_amp_l_ch, static_max_amp_r_cu, static_max_amp_r_qu, static_max_amp_r_ch, static_range_start_l_cu, static_range_start_l_qu, static_range_start_l_ch, static_range_start_r_cu, static_range_start_r_qu, static_range_start_r_ch, static_range_end_l_cu, static_range_end_l_qu, static_range_end_l_ch, static_range_end_r_cu, static_range_end_r_qu, static_range_end_r_ch, xingcheng_l_cu, xingcheng_l_qu, xingcheng_l_ch, xingcheng_r_cu, xingcheng_r_qu, xingcheng_r_ch, range_length_l_cu, range_length_l_qu, range_length_l_ch, range_length_r_cu, range_length_r_qu, range_length_r_ch, pass_rate_l_cu, pass_rate_l_qu, pass_rate_l_ch, pass_rate_r_cu, pass_rate_r_qu, pass_rate_r_ch, select_static_l_cu, select_static_l_qu, select_static_l_ch, select_static_r_cu, select_static_r_qu, select_static_r_ch
from measure.infos
where org_id = (select id
from app.auth_orgs
where name = 'nricm')
;

select *
from measure.bcqs
where measure_id in (
select id
from measure.infos
where org_id = (select id
from app.auth_orgs
where name = 'nricm')
)
;

select *
from measure.statistics
where measure_id in (
select id
from measure.infos
where org_id = (select id
from app.auth_orgs
where name = 'nricm')
)
;

select *
from measure.surveys;

select *
from measure.survey_results
where measure_id in (
select id
from measure.infos
where org_id = (select id
from app.auth_orgs
where name = 'nricm')
)
;

-- copy img
select *
from measure.tongues
where measure_id in (
select id
from measure.infos
where org_id = (select id
from app.auth_orgs
where name = 'nricm')
)
;

select *
from measure.raw_data
where measure_id in (
select id
from measure.infos
where org_id = (select id
from app.auth_orgs
where name = 'nricm')
)
;


subject tags
```
update measure.subjects
set tag_ids = '{fc5f348b-1e38-453c-96e5-b76a08b1bedd,ad2f60d3-de7f-4163-b0bf-b67f8a058d5f}'
where right(regexp_replace(id::text, '[\-a-zA-Z]', '', 'g'), 3)::int % 10 = 0
;
update measure.subjects
set tag_ids = '{ad2f60d3-de7f-4163-b0bf-b67f8a058d5f,92e23770-bc50-413e-ae6a-3339c59d0e95,2f9c1e6e-9cdf-4a0e-9ed1-5a47ce7a975c,ad2f60d3-de7f-4163-b0bf-b67f8a058d5f,01ebb427-898c-4106-9472-8ea5449e6176,fc5f348b-1e38-453c-96e5-b76a08b1bedd}
'
where right(regexp_replace(id::text, '[\-a-zA-Z]', '', 'g'), 3)::int % 10 = 1
;
update measure.subjects
set tag_ids = '{8054fa5a-b635-4225-8a16-52376a23d73d,c2d78d49-4af8-4e5f-bb1a-3b2288a72f13}'
where right(regexp_replace(id::text, '[\-a-zA-Z]', '', 'g'), 3)::int % 10 = 2;

update measure.subjects
set tag_ids = '{3af673a4-a3ec-47fc-a554-231e593ca117,2f9c1e6e-9cdf-4a0e-9ed1-5a47ce7a975c,499b29fa-3303-4597-b017-f2bb5b16450e}
'
where right(regexp_replace(id::text, '[\-a-zA-Z]', '', 'g'), 3)::int % 10 = 3;


update measure.subjects
set tag_ids = '{3af673a4-a3ec-47fc-a554-231e593ca117,499b29fa-3303-4597-b017-f2bb5b16450e}
'
where right(regexp_replace(id::text, '[\-a-zA-Z]', '', 'g'), 3)::int % 10 = 4;

update measure.subjects
set tag_ids = '{499b29fa-3303-4597-b017-f2bb5b16450e}'
where right(regexp_replace(id::text, '[\-a-zA-Z]', '', 'g'), 3)::int % 10 = 5;

update measure.subjects
set tag_ids = '{8054fa5a-b635-4225-8a16-52376a23d73d,c2d78d49-4af8-4e5f-bb1a-3b2288a72f13}'
where right(regexp_replace(id::text, '[\-a-zA-Z]', '', 'g'), 3)::int % 10 = 6;


update measure.subjects
set proj_num = 'project_number1'
where right(regexp_replace(id::text, '[\-a-zA-Z]', '', 'g'), 3)::int % 4 = 0;

update measure.subjects
set proj_num = 'project_number2'
where right(regexp_replace(id::text, '[\-a-zA-Z]', '', 'g'), 3)::int % 4 = 1;

update measure.subjects
set proj_num = 'project_number3'
where right(regexp_replace(id::text, '[\-a-zA-Z]', '', 'g'), 3)::int % 4 = 2;

update measure.infos
set proj_num = measure.subjects.proj_num
from measure.subjects
where measure.subjects.id = measure.infos.subject_id
;
```

```
from azure.storage.blob import BlobServiceClient

AZURE_STORAGE_ACCOUNT_INTERNET="auohealthpublic"
AZURE_STORAGE_KEY_INTERNET="OV6EJHHoe+..fR+ASt9a8kSg==" 
AZURE_STORAGE_ACCOUNT_INTERNET="auohealthpublic"

subject_ids = []
dev_container="dev-image"
prd_container = "image"

src_blob_service = BlobServiceClient(
    account_url=f"https://{AZURE_STORAGE_ACCOUNT_INTERNET}.blob.core.windows.net",
    credential={
        "account_name": AZURE_STORAGE_ACCOUNT_INTERNET,
        "account_key": AZURE_STORAGE_KEY_INTERNET,
    },
)
dest_blob_service = BlobServiceClient(
    account_url=f"https://{AZURE_STORAGE_ACCOUNT_INTERNET}.blob.core.windows.net",
    credential={
        "account_name": AZURE_STORAGE_ACCOUNT_INTERNET,
        "account_key": AZURE_STORAGE_KEY_INTERNET,
    },
)

start_index = subject_ids.index("23a31e5f-a85b-4515-b4e0-0cb2c01129f6")
for subject_id in subject_ids[start_index:]:
    subject_id = str(subject_id)
    print(f"Copying subject {subject_id}")
    for blob in src_blob_service.get_container_client(prd_container).list_blobs(name_starts_with=subject_id):
        print(f"Copying {blob.name}")
        dest_blob_client = dest_blob_service.get_blob_client(
            container=dev_container,
            blob=blob.name,
        )

        if dest_blob_client.exists():
            print(f"Blob {blob.name} already exists in dev")
            continue
        src_blob = src_blob_service.get_blob_client(container=prd_container, blob=blob.name)
        object_content = src_blob.download_blob().readall()

        dest_blob_client = dest_blob_service.get_blob_client(
            container=dev_container,
            blob=blob.name,
        )

        dest_blob_client.upload_blob(object_content, overwrite=True)
    print(f"Finished copying subject {subject_id}")
```

# 匯入問卷
scp 檔案，例如
scp 20240728\ 中醫診斷數位化群體性研究自評問卷_processed.xlsx azure-api-auohealth:~/workspace/
改 survey.py
scp auo_project/core/survey.py azure-api-auohealth:~/workspace/auo_project/core/survey.py
restart api? or vim?

run below code
```

from auo_project.db.session import SessionLocal

from auo_project.core.survey import save_survey_result

await save_survey_result("nricm", ["nricm 問卷"])

```

# 新增使用者


```
poetry run python -m auo_project.cli shell
await create_user(org_name="x_medical_center", username="vivian.nw.chen@auo.com", password="", email="vivian.nw.chen@auo.com", full_name="Vivian Chen")
```

# 改使用者密碼
```
from auo_project.db.session import SessionLocal
db_session = SessionLocal()

from auo_project import crud, schemas

user = await crud.user.get_by_email(db_session=db_session, email="vivian.nw.chen@auo.com")
user = await crud.user.update(
    db_session=db_session,
    db_obj=user,
    obj_in=schemas.UserUpdate(password="")
)

```

# VM 環境
```
# https://docs.docker.com/engine/install/ubuntu/
sudo apt-get remove docker docker-engine docker.io containerd runc

curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh ./get-docker.sh
apt-get install -y uidmap
dockerd-rootless-setuptool.sh install

# nginx
sudo apt-get install nginx -y

# edit nginx config to setup ssl/tls
# https://www.digicert.com/kb/csr-ssl-installation/nginx-openssl.htm
# ./etc/nginx/sites-available/auo-api
```
