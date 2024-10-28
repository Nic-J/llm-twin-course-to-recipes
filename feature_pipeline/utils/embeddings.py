from typing import cast

import numpy as np
from InstructorEmbedding import INSTRUCTOR
from sentence_transformers.SentenceTransformer import SentenceTransformer

from feature_pipeline.config import settings


def embedd_text(text: str) -> np.ndarray:
    model = SentenceTransformer(settings.EMBEDDING_MODEL_ID)
    embeddings = model.encode(text, convert_to_numpy=True)
    return cast(np.ndarray, embeddings)


def embedd_repositories(text: str):
    model = INSTRUCTOR("hkunlp/instructor-xl")
    sentence = text
    instruction = "Represent the structure of the repository"
    return model.encode([instruction, sentence])
    return model.encode([instruction, sentence])
