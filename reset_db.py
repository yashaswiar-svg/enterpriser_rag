"""
reset_db.py — Reset the ChromaDB collection and SQL database.

Run this ONCE when switching embedding models (e.g. text-embedding-004 → gemini-embedding-001).
The existing ChromaDB collection was created with 768-dim embeddings; the new model produces
3072-dim embeddings. ChromaDB enforces a fixed dimension per collection, so we must drop and
recreate it.

After running this, re-upload your documents through the Upload page.

Usage:
    python reset_db.py
"""
import os
import sys
import shutil

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.config.settings import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)


def reset():
    print("=" * 60)
    print("Enterprise RAG — Database Reset")
    print("=" * 60)
    print()
    print("This will:")
    print(f"  1. Delete ChromaDB collection at: {settings.CHROMA_PERSIST_DIR}")
    print(f"  2. Clear all Document/Chunk records from: {settings.DATABASE_URL}")
    print()
    confirm = input("Type 'yes' to proceed: ").strip().lower()
    if confirm != "yes":
        print("Aborted.")
        return

    # 1. Reset ChromaDB — delete the persist directory and let it recreate fresh
    chroma_dir = settings.CHROMA_PERSIST_DIR
    if os.path.exists(chroma_dir):
        shutil.rmtree(chroma_dir)
        print(f"✓ Deleted ChromaDB directory: {chroma_dir}")
    os.makedirs(chroma_dir, exist_ok=True)
    print(f"✓ Recreated empty ChromaDB directory")

    # 2. Clear Document + Chunk + AuditLog tables from SQL DB
    from app.utils.database import get_db_session, Document, Chunk, AuditLog, Report
    db = get_db_session()
    try:
        chunks_deleted = db.query(Chunk).delete()
        docs_deleted = db.query(Document).delete()
        audit_deleted = db.query(AuditLog).delete()
        # Leave reports intact — they're just metadata records
        db.commit()
        print(f"✓ Cleared SQL DB: {docs_deleted} documents, {chunks_deleted} chunks, {audit_deleted} audit logs")
    except Exception as e:
        db.rollback()
        print(f"✗ SQL clear failed: {e}")
        raise
    finally:
        db.close()

    print()
    print("Reset complete. Now:")
    print("  1. Start the FastAPI backend:  uvicorn main:app --port 8000 --reload")
    print("  2. Open app/frontend/index.html in a browser")
    print("  3. Re-upload your documents through the Upload page")
    print()
    print("New embedding model: models/gemini-embedding-001 (dim=3072)")


if __name__ == "__main__":
    reset()
