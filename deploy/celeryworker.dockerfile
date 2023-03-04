FROM python:3.9.6-slim-buster

RUN python -m pip install pip==22.2.2 && \
   pip install poetry==1.2.0

# Configuring poetry
RUN poetry config virtualenvs.create false

# Copying requirements of a project
COPY pyproject.toml poetry.lock /app/src/
WORKDIR /app/src

# Installing requirements
RUN poetry install --no-dev

# Copying actuall application
COPY . /app/src/
RUN chmod +x /app/src/auo_project/worker-start.sh

CMD ["/app/src/auo_project/worker-start.sh"]
