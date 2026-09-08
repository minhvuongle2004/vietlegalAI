import os
import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
from typing import List, Dict, Any, Optional
from pathlib import Path

class LegalRerankerService:
    """
    Dịch vụ Reranker phân loại chéo (Cross-Encoder):
    Mô hình BAAI/bge-reranker-v2-m3 thực hiện Full Cross-Attention giữa Query và Candidate Chunks,
    tái sắp xếp các ứng viên tiềm năng để đưa Điều luật chuẩn xác nhất lên vị trí Top 1.
    """

    def __init__(self, model_name: str = "BAAI/bge-reranker-v2-m3"):
        self.model_name = os.getenv("RERANKER_MODEL_NAME", model_name)
        self.model = None

    def _ensure_loaded(self):
        if self.model is None:
            from sentence_transformers import CrossEncoder
            import torch
            target_device = os.getenv("RERANKER_DEVICE", "cpu")
            if target_device == "cuda" and not torch.cuda.is_available():
                target_device = "cpu"
            model_kwargs = {"torch_dtype": torch.float16} if target_device == "cuda" else {"low_cpu_mem_usage": True}
            print(f"[*] Loading Cross-Encoder Reranker '{self.model_name}' on {target_device}...")
            try:
                self.model = CrossEncoder(
                    self.model_name,
                    max_length=512,
                    device=target_device,
                    model_kwargs=model_kwargs
                )
                print(f"[+] Reranker '{self.model_name}' ready on {target_device}!")
            except Exception as e:
                if target_device == "cuda":
                    print(f"[!] CUDA error ({e}), falling back to CPU...")
                    self.model = CrossEncoder(
                        self.model_name,
                        max_length=512,
                        device="cpu",
                        model_kwargs={"low_cpu_mem_usage": True}
                    )
                    print(f"[+] Reranker '{self.model_name}' ready on CPU!")
                else:
                    raise e

    def rerank(
        self, query: str, candidates: List[Dict[str, Any]], top_k: int = 5
    ) -> List[Dict[str, Any]]:
        if not candidates:
            return []

        self._ensure_loaded()

        pairs = []
        for c in candidates:
            doc_text = f"{c.get('context_header', '')}\n{c.get('content', '')}"
            pairs.append((query, doc_text))

        scores = self.model.predict(pairs, show_progress_bar=False)

        # Gắn rerank_score vào từng candidate
        ranked_candidates = []
        for c, score in zip(candidates, scores):
            item = c.copy()
            item["rerank_score"] = float(score)
            ranked_candidates.append(item)

        # Sắp xếp giảm dần theo rerank_score
        ranked_candidates.sort(key=lambda x: x["rerank_score"], reverse=True)
        return ranked_candidates[:top_k]

_reranker_instance = None

def get_reranker_service() -> LegalRerankerService:
    global _reranker_instance
    if _reranker_instance is None:
        _reranker_instance = LegalRerankerService()
    return _reranker_instance
