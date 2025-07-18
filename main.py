# main.py
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from backend.db import SessionLocal
from sqlalchemy import text
from backend.logic import classify_query_local, generate_sql_query, call_ollama

app = FastAPI()

class QueryRequest(BaseModel):
    query: str

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    import traceback
    traceback.print_exc()
    return JSONResponse(
        status_code=500,
        content={"error": "Internal Server Error", "detail": str(exc)},
    )
@app.post("/chat")
async def chat_handler(request: QueryRequest):
    query = request.query.strip()
    print("Received query:", query)

    if not query:
        return {"error": "Query is required"}

    route = classify_query_local(query)
    print(f"Classified route: {route}")

    if route == "llm":
        response = await call_ollama(query)
    elif route == "sql":
        sql = await generate_sql_query(query)
        print("Generated SQL:", sql)
        db = SessionLocal()
        result = db.execute(text(sql)).fetchall()
        db.close()
        response = f"SQL Executed:\n{sql}\n\nResult: {result}"
    else:
        response = "I couldn't determine how to handle this query."

    return {"response": response}
