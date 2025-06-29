from fastapi import FastAPI, Response
from pydantic import BaseModel

from nips_chat.api import ReplicateAPI
from nips_chat.qa_nips import NIPSQA

DATASET_PATH = "data/nips_dataset.jsonl"
REPLICATE_MODEL_VERSION = "deepseek-ai/deepseek-v3"

app = FastAPI()

class PredictRequest(BaseModel):
    user_q: str

def prediction(user_q: str):
    qa_system = NIPSQA(DATASET_PATH)
    replicate_api = ReplicateAPI(REPLICATE_MODEL_VERSION)

    retrieved = qa_system.retrieve_top_k(user_q, k=3)
    prompt = qa_system.compose_prompt(user_q, retrieved)
    return replicate_api.run(prompt)

@app.post("/predict")
async def predict(request: PredictRequest):
    return Response(prediction(request.user_q), media_type="plain/text")
