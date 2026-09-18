from __future__ import annotations

import subprocess
import tempfile
from functools import lru_cache
from pathlib import Path
from typing import List

from fastapi import FastAPI, HTTPException, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Import the REAL dissertation implementation.
# Run this API from the dissertation project root so that the existing
# relative paths used by src/predict_food.py resolve correctly.
from src.predict_food import (
    load_knowledge_base,
    run_kg,
    run_svm,
    hybrid_decision,
    personalised_decision,
)


app = FastAPI(
    title="P-HAF-KG V2.1 API",
    description=(
        "API wrapper around the implemented P-HAF-KG V2.1 + "
        "TF-IDF/Linear SVM personalised food-analysis pipeline "
        "with Tesseract OCR support."
    ),
    version="1.1.0",
)


# ============================================================
# CORS
# ============================================================

# Demo configuration.
# For production, replace "*" with the exact frontend origin.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# REQUEST / RESPONSE MODELS
# ============================================================

class AnalyseFoodRequest(BaseModel):
    ingredient_text: str = Field(..., min_length=1)
    allergies: List[str] = Field(default_factory=list)


class AnalyseFoodResponse(BaseModel):
    decision: str
    confirmed_allergens: List[str]
    potential_allergens: List[str]
    review_candidates: List[str]
    direct_evidence: List[str]
    precautionary_evidence: List[str]
    user_confirmed_matches: List[str]
    user_potential_matches: List[str]
    user_review_matches: List[str]


# ============================================================
# KNOWLEDGE BASE
# ============================================================

@lru_cache(maxsize=1)
def get_knowledge():
    """Load the dissertation knowledge base once per API process."""
    return load_knowledge_base()


# ============================================================
# CORE FOOD ANALYSIS
# ============================================================

def analyse_food(
    ingredient_text: str,
    allergies: List[str],
):
    """Run the actual dissertation prediction pipeline."""

    user_allergies = {
        str(allergy).strip().lower()
        for allergy in allergies
        if str(allergy).strip()
    }

    knowledge = get_knowledge()

    # P-HAF-KG V2.1
    kg = run_kg(
        ingredient_text,
        knowledge,
    )

    # TF-IDF + Linear SVM
    svm = run_svm(
        ingredient_text,
    )

    # Hybrid reasoning
    hybrid = hybrid_decision(
        kg,
        svm,
    )

    # Personalised decision
    (
        decision,
        confirmed_matches,
        potential_matches,
        review_matches,
    ) = personalised_decision(
        hybrid["confirmed"],
        hybrid["potential"],
        hybrid["review_candidates"],
        user_allergies,
    )

    return {
        "decision": decision,
        "confirmed_allergens": sorted(
            hybrid["confirmed"]
        ),
        "potential_allergens": sorted(
            hybrid["potential"]
        ),
        "review_candidates": sorted(
            hybrid["review_candidates"]
        ),
        "direct_evidence": sorted(
            kg["direct_matches"]
        ),
        "precautionary_evidence": sorted(
            kg["precautionary_matches"]
        ),
        "user_confirmed_matches": sorted(
            confirmed_matches
        ),
        "user_potential_matches": sorted(
            potential_matches
        ),
        "user_review_matches": sorted(
            review_matches
        ),
    }


# ============================================================
# OCR
# ============================================================

SUPPORTED_IMAGE_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".webp",
    ".bmp",
    ".tif",
    ".tiff",
}


def run_ocr(
    image_bytes: bytes,
    filename: str,
) -> str:
    """
    Run Tesseract OCR on an uploaded food-label image.

    Uses the same OCR settings as the existing dissertation
    OCR prototype:
        languages = eng+fra+deu
        page segmentation mode = 6

    OCR only extracts text.
    Allergen analysis remains the responsibility of
    the P-HAF-KG V2.1 pipeline.
    """

    suffix = Path(filename).suffix.lower()

    if suffix not in SUPPORTED_IMAGE_EXTENSIONS:
        raise ValueError(
            "Unsupported image format. "
            "Use JPG, JPEG, PNG, WEBP, BMP, TIF or TIFF."
        )

    temporary_path = None

    try:
        # Save uploaded image temporarily
        with tempfile.NamedTemporaryFile(
            suffix=suffix,
            delete=False,
        ) as temporary_file:

            temporary_file.write(image_bytes)
            temporary_path = Path(
                temporary_file.name
            )

        # Tesseract OCR
        command = [
            "tesseract",
            str(temporary_path),
            "stdout",
            "-l",
            "eng+fra+deu",
            "--psm",
            "6",
        ]

        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            raise RuntimeError(
                "Tesseract failed: "
                + result.stderr.strip()
            )

        # Basic OCR text cleaning
        cleaned_lines = []

        for line in result.stdout.splitlines():
            line = line.strip()

            if line:
                cleaned_lines.append(line)

        return "\n".join(cleaned_lines).strip()

    finally:
        # Remove temporary image
        if temporary_path is not None:
            try:
                temporary_path.unlink(
                    missing_ok=True
                )
            except Exception:
                pass


# ============================================================
# ROOT
# ============================================================

@app.get("/")
def root():
    return {
        "name": "P-HAF-KG V2.1 API",
        "status": "running",
        "model": "P-HAF-KG V2.1",
        "baseline": "TF-IDF + Linear SVM",
        "ocr": "Tesseract",
        "ocr_languages": [
            "eng",
            "fra",
            "deu",
        ],
    }


# ============================================================
# HEALTH
# ============================================================

@app.get("/health")
def health():
    try:
        knowledge = get_knowledge()

        return {
            "status": "ok",
            "model": "P-HAF-KG V2.1",
            "baseline": "TF-IDF + Linear SVM",
            "ocr": "Tesseract",
            "ocr_languages": "eng+fra+deu",
            "knowledge_relationships_loaded": len(
                knowledge
            ),
        }

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Model initialisation failed: {exc}",
        )


# ============================================================
# ANALYZE FOOD
# ============================================================

@app.post(
    "/analyze-food",
    response_model=AnalyseFoodResponse,
)
def analyze_food(
    request: AnalyseFoodRequest,
):
    ingredient_text = request.ingredient_text.strip()

    if not ingredient_text:
        raise HTTPException(
            status_code=400,
            detail="ingredient_text cannot be empty.",
        )

    try:
        return analyse_food(
            ingredient_text,
            request.allergies,
        )

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Prediction failed: {exc}",
        )


# ============================================================
# OCR + ANALYZE FOOD
# ============================================================

@app.post("/ocr-analyze")
async def ocr_analyze(
    file: UploadFile = File(...),
    allergies: str = Form(""),
):
    """
    Upload a food-label image.

    Image
      -> Tesseract OCR
      -> ingredient text
      -> P-HAF-KG V2.1
      -> TF-IDF + Linear SVM
      -> hybrid reasoning
      -> personalised decision
    """

    filename = file.filename or "food_label.jpg"

    try:
        # Read image
        image_bytes = await file.read()

        if not image_bytes:
            raise HTTPException(
                status_code=400,
                detail="Uploaded image is empty.",
            )

        # OCR
        extracted_text = run_ocr(
            image_bytes,
            filename,
        )

        # OCR produced no usable text
        if not extracted_text:
            return {
                "filename": filename,
                "ocr_text": "",
                "allergies": [],
                "message": "No readable text was detected.",
                "analysis": None,
            }

        # Convert:
        # "milk, peanut, soy"
        # into:
        # ["milk", "peanut", "soy"]
        allergy_list = [
            item.strip().lower()
            for item in allergies.split(",")
            if item.strip()
        ]

        # Run actual dissertation model
        analysis = analyse_food(
            extracted_text,
            allergy_list,
        )

        return {
            "filename": filename,
            "ocr_text": extracted_text,
            "allergies": allergy_list,
            "analysis": analysis,
        }

    except HTTPException:
        raise

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"OCR analysis failed: {exc}",
        )

