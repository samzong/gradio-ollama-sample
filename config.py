import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Environment variables configuration
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
os.environ['OLLAMA_HOST'] = OLLAMA_HOST