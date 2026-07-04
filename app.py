import os
import sys

# =====================================================================
# OS COMPLIANCE PATCHES (Must run before ANY other imports)
# =====================================================================

# 1. LINUX/CODESPACES FIX: Force the newer pysqlite3 driver globally
if sys.platform.startswith("linux"):
    try:
        import pysqlite3
        # This completely rewrites the native sqlite3 reference for Python
        sys.modules["sqlite3"] = pysqlite3
        # Explicitly trick Chroma into reading the newer version string
        pysqlite3.sqlite3_version_info = (3, 35, 0) 
    except ImportError:
        pass

# 2. WINDOWS FIX: Replace illegal colons ':' with '_' for file locks
if sys.platform.startswith("win"):
    import builtins
    original_open = builtins.open

    def windows_safe_open(file, *args, **kwargs):
        if isinstance(file, str) and "crewai:" in file:
            file = file.replace("crewai:", "crewai_")
        return original_open(file, *args, **kwargs)

    builtins.open = windows_safe_open
# =====================================================================

# NOW you can safely import Streamlit and CrewAI
import streamlit as st
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process, LLM

# Load variables from local .env file (if running locally)
load_dotenv()

# App UI Settings & Configurations
st.set_page_config(page_title="AI Product Winner Agent", layout="wide")
st.title("🏆 Autonomous Product Winner Crew")
st.subheader("Paste raw e-commerce data to let agents declare the best product.")

# Configure Gemini 2.5 Flash Engine
gemini_llm = LLM(
    model="gemini/gemini-2.5-flash",
    api_key=os.environ.get("GEMINI_API_KEY")
)

# Define specialized AI Agents
data_extractor = Agent(
    role="E-Commerce Data Extraction Expert",
    goal="Filter out marketing fluff and extract clear technical specs and prices.",
    backstory="You are a data engineer who turns messy, unorganized product descriptions into clean, structured technical spec sheets.",
    llm=gemini_llm,
    verbose=True
)

market_analyst = Agent(
    role="Senior Product Analyst",
    goal="Compare parsed specifications and declare a definitive winner with a clear rationale.",
    backstory="You are a critical consumer analyst. You compare value-for-money, feature advantages, and hardware quality gaps to crown a winner.",
    llm=gemini_llm,
    verbose=True
)

# User Interface Layout Input Boxes
col1, col2 = st.columns(2)
with col1:
    prod1 = st.text_area("📦 Paste Product 1 Details (from Amazon / Flipkart):", height=250, placeholder="Example: Product A specifications, price, reviews...")
with col2:
    prod2 = st.text_area("📦 Paste Product 2 Details (from Amazon / Flipkart):", height=250, placeholder="Example: Product B specifications, price, reviews...")

# Execution Trigger Pipeline
if st.button("🚀 Run Comparison Analysis", type="primary"):
    if prod1.strip() and prod2.strip():
        with st.spinner("🧠 Multi-Agent Crew is analyzing features, mapping gaps, and voting on the winner..."):
            
            # Formulate Crew Tasks
            task1 = Task(
                description=f"Extract clear, unbiased technical specifications and pricing metrics from the following inputs:\n\nProduct 1 Details:\n{prod1}\n\nProduct 2 Details:\n{prod2}", 
                expected_output="A structured list of key specifications for both products, separating facts from marketing hyperbole.", 
                agent=data_extractor
            )
            
            task2 = Task(
                description="Review the extracted data from the previous task. Compare them side-by-side. Evaluate price-to-performance metrics, identify core feature gaps, and choose an absolute WINNER with justification.", 
                expected_output="A polished Markdown report featuring a comparison matrix table, identified feature flaws/gaps, and a highly visible header declaring the absolute WINNER.", 
                agent=market_analyst
            )
            
            # Assemble the Crew Framework
            crew = Crew(
                agents=[data_extractor, market_analyst], 
                tasks=[task1, task2], 
                process=Process.sequential
            )
            
            # Execute the workflow
            result = crew.kickoff()
            
            # Render output directly onto the web interface screen
            st.success("🏁 Analysis Complete!")
            st.markdown("---")
            st.markdown(result.raw)
    else:
        st.warning("⚠️ Action Required: Please paste product details into both input fields to run the comparison.")