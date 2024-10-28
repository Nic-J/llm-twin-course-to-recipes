from dataclasses import dataclass, field

from qdrant_client import QdrantClient, models
from qdrant_client.http.exceptions import UnexpectedResponse
from qdrant_client.http.models import Batch, Distance, VectorParams

from feature_pipeline.config import settings
from feature_pipeline.utils.logging import get_logger

logger = get_logger(__name__)


@dataclass
class QdrantDatabaseConnector:
    _instance: QdrantClient = field(init=False)
    host: str = settings.QDRANT_DATABASE_HOST
    port: int = settings.QDRANT_DATABASE_PORT
    url: str | None = settings.QDRANT_CLOUD_URL
    api_key: str | None = settings.QDRANT_APIKEY

    def __post_init__(self) -> None:
        if self._instance is None:
            try:
                if self.url:
                    self._instance = QdrantClient(url=self.url, api_key=self.api_key)
                else:
                    self._instance = QdrantClient(host=self.host, port=self.port)
            except UnexpectedResponse:
                logger.exception(
                    "Couldn't connect to Qdrant.",
                    host=self.host,
                    port=self.port,
                    url=self.url,
                )

                raise

    def get_collection(self, collection_name: str):
        return self._instance.get_collection(collection_name=collection_name)

    def create_non_vector_collection(self, collection_name: str):
        self._instance.create_collection(
            collection_name=collection_name, vectors_config={}
        )

    def create_vector_collection(self, collection_name: str):
        self._instance.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(
                size=settings.EMBEDDING_SIZE, distance=Distance.COSINE
            ),
        )

    def write_data(self, collection_name: str, points: Batch):
        try:
            self._instance.upsert(collection_name=collection_name, points=points)
        except Exception:
            logger.exception("An error occurred while inserting data.")

            raise

    def search(
        self,
        collection_name: str,
        query_vector: list,
        query_filter: models.Filter | None = None,
        limit: int = 3,
    ) -> list:
        return self._instance.search(
            collection_name=collection_name,
            query_vector=query_vector,
            query_filter=query_filter,
            limit=limit,
        )

    def scroll(self, collection_name: str, limit: int):
        return self._instance.scroll(collection_name=collection_name, limit=limit)

    def close(self):
        if self._instance:
            self._instance.close()

            logger.info("Connected to database has been closed.")

            logger.info("Connected to database has been closed.")
