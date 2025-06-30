# NBuild.io NIPs Chatbot RAG Model

NBuild.io chatbot is using RAG-based question answering over NIPs docs. [DeepSeek-V3](https://github.com/deepseek-ai/DeepSeek-V3).

## Install Python and Tools

Since many Python versions may be installed, you must check that Python 3.13, pip and pipenv are installed correctly.

```bash
python3 --version
python3 -m ensurepip
python3 -m pip --version
python3 -m pip install pipenv
python3 -m pipenv --version
```

## Formatter: Google Yapf

Before you start coding, you must install Yapf to active code formatting.

[Visual Studio Code: Google Yapf Extension](https://marketplace.visualstudio.com/items?itemName=eeyore.yapf)

```bash
python3 -m pip install yapf
```

> You should check which Python installation is active in Visual Studio Code or Cursor.

## Official Nostr Sources used by RAG

- [GitHub nostr-protocol/nips](https://github.com/nostr-protocol/nips)

> More to mention soon.

You can [open a ticket here](https://github.com/nbuild-io/nbuild-nips-chat-model/issues/new) if you want to include specific data in the RAG-based chatbot.

## Start RAG-based Chatbot API locally

```bash
python3 -m pip install pipenv
pipenv shell
REPLICATE_API_TOKEN="<token from replicate.com account>" TOKENIZERS_PARALLELISM=false uvicorn nips_chat_api.chat_api:app --app-dir="src" --reload
```

### Using CURL to get a Q answered

```bash
curl -X "POST" "http://127.0.0.1:8000/predict" \
     -H 'Content-Type: application/json; charset=utf-8' \
     -d $'{
  "user_q": "Describe what Nostr is?"
}'
```

## Start RAG-based Chatbot CLI locally

You could also chat with NBuild.io Chatbot via a terminal. We prefer this when improving the RAG-based chatbot and its Nostr and NIPs knowledge.

```bash
REPLICATE_API_TOKEN="<token from replicate.com account>" TOKENIZERS_PARALLELISM=false python3 src/nips_chat/chat_cli.py
```

## Build and Run Docker Image

You should install [Docker Desktop on Mac](https://docs.docker.com/desktop/setup/install/mac-install/) and [Google Cloud CLI](https://cloud.google.com/sdk/docs/install-sdk) before you proceed.

You can deploy our NBuild.io RAG-based Model to other Docker platforms as well. But we recommend to start with Google Cloud Run because of the low operating costs and best reliability.

```bash
gcloud login
gcloud config set project [id]
gcloud services enable run.googleapis.com
```

### Build Docker Image on Google Cloud

```bash
docker build -t gcr.io/[id]/nbuild-nips-chat-model .
docker push gcr.io/[id]/nbuild-nips-chat-model
```

### Deploy to Cloud Run on Google Cloud

```bash
gcloud run deploy nbuild-nips-chat-model \
    --image gcr.io/[id]/nbuild-nips-chat-model \
    --platform managed \
    --region us-central1 \
    --port 8080 \
    --cpu 1 \
    --memory 4Gi \
    --min-instances 1 \
    --max-instances 2 \
    --set-env-vars REPLICATE_API_TOKEN="<token from replicate.com account>",TOKENIZERS_PARALLELISM=false \
    --allow-unauthenticated
```
