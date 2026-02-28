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
        # #  playing with ai by MAKING IT BLIND 
        # prompt = f"""
        # You are a SQL expert. Write a SQL query for this request: {data.text}
        # Return ONLY the SQL code, nothing else.
        # """
    
    

        
        ai_response = model.generate_content(prompt)
        sql_query = ai_response.text.strip().replace("```sql", "").replace("```", "") # Cleaning the output
        
        # Step B: Python executes the AI's SQL query on your local database
        # conn = sqlite3.connect('pharmacy_inventory.db')
        # cursor = conn.cursor()
        # SECURITY FIREWALL: Block destructive SQL commands
        forbidden_words = ["DROP", "DELETE", "UPDATE", "INSERT", "ALTER"]
        if any(word in sql_query.upper() for word in forbidden_words):
            return {"status": "error", "prediction": "SECURITY ALERT: Destructive SQL operations are strictly blocked."}
        
        # Step B: Python executes the AI's SQL query safely
        # conn = sqlite3.connect('pharmacy_inventory.db')
        # cursor = conn.cursor()
        # cursor.execute(sql_query) # <--- THIS IS THE DANGER ZONE
        # --- SECURITY FIREWALL START ---
        # Convert the query to uppercase just for checking, so we catch "drop" and "DROP"
        upper_query = sql_query.upper()
        
        # List of destructive SQL commands we NEVER want the AI to run
        forbidden_keywords = ["DROP", "DELETE", "UPDATE", "INSERT", "ALTER", "TRUNCATE"]
        
        # Check if any forbidden word is inside the query
        if any(keyword in upper_query for keyword in forbidden_keywords):
            return {"prediction": "🚨 SECURITY BREACH AVERTED: Destructive database commands are strictly prohibited by the firewall."}
        # --- SECURITY FIREWALL END ---

        # If it passes the firewall, execute it safely
        conn = sqlite3.connect('pharmacy_inventory.db')
        cursor = conn.cursor()
        
        try:
            cursor.execute(sql_query)
            result = cursor.fetchall()
            conn.close()
            
            # Format the output for the UI
            if not result:
                return {"prediction": "No data found for this query."}
            return {"prediction": str(result)}
            
        except sqlite3.Error as e:
            # If the SQL is just badly written, catch the error instead of crashing the server
            return {"prediction": f"Database Error: {str(e)}"}
        
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