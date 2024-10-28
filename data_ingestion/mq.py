from logging import getLogger

import pika
from pika import BlockingConnection
from pika.adapters.blocking_connection import BlockingChannel
from pika.exceptions import AMQPConnectionError, UnroutableError

from data_ingestion.config import settings

logger = getLogger(__name__)


class RabbitMQConnection:
    """Singleton class to manage RabbitMQ connection."""

    _instance = None

    def __new__(
        cls,
        host: str = None,
        port: int = None,
        username: str = None,
        password: str = None,
        virtual_host: str = "/",
    ):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(
        self,
        host: str = None,
        port: int = None,
        username: str = None,
        password: str = None,
        virtual_host: str = "/",
        fail_silently: bool = False,
        **kwargs,
    ):
        self.host = host or settings.RABBITMQ_HOST
        self.port = port or settings.RABBITMQ_PORT
        self.username = username or settings.RABBITMQ_DEFAULT_USERNAME
        self.password = password or settings.RABBITMQ_DEFAULT_PASSWORD
        self.virtual_host = virtual_host
        self.fail_silently = fail_silently
        self._connection: BlockingConnection | None = None

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def connect(self):
        try:
            credentials = pika.PlainCredentials(self.username, self.password)

            self._connection = pika.BlockingConnection(
                pika.ConnectionParameters(
                    host=self.host,
                    port=self.port,
                    virtual_host=self.virtual_host,
                    credentials=credentials,
                )
            )
            logger.info("connected to rabbitmq")
        except AMQPConnectionError as e:
            print("Failed to connect to RabbitMQ:", e)
            if not self.fail_silently:
                raise e

    def get_channel(self) -> BlockingChannel:
        if self._connection is not None and self._connection.is_open:
            return self._connection.channel()
        raise Exception("Not connected to RabbitMQ")

    def close(self) -> None:
        if self._connection is not None and self._connection.is_open:
            self._connection.close()
            self._connection = None
            print("Closed RabbitMQ connection")


def publish_to_rabbitmq(queue_name: str, data: str):
    """Publish data to a RabbitMQ queue."""
    try:
        # Create an instance of RabbitMQConnection
        rabbitmq_conn = RabbitMQConnection()
        logger.info(f"Connected to RabbitMQ: {rabbitmq_conn.host}:{rabbitmq_conn.port}")

        # Establish connection
        with rabbitmq_conn:
            logger.info(f"attemping to open the channel")
            channel = rabbitmq_conn.get_channel()
            logger.info(
                f"opened channel {channel} on {rabbitmq_conn.host}:{rabbitmq_conn.port}"
            )

            # Ensure the queue exists
            channel.queue_declare(queue=queue_name, durable=True)
            logger.info(
                f"declared queue {queue_name} on {rabbitmq_conn.host}:{rabbitmq_conn.port}"
            )

            # Delivery confirmation
            channel.confirm_delivery()

            # Send data to the queue
            channel.basic_publish(
                exchange="",
                routing_key=queue_name,
                body=data,
                properties=pika.BasicProperties(
                    delivery_mode=2,  # make message persistent
                ),
            )
            print("Sent data to RabbitMQ:", data)
    except UnroutableError:
        print("Message could not be routed")
    except Exception as e:
        print(f"Error publishing to RabbitMQ: {e}")


if __name__ == "__main__":
    publish_to_rabbitmq("test_queue", "Hello, World!")
    publish_to_rabbitmq("test_queue", "Hello, World!")
