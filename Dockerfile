FROM python:3.13-alpine

WORKDIR /app

COPY requirements.txt .
COPY main.py .

RUN pip install -r requirements.txt

ENV PRODUCTION=true
ENV OPENAI_API_KEY=""
ENV OPENAI_API_URL=""
ENV PHOENIX_API_KEY=""
ENV PHOENIX_API_URL=""
ENV HOST="0.0.0.0"

CMD ["python", "main.py"]
