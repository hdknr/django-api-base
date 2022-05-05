ARG BASE_IMAGE=python
ARG TAG=3.10.4
FROM ${BASE_IMAGE}:${TAG} as server

ENV APP_BASE=/usr/src/app \
    LIB_BASE=/usr/src/lib \
    POETRY_VERSION=1.0.10 \
    NAME=django-api-base \
    PATH="/root/.poetry/bin:$PATH"

WORKDIR ${LIB_BASE}/${NAME}
COPY apibase ${LIB_BASE}/${NAME}/apibase
COPY tests ${LIB_BASE}/${NAME}/tests
COPY poetry.lock ${LIB_BASE}/${NAME}/poetry.lock
COPY pyproject.toml  ${LIB_BASE}/${NAME}/pyproject.toml
RUN poetry install  

CMD ["sleep", "infinity"]