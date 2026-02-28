# 💊 PharmaPulse AI: Autonomous B2B Inventory Agent

![PharmaPulse AI Dashboard](./screenshot.png) 
*(Note: Replace `screenshot.png` with an actual screenshot of your Tailwind UI)*

## 🚀 Overview
PharmaPulse AI is a Full-Stack Text-to-SQL AI Agent designed for wholesale pharmaceutical distributors. It bridges the gap between non-technical business owners and complex database analytics. Instead of relying on rigid SQL dashboards, users can query stock levels, expiration dates, and wholesale margins using natural language. 

The system leverages Google's Gemini 2.5 Flash LLM to autonomously translate English prompts into optimized SQLite queries, executes them against a local ledger, and returns clean, formatted data in real-time.



## 🏗️ System Architecture
- **Frontend (The Face):** Decoupled, asynchronous Single Page Application (SPA) built with vanilla JavaScript, HTML5, and Tailwind CSS for a glassmorphism SaaS aesthetic.
- **Backend (The Brain):** High-performance Python REST API powered by **FastAPI**.
- **Database (The Muscle):** Embedded **SQLite** database simulating a high-volume B2B medical inventory ledger.
- **AI Engine:** **Google Gemini 2.5 Flash** integrated via `google-generativeai` for sub-second NLP-to-SQL translation.

## ✨ Key Features
- **Zero-Shot SQL Generation:** Dynamically generates accurate SQL queries across multiple tables and columns without hardcoded parameters.
- **Fuzzy Search & Substring Parsing:** Prompt-engineered to handle complex B2B queries, including wildcard matching for varying drug dosages and string extraction for expiration dates.
- **Secure Environment Variables:** API keys and sensitive configurations are strictly isolated using `python-dotenv`.
- **Asynchronous Execution:** Non-blocking API endpoints ensure UI responsiveness during LLM inference and database querying.

## 🛠️ Quick Start Guide

### 1. Clone the Repository
```bash
git clone [https://github.com/yourusername/pharmapulse-ai.git](https://github.com/yourusername/pharmapulse-ai.git)
cd pharmapulse-ai