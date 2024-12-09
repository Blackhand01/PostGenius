# PostGenius
An AI agent capable of autonomously retrieving the most relevant daily news articles, summarizing them, and generating engaging social media posts in multiple formats, including text, images, videos, and memes, based on user-defined inputs.

---

## Overview

**PostGenius** is an AI-powered application that leverages Retrieval-Augmented Generation (RAG) techniques to produce multimedia content such as text posts, images, memes, and videos based on news articles. It is designed for applications like social media management, marketing campaigns, and content creation. The project integrates various APIs, including Groq, Vectara, OpenAI, RunwayML, and NewsAPI, to deliver an efficient and seamless experience.

---

## Setup and Usage

### 1. Development Environment Setup

#### Requirements
- **Operating System**: macOS/Linux/Windows
- **Python**: Version 3.9 or higher
- **Node.js**: Version 18 or higher
- **Package Management**: `pip`, `npm`, and `virtualenv` for Python environments

#### Steps
1. Clone the repository:
   ```bash
   git clone https://github.com/<your-username>/postgenius.git
   cd postgenius
   ```

2. Set up a Python virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. Install Python dependencies:
   ```bash
   pip install -r backend/requirements.txt
   ```

4. Install JavaScript dependencies for the frontend:
   ```bash
   cd frontend
   npm install
   cd ..
   ```

5. Configure required API keys:
   - Create a `.env` file in the `backend/` directory and add the following keys:
     ```
     NEWSAPI_KEY=your_newsapi_key
     OPENAI_API_KEY=your_openai_key
     GROQ_API_KEY=your_groq_key
     VECTARA_CUSTOMER_ID=your_vectara_customer_id
     VECTARA_API_KEY=your_vectara_api_key
     RUNWAY_API_KEY=your_runway_api_key
     IMGFLIP_USERNAME=your_imgflip_username
     IMGFLIP_PASSWORD=your_imgflip_password
     ```

### 2. Running the Backend and Frontend

#### Backend (FastAPI)
Run the backend from the main directory:
```bash
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend (Next.js)
Run the frontend from the `frontend` directory:
```bash
cd frontend
npm run dev
```

The application will be accessible at:
- **Frontend**: [http://localhost:3000](http://localhost:3000)
- **Backend**: [http://localhost:8000](http://localhost:8000)

---

## Dependencies and Execution Instructions

### Project Dependencies

#### Python (Backend)
- **FastAPI**: Framework for building APIs.
- **Pydantic**: Data validation and parsing.
- **Requests**: For HTTP requests.
- **dotenv**: For managing environment variables.

Install all dependencies with:
```bash
pip install -r backend/requirements.txt
```

#### JavaScript (Frontend)
- **Next.js**: Framework for building web applications.
- **Axios**: For API calls.
- **Radix UI**: Accessible components.
- **Tailwind CSS**: For styling.

Install all dependencies with:
```bash
npm install
```

### System Requirements

- **RAM**: Minimum 8 GB, 16 GB recommended
- **CPU**: Quad-core processor or better
- **Storage**: At least 2 GB of available space

---

## Architecture Diagrams

### Primary Workflow

```plaintext
User Input --> Backend API (FastAPI)
            --> RAG Retrieval (Groq + Vectara)
            --> Content Generation (OpenAI)
            --> Multimedia Creation (RunwayML, Imgflip, OpenAI DALL-E)
            --> Response (Text, Image, Meme, Video, Sources)
```

- **Frontend**: Interface for user input and displaying generated content.
- **Backend**: Manages retrieval and content generation through various API modules.
- **Storage**: Indexed data is stored on Vectara for efficient retrieval.

---

## Workflow Explanation

### Step-by-Step

1. **User Input**: The user provides a prompt, tone, and target platform (e.g., Twitter, Instagram).
2. **Prompt Processing**: The backend uses the `groq.py` module to analyze and optimize the prompt.
3. **Retrieval**:
   - Articles are fetched from NewsAPI and Reddit.
   - Vectara indexes and retrieves relevant articles.
4. **Summary Generation**:
   - OpenAI GPT generates a summary of the retrieved articles.
5. **Multimedia Creation**:
   - **Text**: Social media posts are generated using OpenAI GPT.
   - **Images**: Illustrations are created using OpenAI DALL-E.
   - **Memes**: Memes are generated via Imgflip with captions from OpenAI GPT.
   - **Videos**: Videos are created using RunwayML.
6. **Results**: The generated content is sent to the frontend and displayed to the user.

### Key Features
- **Tone Customization**: Adapts content to styles like humorous, formal, or casual.
- **Multi-Format Support**: Generates text, images, videos, and memes.
- **Cited Sources**: Provides a list of URLs as sources for the generated content.

---

## Useful Commands

### To Run Locally
```bash
# Start the backend
uvicorn main:app --reload

# Start the frontend
cd frontend
npm run dev
```

### To Run in Production
```bash
# Build and start the frontend
cd frontend
npm run build
npm run start

# Start the backend with Gunicorn
cd backend
gunicorn main:app -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Debugging
- View logs for backend and frontend:
  ```bash
  tail -f backend.log
  tail -f frontend.log
  ```