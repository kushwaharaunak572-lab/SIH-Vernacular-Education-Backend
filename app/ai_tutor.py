
import os
import time
from pathlib import Path

from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from google import genai


# Load backend/.env
ENV_FILE = Path(__file__).resolve().parents[1] / ".env"
load_dotenv(ENV_FILE)

router = APIRouter(
    prefix="/ai-tutor",
    tags=["AI Tutor"]
)


class TutorRequest(BaseModel):
    question: str = Field(min_length=1, max_length=2000)
    language: str = Field(default="Hindi", max_length=50)
    subject: str = Field(default="General", max_length=100)


class TutorResponse(BaseModel):
    answer: str
    language: str
    subject: str


@router.get("/health")
def ai_tutor_health():
    return {
        "status": "ready",
        "message": "AI Tutor endpoint is available"
    }


@router.post("/ask", response_model=TutorResponse)
def ask_ai_tutor(request: TutorRequest):
    api_key = os.getenv("GEMINI_API_KEY")
    model = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")

    if not api_key:
        raise HTTPException(
            status_code=503,
            detail="GEMINI_API_KEY missing. Check backend/.env."
        )

    prompt = f"""
You are a friendly tutor for primary-school students.
Explain concepts simply, accurately, and step by step.
Use age-appropriate, everyday examples.
Respond in the requested language.
If the question is unclear, ask a short clarifying question.

Language: {request.language}
Subject: {request.subject}
Student's question: {request.question}
"""

    try:
        client = genai.Client(api_key=api_key)
        response = None

        # Retry up to 3 times for temporary Gemini 503 errors
        for attempt in range(3):
            try:
                response = client.models.generate_content(
                    model=model,
                    contents=prompt
                )
                break

            except Exception as exc:
                error_text = str(exc).upper()

                is_temporary_error = (
                    "503" in error_text
                    or "UNAVAILABLE" in error_text
                )

                if not is_temporary_error or attempt == 2:
                    raise

                # Wait 2 seconds, then 4 seconds before retrying
                time.sleep(2 * (attempt + 1))

        if response is None:
            raise HTTPException(
                status_code=502,
                detail="Gemini did not return a response. Please try again."
            )

        answer = response.text or ""

        if not answer.strip():
            raise HTTPException(
                status_code=502,
                detail="Gemini returned an empty answer. Please try again."
            )

        return TutorResponse(
            answer=answer.strip(),
            language=request.language,
            subject=request.subject
        )

    except HTTPException:
        raise

    except Exception as exc:
        # Do not print API keys or other secrets
        print(
            f"Gemini AI Tutor error: "
            f"{type(exc).__name__}: {exc}"
        )

        raise HTTPException(
            status_code=502,
            detail=(
                "Gemini could not answer. Check the model name, "
                "API key, network, and API quota."
            )
        ) from exc