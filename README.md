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

## Copy Deps from Pipfile.lock to Firebase Functions

Unfortunately, Firebase Functions comes not with an option to choose `pipenv`. It does only install deps from ordinary functions/requirements.txt file.

```bash
pipenv shell
pipenv sync
pipenv run pip freeze > functions/requirements.txt
```

> You should repeat this every time you change the deps. https://github.com/pypa/pipenv/issues/3493

## Start RAG-based Chatbot API locally

```bash
python3 -m pip install pipenv
pipenv shell
REPLICATE_API_TOKEN="<token from replicate.com account>" TOKENIZERS_PARALLELISM=false uvicorn --app-dir="src" nips_chat_api.chat_api:app --reload
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
REPLICATE_API_TOKEN="<token from replicate.com account>" python3 src/nips_chat/chat_cli.py
```

## Deploy RAG-based Chatbot to Firebase Functions

Copy the following configs to the functions/.env file.

```bash
REPLICATE_API_TOKEN="<token from replicate.com account>"
TOKENIZERS_PARALLELISM=false
```

### Install Deps
```bash
python3 -m venv venv
. ./venv/bin/activate
python3 -m pip install -r requirements.txt
```

### Deploy Functions

```bash
firebase login
firebase deploy --only functions
```
