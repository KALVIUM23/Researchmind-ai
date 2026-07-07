import os
import shutil

base = "c:/researchmind-ai/backend/app"

# Create directories
dirs = ["schemas", "middleware", "ingestion", "retrieval", "services"]
for d in dirs:
    os.makedirs(os.path.join(base, d), exist_ok=True)

def move_file(src, dst):
    src_path = os.path.join(base, src)
    dst_path = os.path.join(base, dst)
    if os.path.exists(src_path):
        shutil.move(src_path, dst_path)
        print(f"Moved {src} to {dst}")
    else:
        print(f"Not found: {src}")

# From rag/ to ingestion/
move_file("rag/chunk_management.py", "ingestion/chunk_management.py")
move_file("rag/chunking.py", "ingestion/chunking.py")

# From rag/ to retrieval/
move_file("rag/embedding_cache.py", "retrieval/embedding_cache.py")
move_file("rag/embedding_retry.py", "retrieval/embedding_retry.py")
move_file("rag/embeddings.py", "retrieval/embeddings.py")
move_file("rag/retrieval.py", "retrieval/retrieval.py")

# From rag/ to services/
move_file("rag/answer_generation.py", "services/generation_service.py")

print("Done restructuring files!")
