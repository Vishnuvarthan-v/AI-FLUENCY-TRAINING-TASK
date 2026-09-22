"""Shared configuration: chooses the LLM provider and holds the bookstore data."""
import os
from dotenv import load_dotenv
from openai import OpenAI
 
load_dotenv()
 
PROVIDER = os.getenv("PROVIDER", "ollama").strip().lower()
 
if PROVIDER == "ollama":
    BASE_URL = "http://localhost:11434/v1"
    API_KEY = "ollama"
    MODEL = os.getenv("MODEL", "qwen2.5:1.5b")
elif PROVIDER == "groq":
    BASE_URL = "https://api.groq.com/openai/v1"
    API_KEY = os.getenv("GROQ_API_KEY")
    MODEL = os.getenv("MODEL", "openai/gpt-oss-20b")
elif PROVIDER == "huggingface":
    BASE_URL = "https://router.huggingface.co/v1"
    API_KEY = os.getenv("HF_TOKEN")
    MODEL = os.getenv("MODEL", "openai/gpt-oss-20b")
else:
    raise SystemExit(f"Unknown PROVIDER '{PROVIDER}'. Use ollama, groq or huggingface.")
 
if not API_KEY:
    raise SystemExit(f"No API key found for PROVIDER={PROVIDER}. Check your .env file.")
 
client = OpenAI(base_url=BASE_URL, api_key=API_KEY)
 
# Private bookstore data that no public LLM has ever seen
BOOKS = {
    "ALCH01": {"title": "The Alchemist", "price": 350, "stock": 40},
    "ATOM02": {"title": "Atomic Habits", "price": 450, "stock": 25},
    "SAPI03": {"title": "Sapiens", "price": 550, "stock": 10},
}
 
QUESTIONS = [
    "What is the price of Atomic Habits (ATOM02)?",
    "What is the total cost of 2 copies of The Alchemist (ALCH01) and 1 copy of Sapiens (SAPI03)?",
    "Is the stock of The Alchemist (ALCH01) more than Sapiens (SAPI03), and by how much?",
    "Write a two-line message announcing a weekend book fair discount.",
]
 
def banner(system_name):
    print(f"\n=== {system_name} | provider: {PROVIDER} | model: {MODEL} ===\n")
