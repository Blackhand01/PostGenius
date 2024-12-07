#!/bin/bash

# Creazione della struttura di directory
mkdir -p backend/services
mkdir -p backend/utils
mkdir -p backend/models

# Creazione dei file principali
touch backend/main.py
touch backend/requirements.txt
touch backend/.env
touch backend/README.md

# Creazione dei file nei sottodirectory
touch backend/services/news_retrieval.py
touch backend/services/vectara.py
touch backend/services/groq.py

touch backend/utils/llm.py
touch backend/utils/image_generation.py
touch backend/utils/meme_generation.py
touch backend/utils/video_generation.py
touch backend/utils/openai_client.py

touch backend/models/requests.py
touch backend/models/responses.py

echo "La struttura è stata creata con successo!"
# bash create_backend_structure.sh
