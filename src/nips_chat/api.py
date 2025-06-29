import os
import replicate
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(filename="api.log", level=logging.INFO)

REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN")


class ReplicateAPI:
    """Wrapper class for interacting with Replicate API."""

    def __init__(self, model_version: str):
        """
        Initialize with a given model version.

        Args:
            model_version (str): Replicate model version ID
        """
        self.model_version = model_version
        if not REPLICATE_API_TOKEN:
            raise ValueError("REPLICATE_API_TOKEN environment variable not set.")

    def ask(self, question: str, context: str) -> str:
        """
        Ask a question to the language model with context.

        Args:
            question (str): The user question.
            context (str): The retrieved context to inject.

        Returns:
            str: The model's answer or an error message.
        """
        prompt = f"""[INST] <<SYS>>You are a helpful assistant answering questions about NIPS documentation.<</SYS>>

        Question: {question}

        Context: {context}

        Answer:
        [/INST]"""

        logger.info("Sending prompt to Replicate...")

        try:
            output = replicate.run(
              self.model_version,
              input={"prompt": prompt, "max_new_tokens": 512}
            )

            if not isinstance(output, list):
                output = list(output)

            logger.info("Replicate response contains %d item(s).", len(output))

            result_parts = []

            for i, item in enumerate(output):
                try:
                    if isinstance(item, str):
                        result_parts.append(item)
                    elif hasattr(item, "read"):
                        content = item.read().decode("utf-8")
                        result_parts.append(content)
                    else:
                        logger.warning(f"[{i}] Unknown output item type: {type(item)}. Coercing to string.")
                        result_parts.append(str(item))  # Fallback
                except Exception as e:
                    logger.warning(f"[{i}] Skipped item due to error: {e}")

            return "".join(result_parts).strip() if result_parts else "Error: No output returned."

        except Exception as e:
            logger.error(f"Error calling Replicate API: {str(e)}")
            return "Error: Failed to call Replicate API."

    def run(self, full_prompt: str) -> str:
        """
        Run a full prompt through the model (for when prompt is already formatted).

        Args:
            full_prompt (str): The full prompt to send.

        Returns:
            str: The model's response.
        """
        logger.info(f"Sending full prompt to Replicate:\n{full_prompt}\n")

        try:
            output = replicate.run(
              self.model_version,
              input={"prompt": full_prompt, "max_new_tokens": 512}
            )

            logger.info(f"Full Replicate response: {output}")

            if isinstance(output, str):
                return output.strip()
            elif isinstance(output, list):
                return "".join(output).strip()
            else:
                logger.error("Unexpected response format from Replicate.")
                return "Error: Unexpected response format."

        except Exception as e:
            logger.error(f"Error calling Replicate API: {str(e)}")
            return "Error: Failed to call Replicate API."

    def run_stream(self, full_prompt: str):
        """
        Run a full prompt through the model with streaming output.

        Args:
            full_prompt (str): The full prompt to send.

        Yields:
            str: Streaming output from the model.
        """
        try:
            iterator = replicate.run(
              self.model_version,
              input={"prompt": full_prompt, "max_new_tokens": 512},
              stream=True
            )

            for text in iterator:
                yield text

        except Exception as e:
            logger.error(f"Error calling Replicate API for streaming: {str(e)}")
            yield "Error: Failed to call Replicate API."
