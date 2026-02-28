import os
import sqlite3
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import google.generativeai as genai
from dotenv import load_dotenv

# 1. Boot up the AI
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-2.5-flash')

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class UserInput(BaseModel):
    text: str

# 2. The Database Map (So the AI knows what columns exist)
DB_SCHEMA = """
Table name: inventory
Columns: 
- id (INTEGER)
- medicine_name (TEXT)
- generic_name (TEXT)
- category (TEXT)
- stock_box_count (INTEGER)
- wholesale_price_per_box (REAL)
- expiry_date (TEXT, format YYYY-MM-DD)
"""

@app.post("/predict")
async def make_prediction(data: UserInput):
    try:
        # Step A: Force the AI to act as a SQL translator
        prompt = f"""
        You are an expert SQL Data Analyst for a wholesale pharmacy.
        Here is the database schema: {DB_SCHEMA}
        
        The user asked: "{data.text}"
        
        Write a valid SQLite query to answer this question. 
        IMPORTANT RULES:
        1. When searching for a medicine, always use the LIKE operator with wildcards (e.g., LIKE '%medicine%') because the database contains dosages in the names.
        2. Search across both medicine_name AND generic_name.
        3. Return ONLY the raw SQL code. Do not include markdown formatting, backticks, or any explanations. Just the SQL.
        """
        
        ai_response = model.generate_content(prompt)
        sql_query = ai_response.text.strip().replace("```sql", "").replace("```", "") # Cleaning the output
        
        # Step B: Python executes the AI's SQL query on your local database
        conn = sqlite3.connect('pharmacy_inventory.db')
        cursor = conn.cursor()
        cursor.execute(sql_query)
        db_results = cursor.fetchall()
        conn.close()
        
        # Step C: Format the output for the screen
        if not db_results:
            return {"status": "success", "prediction": f"Executed Query: {sql_query}\n\nResult: No matching records found."}
            
        # Extract the raw answer from the ugly database tuple!
        clean_answer = db_results[0][0]
            
        return {"status": "success", "prediction": f"Executed Query: {sql_query}\n\nResult: We have {clean_answer} boxes in stock."}
        
    except Exception as e:
        return {"status": "error", "prediction": f"System Failure: {str(e)}"}