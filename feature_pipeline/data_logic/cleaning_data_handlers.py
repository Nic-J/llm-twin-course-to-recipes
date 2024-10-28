from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from feature_pipeline.models.clean import (
    ArticleCleanedModel,
    PostCleanedModel,
    RepositoryCleanedModel,
)
from feature_pipeline.models.raw import (
    ArticleRawModel,
    PostsRawModel,
    RepositoryRawModel,
)
from feature_pipeline.utils.cleaning import clean_text

RawModelT = TypeVar("RawModelT")
CleanedModelT = TypeVar("CleanedModelT")


class CleaningDataHandler(ABC, Generic[RawModelT, CleanedModelT]):
    """
    Abstract class for all cleaning data handlers.
    All data transformations logic for the cleaning step is done here
    """

    @abstractmethod
    def clean(self, data_model: RawModelT) -> CleanedModelT:
        pass


class PostCleaningHandler(CleaningDataHandler[PostsRawModel, PostCleanedModel]):
    def clean(self, data_model: PostsRawModel) -> PostCleanedModel:
        return PostCleanedModel(
            entry_id=data_model.entry_id,
            platform=data_model.platform,
            cleaned_content=clean_text("".join(data_model.content.values())),
            author_id=data_model.author_id if data_model.author_id else "",
            image=data_model.image if data_model.image else None,
            type=data_model.type,
        )


class ArticleCleaningHandler(CleaningDataHandler[ArticleRawModel, ArticleCleanedModel]):
    def clean(self, data_model: ArticleRawModel) -> ArticleCleanedModel:
        return ArticleCleanedModel(
            entry_id=data_model.entry_id,
            platform=data_model.platform,
            link=data_model.link,
            cleaned_content=clean_text("".join(data_model.content.values())),
            author_id=data_model.author_id,
            type=data_model.type,
        )


class RepositoryCleaningHandler(
    CleaningDataHandler[RepositoryRawModel, RepositoryCleanedModel]
):
    def clean(self, data_model: RepositoryRawModel) -> RepositoryCleanedModel:
        return RepositoryCleanedModel(
            entry_id=data_model.entry_id,
            name=data_model.name,
            link=data_model.link,
            cleaned_content=clean_text("".join(data_model.content.values())),
            owner_id=data_model.owner_id,
            type=data_model.type,
        )
