FROM python:3.11.10-bullseye

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y netcat && apt-get clean

RUN pip install poetry==1.8.2
ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

WORKDIR /todo

COPY pyproject.toml poetry.lock ./
RUN poetry install --no-root

COPY docker-entrypoint.sh ./

COPY . .

ENTRYPOINT ["sh", "./docker-entrypoint.sh"]