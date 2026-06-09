# Project 1 Planning: The Unofficial Guide

> Write this document before you write any pipeline code.
> Your spec and architecture diagram are what you'll use to direct AI tools (Claude, Copilot, etc.) to generate your implementation — the more specific they are, the more useful the generated code will be.
> Update the Retrieval Approach and Chunking Strategy sections if you change your approach during implementation.
> Update this file before starting any stretch features.

---

## Domain

This guide covers student reviews of professors in the Computer Science 
and Mathematics departments at [Your School Name]. Students rely heavily 
on word-of-mouth and scattered Reddit/RMP posts to make course decisions, 
but this knowledge is fragmented across platforms and hard to search 
systematically. This system makes it searchable through natural language 
queries.

---

## Documents

| # |     Source      |            Description                   |         URL or location              |
|---|-----------------|------------------------------------------|--------------------------------------|
| 1 | ratemyprofessor | Ivaylo Ilinkin — CS dept, 5 reviews      | documents/ivaylo_ilinkin_cs.txt      |
| 2 | ratemyprofessor | Sunghee Kim — CS dept, 5 reviews         | documents/sunghee_kim_cs.txt         |
| 3 | ratemyprofessor | Todd Neller — CS dept, 5 reviews         | documents/todd_neller_cs.txt         |
| 4 | ratemyprofessor | Clif Presser — CS dept, 5 reviews        | documents/clif_presser_cs.txt        |
| 5 | ratemyprofessor | Daniel White — CS dept, 5 reviews        | documents/daniel_white_cs.txt        |
| 6 | ratemyprofessor | Daniel White — CS dept, 5 reviews        | documents/bela_bajnok_math.txt       |
| 7 | ratemyprofessor | Benjamin Kennedy — Math dept, 5 reviews  | documents/benjamin_kennedy_math.txt  |
| 8 | ratemyprofessor | Caitlin Hult — Math dept, 5 reviews      | documents/caitlin_hult_math.txt      |
| 9 | ratemyprofessor | Keir Lockridge — Math dept, 5 reviews    | documents/keir_lockridge_math.txt    |
| 10 |ratemyprofessor | Ricardo Conceicao — Math dept, 5 reviews | documents/ricardo_conceicao_math.txt |

---

## Chunking Strategy

**Chunk size:** 300 characters

**Overlap:** 50 characters

**Reasoning:** Each document contains 5 reviews for one professor. Reviews are medium length — roughly one short paragraph (3–5 sentences) each. A 300-character chunk is large enough to capture one complete student opinion without merging two different reviews together, which would dilute retrieval. A 50-character overlap ensures that if a sentence trails across a chunk boundary, the key idea isn't lost entirely. Chunks larger than ~400 characters risk blending two reviews into one chunk, making it harder to match a specific query (like "what do students say about exams") to the right opinion.

---

## Retrieval Approach

**Embedding model:** all-MiniLM-L6-v2 via sentence-transformers (runs locally — no API key, no rate limits)

**Top-k:** 5 chunks per query

**Production tradeoff reflection:**
- *Cost:* all-MiniLM-L6-v2 is free and local. For production I'd consider OpenAI's text-embedding-3-small, which costs per token but scores higher on retrieval benchmarks for nuanced opinion text.
- *Context length:* MiniLM handles short reviews well. Longer documents like syllabi or handbooks would need a model with a larger context window.
- *Multilingual support:* MiniLM is English-only. A diverse student body would need paraphrase-multilingual-MiniLM-L12-v2 or similar.
- *Latency:* Running locally removes network latency but adds model load time on startup — acceptable for a demo, a tradeoff in production.

---

## Evaluation Plan

| # | Question | Expected answer |
|---|----------|-----------------|
| 1 | What do students say about Ivaylo Ilinkin's exams?| Reviews mention exam difficulty and whether they are fair or heavily curved |
| 2 | Which professors require strict attendance?| Specific professor names from CS or Math whose reviews mention mandatory attendance |
| 3 | What is Caitlin Hult's teaching personality like according to students?| Reviews describing her approachability, enthusiasm, or classroom style |
| 4 | Do any professors offer extra credit opportunities?| Specific professor names whose reviews mention extra credit being available|
| 5 | What do students say about making up missed work in the Math department?| Reviews from Math professors mentioning makeup policies or flexibility|

---

## Anticipated Challenges

1.**Very short reviews:** Some reviews are only one sentence long, which means a chunk may not carry enough semantic meaning for the embedding model to match it accurately to a query. These short chunks may return high distance scores (weak matches) or get outcompeted by longer, richer chunks even when they're technically relevant.

2.**Missing course context:** Many reviews don't mention the course number or course name — they just say "this class" or "the professor." This means a query like "what do students say about CS201" will likely fail because that context isn't in the documents. Retrieval will have to rely on professor name matching instead.

---

## Architecture

<!-- Draw a diagram of your pipeline showing the five stages:
     Document Ingestion → Chunking → Embedding + Vector Store → Retrieval → Generation
     Label each stage with the tool or library you're using.
     You can use ASCII art, a Mermaid diagram, or embed a sketch as an image.
     You'll use this diagram as context when prompting AI tools to implement each stage. -->

```
Raw .txt files (documents/)
        │
        V
[ Ingestion & Cleaning ]  ← ingest.py / Python
  Load each .txt file, strip extra whitespace,
  attach professor name + dept as metadata
        │
        V
[ Chunking ]              ← ingest.py / LangChain CharacterTextSplitter
  chunk_size=300, chunk_overlap=50
        │
        V
[ Embedding ]             ← embed.py / sentence-transformers
  Model: all-MiniLM-L6-v2 (local)
        │
        V
[ Vector Store ]          ← embed.py / ChromaDB (local)
  Store chunks + metadata (source filename, professor, dept)
        │
        V
[ Retrieval ]             ← query.py / ChromaDB similarity search
  top-k = 5 chunks per query
        │
        V
[ Generation ]            ← query.py / Groq API
  Model: llama-3.3-70b-versatile
  Grounded prompt — answer from context only
        │
        V
[ Gradio UI ]             ← app.py / Gradio
  Input: question textbox
  Output: answer + source list
  Runs at localhost:7860
```

---

## AI Tool Plan

**Milestone 3 — Ingestion and chunking:** I'll give Claude my Documents section and Chunking Strategy section and ask it to generate an ingest.py script that loads all .txt files from documents/, cleans whitespace, splits into chunks of 300 characters with 50-character overlap, and attaches source metadata (filename, professor name, department) to each chunk. I'll verify by printing 5 sample chunks and checking they are readable and self-contained.

**Milestone 4 — Embedding and retrieval:** I'll give Claude my Retrieval Approach section and Architecture diagram and ask it to generate an embed.py script that embeds all chunks using all-MiniLM-L6-v2 and stores them in ChromaDB with metadata. I'll also ask it to implement a retrieve() function in query.py that accepts a query string and returns the top 5 chunks with source info. I'll verify by running 3 test queries and checking the returned chunks are relevant.

**Milestone 5 — Generation and interface:** I'll give Claude my grounding requirement (answer from retrieved context only, cite sources) and ask it to implement the full query.py generation function using Groq and a grounded prompt template, plus an app.py Gradio interface with a question input and answer + sources output. I'll verify by asking an out-of-scope question and confirming the system declines rather than hallucinating.
