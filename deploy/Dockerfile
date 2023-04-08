FROM python:3.9.6-slim-buster

RUN python -m pip install pip==22.2.2 && \
   pip install poetry==1.2.0

# Configuring poetry
RUN poetry config virtualenvs.create false

# Copying requirements of a project
COPY pyproject.toml /app/src/
WORKDIR /app/src

# Installing requirements
RUN poetry install --only main

# Copying actuall application
COPY . /app/src/

# Ref: https://github.com/tiangolo/sqlmodel/pull/256
RUN poetry run python -m auo_project.patch_sqlmodel

RUN chmod +x /app/src/auo_project/worker-start.sh

CMD ["/usr/local/bin/python", "-m", "auo_project"]
