"""
knowledge_base.py
Retrieves relevant clinical guidelines from ChromaDB for each reasoning hop.
"""
import chromadb
from chromadb.utils import embedding_functions


class KnowledgeBase:
    def __init__(self, db_path="E:/Oishee/Thesis/chroma_db",
                 collection_name="clinical_guidelines"):
        self.embed_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2"
        )
        client = chromadb.PersistentClient(path=db_path)
        self.collection = client.get_collection(
            collection_name, embedding_function=self.embed_fn
        )

    def retrieve(self, query, n_results=2, condition=None):
        """
        Fetch the most relevant guideline chunks for a query.
        Optionally filter by condition (sepsis/pneumonia/aki).
        """
        where = {"condition": condition} if condition else None
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results,
            where=where,
        )

        chunks = []
        for i in range(len(results["ids"][0])):
            chunks.append({
                "condition": results["metadatas"][0][i]["condition"],
                "hop": results["metadatas"][0][i]["hop"],
                "text": results["documents"][0][i],
                "distance": results["distances"][0][i],
            })
        return chunks

    def format_for_prompt(self, chunks):
        """Turn retrieved chunks into a clean text block for the LLM prompt."""
        lines = []
        for c in chunks:
            lines.append(f"[Guideline: {c['condition'].upper()} - {c['hop']}]\n{c['text']}")
        return "\n\n".join(lines)


# Quick test when run directly
if __name__ == "__main__":
    kb = KnowledgeBase()
    print("Testing knowledge base retrieval...\n")

    query = "Patient with fever, high respiratory rate, and low blood pressure"
    chunks = kb.retrieve(query, n_results=2)

    print(f"QUERY: {query}\n")
    print("RETRIEVED GUIDELINES:")
    for c in chunks:
        print(f"  [{c['condition'].upper()} / {c['hop']}] distance={c['distance']:.3f}")
        print(f"  {c['text'][:100]}...\n")

    print("-" * 60)
    print("Testing condition filter (only AKI guidelines):")
    aki_chunks = kb.retrieve("kidney problem", n_results=2, condition="aki")
    for c in aki_chunks:
        print(f"  [{c['condition'].upper()} / {c['hop']}]")