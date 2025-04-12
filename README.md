# aigenburg

aigenburg is a simple API to limit public unauthenticated access to LLM endpoints to only allowed prompts.
It is designed to be used in conjuction with Arize Phoenix prompt management and monitoring system.

## Design

1. Client calls the API with @arize/phoenix-client library, aigenburg is compliant with the Phoenix client library.
2. aigenburg will use the prompt name or prompt id and get it from upstream Arize Phoenix server.
3. If the prompt is defined, FirewallLLM will call the actual LLM API with the prompt (OpenAI style API is supported).
4. The response from the LLM API is sent to the client.


## Installation

```
pip install -r requirements.txt
```

or:
```
pip install tornado
pip install openai
pip install arize-phoenix-client
```

## Development

```
source .env
source .venv/bin/activate
python main.py
```
