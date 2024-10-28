import json
import time
from collections.abc import Iterable
from dataclasses import dataclass, field
from datetime import datetime
from typing import Generic, TypeVar

from bytewax.inputs import FixedPartitionedSource, StatefulSourcePartition
from config import settings
from mq import RabbitMQConnection
from pika.adapters.blocking_connection import BlockingChannel
from utils.logging import get_logger

logger = get_logger(__name__)

DataT = TypeVar("DataT")
MessageT = TypeVar("MessageT")


@dataclass
class RabbitMQPartition(StatefulSourcePartition, Generic[DataT, MessageT]):
    queue_name: str
    resume_state: MessageT | None = None
    connection: RabbitMQConnection = field(init=False)
    channel: BlockingChannel = field(init=False)
    _in_flight_msg_ids: set = field(init=False)

    def __post_init__(self):
        if self.resume_state is None:
            self._in_flight_msg_ids = set()
        self.connection = RabbitMQConnection()
        self.connection.connect()

        channel = self.connection.get_channel()
        if channel is None:
            raise ValueError("Channel not initialized")
        self.channel = channel

    def next_batch(self, sched: datetime | None) -> Iterable[DataT]:
        try:
            method_frame, header_frame, body = self.channel.basic_get(
                queue=self.queue_name, auto_ack=True
            )
        except Exception:
            logger.error(
                f"Error while fetching message from queue.", queue_name=self.queue_name
            )
            time.sleep(10)
            self.connection.connect()
            channel = self.connection.get_channel()
            if channel is None:
                raise ValueError("Channel not initialized")
            self.channel = channel
            return []

        if method_frame:
            message_id = method_frame.delivery_tag
            self._in_flight_msg_ids.add(message_id)
            return [json.loads(body)]
        else:
            return []

    def snapshot(self) -> MessageT | set:
        return self._in_flight_msg_ids

    def garbage_collect(self, state):
        closed_in_flight_msg_ids = state
        for msg_id in closed_in_flight_msg_ids:
            self.channel.basic_ack(delivery_tag=msg_id)
            self._in_flight_msg_ids.remove(msg_id)

    def close(self):
        self.channel.close()


class RabbitMQSource(FixedPartitionedSource):
    def list_parts(self) -> list[str]:
        return ["single partition"]

    def build_part(
        self, now: datetime, for_part: str, resume_state: MessageT | None = None
    ) -> StatefulSourcePartition[object, MessageT]:
        return RabbitMQPartition(queue_name=settings.RABBITMQ_QUEUE_NAME)
