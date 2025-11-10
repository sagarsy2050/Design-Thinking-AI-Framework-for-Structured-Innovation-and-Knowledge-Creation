# 🧠 Design Thinking AI Framework for Structured Innovation and Knowledge Creation

A **Streamlit-based intelligent reasoning system** that guides users through a **structured 7-stage problem-solving process**, powered by **Ollama (LLM)**, **ontology-based knowledge representation**, and **semantic graph visualization**.
Design thinking and innovation empower problem solvers to empathize, define, ideate, prototype, and test solutions creatively, and when combined with ontology-driven knowledge structures, this creativity becomes organized, explainable, and reusable. Ontology ensures that ideas, constraints, and solutions are represented semantically rather than lost in unstructured text, while Large Language Models (LLMs) like Ollama add cognitive depth by simulating human reasoning, generating insights, and refining hypotheses. This fusion bridges creative intuition and logical structure, enabling both divergent and convergent thinking, transforming abstract innovation into a machine-understandable knowledge network. Design thinking drives the “why” and “what if,” while ontology and LLMs ensure the “how” and “what next,” creating a continuous loop of imagination, reasoning, and validation. Acting as cognitive memory, ontology helps each iteration build on verified knowledge, while LLMs expand ideas across contexts for adaptability and continuous learning. This synergy enables not only problem-solving but also knowledge creation, transparency, traceability, and collaboration across domains, uniting human-centered creativity with AI-structured logic into a true hybrid intelligence model that turns design ideas into semantically rich, testable, and scalable solutions—ultimately fostering systemic innovation where every insight becomes part of an evolving, intelligent knowledge ecosystem.
---

## 🚀 Overview

This application turns **unstructured problems** into **structured, explainable reasoning flows** using a combination of:

- 💡 **Large Language Models (via Ollama)**
- 🧩 **Ontology agents** (for entity–relation extraction)
- 🕸️ **Knowledge Graphs (RDF + NetworkX)**
- 📄 **Automated PDF Reports**
- 🧭 **7-stage cognitive problem-solving pipeline**

It’s designed for **explainable AI reasoning**, **knowledge engineering**, and **decision support** — combining **human-like structured thinking** with **machine-readable semantics**.

---

## 🧱 Architecture Summary

                        User Inputs (Problem, Context)
                                    │
                                    ▼
                        ┌──────────────────────────┐
                        │       Streamlit UI       │
                        │    (Stage 1 → Stage 7)   │
                        └──────────────────────────┘
                                    │
                                    ▼
                        ┌──────────────────────────┐
                        │ Ollama LLM Engine        │
                        │ (llama3.2-vision model)  │
                        └──────────────────────────┘
                                    │
                                    ▼
                        ┌──────────────────────────┐
                        │ Ontology Agent           │
                        │ (extracts entities,      │
                        │ relations, attributes)   │
                        └──────────────────────────┘
                                    │
                                    ▼
                        ┌──────────────────────────┐
                        │ RDF Knowledge Graph      │
                        │ (rdflib + networkx)      │
                        └──────────────────────────┘
                                    │
                                    ▼
                        ┌──────────────────────────┐
                        │ Q&A Extractor Agent      │
                        │ (for summarization)      │
                        └──────────────────────────┘
                                    │
                                    ▼
                        ┌──────────────────────────┐
                        │ PDF Generator (reportlab)│
                        │ (Stage & Master Reports) │
                        └──────────────────────────┘

---

## 🧩 The 7-Stage Problem-Solving Model
------------------------------------------------------------------------------------------------
| Stage                                 | Purpose                                               |
|:------|:------------------------------|-------------------------------------------------=-=---|
| **1. Understand the Problem**         | Restate, define constraints, and identify subproblems |
| **2. Research & Gather Information**  | Collect data, assumptions, and missing context        |
| **3. Generate Possible Solutions**    | Brainstorm alternatives with pros/cons                |
| **4. Select the Best Solution**       | Evaluate based on criteria and justification          |
| **5. Plan Implementation**            | Design stepwise plan and allocate resources           |
| **6. Testing & Verification**         | Define tests, predict risks, validate outcomes        |
| **7. Reflection & Optimization**      | Review, learn, and suggest improvements               |
------------------------------------------------------------------------------------------------

Each stage has a **dedicated LLM prompt template**, runs through **ontology extraction**, **Q&A summarization**, and **PDF export**.

---

## 🧠 Key Features
-----------------------------------------------------------------------------------------------------
| Feature                      | Description                                                         |
|------------------------------|-------------------------------------------------------------------- |
| 🧭 **Structured Reasoning** | Uses a 7-stage cognitive process for clear, logical problem-solving |
| 🧩 **Ontology Extraction**  | Converts LLM outputs into semantic JSON → RDF triples               |
| 🕸️ **Knowledge Graph**      | Visualizes entities, relations, and attributes across all stages    |
| 💬 **Q&A Extraction**       | Distills each stage output into concise question-answer pairs       |
| 📄 **PDF Reports**          | Generates per-stage and master reports with embedded graphs         |
| 🔁 **Session Persistence**  | Each stage’s output is stored and reused in later stages            |
| ⚡ **Local LLM (Ollama)**   | Works offline using llama3.2-vision or any supported model          |
-----------------------------------------------------------------------------------------------------
---

## 🧰 Technology Stack
---------------------------------------------------------------
| Component                      | Library / Tool             |
|--------------------- ----------|----------------------------|
| **UI Framework**               | Streamlit                  |
| **LLM Backend**                | Ollama (`llama3.2-vision`) |
| **Ontology / Semantic Graphs** | RDFLib, rdflib-namespace   |
| **Graph Visualization**        | NetworkX + Matplotlib      |
| **PDF Generation**             | ReportLab                  |
| **Image Handling**             | Pillow (PIL)               |
| **Data Serialization**         | JSON, Turtle (RDF)         |
---------------------------------------------------------------
---

## ⚙️ Installation & Setup

### 1️⃣ Prerequisites
- Python **3.10+**
- [Ollama](https://ollama.ai/download) installed locally  
  *(with model `llama3.2-vision` or compatible)*
- Basic dependencies for Streamlit and rdflib.

### 2️⃣ Clone the Repository
```bash
git clone https://github.com/yourusername/7stage-problem-solver.git
cd 7stage-problem-solver

3️⃣ Install Dependencies

pip install -r requirements.txt

4️⃣ Run the Application

streamlit run LLM-app.py

streamlit run app.py

🧮 Functional Workflow
Step-by-step data flow

   1. User provides inputs for the current stage (problem, context, etc.).

   2. LLM runs (via Ollama) to generate structured output.

   3. Ontology Agent converts text → structured semantic JSON.

    4.RDF graph updates with new entities and relationships.

    5.Q&A Agent extracts concise summaries.

    6.Stage PDF is generated.

    7.After Stage 7, Master Report combines all knowledge + graph + Turtle export.
🧾 Outputs

Stage PDFs: Contain Q&A summary + optional graph snapshot

Master PDF Report: All stages + final knowledge graph + RDF code

Turtle RDF Export: Machine-readable ontology data

💼 Example Use Cases

    1.Decision Support Systems

    2.Strategic Planning & Analysis

    3.Scientific Research Workflows

    4.Root-Cause or Failure Analysis

    5.Policy & Governance Modelling

    6.Educational or Training Simulations
