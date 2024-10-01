FROM python:3.11.10-bullseye

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN pip install poetry==1.8.2
ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

WORKDIR /todo

COPY pyproject.toml poetry.lock ./
RUN poetry install --no-root

COPY . .


ENTRYPOINT ["docker-entrypoint.sh"]
CMD  ["poetry", "run", "python", "todo/manage.py", "runserver", "0.0.0.0:8000"]