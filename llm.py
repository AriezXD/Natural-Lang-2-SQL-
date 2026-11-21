
import os
import time

from dotenv import load_dotenv
from google import genai
from google.genai import errors

from database import get_schema, format_schema
from prompts import SYSTEM_PROMPT

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

if not API_KEY:
    raise ValueError("GEMINI_API_KEY not found in .env file")

client = genai.Client(api_key=API_KEY)


def generate_sql(question: str) -> str:
    """Convert a natural language question into SQL."""

    if not question or not question.strip():
        raise ValueError("Question cannot be empty")

    schema = format_schema(get_schema())

    prompt = SYSTEM_PROMPT.format(
        schema=schema,
        question=question
    )

    max_retries = 3

    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model=MODEL,
                contents=prompt
            )

            if not response.text:
                raise RuntimeError("Gemini returned an empty response")

            return response.text.strip()

        except errors.APIError as e:
            # Retry temporary server-side errors
            if e.code in (429, 500, 502, 503, 504):
                if attempt < max_retries - 1:
                    wait_time = 2 ** (attempt + 1)

                    print(
                        f"Gemini temporarily unavailable. "
                        f"Retrying in {wait_time} seconds..."
                    )

                    time.sleep(wait_time)
                    continue

                raise RuntimeError(
                    f"Gemini API unavailable after {max_retries} attempts. "
                    f"Error: {e.message}"
                ) from e

            # Don't retry permanent client-side errors
            raise RuntimeError(
                f"Gemini API error ({e.code}): {e.message}"
            ) from e
