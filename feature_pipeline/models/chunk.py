from feature_pipeline.models.base import DataModel


class PostChunkModel(DataModel[str]):
    platform: str
    chunk_id: str
    chunk_content: str
    author_id: str
    image: str | None = None


class ArticleChunkModel(DataModel[str]):
    platform: str
    link: str
    chunk_id: str
    chunk_content: str
    author_id: str


class RepositoryChunkModel(DataModel[str]):
    name: str
    link: str
    chunk_id: str
    chunk_content: str
    owner_id: str
