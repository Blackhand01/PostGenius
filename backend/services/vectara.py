import os
from dotenv import load_dotenv
import requests
import json


load_dotenv()

VECTARA_CUSTOMER_ID = os.getenv("VECTARA_CUSTOMER_ID")
VECTARA_API_KEY = os.getenv("VECTARA_API_KEY")
VECTARA_CORPORA = os.getenv("VECTARA_CORPORA")
VECTARA_CORPUS_API_KEY = os.getenv("VECTARA_CORPUS_API_KEY")

def indicizza_documento_vectara(documento):
    url = "https://api.vectara.io/v2/corpora/"+VECTARA_CORPORA+"/documents"
    payload = {
        "id": documento['id'],
        "type": "core",
        "metadata": documento['metadata'],
        "document_parts": [{
            "text": documento['text'],
            "context": "string",
            "custom_dimensions": {}
            }],
        
    }
    headers = {
        "Content-Type": "application/json",
        'Accept': 'application/json',
        "x-api-key": VECTARA_API_KEY
    }
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    #print("\n\n\n Risulatoto indx: ", response)
    if response.status_code == 201:
        print("\nDocumento indicizzato con successo.")
    else:
        print(f"Errore nell'indicizzazione: {response.status_code} - {response.text}")


def cerca_documenti(prompt, num_results=3, metadata_filter=""):
    url = "https://api.vectara.io/v2/query"  # URL corretto

    # Costruzione del payload
    payload = {
        "query": prompt,
        "search": {
            "corpora": [
                {
                    "corpus_key": VECTARA_CORPORA,  # Specifica il corpus nel payload
                    "metadata_filter": metadata_filter,
                    "lexical_interpolation": 0.005,
                    "custom_dimensions": {}
                }
            ],
            "offset": 0,
            "limit": num_results,
            "context_configuration": {
                "sentences_before": 2,
                "sentences_after": 2,
                "start_tag": "<em>",
                "end_tag": "</em>"
            },
            "reranker": {
                "type": "customer_reranker",
                "reranker_id": "rnk_272725719"
            }
        },
        "generation": {
            "generation_preset_name": "mockingbird-1.0-2024-07-16",
            "max_used_search_results": 3,
            "response_language": "eng",
            "enable_factual_consistency_score": True,
            "max_response_characters": 500
        },
        "stream_response": False,
        "save_history": True
    }

    # Intestazioni della richiesta
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "x-api-key": VECTARA_API_KEY
    }

    # Effettua la richiesta
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    
    print("Risultato coglione: ", response.json())

    # Verifica della risposta
    if response.status_code == 200:
        risultati = response.json()
        output = risultati['summary']
        return output
    else:
        raise ValueError(f"Errore nella ricerca: {response.status_code} - {response.text}")
