import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")



# Inizializza il modello ChatGroq
chat_groq = ChatGroq(
    model="mixtral-8x7b-32768",
    temperature=0,
    groq_api_key=GROQ_API_KEY
)

def genera_embedding(testo):
    response = chat_groq.invoke([{"role": "user", "content": testo}])
    return response['embedding']