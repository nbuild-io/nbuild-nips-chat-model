FROM python:3.13.5-slim

WORKDIR /app

COPY . .

RUN python3 -m pip install pipenv && \
    pipenv lock && \
    pipenv install --system --deploy

EXPOSE 8080

CMD ["uvicorn", "nips_chat_api.chat_api:app", "--app-dir", "src", "--host", "0.0.0.0", "--port", "8080", "--reload"]
