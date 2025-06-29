import os
from qa_nips import NIPSQA
from api import ReplicateAPI

DATASET_PATH = "data/nips_dataset.jsonl"
REPLICATE_MODEL_VERSION = "deepseek-ai/deepseek-v3"


def run_cli() -> None:
    """
    Runs the interactive CLI chatbot for NIPS Q&A.
    """
    print("Initializing NIPS Q&A system...")
    qa_system = NIPSQA(DATASET_PATH)
    replicate_api = ReplicateAPI(REPLICATE_MODEL_VERSION)

    print("\nNIPS Q&A System Ready. Ask questions (type 'exit' to quit).")
    while True:
        user_q = input("\nYour question: ")
        if user_q.lower() == "exit":
            print("Goodbye, thank you for using the NIPS Chat!")
            break
        try:
            retrieved = qa_system.retrieve_top_k(user_q, k=3)
            prompt = qa_system.compose_prompt(user_q, retrieved)
            answer = replicate_api.run(prompt)
            print(f"\nAnswer:\n{answer}\n")
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    run_cli()
