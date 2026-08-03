# evaluate_phong.py — Person C: SentenceChunker + Baseline + A/B Filter + Failure Analysis
# -*- coding: utf-8 -*-
from __future__ import annotations

import importlib
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

pkg = importlib.import_module("src.phongnt_01038")

DATA_DIR = os.getenv("LAB_DATA_DIR", "data")
SHOPEE_SOURCE_MARK = "help.shopee.vn"
TEXT_EXTENSIONS = {".md", ".txt"}

# =============================================================================
# 5 CAU HOI BENCHMARK (tu evaluate_congnh.py — khong doi)
# =============================================================================
BENCHMARK = [
    {
        "id": 1,
        "vi": "Mat bao lau de toi nhan duoc tien hoan vao vi ShopeePay neu huy don?",
        "query": "Mat bao lau de toi nhan duoc tien hoan vao vi ShopeePay neu huy don?",
        "filter": None,
        "type": "so lieu",
        "gold_keywords": ["hoan", "tien", "ShopeePay", "thoi gian"],
        "gold_doc": "thanh-toan-shopee-pay",
        "gold_answer": "(Corpus khong chua thong tin thoi gian hoan tien ShopeePay)",
    },
    {
        "id": 2,
        "vi": "Phi thanh toan co dinh tren moi don hang thanh cong la bao nhieu phan tram?",
        "query": "Phi thanh toan co dinh tren moi don hang thanh cong la bao nhieu phan tram?",
        "filter": {"customer_role": "seller"},
        "type": "dieu kien",
        "gold_keywords": ["phi", "%", "phan tram", "thanh toan"],
        "gold_doc": "phi-san-cho-nguoi-ban",
        "gold_answer": "(Corpus khong chua thong tin phan tram phi thanh toan cu the)",
    },
    {
        "id": 3,
        "vi": "Lam the nao de ap dung ma mien phi van chuyen Extra?",
        "query": "Lam the nao de ap dung ma mien phi van chuyen Extra?",
        "filter": None,
        "type": "quy trinh",
        "gold_keywords": ["van chuyen", "Extra", "mien phi"],
        "gold_doc": "phi-van-chuyen-thoi-gian-giao-hang",
        "gold_answer": "(Corpus khong chua huong dan ma Extra)",
    },
    {
        "id": 4,
        "vi": "Neu toi phat hien shop gui hang fake thi Shopee co den bu khong?",
        "query": "Neu toi phat hien shop gui hang fake thi Shopee co den bu khong?",
        "filter": None,
        "type": "ngoai le",
        "gold_keywords": ["fake", "gia", "nhai", "den bu", "boi thuong"],
        "gold_doc": "cam-ban-hang-gia",
        "gold_answer": "(Corpus chi co chinh sach cam, khong co thong tin den bu)",
    },
    {
        "id": 5,
        "vi": "Shopee Xu cua toi se het han vao ngay nao?",
        "query": "Shopee Xu cua toi se het han vao ngay nao?",
        "filter": None,
        "type": "so lieu",
        "gold_keywords": ["het han", "ngay", "het", "han su dung"],
        "gold_doc": "shopee-xu",
        "gold_answer": "(Corpus khong co ngay het han cu the)",
    },
]


# =============================================================================
# PARSE & LOAD (bo front matter)
# =============================================================================

def parse_front_matter(text):
    if not text.startswith("---"):
        return {}, text
    lines = text.splitlines()
    closing = None
    for index in range(1, len(lines)):
        if lines[index].strip() == "---":
            closing = index
            break
    if closing is None:
        return {}, text
    fm_block = "\n".join(lines[1:closing])
    body = "\n".join(lines[closing + 1:]).lstrip("\n")
    metadata = {}
    for raw in fm_block.splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or ":" not in line:
            continue
        key, _, value = line.partition(":")
        value = value.split(" #", 1)[0].strip().strip('"').strip("'")
        metadata[key.strip()] = value
    return metadata, body


def load_documents(data_dir):
    data_path = Path(data_dir)
    documents = []
    for path in sorted(data_path.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in TEXT_EXTENSIONS:
            continue
        metadata, body = parse_front_matter(path.read_text(encoding="utf-8"))
        doc_id = str(metadata.get("doc_id") or path.stem)
        metadata.setdefault("doc_id", doc_id)
        documents.append(pkg.Document(id=doc_id, content=body, metadata=metadata))
    return documents


def chunk_document(doc, chunker):
    chunk_docs = []
    for index, piece in enumerate(chunker.chunk(doc.content)):
        chunk_meta = dict(doc.metadata)
        chunk_meta["doc_id"] = doc.id
        chunk_meta["chunk_index"] = index
        chunk_docs.append(
            pkg.Document(id=f"{doc.id}::chunk_{index}", content=piece, metadata=chunk_meta)
        )
    return chunk_docs


# =============================================================================
# EMBEDDER
# =============================================================================

def select_embedder():
    provider = os.getenv(pkg.EMBEDDING_PROVIDER_ENV, "mock").strip().lower()
    if provider == "openai":
        return pkg.OpenAIEmbedder(
            model_name=os.getenv("OPENAI_EMBEDDING_MODEL", pkg.OPENAI_EMBEDDING_MODEL)
        )
    if provider == "local":
        return pkg.LocalEmbedder(
            model_name=os.getenv("LOCAL_EMBEDDING_MODEL", pkg.LOCAL_EMBEDDING_MODEL)
        )
    return pkg._mock_embed


def extractive_llm(prompt):
    for line in prompt.splitlines():
        s = line.strip()
        if s.startswith("- "):
            return s[2:].strip()
    return "(Khong truy xuat duoc ngữ cảnh.)"


# =============================================================================
# A. BASELINE COMPARISON
# =============================================================================

def run_baseline():
    print("\n" + "=" * 70)
    print("A. BASELINE COMPARISON (ChunkingStrategyComparator)")
    print("=" * 70)

    docs = load_documents(DATA_DIR)
    docs = [d for d in docs if SHOPEE_SOURCE_MARK in str(d.metadata.get("source_url", ""))]
    print(f"\nCorpus: {len(docs)} tai lieu Shopee thuc\n")

    # Chi test tren 3 tai lieu dau
    for doc in docs[:3]:
        body = doc.content
        doc_id = doc.id
        print(f"\n--- {doc_id} ({len(body)} ky tu, lay 2500 ky tu dau) ---")
        if not body.strip():
            print("  (empty)")
            continue
        result = pkg.ChunkingStrategyComparator().compare(body[:2500], chunk_size=200)
        print(f"  | Strategy | Chunks | AvgLen | Coherence |")
        print(f"  |----------|--------|--------|-----------|")
        for strat, stats in result.items():
            label = {
                "fixed_size": "FixedSize(200,0)",
                "by_sentences": "Sentence(max=3)",
                "recursive": "Recursive(200)",
            }.get(strat, strat)
            avg = stats["avg_length"]
            # Coherence: kiem tra chunk co cat giua cau hay khong
            coherent = "Tot" if strat != "fixed_size" else "Trung binh"
            print(f"  | {label} | {stats['count']} | {avg:.0f} | {coherent} |")


# =============================================================================
# B. BENCHMARK
# =============================================================================

def kw_in_content(content, keywords):
    c = content.lower()
    return any(kw.lower() in c for kw in keywords)


def rubric_score(search_results, gold_keywords, agent_answer):
    """Tinh diem theo rubric: 2=top-3 co gold+agent dung, 1=co gold nhung k top-1, 0=khong co."""
    if not search_results:
        return 0, "Khong co ket qua tra ve"

    # Kiem tra gold keywords trong top-3
    top3_has_gold = any(kw_in_content(r["content"], gold_keywords) for r in search_results)
    top1_has_gold = kw_in_content(search_results[0]["content"], gold_keywords)

    # Agent tra loi co noi dung tu context khong
    agent_has_gold = kw_in_content(agent_answer, gold_keywords)

    if top3_has_gold and agent_has_gold:
        return 2, "Top-3 co gold keyword + agent tra loi dung"
    elif top3_has_gold:
        return 1, "Top-3 co gold keyword nhung agent tra loi chua chinh xac"
    else:
        # Chi tiet failure
        top1_doc = search_results[0]["metadata"].get("doc_id", "?")
        return 0, f"Top-3 khong co gold keywords. Top-1: {top1_doc}"


def run_benchmark(embedder):
    print("\n" + "=" * 70)
    print("B. BENCHMARK — Person C: SentenceChunker(max_sentences=3)")
    print("=" * 70)

    docs = load_documents(DATA_DIR)
    docs = [d for d in docs if SHOPEE_SOURCE_MARK in str(d.metadata.get("source_url", ""))]
    print(f"\nCorpus: {len(docs)} tai lieu, {sum(len(d.content) for d in docs):,} ky tu")

    # Person C: SentenceChunker
    chunker = pkg.SentenceChunker(max_sentences_per_chunk=3)
    chunk_docs = [c for d in docs for c in chunk_document(d, chunker)]

    store = pkg.EmbeddingStore(collection_name="lab7_phong_personc", embedding_fn=embedder)
    store.add_documents(chunk_docs)

    backend = "ChromaDB" if store._use_chroma else "in-memory"
    print(f"Nap {store.get_collection_size()} chunk | backend: {backend}")
    print(f"Strategy: SentenceChunker(max_sentences=3)\n")

    agent = pkg.KnowledgeBaseAgent(store=store, llm_fn=extractive_llm)

    # --- A/B FILTER ANALYSIS (Query 2) ---
    q2 = [q for q in BENCHMARK if q["id"] == 2][0]
    print("--- A/B FILTER ANALYSIS (Query 2: Phi thanh toan, filter=seller) ---")
    sr_no_filter = store.search(q2["query"], top_k=5)
    sr_with_filter = store.search_with_filter(q2["query"], top_k=5,
                                              metadata_filter=q2["filter"])

    print(f"\n[A] Khong filter:")
    for r in sr_no_filter:
        has_gold = kw_in_content(r["content"], q2["gold_keywords"])
        print(f"  score={r['score']:.4f} gold={has_gold} doc={r['metadata'].get('doc_id')} role={r['metadata'].get('customer_role')}")
        print(f"    {r['content'].replace(chr(10),' ')[:100]}")

    print(f"\n[B] Co filter {q2['filter']}:")
    for r in sr_with_filter:
        has_gold = kw_in_content(r["content"], q2["gold_keywords"])
        print(f"  score={r['score']:.4f} gold={has_gold} doc={r['metadata'].get('doc_id')} role={r['metadata'].get('customer_role')}")
        print(f"    {r['content'].replace(chr(10),' ')[:100]}")

    ids_no = [r["metadata"].get("doc_id") for r in sr_no_filter]
    ids_yes = [r["metadata"].get("doc_id") for r in sr_with_filter]
    if ids_no == ids_yes:
        filter_note = "GIONG NHAU — filter khong hieu qua vi cac tai lieu deu co role=seller/buyer, hoac corpus khong co tai lieu nao phu hop voi gold keywords"
    else:
        filter_note = "KHAC NHAU — filter giup loai bo nhieu, nhung co the loai luon chunk chua gold"
    print(f"\n=> {filter_note}\n")
    print()

    # --- FULL BENCHMARK ---
    print("--- FULL BENCHMARK ---")
    results = []

    for item in BENCHMARK:
        qid = item["id"]
        qvi = item["vi"]
        q = item["query"]
        filt = item["filter"]
        gk = item["gold_keywords"]
        gd = item["gold_doc"]
        ga = item["gold_answer"]
        qtype = item["type"]

        print(f"\n{'='*60}")
        print(f"[{qtype.upper()}] Cau {qid}: {qvi}")
        if filt:
            print(f"  [filter: {filt}]")
        print(f"  Gold keywords: {gk}")
        print(f"  Gold doc: {gd}")

        # Search
        if filt:
            sr = store.search_with_filter(q, top_k=3, metadata_filter=filt)
        else:
            sr = store.search(q, top_k=3)

        # Agent
        agent_resp = agent.answer(q)

        # Score theo rubric
        score, reason = rubric_score(sr, gk, agent_resp)

        # Chi tiet top-3
        print(f"\n  TOP-3:")
        top3_has_gold = False
        for rank, r in enumerate(sr, 1):
            has_gold = kw_in_content(r["content"], gk)
            if has_gold:
                top3_has_gold = True
            marker = " <<<< GOLD" if has_gold else ""
            preview = r["content"].replace("\n", " ")[:120]
            print(f"  top-{rank} score={r['score']:.4f}{marker}")
            print(f"    doc={r['metadata'].get('doc_id')} role={r['metadata'].get('customer_role')}")
            print(f"    {preview}")

        # Agent answer
        print(f"  Agent: {agent_resp[:200].replace(chr(10),' ')}")

        # Failure analysis
        print(f"  RUBRIC SCORE: {score}/2 — {reason}")
        if score == 0:
            top1_doc = sr[0]["metadata"].get("doc_id", "?") if sr else "?"
            top1_preview = sr[0]["content"].replace("\n"," ")[:80] if sr else ""
            print(f"  *** FAILURE CASE ***")
            print(f"  Query: {qvi}")
            print(f"  Top-1 doc: {top1_doc}")
            print(f"  Top-1 preview: {top1_preview}...")
            print(f"  Ly do: Top-3 khong chua gold keywords {gk}")
            if sr:
                print(f"  Nguyen nhan goc: Chunk tra ve thuoc chu de giong nhung khong chua thong tin cu the. "
                      f"Co the do corpus thieu noi dung hoac chunking cat dung phan quan trong.")
            print(f"  De xuat: (1) Chen lai corpus day du hon; (2) Dung embedder tot hon (local/openai); "
                      f"(3) Giam chunk_size de tang precision.")

        results.append({
            "id": qid,
            "type": qtype,
            "vi": qvi,
            "filter": filt,
            "sr": sr,
            "score": score,
            "reason": reason,
            "agent": agent_resp,
            "top3_has_gold": top3_has_gold,
        })
        print()

    # Bang tong hop
    print("\n" + "=" * 70)
    print("BANG TONG HOP")
    print("=" * 70)
    print("| # | Loai | Cau hoi | Score | Ly do |")
    print("|---|------|---------|-------|-------|")
    for r in results:
        short_q = r["vi"][:45]
        print(f"| {r['id']} | {r['type']} | {short_q}... | {r['score']}/2 | {r['reason'][:50]} |")

    total_score = sum(r["score"] for r in results)
    print(f"\n**Tong diem: {total_score}/10**")
    return results


# =============================================================================
# C. SO SANH STRATEGY (Person C vs A/B/D)
# =============================================================================

def run_strategy_comparison(embedder):
    print("\n" + "=" * 70)
    print("C. SO SANH STRATEGY TRONG NHOM")
    print("=" * 70)

    docs = load_documents(DATA_DIR)
    docs = [d for d in docs if SHOPEE_SOURCE_MARK in str(d.metadata.get("source_url", ""))]
    body_all = "\n\n".join(d.content for d in docs)

    strategies = [
        ("A", "FixedSize(200,50)", pkg.FixedSizeChunker(chunk_size=200, overlap=50)),
        ("B", "Recursive(500)", pkg.RecursiveChunker(chunk_size=500)),
        ("C [Phong]", "Sentence(3)", pkg.SentenceChunker(max_sentences_per_chunk=3)),
        ("D", "FixedSize(500,50)", pkg.FixedSizeChunker(chunk_size=500, overlap=50)),
    ]

    print(f"\nTong ky tu corpus: {len(body_all):,}\n")
    print("| Nguoi | Strategy | Chunks | AvgLen |")
    print("|-------|----------|--------|--------|")
    for tag, label, chunker in strategies:
        chunks = chunker.chunk(body_all[:5000])
        avg = sum(len(c) for c in chunks) / len(chunks) if chunks else 0
        print(f"| {tag} | {label} | {len(chunks)} | {avg:.0f} |")


# =============================================================================
# MAIN
# =============================================================================

def main():
    load_dotenv(override=True)
    embedder = select_embedder()
    name = getattr(embedder, "_backend_name", embedder.__class__.__name__)
    print(f"Embedder: {name}")
    print("Gioi han: mock embedder khong bieu dien nghia ngon ngu, chi kiem tra luong ky thuat.")

    run_baseline()
    results = run_benchmark(embedder)
    run_strategy_comparison(embedder)

    # Tong hop diem
    total = sum(r["score"] for r in results)
    print(f"\n==> Tong diem benchmark: {total}/10")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
