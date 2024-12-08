import os
from dotenv import load_dotenv
import requests
import json


load_dotenv()

VECTARA_CUSTOMER_ID = os.getenv("VECTARA_CUSTOMER_ID")
VECTARA_API_KEY = os.getenv("VECTARA_API_KEY")
VECTARA_CORPORA = os.getenv("VECTARA_CORPORA")

def indicizza_documento_vectara(documento):
    url = "https://api.vectara.io/v2/corpora/{VECTARA_CORPORA}/documents"
    headers = {
        "Content-Type": "application/json",
        'Accept': 'application/json',
        "Authorization": {VECTARA_API_KEY}
    }
    payload = {
        #"corpus_key": [{"customer_id": VECTARA_CUSTOMER_ID, "corpus_id": VECTARA_CORPORA}],
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


def cerca_documenti(prompt, num_results=5, metadata_filter=None):
    
    url = "https://api.vectara.io/v2/corpora/{VECTARA_CORPORA}/query"
    
    # Costruzione del payload
    payload = {
        "query": prompt,
        "search": {
            "custom_dimensions": {},
            "metadata_filter": metadata_filter if metadata_filter else "",
            "lexical_interpolation": 0.025,
            "semantics": "default",
            "offset": 0,
            "limit": num_results,
            "context_configuration": {
                "characters_before": 30,
                "characters_after": 30,
                "sentences_before": 3,
                "sentences_after": 3,
                "start_tag": "<em>",
                "end_tag": "</em>"
            },
            "reranker": {
                "type": "customer_reranker",
                "reranker_name": "Rerank_Multilingual_v1",
                "limit": 0,
                "cutoff": 0
            }
        },
        "generation": {
            "generation_preset_name": "vectara-summary-ext-v1.2.0",
            "max_used_search_results": 5,
            "prompt_template": (
                "[\n"
                "  {\"role\": \"system\", \"content\": \"You are a helpful search assistant.\"},\n"
                "  #foreach ($qResult in $vectaraQueryResults)\n"
                "     {\"role\": \"user\", \"content\": \"Given the $vectaraIdxWord[$foreach.index] search result.\"},\n"
                "     {\"role\": \"assistant\", \"content\": \"${qResult.getText()}\" },\n"
                "  #end\n"
                "  {\"role\": \"user\", \"content\": \"Generate a summary for the query '${vectaraQuery}' based on the above results.\"}\n"
                "]"
            ),
            "max_response_characters": 300,
            "response_language": "auto",
            "model_parameters": {
                "max_tokens": 0,
                "temperature": 0,
                "frequency_penalty": 0,
                "presence_penalty": 0
            },
            "citations": {
                "style": "none",
                "url_pattern": "https://vectara.com/documents/{doc.id}",
                "text_pattern": "{doc.title}"
            },
            "enable_factual_consistency_score": True
        },
        "stream_response": False,
        "save_history": False
    }
    
    # Intestazioni della richiesta
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "x-api-key": VECTARA_API_KEY
    }

    # Effettua la richiesta
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    
    # Verifica della risposta
    if response.status_code == 200:
        risultati = response.json()
        output = []
        for risultato in risultati.get("search_results", []):
            output.append({
                "document_id": risultato.get("document_id"),
                "text": risultato.get("text"),
                "score": risultato.get("score"),
                "metadata": risultato.get("document_metadata"),
            })
        return output
    else:
        raise ValueError(f"Errore nella ricerca: {response.status_code} - {response.text}")
