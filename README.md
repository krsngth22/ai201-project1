# The Unofficial Guide — Project 1

> **How to use this template:**
> Complete each section *after* you've built and tested the corresponding part of your system.
> Do not write placeholder text — if a section isn't done yet, leave it blank and come back.
> Every section below is required for submission. One-liners will not receive full credit.

---

## Domain

This system covers student reviews of professors in the Computer Science and Mathematics departments at Gettysburg College. This knowledge is valuable because students rely on fragmented, hard-to-search sources like Rate My Professors and word-of-mouth to make course decisions. This system makes that knowledge queryable through natural language.

**Sources (all from Rate My Professors):**
- ivaylo_ilinkin_cs.txt — CS, 5 reviews
- sunghee_kim_cs.txt — CS, 5 reviews
- todd_neller_cs.txt — CS, 5 reviews
- clif_presser_cs.txt — CS, 5 reviews
- daniel_white_cs.txt — CS, 5 reviews
- bela_bajnok_math.txt — Math, 5 reviews
- benjamin_kennedy_math.txt — Math, 5 reviews
- caitlin_hult_math.txt — Math, 5 reviews
- keir_lockridge_math.txt — Math, 5 reviews
- ricardo_conceicao_math.txt — Math, 5 reviews
---

## Document Sources

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

**Chunk size:** 400 characters

**Overlap:** 50 characters  

**Why these choices fit your documents:** Reviews are medium length paragraphs. 400 characters captures one complete opinion without merging two reviews. 50 character overlap prevents losing a thought that trails across a boundary.

**Final chunk count:** 46

---

## Embedding Model

**Model used:** all-MiniLM-L6-v2 via sentence-transformers (runs locally)

**Production tradeoff reflection:** Source filenames from retrieved chunks are collected programmatically and displayed in the Sources panel of the Gradio UI. The LLM is also instructed to cite which professor/source its answer comes from within the answer text.

---

## Grounded Generation

**System prompt grounding instruction:** You are a helpful assistant for students at Gettysburg College.You answer questions about professors using ONLY the student reviews provided to you.Do not use any outside knowledge. Do not guess or infer beyond what the reviews say. If the provided reviews do not contain enough information to answer the question, say exactly: "I don't have enough information in my documents to answer that." Do NOT include a sources or references section in your answer. Sources are handled separately.

**How source attribution is surfaced in the response:** Source filenames from retrieved chunks are collected programmatically and displayed in the Sources panel of the Gradio UI. The LLM is also instructed to cite which professor/source its answer comes from within the answer text.

---

## Evaluation Report

<!-- Run your 5 test questions from planning.md through your system and record the results.
     Be honest — a partially accurate or inaccurate result that you explain well is more
     valuable than a suspiciously perfect result. -->

| # | Question | Expected answer | System response (summarized) | Retrieval quality | Response accuracy |
|---|----------|-----------------|------------------------------|-------------------|-------------------|
| 1 | Ilinkin's exam?| Exam difficulty, paper-based, IQ tests| Correctly described both, cited ivaylo_ilinkin_cs.txt| Relevant| Accurate|
| 2 | Approachable office hours?|Ilinkin and Presser | Only identified Presser, missed Ilinkin| Partially relevant| Partially accurate|
| 3 | Hult workload?| Heavy HW, memorization, tests = 68%| Correctly described all three, cited caitlin_hult_math.txt| Relevant| Accurate|
| 4 | Thorough understanding?| Benjamin Kennedy| Correctly identified Kennedy with quote| Relevant| Accurate|
| 5 | Math grading fairness?| Bajnok grade drops, Kennedy hard grader| Refused — said not enough information| Off-target| Inaccurate|

**Retrieval quality:** Relevant / Partially relevant / Off-target  
**Response accuracy:** Accurate / Partially accurate / Inaccurate

---

## Failure Case Analysis

**Question that failed:** What do students say about grading fairness across Math department professors?

**What the system returned:** "I don't have enough information in my documents to answer that."

**Root cause (tied to a specific pipeline stage):** Retrieval failure. The query used the abstract phrase "grading fairness" but reviews use concrete words like "curved," "dropped," and "hard grader." The embedding model couldn't bridge that gap, so it returned CS chunks (Kim, Neller, Presser) that don't mention grading at all, leaving the LLM with no relevant context.

**What you would change to fix it:** Add BM25 keyword search alongside semantic search (hybrid search). BM25 would have matched the keyword "grading" directly even without semantic similarity, surfacing the Bajnok and Kennedy chunks.

---

## Spec Reflection

**One way the spec helped you during implementation:** Writing the chunking strategy before coding forced me to commit to chunk size before seeing the data. When I ran the pipeline, chunks aligned almost perfectly with individual reviews.

**One way your implementation diverged from the spec, and why:** I planned chunk size 300 in planning.md but increased it to 400 during Milestone 3 because LangChain warned that individual reviews exceeded 300 characters. I updated planning.md to reflect the change.

---

## AI Usage

**Instance 1**

- *What I gave the AI:* My Documents section and Chunking Strategy from planning.md
- *What it produced:* A working ingest.py that loaded files, cleaned whitespace, and split into chunks with source metadata
- *What I changed or overrode:* Chunk size from 300 to 400 after seeing the size warnings in the output, and changed the import from langchain.text_splitter to langchain_text_splitters after a module error

**Instance 2**

- *What I gave the AI:* My grounding requirement and asked for query.py using Groq
- *What it produced:*  A generation function with a system prompt and grounded user prompt
- *What I changed or overrode:* Added load_dotenv() before Groq client initialization after an API key error, and removed the "list your sources" instruction from the system prompt after noticing it caused duplicate source output in the UI
