# evaluate_duong.py — Kịch bản đánh giá với MarkdownHeadingChunker
from __future__ import annotations

import importlib
import os
import sys

from dotenv import load_dotenv

# Import các package cá nhân của bạn và alias cho "src"
pkg = importlib.import_module("src.duongnt-01966")
sys.modules["src"] = pkg

import ingest

# Bắt buộc dùng local embedding (SentenceTransformer) thay vì mock để tìm kiếm chuẩn xác
os.environ["EMBEDDING_PROVIDER"] = "local"
from main import _select_embedder, demo_llm

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

chunking_pkg = importlib.import_module("src.duongnt-01966.chunking")
agent_pkg = importlib.import_module("src.duongnt-01966.agent")


MarkdownHeadingChunker = getattr(chunking_pkg, 'MarkdownHeadingChunker')
KnowledgeBaseAgent = getattr(agent_pkg, 'KnowledgeBaseAgent')

# Thư mục dữ liệu (Bạn có thể đổi thành thư mục chứa dataset của nhóm)
DATA_DIR = os.getenv("LAB_DATA_DIR", "data")


# 5 câu hỏi benchmark từ REPORT_NHOM.md
BENCHMARK_QUESTIONS = [
    "Mất bao lâu để tôi nhận được tiền hoàn vào ví ShopeePay nếu hủy đơn?",
    "Phí thanh toán cố định hiện tại trên mỗi đơn hàng thành công là bao nhiêu phần trăm?",
    "Làm thế nào để áp dụng mã miễn phí vận chuyển Extra?",
    "Nếu tôi phát hiện shop gửi hàng fake thì Shopee có đền bù không?",
    "Shopee Xu của tôi sẽ hết hạn vào ngày nào?"
]

def run_evaluation():
    print(f"=== Đang nạp dữ liệu từ {DATA_DIR} ===")
    embedder = _select_embedder()
    print(f"Sử dụng Embedder: {getattr(embedder, '_backend_name', embedder.__class__.__name__)}")
    
    # Sử dụng Chunker VIP của bạn
    chunker = MarkdownHeadingChunker()
    
    # Nạp Knowledge Base
    store = ingest.build_knowledge_base(DATA_DIR, embedding_fn=embedder, chunker=chunker)
    print(f"Đã nạp {store.get_collection_size()} chunks bằng MarkdownHeadingChunker.\n")
    print("="*60 + "\n")
    
    agent = KnowledgeBaseAgent(store=store, llm_fn=demo_llm)
    
    for i, question in enumerate(BENCHMARK_QUESTIONS, start=1):
        print(f"📝 CÂU {i}: {question}")
        
        # 1. Tìm top-k chunk
        results = store.search(question, top_k=3)
        if results:
            top1 = results[0]
            print(f"  [Top-1 Score]   : {top1['score']:.4f}")
            print(f"  [Top-1 Source]  : {top1['metadata'].get('source')}")
            content_preview = top1['content'][:150].replace('\n', ' ')
            print(f"  [Top-1 Preview] : {content_preview}...")
            
            # Print các rank khác nếu cần xem relevant lọt top-3 không
            for rank, res in enumerate(results[1:], start=2):
                print(f"  [Top-{rank} Score]   : {res['score']:.4f} (Source: {res['metadata'].get('source')})")
        else:
            print("  -> Không tìm thấy chunk nào.")
            
        # 2. Lấy câu trả lời của Agent
        print("\n🤖 AGENT TRẢ LỜI:")
        answer = agent.answer(question, top_k=3)
        print(f"  {answer}")
        
        print("\n" + "="*60 + "\n")

if __name__ == "__main__":
    run_evaluation()
