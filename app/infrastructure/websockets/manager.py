import json
from abc import (
    ABC,
    abstractmethod,
)
from collections import defaultdict
from dataclasses import (
    dataclass,
    field,
)
from typing import Any

from fastapi import WebSocket


@dataclass
class BaseConnectionManager(ABC):
    connections_map: dict[str, list[WebSocket]] = field(
        default_factory=lambda: defaultdict(list),
        kw_only=True,
    )

    @abstractmethod
    async def accept_connection(self, websocket: WebSocket, key: str): ...

    @abstractmethod
    async def remove_connection(self, websocket: WebSocket, key: str): ...

    @abstractmethod
    async def send_json_to_all(self, key: str, data: dict[str, Any]): ...


@dataclass
class ConnectionManager(BaseConnectionManager):
    async def accept_connection(self, websocket: WebSocket, key: str):
        # WebSocket уже принят в endpoint, просто добавляем в список
        self.connections_map[key].append(websocket)

    async def remove_connection(self, websocket: WebSocket, key: str):
        if websocket in self.connections_map[key]:
            self.connections_map[key].remove(websocket)

    async def send_json_to_all(self, key: str, data: dict[str, Any]):
        """Отправляет JSON данные всем подключенным клиентам по ключу."""
        message = json.dumps(data)
        disconnected = []
        for websocket in self.connections_map[key]:
            try:
                await websocket.send_text(message)
            except Exception:
                disconnected.append(websocket)

        # Удаляем отключенные соединения
        for websocket in disconnected:
            await self.remove_connection(websocket, key)
