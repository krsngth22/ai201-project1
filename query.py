import os
from dotenv import load_dotenv
load_dotenv()  
from groq import Groq
from embed import retrieve

# Load Groq client 
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
MODEL = "llama-3.3-70b-versatile"

# Prompt template 
SYSTEM_PROMPT = """You are a helpful assistant for students at Gettysburg College.
You answer questions about professors using ONLY the student reviews provided to you.
Do not use any outside knowledge. Do not guess or infer beyond what the reviews say.
If the provided reviews do not contain enough information to answer the question, say exactly: "I don't have enough information in my documents to answer that."
Do NOT include a sources or references section in your answer. Sources are handled separately."""

def ask(question):
    chunks = retrieve(question, top_k=5)

    # Build context from chunks
    context_parts = []
    seen_sources = set()
    sources = []
    for chunk in chunks:
        context_parts.append(
            f"[Source: {chunk['source']} | Professor: {chunk['professor']}]\n{chunk['text']}"
        )
        if chunk["source"] not in seen_sources:
            seen_sources.add(chunk["source"])
            sources.append(chunk["source"])

    context = "\n\n".join(context_parts)

    # Build prompt
    user_prompt = f"""Use ONLY the following student reviews to answer the question.
Do not use any knowledge outside of these reviews.

--- REVIEWS ---
{context}
--- END REVIEWS ---

Question: {question}

Answer (cite which professor/source your answer comes from):"""

    # Call Groq
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.2,
    )

    answer = response.choices[0].message.content.strip()

    return {
        "answer": answer,
        "sources": sources,
        "chunks": chunks,
    }

if __name__ == "__main__":
    test_questions = [
        "What do students say about Ilinkin's exams?",
        "What is the weather like on Mars?",  # out-of-scope test
    ]

    for q in test_questions:
        print("=" * 60)
        print(f"Q: {q}")
        result = ask(q)
        print(f"\nA: {result['answer']}")
        print(f"\nRetrieved from: {', '.join(result['sources'])}")
        print("=" * 60 + "\n")