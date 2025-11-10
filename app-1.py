# ===================================================
# Empathize QA App (5W1H Framework)
# ===================================================

import streamlit as st
import json
import time
import openai
from typing import Dict, List

# -------------------------------
# 1. Expanded WH Question Bank
# -------------------------------
wh_questions = {
    "Who": [
        "Who uses this product/service the most?",
        "Who experiences the biggest pain points?",
        "Who influences the user’s decisions?",
        "Who is left out or ignored in current solutions?",
        "Who else is affected by this problem?",
        "Who do users turn to for advice or support?",
        "Who benefits most from the solution?",
        "Who are the secondary stakeholders impacted by this product/service?",
        "Who are the competitors’ primary users?",
        "Who might adopt this product/service in the future?"
    ],
    "What": [
        "What tasks do users try to accomplish?",
        "What problems frustrate users the most?",
        "What features are missing in current products/services?",
        "What do users enjoy about the current solution?",
        "What are users’ expectations and goals?",
        "What barriers prevent users from success?",
        "What motivates users to continue using a product/service?",
        "What are the most critical user needs?",
        "What alternative solutions do users consider?",
        "What outcomes do users prioritize?"
    ],
    "Where": [
        "Where do users interact with the product/service?",
        "Where do frustrations usually occur?",
        "Where are users most comfortable performing tasks?",
        "Where are bottlenecks in the workflow?",
        "Where do environmental factors impact user experience?",
        "Where do users access alternative solutions?",
        "Where are users located geographically?",
        "Where do users share feedback about the product/service?"
    ],
    "When": [
        "When do users experience the most stress?",
        "When do tasks need to be completed?",
        "When do problems occur most often?",
        "When are users likely to switch solutions?",
        "When is it most convenient for users to interact with the system?",
        "When do users feel most motivated to use the product/service?",
        "When do external events impact usage?",
        "When do users evaluate the product/service’s value?"
    ],
    "Why": [
        "Why do users choose this product/service?",
        "Why are current solutions inadequate?",
        "Why do certain problems persist?",
        "Why are some tasks frustrating?",
        "Why would users recommend or abandon a solution?",
        "Why do users prioritize certain features over others?",
        "Why do users trust or distrust the product/service?",
        "Why do users feel emotionally connected to the product/service?"
    ],
    "How": [
        "How do users currently solve this problem?",
        "How do users feel during the process?",
        "How do users describe their needs?",
        "How do users overcome obstacles?",
        "How do users measure success or satisfaction?",
        "How do users discover the product/service?",
        "How do users interact with support or community resources?",
        "How do users adapt the product/service to their needs?"
    ]
}


# -------------------------------
# 2. Function to fetch AI-generated answers
# -------------------------------
def ask_questions_ai(questions: Dict[str, List[str]], subject: str, api_key: str) -> Dict:
    """Use OpenAI GPT to answer WH questions for a target subject."""
    responses = {}
    try:
        openai.api_key = api_key
        for category, qs in questions.items():
            responses[category] = {}
            for q in qs:
                prompt = (
                    f"Target subject: {subject}\n"
                    f"Question: {q}\n"
                    f"Answer in 2-3 sentences with specific details:"
                )
                try:
                    response = openai.ChatCompletion.create(
                        model="gpt-4o-mini",
                        messages=[{"role": "user", "content": prompt}],
                        temperature=0.7,
                        max_tokens=150
                    )
                    answer_text = response['choices'][0]['message']['content'].strip()
                    responses[category][q] = answer_text
                    time.sleep(0.5)  # Avoid rate limits

                except openai.error.AuthenticationError:
                    responses[category][q] = "Error: Invalid API key"
                    st.error(f"Invalid API key for question: {q}")

                except openai.error.RateLimitError:
                    responses[category][q] = "Error: Rate limit exceeded"
                    st.error(f"Rate limit exceeded for question: {q}")
                    time.sleep(5)

                except Exception as e:
                    responses[category][q] = f"Error: {str(e)}"
                    st.error(f"Error for question {q}: {str(e)}")

    except Exception as e:
        st.error(f"Error during AI query: {str(e)}")

    return responses


# -------------------------------
# 3. Function to generate summary
# -------------------------------
def generate_summary(responses: Dict) -> str:
    """Generate a markdown summary of key insights from responses."""
    summary = "# Empathizing Perception Summary\n\n"
    summary += (
        "This summary synthesizes insights from the 5W1H framework to understand "
        "user needs, pain points, and opportunities.\n\n"
    )

    for category, qs in responses.items():
        summary += f"## {category}\n"
        for q, answer in qs.items():
            if not answer.startswith("Error:") and answer != "No response provided":
                summary += f"### {q}\n{answer}\n\n"
        summary += "---\n"

    # Add key insights section
    summary += "## Key Insights\n"
    summary += "- **Users and Stakeholders**: Identified primary users, influencers, and underserved groups to target.\n"
    summary += "- **Pain Points**: Highlighted frustrations and barriers that need addressing.\n"
    summary += "- **Opportunities**: Uncovered missing features and motivations for improved solutions.\n"
    summary += "- **Context**: Mapped where and when issues occur to design context-aware solutions.\n"
    summary += "\nUse these insights to define problems and ideate user-centered solutions."

    return summary


# -------------------------------
# 4. Main Streamlit App
# -------------------------------
def main():
    st.title("Empathize QA App")
    st.markdown(
        "Use the **5W1H framework** to gather insights for user-centered design. "
        "Choose a mode to answer questions manually or via AI."
    )

    # Mode selection
    mode = st.radio("Select Input Mode", ["Manual Input", "AI-Generated Answers"])

    # Initialize session state
    if 'responses' not in st.session_state:
        st.session_state.responses = {}
    if 'summary' not in st.session_state:
        st.session_state.summary = ""

    # Manual Input Mode
    if mode == "Manual Input":
        st.subheader("Manual Input")
        subject = st.text_input(
            "Enter target subject (e.g., product, service, user group)", key="manual_subject"
        )
        if subject:
            for category, qs in wh_questions.items():
                st.markdown(f"### {category} Questions")
                for q in qs:
                    response_key = f"{category}_{q}"
                    answer = st.text_area(q, key=response_key, height=100)
                    if category not in st.session_state.responses:
                        st.session_state.responses[category] = {}
                    if answer:
                        st.session_state.responses[category][q] = answer or "No response provided"

    # AI Mode
    elif mode == "AI-Generated Answers":
        st.subheader("AI-Generated Answers")
        subject = st.text_input(
            "Enter target subject (e.g., product, service, user group)", key="ai_subject"
        )
        api_key = st.text_input("Enter OpenAI API key", type="password", key="api_key")

        if st.button("Generate AI Answers"):
            if not subject:
                st.error("Please enter a target subject.")
                return
            if not api_key:
                st.error("Please enter an OpenAI API key.")
                return

            with st.spinner("Generating AI responses..."):
                responses = ask_questions_ai(wh_questions, subject, api_key)
                st.session_state.responses = responses
                st.session_state.summary = generate_summary(responses)
                st.success("AI responses generated successfully!")

    # Display Summary
    if st.session_state.summary:
        st.markdown("---")
        st.markdown(st.session_state.summary)


if __name__ == "__main__":
    main()
