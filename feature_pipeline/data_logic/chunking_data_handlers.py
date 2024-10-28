from __future__ import annotations

import hashlib
from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from feature_pipeline.models.base import DataModel
from feature_pipeline.models.chunk import (
    ArticleChunkModel,
    PostChunkModel,
    RepositoryChunkModel,
)
from feature_pipeline.models.clean import (
    ArticleCleanedModel,
    PostCleanedModel,
    RepositoryCleanedModel,
)
from feature_pipeline.utils.chunking import chunk_text

CleanedDataModel = TypeVar("CleanedDataModel", bound=DataModel)
ChunkedDataModel = TypeVar("ChunkedDataModel")


class ChunkingDataHandler(ABC, Generic[CleanedDataModel, ChunkedDataModel]):
    """
    Abstract class for all Chunking data handlers.
    All data transformations logic for the chunking step is done here
    """

    @abstractmethod
    def chunk(self, data_model: CleanedDataModel) -> list[ChunkedDataModel]:
        pass


class PostChunkingHandler(ChunkingDataHandler[PostCleanedModel, PostChunkModel]):
    def chunk(self, data_model: PostCleanedModel) -> list[PostChunkModel]:
        data_models_list = []

        text_content = data_model.cleaned_content
        chunks = chunk_text(text_content)

        for chunk in chunks:
            model = PostChunkModel(
                entry_id=data_model.entry_id,
                platform=data_model.platform,
                chunk_id=hashlib.md5(chunk.encode()).hexdigest(),
                chunk_content=chunk,
                author_id=data_model.author_id,
                image=data_model.image if data_model.image else None,
                type=data_model.type,
            )
            data_models_list.append(model)

        return data_models_list


class ArticleChunkingHandler(
    ChunkingDataHandler[ArticleCleanedModel, ArticleChunkModel]
):
    def chunk(self, data_model: ArticleCleanedModel) -> list[ArticleChunkModel]:
        data_models_list = []

        text_content = data_model.cleaned_content
        chunks = chunk_text(text_content)

        for chunk in chunks:
            model = ArticleChunkModel(
                entry_id=data_model.entry_id,
                platform=data_model.platform,
                link=data_model.link,
                chunk_id=hashlib.md5(chunk.encode()).hexdigest(),
                chunk_content=chunk,
                author_id=data_model.author_id,
                type=data_model.type,
            )
            data_models_list.append(model)

        return data_models_list


class RepositoryChunkingHandler(
    ChunkingDataHandler[RepositoryCleanedModel, RepositoryChunkModel]
):
    def chunk(self, data_model: RepositoryCleanedModel) -> list[RepositoryChunkModel]:
        data_models_list = []

        text_content = data_model.cleaned_content
        chunks = chunk_text(text_content)

        for chunk in chunks:
            model = RepositoryChunkModel(
                entry_id=data_model.entry_id,
                name=data_model.name,
                link=data_model.link,
                chunk_id=hashlib.md5(chunk.encode()).hexdigest(),
                chunk_content=chunk,
                owner_id=data_model.owner_id,
                type=data_model.type,
            )
            data_models_list.append(model)

        return data_models_list
