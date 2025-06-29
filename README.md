# NBuild.io NIPs Chatbot Model

NBuild.io chatbot model is using RAG-based Question and Answering over NIPs docs. [DeepSeek-V3](https://github.com/deepseek-ai/DeepSeek-V3).

## Official Nostr Sources used by RAG

- [GitHub nostr-protocol/nips](https://github.com/nostr-protocol/nips)

> More to mention soon.

You can [open a ticket here](https://github.com/nbuild-io/nbuild-nips-chat-model/issues/new) if you want to include specific data in the RAG-based chatbot.

## Start RAG-based Chatbot API locally

```bash
pip3 install pipenv
pipenv shell
REPLICATE_API_TOKEN="<token from replicate.com account>" uvicorn nips_chat_api.chat_api:app --reload
```

### Using CURL to get a Q answered
```bash
curl -X "POST" "http://127.0.0.1:8000/predict" \
     -H 'Content-Type: application/json; charset=utf-8' \
     -d $'{
  "user_q": "Describe what Nostr is?"
}'
```
