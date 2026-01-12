import json
from typing import (
    Any,
    Dict,
)

from aiokafka import AIOKafkaProducer

from settings.kafka import KafkaConfig


class KafkaProducer:
    """Kafka producer for sending events."""

    def __init__(self, config: KafkaConfig) -> None:
        self.config = config
        self._producer: AIOKafkaProducer | None = None

    async def start(self) -> None:
        """Start the Kafka producer."""
        self._producer = AIOKafkaProducer(
            bootstrap_servers=self.config.kafka_url,
            value_serializer=lambda v: json.dumps(v).encode("utf-8"),
        )
        await self._producer.start()

    async def stop(self) -> None:
        """Stop the Kafka producer."""
        if self._producer:
            await self._producer.stop()

    async def send_event(
        self,
        event_type: str,
        aggregate_type: str,
        aggregate_id: str,
        payload: Dict[str, Any],
    ) -> None:
        """Send event to Kafka.

        Args:
            event_type: Type of the event (e.g., user.created)
            aggregate_type: Type of the aggregate (e.g., user)
            aggregate_id: ID of the aggregate
            payload: Event payload data

        """
        if not self._producer:
            raise RuntimeError("Producer is not started")

        topic = f"{self.config.kafka_topic_prefix}.{aggregate_type}.events"

        event = {
            "event_type": event_type,
            "aggregate_type": aggregate_type,
            "aggregate_id": aggregate_id,
            "payload": payload,
        }

        await self._producer.send_and_wait(topic, event)
