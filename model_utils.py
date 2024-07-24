import sys
import ollama

def get_available_models():
    try:
        models = ollama.list()
        return [model['name'] for model in models['models']]
    except Exception as e:
        print(f"Error fetching models: {e}")
        sys.exit(1)

def initialize_models():
    available_models = get_available_models()
    if not available_models:
        print("No models available from Ollama service.")
        sys.exit(1)
    return available_models[0], available_models