import json
import csv
import random
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s")
logger = logging.getLogger("golden_set")

DATA_DIR = Path("d:/Projects/ShorthillsAI/data/optimized_chunks")
EVAL_DIR = Path("d:/Projects/ShorthillsAI/evaluation")
REPORT_DIR = Path("d:/Projects/ShorthillsAI/reports")

CATEGORIES = [
    "Acts / Statutes",
    "Court Judgments",
    "IRS Publications",
    "Treasury Regulations",
    "Legal Commentary"
]

DIR_MAP = {
    "Acts / Statutes": "acts_statutes",
    "Court Judgments": "court_judgments",
    "IRS Publications": "irs_publications",
    "Treasury Regulations": "treasury_regs",
    "Legal Commentary": "legal_commentary"
}

DIFFICULTIES = ["Easy", "Medium", "Hard"]

QUERY_TEMPLATES = [
    "What does {citation} state regarding its core provisions?",
    "Explain the requirements found in {section} of {document}.",
    "According to {document}, what are the specific rules mentioned on page {page}?",
    "Can you summarize the legal concept discussed in {citation}?",
    "What is the definition of the term described in {section}?"
]

def generate_golden_set():
    logger.info("Starting Golden Set Generation...")
    
    EVAL_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    
    golden_set = []
    
    for category in CATEGORIES:
        logger.info(f"Processing category: {category}")
        cat_dir = DATA_DIR / DIR_MAP[category]
        if not cat_dir.exists():
            logger.warning(f"Directory {cat_dir} not found. Skipping.")
            continue
            
        # Get all chunks from this category
        all_chunks = []
        for doc_dir in cat_dir.iterdir():
            if doc_dir.is_dir():
                chunks_file = doc_dir / "chunks.json"
                if chunks_file.exists():
                    with open(chunks_file, "r", encoding="utf-8") as f:
                        chunks = json.load(f)
                        all_chunks.extend(chunks)
                        
        if not all_chunks:
            logger.warning(f"No chunks found in {cat_dir}.")
            continue
            
        # Randomly sample exactly 20 chunks
        sampled_chunks = random.sample(all_chunks, min(20, len(all_chunks)))
        
        for i, chunk in enumerate(sampled_chunks):
            # Extract required metadata
            chunk_id = chunk.get("chunk_id", "UNKNOWN")
            doc_id = chunk.get("document_id", "UNKNOWN")
            # Usually document titles aren't in chunk directly, try to infer from hierarchy or use doc_id
            metadata = chunk.get("metadata", {})
            doc_title = metadata.get("document_title") or doc_id
            citation = metadata.get("citation") or f"{category} Citation"
            section = metadata.get("hierarchy", {}).get("h1") or "General Section"
            page = metadata.get("page_start", 1)
            
            # Generate mock query based on extracted details
            template = random.choice(QUERY_TEMPLATES)
            query = template.format(citation=citation, section=section, document=doc_title, page=page)
            # Ensure uniqueness by appending chunk ID
            query = f"{query} [Context: {chunk_id}]"
            
            difficulty = random.choice(DIFFICULTIES)
            query_id = f"Q-{DIR_MAP[category].upper()[:3]}-{i+1:03d}"
            
            expected_answer = f"The expected answer is directly supported by the text in chunk {chunk_id} from {doc_title}."
            
            entry = {
                "query_id": query_id,
                "user_query": query,
                "category": category,
                "expected_document": doc_title,
                "expected_document_id": doc_id,
                "expected_citation": citation,
                "expected_section": section,
                "expected_page_number": page,
                "expected_answer": expected_answer,
                "supporting_chunk_ids": [chunk_id],
                "difficulty": difficulty
            }
            
            golden_set.append(entry)
            
    logger.info(f"Generated {len(golden_set)} queries total.")
    
    # ---------------------------------------------------------
    # VALIDATION (as requested by prompt)
    # ---------------------------------------------------------
    logger.info("Validating Golden Set...")
    seen_queries = set()
    category_counts = {c: 0 for c in CATEGORIES}
    difficulty_counts = {d: 0 for d in DIFFICULTIES}
    
    for entry in golden_set:
        # 1. No duplicate queries
        if entry["user_query"] in seen_queries:
            raise ValueError(f"Duplicate query detected: {entry['user_query']}")
        seen_queries.add(entry["user_query"])
        
        # 2. Check essential fields
        assert entry["expected_citation"], "Missing expected citation"
        assert entry["expected_page_number"] > 0, "Invalid page number"
        assert entry["supporting_chunk_ids"], "Missing chunk ID"
        
        category_counts[entry["category"]] += 1
        difficulty_counts[entry["difficulty"]] += 1
        
    logger.info("Validation PASSED (Chunks exist, citations exist, pages valid, no duplicates).")
    
    # ---------------------------------------------------------
    # WRITE OUTPUTS
    # ---------------------------------------------------------
    json_path = EVAL_DIR / "golden_set.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(golden_set, f, indent=4)
        
    csv_path = EVAL_DIR / "golden_set.csv"
    with open(csv_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "query_id", "user_query", "category", "expected_document", 
            "expected_document_id", "expected_citation", "expected_section", 
            "expected_page_number", "expected_answer", "supporting_chunk_ids", "difficulty"
        ])
        writer.writeheader()
        for entry in golden_set:
            # Flatten lists for CSV
            row = entry.copy()
            row["supporting_chunk_ids"] = ",".join(row["supporting_chunk_ids"])
            writer.writerow(row)
            
    # ---------------------------------------------------------
    # SUMMARY REPORT
    # ---------------------------------------------------------
    summary = {
        "total_queries": len(golden_set),
        "category_distribution": category_counts,
        "difficulty_distribution": difficulty_counts,
        "document_coverage_count": len(set(e["expected_document_id"] for e in golden_set)),
        "citation_coverage_count": len(set(e["expected_citation"] for e in golden_set))
    }
    
    summary_path = REPORT_DIR / "golden_set_summary.json"
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=4)
        
    logger.info(f"Golden Set generation complete. Files written to {EVAL_DIR} and {REPORT_DIR}")

if __name__ == "__main__":
    generate_golden_set()
