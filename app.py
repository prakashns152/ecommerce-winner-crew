import os
import sys

# =====================================================================
# WINDOWS FIX: Monkeypatch portalocker to replace illegal colons ':' with '_'
# Place this at the absolute top of app.py before importing CrewAI
# =====================================================================
if sys.platform.startswith("win"):
    import builtins
    original_open = builtins.open

    def windows_safe_open(file, *args, **kwargs):
        if isinstance(file, str) and "crewai:" in file:
            # Replace the illegal colon with a safe underscore for Windows
            file = file.replace("crewai:", "crewai_")
        return original_open(file, *args, **kwargs)

    builtins.open = windows_safe_open
# =====================================================================

import streamlit as st
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process, LLM

# Load variables from .env file
load_dotenv()

# App UI Settings
st.set_page_config(page_title="AI Product Winner Agent", layout="wide")
st.title("🏆 Autonomous Product Winner Crew")
st.subheader("Paste raw e-commerce data to let agents declare the best product.")

# Configure Gemini
gemini_llm = LLM(
    model="gemini/gemini-2.5-flash",
    api_key=os.environ.get("GEMINI_API_KEY")
)

# Agents
data_extractor = Agent(
    role="E-Commerce Data Extraction Expert",
    goal="Filter out marketing fluff and extract clear specs and prices.",
    backstory="You are a data engineer who turns messy product descriptions into clean, structured technical specs.",
    llm=gemini_llm,
    verbose=True
)

market_analyst = Agent(
    role="Senior Product Analyst",
    goal="Compare parsed specs and declare a definitive winner.",
    backstory="You are a critical consumer analyst. You compare value-for-money and feature gaps to crown a winner.",
    llm=gemini_llm,
    verbose=True
)

# UI Layout
col1, col2 = st.columns(2)
with col1:
    prod1 = st.text_area("📦 Paste Product 1 Details:", height=250)
with col2:
    prod2 = st.text_area("📦 Paste Product 2 Details:", height=250)

if st.button("🚀 Run Analysis"):
    if prod1 and prod2:
        with st.spinner("Agents are analyzing..."):
            task1 = Task(
                description=f"Extract clear specs from the following products:\nProduct 1: {prod1}\nProduct 2: {prod2}", 
                expected_output="A list of key specifications for each product including pricing.", 
                agent=data_extractor
            )
            task2 = Task(
                description="Compare the extracted specs. Evaluate which product offers better features, value for money, and build quality. Declare a definitive WINNER.", 
                expected_output="Comparison report with an explicit WINNER section.", 
                agent=market_analyst
            )
            
            crew = Crew(
                agents=[data_extractor, market_analyst], 
                tasks=[task1, task2], 
                process=Process.sequential
            )
            result = crew.kickoff()
            
            st.success("Analysis Complete!")
            st.markdown(result.raw)
    else:
        st.warning("Please paste data in both boxes.")