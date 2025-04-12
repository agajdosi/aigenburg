import asyncio
import logging
import os
import tornado
from openai import OpenAI
from phoenix.client import Client
from phoenix.client.utils import template_formatters
from httpx import HTTPStatusError

openai_client: OpenAI
phoenix_client: Client

class IndexHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("OK")

class GenerateHandler(tornado.web.RequestHandler):
    def args_to_dict(self) -> dict:
        params = self.request.arguments
        for k,v in params.items():
            params[k] = v[0].decode("utf-8")
        return params
    
    def get(self):
        self.post()

    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "*")
        self.set_header("Access-Control-Allow-Methods", "POST, GET, OPTIONS")

    def options(self):
        self.set_default_headers()
        self.set_status(204)
        self.finish()

    def post(self):        
        global openai_client, phoenix_client
        self.set_default_headers()
        params = self.args_to_dict()
        try:
            identifier = params.pop("prompt_identifier")
        except KeyError:
            self.set_status(400)
            self.write("prompt_identifier is required")
            return
        
        try:
            prompt_version = phoenix_client.prompts.get(prompt_identifier=identifier)
        except HTTPStatusError as e:
            self.set_status(e.response.status_code)
            self.write(f"prompt_identifier not found. {str(e)}")
            return
        
        logging.info("Got prompt version: " + str(prompt_version.id))
        
        # Format the prompt with the variables and request the LLM
        try:
            formatted_prompt = prompt_version.format(variables=params)
            logging.info("Formatted prompt: " + str(formatted_prompt))
        except template_formatters.TemplateFormatterError as e:
            self.set_status(400)
            self.write(f"Error formatting prompt: {str(e)}")
            return

        resp = openai_client.chat.completions.create(**formatted_prompt)
        resp_json = resp.model_dump_json()
        logging.info("Response: " + resp_json)
        self.write(resp_json)

        
def configure_clients():
    global openai_client, phoenix_client
    openai_api_key = os.getenv("OPENAI_API_KEY")
    openai_api_url = os.getenv("OPENAI_API_URL")
    phoenix_api_key = os.getenv("PHOENIX_API_KEY")
    phoenix_api_url = os.getenv("PHOENIX_API_URL")
    openai_client = OpenAI(
        api_key=openai_api_key,
        base_url=openai_api_url,
    )
    phoenix_client = Client(
        api_key=phoenix_api_key,
        base_url=phoenix_api_url,
    )

async def main():
    configure_clients()
    app = tornado.web.Application([
        (r"/", IndexHandler),
        (r"/v1/generate", GenerateHandler),
         ],
        debug=os.getenv("DEBUG", "false") == "true",
        autoreload=os.getenv("DEBUG", "false") == "true",
    )
    app.listen(8888)
    await asyncio.Event().wait()



if __name__ == "__main__":
    asyncio.run(main())

