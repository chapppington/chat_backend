import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from infrastructure.database.gateways.postgres import Database
from infrastructure.messaging.kafka_producer import KafkaProducer
from infrastructure.workers.outbox_worker import OutboxWorker

from settings.config import Config
from settings.kafka import KafkaConfig


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Global worker instance
worker: OutboxWorker | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for FastAPI app."""
    global worker

    # Initialize dependencies
    config = Config()
    kafka_config = KafkaConfig()

    database = Database(
        url=config.postgres_connection_uri,
        ro_url=config.postgres_connection_uri,
    )

    kafka_producer = KafkaProducer(config=kafka_config)

    # Create and start worker
    worker = OutboxWorker(
        database=database,
        kafka_producer=kafka_producer,
        batch_size=10,
        poll_interval=1.0,
    )

    # Start worker in background task
    worker_task = asyncio.create_task(worker.run())

    logger.info("Outbox worker service started")

    yield

    # Cleanup
    logger.info("Stopping outbox worker service...")
    if worker:
        await worker.stop()
    worker_task.cancel()
    try:
        await worker_task
    except asyncio.CancelledError:
        pass
    logger.info("Outbox worker service stopped")


def create_app() -> FastAPI:
    """Create FastAPI application for outbox worker."""
    app = FastAPI(
        title="Outbox Worker",
        description="Worker service for processing outbox events and sending them to Kafka",
        lifespan=lifespan,
    )

    @app.get("/health")
    async def healthcheck():
        """Health check endpoint."""
        return {"status": "ok"}

    return app
