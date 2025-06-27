import json
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Tuple


class NIPSQA:
    """
    NIPSQA class for RAG-based Question Answering over NIPS documentation.

    Args:
        dataset_path (str): Path to the JSONL file with question-answer pairs.
    """

    def __init__(self, dataset_path: str) -> None:
        self.dataset_path = dataset_path
        self.data = self._load_dataset()
        self.embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
        self.index, self.index_to_qa = self._build_faiss_index()

    def _load_dataset(self) -> List[Dict[str, str]]:
        """
        Loads the Q&A dataset from the JSONL file.

        Returns:
            List[Dict[str, str]]: List of Q&A pairs.
        """
        data = []
        with open(self.dataset_path, "r", encoding="utf-8") as f:
            for line in f:
                data.append(json.loads(line))
        return data

    def _build_faiss_index(self) -> Tuple[faiss.IndexFlatL2, Dict[int, Dict[str, str]]]:
        """
        Builds a FAISS index from the dataset.

        Returns:
            Tuple[faiss.IndexFlatL2, Dict[int, Dict[str, str]]]: The FAISS index and a mapping from index to Q&A pairs.
        """
        index = faiss.IndexFlatL2(384)  # 384 is the dim of MiniLM-L6-v2
        index_to_qa = {}
        embeddings = []

        for i, item in enumerate(self.data):
            combined_text = f"Question: {item['question']} Answer: {item['answer']}"
            embedding = self.embedding_model.encode(combined_text, show_progress_bar=False)
            embeddings.append(embedding)
            index_to_qa[i] = item

        embeddings_np = np.array(embeddings).astype("float32")
        index.add(embeddings_np)  # x parameter isn't required since embeddings_np converts to a 2D properly

        return index, index_to_qa

    def retrieve_top_k(self, query: str, k: int = 3) -> List[Dict[str, str]]:
        """
        Retrieves the top-k most relevant Q&A pairs for a given query.

        Args:
            query (str): The user query.
            k (int, optional): Number of top results to return. Default to 3.

        Returns:
            List[Dict[str, str]]: List of top-k Q&A pairs.
        """
        query_embedding = self.embedding_model.encode(query, show_progress_bar=False).astype("float32")
        query_embedding = np.expand_dims(query_embedding, axis=0)

        distances, indices = self.index.search(query_embedding, k)
        results = [self.index_to_qa[idx] for idx in indices[0]]

        return results

    def compose_prompt(self, user_question: str, retrieved_qa_pairs: List[Dict[str, str]]) -> str:
        """
        Composes a full prompt for the LLM using retrieved Q&A pairs.

        Args:
            user_question (str): The user question.
            retrieved_qa_pairs (List[Dict[str, str]]): Retrieved Q&A pairs.

        Returns:
            str: The formatted prompt.
        """
        context = ""
        for pair in retrieved_qa_pairs:
            context += f"Q: {pair['question']}\nA: {pair['answer']}\n\n"

        prompt = (
            f"You are a helpful assistant specialized in the NIPS documentation.\n\n"
            f"Here is some relevant context:\n\n"
            f"{context}"
            f"User Question: {user_question}\n"
            f"Answer:"
        )
        return prompt
