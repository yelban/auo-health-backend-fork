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

## Docker

You can start the project with docker using this command:

```bash
docker compose -f deploy/docker-compose.yml --project-directory . up --build -d
```

If you want to develop in docker with autoreload add `-f deploy/docker-compose.dev.yml` to your docker command.
Like this:

```bash
docker compose -f deploy/docker-compose.yml -f deploy/docker-compose.dev.yml --project-directory . up -d
```

```bash
docker compose -f deploy/docker-compose.yml -f deploy/docker-compose.prd.yml --project-directory . up
```

This command exposes the web application on port 8000, mounts current directory and enables autoreload.

But you have to rebuild image every time you modify `poetry.lock` or `pyproject.toml` with this command:

```bash
docker compose -f deploy/docker-compose.yml --project-directory . build
```

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
## Opentelemetry

If you want to start your project with opentelemetry collector
you can add `-f ./deploy/docker-compose.otlp.yml` to your docker command.

Like this:

```bash
docker compose -f deploy/docker-compose.yml -f deploy/docker-compose.otlp.yml --project-directory . up
```

This command will start opentelemetry collector and jaeger.
After sending a requests you can see traces in jaeger's UI
at http://localhost:16686/.

This docker configuration is not supposed to be used in production.
It's only for demo purpose.

You can read more about opentelemetry here: https://opentelemetry.io/

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

## Kubernetes
To run your app in kubernetes
just run:
```bash
kubectl apply -f deploy/kube
```

It will create needed components.

If you haven't pushed to docker registry yet, you can build image locally.

```bash
docker compose -f deploy/docker-compose.yml --project-directory . build
docker save --output auo_project.tar auo_project:latest
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
await rewrite_file("c3d30600-9f91-45fc-9d98-0a16986646d6")
```


## zip files
```
find . -d 1 -type dir -exec zip -r {}.zip {} \;
```
