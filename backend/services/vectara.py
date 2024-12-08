import os
from dotenv import load_dotenv
import requests
import json


load_dotenv()

VECTARA_CUSTOMER_ID = os.getenv("VECTARA_CUSTOMER_ID")
VECTARA_API_KEY = os.getenv("VECTARA_API_KEY")
VECTARA_CORPORA = os.getenv("VECTARA_CORPORA")

def indicizza_documento_vectara(documento):
    url = "https://api.vectara.io/v1/index"
    headers = {
        "Content-Type": "application/json",
        "customer-id": VECTARA_CUSTOMER_ID,
        "Authorization": f"Bearer {VECTARA_API_KEY}"
    }
    payload = {
        "corpus_key": [{"customer_id": VECTARA_CUSTOMER_ID, "corpus_id": VECTARA_CORPORA}],
        "document": [{
            "documentId": documento['id'],
            "title": documento['titolo'],
            "metadataJson": json.dumps(documento['metadata']),
            "section": [{"text": documento['contenuto']}],
        }]
    }
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    if response.status_code == 200:
        print("Documento indicizzato con successo.")
    else:
        print(f"Errore nell'indicizzazione: {response.status_code} - {response.text}")

def cerca_documenti(prompt):
    url = "https://api.vectara.io/v1/query"
    headers = {
        "Content-Type": "application/json",
        "customer-id": VECTARA_CUSTOMER_ID,
        "Authorization": f"Bearer {VECTARA_API_KEY}"
    }
    payload = {
        "query": [{
            "query": prompt,
            "num_results": 5,
            "corpus_key": [{"customer_id": VECTARA_CUSTOMER_ID, "corpus_id": VECTARA_CORPORA}],
        }]
    }
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    if response.status_code == 200:
        risultati = response.json()
        for risultato in risultati.get("responseSet", []):
            for documento in risultato.get("document", []):
                print(f"Titolo: {documento.get('title')}")
                print(f"Contenuto: {documento.get('snippet')}\n")
    else:
        print(f"Errore nella ricerca: {response.status_code} - {response.text}")
