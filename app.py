# --------------------------------------------------------------
#  app.py   –   7-Stage Problem-Solving Assistant + Ontology Agents
# --------------------------------------------------------------

import streamlit as st
import subprocess
import shutil
import os
import json
import re
import io
import base64
from datetime import datetime

# ---------- 3rd-party ----------
from rdflib import Graph, Literal, RDF, RDFS, URIRef, Namespace
from rdflib.namespace import XSD
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
import matplotlib.pyplot as plt
import networkx as nx
from PIL import Image as PILImage

# ==============================================================
# 1. CONFIG & OLLAMA SETUP
# ==============================================================

OLLAMA_EXE = shutil.which("ollama") or r"C:\Users\Sagar Yadav\AppData\Local\Programs\Ollama\ollama.exe"
MODEL = "llama3.2-vision"

if not os.path.exists(OLLAMA_EXE):
    st.error(f"Ollama executable not found at `{OLLAMA_EXE}`")
    st.stop()

# --------------------------------------------------------------
# 2. ONTOLOGY NAMESPACE & GLOBAL GRAPH
# --------------------------------------------------------------
PSO = Namespace("http://example.org/problem-solving-ontology#")
if "kg" not in st.session_state:
    st.session_state.kg = Graph()
    st.session_state.kg.bind("pso", PSO)

# ==============================================================
# 3. OLLAMA HELPER
# ==============================================================

def run_ollama(prompt: str) -> str:
    """Execute `ollama run <model>` with the given prompt."""
    try:
        result = subprocess.run(
            [OLLAMA_EXE, "run", MODEL],
            input=prompt,
            capture_output=True,
            text=True,
            timeout=180,
        )
        return result.stdout.strip() if result.returncode == 0 else f"Error: {result.stderr}"
    except Exception as e:
        return f"Exception: {e}"

# ==============================================================
# 4. STAGE PROMPT TEMPLATES (unchanged from your original)
# ==============================================================

STAGE_PROMPTS = {
    "stage1": "Stage 1: Understand the Problem\nProblem: {problem}\nContext: {context}\n"
              "Instructions:\n- Restate the problem.\n- Identify key constraints.\n- Break into subproblems.\n",
    "stage2": "Stage 2: Research & Gather Information\nProblem Summary: {stage1_output}\n"
              "User Data: {user_data}\nInstructions:\n- Identify needed info/data.\n- Make assumptions if data missing.\n",
    "stage3": "Stage 3: Generate Possible Solutions\nProblem Summary: {stage1_output}\n"
              "Assumptions: {stage2_output}\nPreferences: {preferences}\n"
              "Instructions:\n- List multiple solutions.\n- Pros and cons.\n- Explain reasoning.\n",
    "stage4": "Stage 4: Select the Best Solution\nPossible Solutions: {stage3_output}\n"
              "Selection Criteria: {criteria}\nInstructions:\n- Compare and justify chosen solution.\n- Provide reasoning.\n",
    "stage5": "Stage 5: Plan Implementation\nSelected Solution: {stage4_output}\n"
              "Resources: {resources}\nInstructions:\n- Break solution into steps.\n- Assign priorities.\n- Expected outcomes.\n",
    "stage6": "Stage 6: Testing & Verification\nImplementation Plan: {stage5_output}\n"
              "Testing Info: {testing_info}\nInstructions:\n- Define test methods.\n- Predict issues & mitigations.\n",
    "stage7": "Stage 7: Reflection & Optimization\nSolution Outcome: {stage6_output}\n"
              "Reflections: {reflection}\nInstructions:\n- Suggest improvements.\n- Optimize and summarize learnings.\n",
}

def run_stage(stage_key: str, **kwargs) -> str:
    """Format the stage prompt and run Ollama."""
    prompt = STAGE_PROMPTS[stage_key].format(**kwargs)
    return run_ollama(prompt)

# ==============================================================
# 5. ONTOLOGY AGENT
# ==============================================================

ONTOLOGY_AGENT_PROMPT = """
You are an Ontology Engineer. From the text extract:
1. Entities (Problem, Subproblem, Solution, Step, Resource, Test, …)
2. Relations (hasSubproblem, solvedBy, requiresResource, testedBy, …)
3. Attributes (priority, status, difficulty)

Return **only** valid JSON:
{
  "entities": [{"id":"E1","label":"Main Problem","type":"Problem"}],
  "relations": [{"from":"E1","to":"E2","type":"hasSubproblem"}],
  "attributes": [{"entity":"E1","key":"priority","value":"high"}]
}
Text:
{text}
"""

def ontology_agent(text: str) -> dict:
    raw = run_ollama(ONTOLOGY_AGENT_PROMPT.replace("{text}", text))
    # try direct JSON
    try:
        return json.loads(raw)
    except Exception:
        pass
    # fallback: extract first {...}
    m = re.search(r"\{.*\}", raw, re.DOTALL)
    if m:
        try:
            return json.loads(m.group(0))
        except Exception:
            return {}
    return {}

# ==============================================================
# 6. Q&A EXTRACTOR AGENT
# ==============================================================

QA_EXTRACTOR_PROMPT = """
Extract Question-Answer pairs from the text.
Format:
Q1: <question>
A1: <answer>
...
Text:
{text}
"""

def qa_extractor(text: str) -> list[tuple[str, str]]:
    raw = run_ollama(QA_EXTRACTOR_PROMPT.replace("{text}", text))
    pairs = []
    lines = [l.strip() for l in raw.split("\n") if l.strip()]
    i = 0
    while i < len(lines):
        if lines[i].startswith("Q"):
            q = lines[i][3:].strip()
            a = ""
            if i + 1 < len(lines) and lines[i + 1].startswith("A"):
                a = lines[i + 1][3:].strip()
                i += 2
            else:
                i += 1
            pairs.append((q, a))
        else:
            i += 1
    # fallback if no Q/A found
    if not pairs:
        pairs.append(("Full stage output", text[:1000] + ("…" if len(text) > 1000 else "")))
    return pairs

# ==============================================================
# 7. KNOWLEDGE GRAPH UPDATE
# ==============================================================

def update_kg(stage_num: int, ont: dict):
    g = st.session_state.kg
    stage_uri = PSO[f"Stage{stage_num}"]

    # entities
    for e in ont.get("entities", []):
        eid = f"{e['id']}_S{stage_num}"
        uri = PSO[eid]
        g.add((uri, RDF.type, PSO[e.get("type", "Entity")]))
        g.add((uri, RDFS.label, Literal(e.get("label", ""))))
        g.add((uri, PSO.inStage, stage_uri))

    # relations
    for r in ont.get("relations", []):
        fr = PSO[f"{r['from']}_S{stage_num}"]
        to = PSO[f"{r['to']}_S{stage_num}"]
        g.add((fr, PSO[r.get("type", "relatedTo")], to))

    # attributes
    for a in ont.get("attributes", []):
        uri = PSO[f"{a['entity']}_S{stage_num}"]
        g.add((uri, PSO[a.get("key", "property")], Literal(a.get("value", ""), datatype=XSD.string)))

# ==============================================================
# 8. GRAPH VISUALISATION (PNG bytes)
# ==============================================================

def kg_png() -> bytes:
    G = nx.DiGraph()
    for s, p, o in st.session_state.kg:
        if isinstance(s, URIRef) and isinstance(o, URIRef):
            s_label = s.split("#")[-1].split("_S")[0]
            o_label = o.split("#")[-1].split("_S")[0]
            p_label = p.split("#")[-1]
            G.add_edge(s_label, o_label, label=p_label)

    plt.figure(figsize=(10, 6))
    pos = nx.spring_layout(G, k=2, iterations=50)
    nx.draw(G, pos, with_labels=True, node_color="#a8d5ff", node_size=2200,
            font_size=8, arrows=True, edge_color="#555555")
    edge_labels = nx.get_edge_attributes(G, "label")
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=7)
    plt.title("Problem-Solving Knowledge Graph")

    buf = io.BytesIO()
    plt.savefig(buf, format="png", dpi=150, bbox_inches="tight")
    plt.close()
    buf.seek(0)
    return buf.getvalue()

# ==============================================================
# 9. PDF GENERATOR (per stage)
# ==============================================================

def stage_pdf(stage_num: int, title: str, qa_pairs: list[tuple[str, str]], graph_img: bytes | None = None) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="Q", fontSize=12, textColor="navy", leftIndent=20))
    styles.add(ParagraphStyle(name="A", fontSize=11, leftIndent=40, spaceAfter=8))

    story = [
        Paragraph(f"<b>Stage {stage_num}: {title}</b>", styles["Title"]),
        Spacer(1, 12),
    ]

    for idx, (q, a) in enumerate(qa_pairs, 1):
        story.append(Paragraph(f"Q{idx}: {q}", styles["Q"]))
        story.append(Paragraph(f"A{idx}: {a}", styles["A"]))
        story.append(Spacer(1, 6))

    if graph_img:
        img_io = io.BytesIO(graph_img)
        story.append(PageBreak())
        story.append(Paragraph("Knowledge-Graph Snapshot", styles["Heading2"]))
        story.append(Image(img_io, width=6 * inch, height=4 * inch))

    doc.build(story)
    return buffer.getvalue()

# ==============================================================
# 10. UI – ONE FUNCTION PER STAGE
# ==============================================================

def render_stage(stage_num: int, title: str, inputs: dict, deps: list):
    """Render inputs, run LLM + agents, store PDF & QA."""
    st.header(f"Stage {stage_num}: {title}")

    # ---- inputs ----
    stage_inputs = {}
    for label, key in inputs.items():
        stage_inputs[key] = st.text_area(
            label,
            value=st.session_state.get(key, ""),
            key=f"input_{key}_{stage_num}"
        )

    # ---- dependency check ----
    ready = all(st.session_state.get(d, "") != "" for d in deps)

    if ready and st.button(f"Run Stage {stage_num} + Agents", key=f"run_{stage_num}"):
        with st.spinner("LLM → Ontology → Q&A → PDF …"):
            # 1. LLM
            kwargs = {
                **stage_inputs,
                **{f"stage{i}_output": st.session_state.get(f"stage{i}_output", "") for i in range(1, stage_num)}
            }
            llm_out = run_stage(f"stage{stage_num}", **kwargs)
            st.session_state[f"stage{stage_num}_output"] = llm_out

            # 2. Ontology
            ont = ontology_agent(llm_out)
            update_kg(stage_num, ont)

            # 3. Q&A
            qa = qa_extractor(llm_out)
            st.session_state[f"stage{stage_num}_qa"] = qa

            # 4. PDF
            graph_img = kg_png() if stage_num > 1 else None
            pdf_bytes = stage_pdf(stage_num, title, qa, graph_img)
            st.session_state[f"stage{stage_num}_pdf"] = pdf_bytes

        st.success(f"Stage {stage_num} finished!")

    # ---- show LLM output ----
    out = st.session_state.get(f"stage{stage_num}_output", "")
    if out:
        st.text_area(f"Stage {stage_num} LLM output", out, height=200, key=f"out_{stage_num}")

    # ---- show Q&A ----
    if f"stage{stage_num}_qa" in st.session_state:
        st.subheader("Extracted Q&A")
        for q, a in st.session_state[f"stage{stage_num}_qa"]:
            st.markdown(f"**Q:** {q}\n**A:** {a}")

    # ---- PDF download ----
    if f"stage{stage_num}_pdf" in st.session_state:
        pdf = st.session_state[f"stage{stage_num}_pdf"]
        st.download_button(
            label=f"Download Stage {stage_num} PDF",
            data=pdf,
            file_name=f"stage_{stage_num}_{title.replace(' ', '_')}.pdf",
            mime="application/pdf",
            key=f"dl_{stage_num}"
        )

# ==============================================================
# 11. PAGE LAYOUT
# ==============================================================

st.set_page_config(page_title="7-Stage Problem Solver + Ontology", layout="wide")
st.title("Universal 7-Stage Problem-Solving Assistant")
st.caption("Ollama (local) + Ontology Agents + PDF export")

st.sidebar.header("Model")
st.sidebar.write(f"**Model:** {MODEL}")
st.sidebar.write(f"**Ollama:** `{OLLAMA_EXE}`")

# initialise session keys
for i in range(1, 8):
    for suffix in ["_output", "_qa", "_pdf"]:
        key = f"stage{i}{suffix}"
        if key not in st.session_state:
            st.session_state[key] = ""

# --------------------------------------------------------------
# 12. STAGES
# --------------------------------------------------------------

render_stage(
    1, "Understand the Problem",
    {"Describe your problem:": "problem", "Provide context:": "context"},
    []
)

render_stage(
    2, "Research & Gather Information",
    {"Available data / assumptions:": "user_data"},
    ["stage1_output"]
)

render_stage(
    3, "Generate Possible Solutions",
    {"Preferences / priorities:": "preferences"},
    ["stage1_output", "stage2_output"]
)

render_stage(
    4, "Select the Best Solution",
    {"Selection criteria:": "criteria"},
    ["stage3_output"]
)

render_stage(
    5, "Plan Implementation",
    {"Resources / team:": "resources"},
    ["stage4_output"]
)

render_stage(
    6, "Testing & Verification",
    {"Testing info:": "testing_info"},
    ["stage5_output"]
)

render_stage(
    7, "Reflection & Optimization",
    {"Reflections / lessons:": "reflection"},
    ["stage6_output"]
)

# --------------------------------------------------------------
# 13. MASTER REPORT (after stage 7)
# --------------------------------------------------------------

if st.session_state.stage7_output and st.button("Generate Master PDF + Full Graph"):
    with st.spinner("Building master report…"):
        master_buf = io.BytesIO()
        doc = SimpleDocTemplate(master_buf, pagesize=letter)
        styles = getSampleStyleSheet()
        story = [Paragraph("Problem-Solving Master Report", styles["Title"]), Spacer(1, 20)]

        for i in range(1, 8):
            story.append(Paragraph(f"Stage {i}", styles["Heading1"]))
            for q, a in st.session_state.get(f"stage{i}_qa", []):
                story.append(Paragraph(f"Q: {q}", ParagraphStyle(name="Q", fontSize=11, textColor="navy")))
                story.append(Paragraph(f"A: {a}", styles["Normal"]))
            story.append(PageBreak())

        # full graph image
        full_img = kg_png()
        img_io = io.BytesIO(full_img)
        story.append(PageBreak())
        story.append(Paragraph("Final Knowledge Graph", styles["Heading1"]))
        story.append(Image(img_io, width=7 * inch, height=5 * inch))

        # Turtle export
        turtle = st.session_state.kg.serialize(format="turtle").decode()
        story.append(PageBreak())
        story.append(Paragraph("Knowledge Graph (Turtle)", styles["Heading2"]))
        story.append(Paragraph(f"<pre>{turtle}</pre>", ParagraphStyle(name="Code", fontName="Courier", fontSize=7)))

        doc.build(story)
        master_pdf = master_buf.getvalue()

        st.download_button(
            "Download Master Report (PDF)",
            data=master_pdf,
            file_name=f"master_problem_solving_{datetime.now():%Y%m%d_%H%M}.pdf",
            mime="application/pdf"
        )

        st.image(full_img, caption="Final Knowledge Graph")

st.success("All stages include **ontology agents**, **Q&A extraction**, and **PDF export**.")