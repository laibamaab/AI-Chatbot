# backend/logic.py
import httpx

OLLAMA_URL = "http://localhost:11434"

def classify_query_local(query: str) -> str:
    keywords = ["customers", "sales", "products", "tips", "price", "amount", "email"]
    return "sql" if any(word in query.lower() for word in keywords) else "llm"

async def async_post_ollama(payload):
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(f"{OLLAMA_URL}/api/generate", json=payload)
            response.raise_for_status()
            return response.json()
    except Exception as e:
        print(f"LLM Error: {e}")
        raise

async def call_ollama(query: str, model: str = "mistral") -> str:
    payload = {
        "model": model,
        "prompt": query,
        "stream": False
    }

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(f"{OLLAMA_URL}/api/generate", json=payload)
            response.raise_for_status()

            print("Raw response text:", response.text)
            raw = response.json()
            print("General LLM Response:", raw) 

            return raw.get("response", "No response from model.")
        
    except Exception as e:
        print(f"LLM Error: {e}")
        return "Sorry, I couldn't get an answer from the language model."

async def generate_sql_query(question: str) -> str:
    prompt = f"""
You are an expert PostgreSQL SQL query generator.

Here are the database tables and relationships:

    customers(id, name, email, orders)
    products(id, name, price)
    sales(id, product_id, customer_id, amount, date)  FK: product_id → products.id, customer_id → customers.id
    tips(id, customer_id, tip_amount)

A customer can purchase many products via the sales table.
Write a SQL query to answer the following question:

User: {question}

ONLY return the SQL query. No explanation.
"""
    try:
        payload = {"model": "mistral", "prompt": prompt, "stream": False}
        response = await async_post_ollama(payload)
        print("Raw response from Mistral:", response)
        return response["response"].strip()
    
    except Exception as e:
        print(f"SQL Generator LLM Error: {e}")
        return "SELECT 'LLM failed to generate SQL.';"
