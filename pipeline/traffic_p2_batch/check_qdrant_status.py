import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
from pathlib import Path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.app.services.rag.vector_store import QdrantVectorStore

vs_prod = QdrantVectorStore(collection_name="vietlegal_articles")
prod_info = vs_prod.client.get_collection("vietlegal_articles")
print(f"Production 'vietlegal_articles' points count: {prod_info.points_count}")
assert prod_info.points_count == 7658, f"Expected 7658 points, got {prod_info.points_count}"

collections = vs_prod.client.get_collections().collections
print("All collections:", [c.name for c in collections])

vs_prod.close()
