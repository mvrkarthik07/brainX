import faiss
import numpy as np

from brain.config.settings import FAISS_INDEX_PATH, DEFAULT_USER_DIR, EMBEDDING_DIM

def create_empty_index() -> faiss.Index: ## creates empty index with inner product metric, which is equivalent to cosine similarity when embeddings are normalised
    """
    User inner product search.
    Later we will normalise embeddings so this behaves like cosine similarity.
    """
    return faiss.IndexFlatIP(EMBEDDING_DIM)
def save_index(index: faiss.Index): # saves the index to disk, ensuring the directory exists
    
    
    DEFAULT_USER_DIR.mkdir(parents=True, exist_ok=True)
    faiss.write_index(index, str(FAISS_INDEX_PATH))

def load_or_create_index() -> faiss.Index: # loads the index from disk if it exists, otherwise creates a new one and saves it
    DEFAULT_USER_DIR.mkdir(parents=True, exist_ok=True)
    if FAISS_INDEX_PATH.exists():
        return faiss.read_index(str(FAISS_INDEX_PATH))
    
    index = create_empty_index()
    save_index(index)
    return index

def normalize_vector(vector: np.ndarray) -> np.ndarray: # normalises a vector to unit length
    vector = vector.astype(np.float32)

    norm = np.linalg.norm(vector)
    if norm == 0:
        raise ValueError("Cannot normalize zero-length vector")
    return vector / norm

def add_dummy_vector() -> int: # adds a dummy vector to the index to ensure it is not empty, which can cause issues with some versions of faiss. Returns the total number of vectors in the index after adding the dummy.
    index = load_or_create_index()
    dummy_vector = np.zeros((1, EMBEDDING_DIM), dtype=np.float32)
    dummy = dummy / np.linalg.norm(dummy_vector, axis=1, keepdims=True)
    index.add(dummy_vector)
    save_index(index)
    return index.ntotal 

def faiss_health() -> dict: ##checks the health of faiss by trying to load or create the index, and returns some information about it. If there is an error, it returns the error message.

    try:

        index = load_or_create_index()

        return {

            "ok": True,

            "index_path": str(FAISS_INDEX_PATH),

            "dimension": index.d,

            "vectors": index.ntotal,

            "index_type": type(index).__name__,

        }

    except Exception as exc:

        return {

            "ok": False,

            "error": str(exc),

        }




