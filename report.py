"""Writes reports/relatorio.md: the assistant's answer for each question and flight, and recall@3 per retriever."""

import pathlib

from assistant.data import EVAL, PASSAGES
from assistant.graph import ask
from assistant.retrieval import CHOSEN_RETRIEVER, RETRIEVERS, recall_at_k

FLIGHTS = ["UA100", "UA200", "UA300", "UA900"]

lines = ["# Relatório do assistente de remarcação", "", "## Respostas por voo", "",
         "| Pergunta | Voo | Resposta | Fontes | Assentos | Sistema fora do ar | Tentativas |",
         "| --- | --- | --- | --- | --- | --- | --- |"]
for flight in FLIGHTS:
    for e in EVAL:
        r = ask(e["question"], flight)
        seats = "-" if r["seats"] is None else r["seats"]
        down = "sim" if r["booking_failed"] else "não"
        lines.append(f"| {e['question']} | {flight} | {r['answer']} | {', '.join(r['sources'])} | "
                     f"{seats} | {down} | {r['attempts']} |")

relevant = [e["relevant"] for e in EVAL]
lines += ["", "## Recall@3 por retriever", "", "| Retriever | recall@3 | Escolhido |", "| --- | --- | --- |"]
for name, retrieve in RETRIEVERS.items():
    ranked = [[p["id"] for p in retrieve(e["question"], PASSAGES, 3)] for e in EVAL]
    score = recall_at_k(ranked, relevant, 3)
    chosen = "sim" if name == CHOSEN_RETRIEVER else "não"
    lines.append(f"| {name} | {score:.2f} | {chosen} |")

out = pathlib.Path(__file__).parent / "reports" / "relatorio.md"
out.parent.mkdir(exist_ok=True)
out.write_text("\n".join(lines) + "\n", encoding="utf-8")
print(f"wrote {out}")
