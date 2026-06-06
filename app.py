"""Milestone 5 — Query interface (Gradio).

A minimal web UI over the grounded-generation pipeline. Type a question, get a
grounded answer plus the list of sources it was retrieved from.

Run:  python app.py     then open http://localhost:7860
"""

import gradio as gr

from generate import ask


def handle_query(question):
    if not question or not question.strip():
        return "Please enter a question.", ""
    result = ask(question)
    sources = "\n".join(f"• {s}" for s in result["sources"]) or "(no sufficiently relevant sources)"
    return result["answer"], sources


with gr.Blocks(title="Unofficial Guide — OSU Financial Aid") as demo:
    gr.Markdown(
        "# Unofficial Guide — Ohio State Financial Aid\n"
        "Ask about appeals, FAFSA/disbursement timing, scholarships, or work-study. "
        "Answers come **only** from collected student forums, guides, and official pages."
    )
    inp = gr.Textbox(label="Your question", placeholder="e.g. How do I get a financial aid appeal approved?")
    btn = gr.Button("Ask", variant="primary")
    answer = gr.Textbox(label="Answer", lines=8)
    sources = gr.Textbox(label="Retrieved from", lines=4)

    btn.click(handle_query, inputs=inp, outputs=[answer, sources])
    inp.submit(handle_query, inputs=inp, outputs=[answer, sources])


if __name__ == "__main__":
    demo.launch()
