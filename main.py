import asyncio
import os
import tornado
from openai import OpenAI
from phoenix.client import Client

openai_client: OpenAI
phoenix_client: Client

class IndexHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("OK")

class GenerateHandler(tornado.web.RequestHandler):
    def get(self):
        global openai_client, phoenix_client
        prompt = phoenix_client.get_prompt(self.request.body)
        self.write(prompt)


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
    ])
    app.listen(8888)
    await asyncio.Event().wait()



if __name__ == "__main__":
    asyncio.run(main())

