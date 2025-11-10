import streamlit as st
import subprocess
import shutil
import os

# -----------------------------
# CONFIG: Detect Ollama executable automatically
# -----------------------------
OLLAMA_EXE = shutil.which("ollama") or r"C:\Users\Sagar Yadav\AppData\Local\Programs\Ollama\ollama.exe"
MODEL = "llama3.2-vision"

# Verify Ollama installation
if not os.path.exists(OLLAMA_EXE):
    st.error(f"Ollama executable not found at {OLLAMA_EXE}. Please install or update the path.")
    st.stop()

# -----------------------------
# RUN OLLAMA FUNCTION
# -----------------------------
def run_ollama(prompt: str) -> str:
    """Run Ollama CLI with the given prompt and return output."""
    try:
        result = subprocess.run(
            [OLLAMA_EXE, "run", MODEL],
            input=prompt,
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            return f"⚠️ Error:\n{result.stderr}"
        return result.stdout.strip()
    except Exception as e:
        return f"❌ Exception: {e}"

# -----------------------------
# 7-Stage Prompt Templates
# -----------------------------
STAGE_PROMPTS = {
    "stage1": "Stage 1: Understand the Problem\nProblem: {problem}\nContext: {context}\nInstructions:\n- Restate the problem.\n- Identify key constraints.\n- Break into subproblems.\n",
    "stage2": "Stage 2: Research & Gather Information\nProblem Summary: {stage1_output}\nUser Data: {user_data}\nInstructions:\n- Identify needed info/data.\n- Make assumptions if data missing.\n",
    "stage3": "Stage 3: Generate Possible Solutions\nProblem Summary: {stage1_output}\nAssumptions: {stage2_output}\nPreferences: {preferences}\nInstructions:\n- List multiple solutions.\n- Pros and cons.\n- Explain reasoning.\n",
    "stage4": "Stage 4: Select the Best Solution\nPossible Solutions: {stage3_output}\nSelection Criteria: {criteria}\nInstructions:\n- Compare and justify chosen solution.\n- Provide reasoning.\n",
    "stage5": "Stage 5: Plan Implementation\nSelected Solution: {stage4_output}\nResources: {resources}\nInstructions:\n- Break solution into steps.\n- Assign priorities.\n- Expected outcomes.\n",
    "stage6": "Stage 6: Testing & Verification\nImplementation Plan: {stage5_output}\nTesting Info: {testing_info}\nInstructions:\n- Define test methods.\n- Predict issues & mitigations.\n",
    "stage7": "Stage 7: Reflection & Optimization\nSolution Outcome: {stage6_output}\nReflections: {reflection}\nInstructions:\n- Suggest improvements.\n- Optimize and summarize learnings.\n"
}

# -----------------------------
# RUN A STAGE
# -----------------------------
def run_stage(stage_name, **kwargs):
    prompt = STAGE_PROMPTS[stage_name].format(**kwargs)
    return run_ollama(prompt)

# -----------------------------
# STREAMLIT APP UI
# -----------------------------
st.set_page_config(page_title="🧠 7-Stage Problem-Solving Assistant", layout="wide")
st.title("🧠 Universal Problem-Solving Assistant (Local LLM)")
st.caption("Powered by Ollama + Streamlit — runs fully offline with `llama3.2-vision`.")

# Show model & environment
st.sidebar.header("🧩 Model & Environment")
st.sidebar.write(f"**Model:** {MODEL}")
st.sidebar.write(f"**Ollama Path:** {OLLAMA_EXE}")

# Initialize session state
for i in range(1, 8):
    key = f"stage{i}_output"
    if key not in st.session_state:
        st.session_state[key] = ""

# -----------------------------
# STAGES 1–7
# -----------------------------
def render_stage(stage_num, title, inputs, dependencies=None, copy_to=None):
    st.header(f"Stage {stage_num}: {title}")

    # Render inputs
    stage_inputs = {}
    for label, key in inputs.items():
        stage_inputs[key] = st.text_area(label, value=st.session_state.get(key, ""), key=key)

    # Dependency check
    deps_ok = all(st.session_state.get(dep, "") for dep in (dependencies or []))

    if deps_ok:
        if st.button(f"▶️ Run Stage {stage_num}"):
            st.session_state[f"stage{stage_num}_output"] = run_stage(
                f"stage{stage_num}",
                **{**stage_inputs, **{f"stage{i}_output": st.session_state.get(f'stage{i}_output', '') for i in range(1, stage_num)}}
            )
    else:
        st.info("⚠️ Please complete previous stage(s) first.")

    output = st.session_state[f"stage{stage_num}_output"]
    if output:
        st.text_area(f"Stage {stage_num} Output", output, height=200)
        if copy_to and st.button(f"Copy Stage {stage_num} Output → {copy_to.replace('_', ' ').title()}"):
            st.session_state[copy_to] = output

# Stage Definitions
render_stage(1, "Understand the Problem", {"Describe your problem:": "problem", "Provide context:": "context"}, copy_to="user_data")
render_stage(2, "Research & Gather Information", {"Available data:": "user_data"}, dependencies=["stage1_output"], copy_to="preferences")
render_stage(3, "Generate Possible Solutions (Ideation)", {"Preferences or priorities:": "preferences"}, dependencies=["stage1_output", "stage2_output"], copy_to="criteria")
render_stage(4, "Select the Best Solution", {"Selection criteria:": "criteria"}, dependencies=["stage3_output"], copy_to="resources")
render_stage(5, "Plan Implementation / Execution", {"Resources or team info:": "resources"}, dependencies=["stage4_output"], copy_to="testing_info")
render_stage(6, "Testing & Verification", {"Testing info:": "testing_info"}, dependencies=["stage5_output"], copy_to="reflection")
render_stage(7, "Reflection & Optimization", {"Reflections:": "reflection"}, dependencies=["stage6_output"])

# -----------------------------
# Generate Knowledge Graph
# -----------------------------
if st.session_state.stage7_output:
    if st.button("🧩 Generate Knowledge Graph / Logical Points"):
        points = [p.strip() for p in st.session_state.stage7_output.split("\n") if p.strip()]
        st.subheader("🧠 Logical Points Extracted")
        for i, point in enumerate(points, start=1):
            st.markdown(f"{i}. {point}")

st.success("✅ Workflow ready! Proceed step-by-step from Stage 1 → Stage 7.")
