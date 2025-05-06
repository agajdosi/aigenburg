import os
from typing import Optional, Dict
import json

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI
from phoenix.client import Client
from phoenix.client.utils import template_formatters
from phoenix.otel import register
from httpx import HTTPStatusError
from pydantic import BaseModel
from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode
from openinference.semconv.trace import SpanAttributes, OpenInferenceSpanKindValues

app = FastAPI(
    title="aigenburg API",
    description=
        "aigenburg is a dead simple API for unauthenticated requests to OpenAI or any other OpenAI compatible API provider (e.g. LiteLLM proxy). "
        "Prompts are defined in Arize Phoenix server. Undefined prompts are not allowed. "
        "This brings basic security as attackers can't call the API with arbitrary prompts.",
    version="0.1.0",
    contact={
        "name": "aigenburg",
        "url": "https://github.com/agajdosi/aigenburg",
    },
    openapi_url="/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    swagger_ui_parameters={"defaultModelsExpandDepth": -1},
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency for OpenAI client
def get_openai_client():
    return OpenAI(
        api_key=os.getenv("OPENAI_API_KEY"),
        base_url=os.getenv("OPENAI_API_URL"),
    )

# Dependency for Phoenix client
def get_phoenix_client():
    return Client(
        api_key=os.getenv("PHOENIX_API_KEY"),
        base_url=os.getenv("PHOENIX_API_URL"),
    )

@app.get("/health")
async def index():
    return "OK"

class GenerateRequest(BaseModel):
    prompt_identifier: str
    prompt_variables: Optional[Dict[str, str]] = None # Phoenix templater has problems with non-string values, so forcing the use of strings

@app.post("/generate")
async def generate(
    request: GenerateRequest,
    openai_client: OpenAI = Depends(get_openai_client),
    phoenix_client: Client = Depends(get_phoenix_client)
):
    """Generate a response for a latest prompt version, filled with the provided variables."""
    tracer = trace.get_tracer(__name__)
    with tracer.start_as_current_span(request.prompt_identifier) as span:
        span.set_attribute(SpanAttributes.OPENINFERENCE_SPAN_KIND, OpenInferenceSpanKindValues.CHAIN.value)
        span.set_attribute(SpanAttributes.INPUT_VALUE, json.dumps(request.prompt_variables))
        try:
            prompt_version = phoenix_client.prompts.get(prompt_identifier=request.prompt_identifier)
            span.set_attribute("prompt.version_id", str(prompt_version.id))
                
        except HTTPStatusError as e:
            detail = f"prompt_identifier not found. {str(e)}"
            span.set_status(Status(StatusCode.ERROR), f"{detail} ({e.response.status_code})")
            raise HTTPException(
                status_code=e.response.status_code,
                detail=detail
            )
            
        # Format the prompt with the variables and request the LLM
        try:
            formatted_prompt = prompt_version.format(variables=request.prompt_variables or {})
        except template_formatters.TemplateFormatterError as e:
            detail = f"Error formatting prompt: {str(e)}"
            span.set_status(Status(StatusCode.ERROR), detail)
            raise HTTPException(
                status_code=400,
                detail=detail
            )

        resp = openai_client.chat.completions.create(**formatted_prompt)
        resp_text = resp.choices[0].message.content
        span.set_attribute(SpanAttributes.OUTPUT_VALUE, str(resp_text))
        resp_json = resp.model_dump_json()
        span.set_status(Status(StatusCode.OK))
        return resp_json

if __name__ == "__main__":
    collector_endpoint = os.environ.get("PHOENIX_COLLECTOR_ENDPOINT")
    if not collector_endpoint:
        print("No Phoenix collector endpoint provided, skipping tracer configuration")
    else:
        project = os.environ.get("PHOENIX_OTEL_PROJECT", "aigenburg")
        print(f"Configuring Phoenix tracer for {project} to endpoint {collector_endpoint}")
        tracer_provider = register(project_name=project, auto_instrument=True)
        #tracer = tracer_provider.get_tracer(__name__)

    import uvicorn
    uvicorn.run(
        app,
        host=os.getenv("HOST", "127.0.0.1"),
        port=int(os.getenv("PORT", 8888)),
        reload=False
    )

