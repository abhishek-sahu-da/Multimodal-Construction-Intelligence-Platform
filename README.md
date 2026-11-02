# Multimodal Construction Intelligence Platform

A Streamlit capstone-style app based on the uploaded Skill Wallet & FutureSkills Prime guide's Project 1 specification.

## Features
- Construction photo upload and preliminary PPE/safety audit
- Crack diagnostics and cautious structural-integrity triage
- Planning estimates: budget, expenditure incurred, indicative asset value, steel and cement
- Weather-aware daily site advisory and rule-based assistant
- Downloadable JSON reports
- Optional Gemini image analysis; transparent demo mode if no API key is provided
- No database required

## Run locally
1. Install Python 3.9 or newer.
2. Create/activate a virtual environment (recommended).
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Start:
   ```bash
   streamlit run app.py
   ```

## Optional Gemini setup
Enter a valid Gemini API key in the app sidebar. The key is held in session state and is not written to disk by this app. If the API is unavailable or no key is supplied, demo output is used.

## Deploy to Streamlit Community Cloud
1. Push `app.py`, `requirements.txt`, and `README.md` to a public GitHub repository.
2. Connect the repository to Streamlit Community Cloud.
3. Select `app.py` and deploy.
4. Copy the HTTPS demo URL into Skill Wallet's **Add Demo Link** field.
5. Submit the GitHub repository URL into Skill Wallet's **Add Github Link** field.

## Limitations and safety
This is a student demonstration and decision-support prototype. AI image outputs can be wrong. Never use it to certify PPE compliance, determine structural safety, approve lifting operations, or replace a qualified safety officer/structural engineer. Rates and quantities are illustrative assumptions; use project-specific BOQs, local rates, and professional advice.
