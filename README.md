# aigenburg

**aigenburg** is a lightweight LLM API firewall designed to restrict unauthenticated public access to LLM (Large Language Model) endpoints, allowing only predefined and approved prompts.
It is built to seamlessly integrate with the [Arize Phoenix](https://arize.com/phoenix/) prompt management and monitoring platform; and OpenAI-compatible APIs.

## How It Works

1. The client sends a request to generate text using a specific prompt, optionally including variable values.  
2. aigenburg validates the request by fetching the prompt (by name or ID) from the upstream Arize Phoenix server.  
3. If the prompt exists, it is considered authorized. aigenburg then forwards the request to the LLM API. OpenAI-compatible APIs are currently supported.  
4. The response from the LLM API is returned to the client.

## Development

### Prerequisites

```
pip install -r requirements.txt
```

or:
```
pip install tornado
pip install openai
pip install arize-phoenix-client
```

### Run the application

```
source .venv/bin/activate
OPENAI_API_KEY=your_openai_api_key \
OPENAI_API_URL=your_openai_api_url \
PHOENIX_API_KEY=your_phoenix_api_key \
PHOENIX_API_URL=your_phoenix_api_url \
python main.py
```

or ideally use a .env file to set the environment variables.
```
source .venv/bin/activate
source .env
python main.py
```


## Docker Image

### Build and Run Docker Container
```bash
docker build --platform linux/amd64 -t ghcr.io/agajdosi/aigenburg:latest .
docker run -d -p 8080:8080 ghcr.io/agajdosi/aigenburg:latest
```

### Build and Publish Docker Image
```bash
docker build --platform linux/amd64 -t ghcr.io/agajdosi/aigenburg:latest .
docker push ghcr.io/agajdosi/aigenburg:latest
```
