import gradio as gr
from dotenv import load_dotenv
from query import ask

load_dotenv()

def handle_query(question):
    if not question.strip():
        return "Please enter a question.", ""

    result = ask(question)
    sources = "\n".join(f"• {s}" for s in result["sources"])
    return result["answer"], sources

# Gradio UI 
with gr.Blocks(title="Gettysburg College Unofficial Professor Guide") as demo:
    gr.Markdown("# 🎓 Gettysburg College Unofficial Professor Guide")
    gr.Markdown("Ask questions about CS and Math professors based on real student reviews.")

    with gr.Row():
        inp = gr.Textbox(
            label="Your question",
            placeholder="e.g. What do students say about Ilinkin's exams?",
            lines=2,
        )

    btn = gr.Button("Ask", variant="primary")

    with gr.Row():
        answer = gr.Textbox(label="Answer", lines=10)
        sources = gr.Textbox(label="Sources", lines=10)

    btn.click(handle_query, inputs=inp, outputs=[answer, sources])
    inp.submit(handle_query, inputs=inp, outputs=[answer, sources])

if __name__ == "__main__":
    demo.launch()