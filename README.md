# Autonomous Product Winner Crew

An advanced Multi-Agent workflow powered by **CrewAI** and **Google Gemini 2.5 Flash** that takes messy, raw text from e-commerce listings, cleans it, maps feature gaps, and votes on an absolute comparison winner.

##  One-Click Testing (100% Free Cloud Setup)

You do not need to download this repository or install Python locally. You can test this live system directly inside your web browser using **GitHub Codespaces**:

1. Click the green **"Code"** button at the top right of this repository, select the **Codespaces** tab, and click **"Create codespace on main"**.
2. Once the environment loads (requirements install automatically), paste your secure Gemini API key into the terminal and hit enter:
   ```bash
   export GEMINI_API_KEY="your-gemini-key-here" && streamlit run app.py