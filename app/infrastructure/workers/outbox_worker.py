import asyncio
import logging
from datetime import datetime

from infrastructure.database.gateways.postgres import Database
from infrastructure.database.models.outbox.outbox import (
    OutboxEventModel,
    OutboxEventStatus,
)
from infrastructure.messaging.kafka_producer import KafkaProducer
from sqlalchemy import (
    select,
    update,
)


logger = logging.getLogger(__name__)


class OutboxWorker:
    """Worker for processing outbox events and sending them to Kafka."""

    def __init__(
        self,
        database: Database,
        kafka_producer: KafkaProducer,
        batch_size: int = 10,
        poll_interval: float = 1.0,
    ) -> None:
        self.database = database
        self.kafka_producer = kafka_producer
        self.batch_size = batch_size
        self.poll_interval = poll_interval
        self._running = False

    async def start(self) -> None:
        """Start the outbox worker."""
        logger.info("Starting outbox worker...")
        await self.kafka_producer.start()
        self._running = True
        logger.info("Outbox worker started")

    async def stop(self) -> None:
        """Stop the outbox worker."""
        logger.info("Stopping outbox worker...")
        self._running = False
        await self.kafka_producer.stop()
        logger.info("Outbox worker stopped")

    async def process_events(self) -> None:
        """Process pending outbox events."""
        while self._running:
            try:
                # Получаем список событий для обработки
                async with self.database.get_read_only_session() as session:
                    stmt = (
                        select(OutboxEventModel)
                        .where(OutboxEventModel.status == OutboxEventStatus.PENDING.value)
                        .limit(self.batch_size)
                        .order_by(OutboxEventModel.created_at)
                    )
                    result = await session.execute(stmt)
                    events = result.scalars().all()

                if not events:
                    await asyncio.sleep(self.poll_interval)
                    continue

                logger.info(f"Found {len(events)} pending events to process")

                # Обрабатываем каждое событие в отдельной транзакции
                for event in events:
                    try:
                        # Отправляем событие в Kafka
                        await self.kafka_producer.send_event(
                            event_type=event.event_type,
                            aggregate_type=event.aggregate_type,
                            aggregate_id=event.aggregate_id,
                            payload=event.payload,
                        )

                        # Обновляем статус события в отдельной транзакции
                        async with self.database.get_session() as update_session:
                            update_stmt = (
                                update(OutboxEventModel)
                                .where(OutboxEventModel.oid == event.oid)
                                .values(
                                    status=OutboxEventStatus.PROCESSED.value,
                                    processed_at=datetime.utcnow().isoformat(),
                                )
                            )
                            await update_session.execute(update_stmt)
                            # Commit происходит автоматически при выходе из контекста

                        logger.info(f"Processed event {event.oid} of type {event.event_type}")
                    except Exception as e:
                        logger.error(
                            f"Error processing event {event.oid}: {e}",
                            exc_info=True,
                        )
                        # В случае ошибки событие остается со статусом PENDING
                        # и будет обработано в следующей итерации

            except Exception as e:
                logger.error(f"Error in outbox worker: {e}", exc_info=True)
                await asyncio.sleep(self.poll_interval)

    async def run(self) -> None:
        """Run the worker loop."""
        await self.start()
        try:
            await self.process_events()
        finally:
            await self.stop()
