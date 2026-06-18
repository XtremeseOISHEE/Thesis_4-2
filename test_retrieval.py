import chromadb
from chromadb.utils import embedding_functions

sentence_ef = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)

client = chromadb.PersistentClient(path="E:/Oishee/Thesis/chroma_db")
collection = client.get_collection("clinical_guidelines", embedding_function=sentence_ef)

# Test queries simulating what each hop would ask
test_queries = [
    "Patient has fever, high respiratory rate, low blood pressure. Could this be sepsis?",
    "Chest X-ray shows lung consolidation, patient has cough and fever",
    "Creatinine increased from 1.0 to 2.5, urine output very low",
]

for q in test_queries:
    print("=" * 70)
    print(f"QUERY: {q}")
    print("-" * 70)
    results = collection.query(query_texts=[q], n_results=2)
    for i in range(len(results['ids'][0])):
        meta = results['metadatas'][0][i]
        doc = results['documents'][0][i]
        dist = results['distances'][0][i]
        print(f"  [{meta['condition'].upper()} / {meta['hop']}] (distance: {dist:.3f})")
        print(f"  {doc[:120]}...")
        print()