import os
from langchain_text_splitters import CharacterTextSplitter

# Configuration
DOCS_DIR = "documents"
CHUNK_SIZE = 400
CHUNK_OVERLAP = 50

# Load and clean documents
def load_documents(docs_dir):
    documents = []
    for filename in os.listdir(docs_dir):
        if not filename.endswith(".txt"):
            continue
        filepath = os.path.join(docs_dir, filename)
        with open(filepath, "r", encoding="utf-8") as f:
            raw_text = f.read()

        # Collapse extra whitespace and blank lines
        cleaned = "\n".join(
            line.strip() for line in raw_text.splitlines() if line.strip()
        )

        # Parse professor name and department from filename (firstname_lastname_dept.txt)
        parts = filename.replace(".txt", "").split("_")
        department = parts[-1]                       
        professor = " ".join(parts[:-1]).title()     

        documents.append({
            "text": cleaned,
            "source": filename,
            "professor": professor,
            "department": department,
        })

    print(f"Loaded {len(documents)} documents\n")
    return documents

# Chunk documents
def chunk_documents(documents):
    splitter = CharacterTextSplitter(
        separator="\n",
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        length_function=len,
    )

    all_chunks = []
    for doc in documents:
        chunks = splitter.split_text(doc["text"])
        for i, chunk in enumerate(chunks):
            if len(chunk.strip()) == 0:
                continue
            all_chunks.append({
                "text": chunk.strip(),
                "source": doc["source"],
                "professor": doc["professor"],
                "department": doc["department"],
                "chunk_index": i,
            })

    print(f"Total chunks created: {len(all_chunks)}\n")
    return all_chunks

if __name__ == "__main__":
    documents = load_documents(DOCS_DIR)
    chunks = chunk_documents(documents)

    print("=" * 60)
    print("SAMPLE CHUNKS")
    print("=" * 60)
    for chunk in chunks[:5]:
        print(f"\nSource:     {chunk['source']}")
        print(f"Professor:  {chunk['professor']}")
        print(f"Department: {chunk['department']}")
        print(f"Chunk #{chunk['chunk_index']}")
        print(f"Text:\n{chunk['text']}")
        print("-" * 60)