DC = docker compose
STORAGES_FILE = docker_compose/storages.yaml
STORAGES_CONTAINER = postgres
LOGS = docker logs
ENV = --env-file .env
EXEC = docker exec -it
EXEC_NO_TTY = docker exec
APP_FILE = docker_compose/app.yaml
APP_CONTAINER = main-app

.PHONY: all
all:
	${DC} -f ${STORAGES_FILE} -f ${APP_FILE} ${ENV} up --build -d

.PHONY: all-down
all-down:
	${DC} -f ${STORAGES_FILE} -f ${APP_FILE} ${ENV} down

.PHONY: app-logs
app-logs:
	${LOGS} ${APP_CONTAINER} -f

.PHONY: app-shell
app-shell:
	${EXEC} ${APP_CONTAINER} bash


.PHONY: app-down
app-down:
	${DC} -f ${APP_FILE} ${ENV} down

.PHONY: app-up
app-up:
	${DC} -f ${STORAGES_FILE} -f ${APP_FILE} ${ENV} up --build -d main-app


.PHONY: storages
storages:
	${DC} -f ${STORAGES_FILE} ${ENV} up --build -d

.PHONY: storages-down
storages-down:
	${DC} -f ${STORAGES_FILE} ${ENV} down

.PHONY: storages-logs
storages-logs:
	${LOGS} ${STORAGES_CONTAINER} -f

.PHONY: postgres 
postgres:
	${EXEC} ${STORAGES_CONTAINER} psql -U postgres


.PHONY: precommit 
precommit:
	pre-commit run --all-files


.PHONY: migrations
migrations:
	${EXEC} ${APP_CONTAINER} alembic revision --autogenerate

.PHONY: migrate
migrate:
	${EXEC_NO_TTY} ${APP_CONTAINER} alembic upgrade head

.PHONY: test 
test:
	${EXEC} ${APP_CONTAINER} pytest
