DC = docker compose
STORAGES_FILE = docker_compose/storages.yaml
STORAGES_CONTAINER = postgres
MESSAGING_FILE = docker_compose/messaging.yaml
MESSAGING_CONTAINER = main-kafka
LOGS = docker logs
ENV = --env-file .env
EXEC = docker exec -it
EXEC_NO_TTY = docker exec
APP_FILE = docker_compose/app.yaml
APP_CONTAINER = main-app
WORKER_FILE = docker_compose/worker.yaml
WORKER_CONTAINER = outbox-worker

.PHONY: all
all:
	${DC} -f ${STORAGES_FILE} -f ${APP_FILE} -f ${MESSAGING_FILE} -f ${WORKER_FILE} ${ENV} up --build -d

.PHONY: all-down
all-down:
	${DC} -f ${STORAGES_FILE} -f ${APP_FILE} -f ${MESSAGING_FILE} -f ${WORKER_FILE} ${ENV} down

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


.PHONY: messaging
messaging:
	${DC} -f ${MESSAGING_FILE} ${ENV} up  --build -d

.PHONY: messaging-down
messaging-down:
	${DC} -f ${MESSAGING_FILE} ${ENV} down

.PHONY: messaging-logs
messaging-logs:
	${LOGS} ${MESSAGING_CONTAINER} -f


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

.PHONY: worker-up
worker-up:
	${DC} -f ${STORAGES_FILE} -f ${MESSAGING_FILE} -f ${WORKER_FILE} ${ENV} up --build -d

.PHONY: worker-down
worker-down:
	${DC} -f ${WORKER_FILE} ${ENV} down

.PHONY: worker-logs
worker-logs:
	${LOGS} ${WORKER_CONTAINER} -f
