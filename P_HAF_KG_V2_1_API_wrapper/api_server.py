from __future__ import annotations

import csv
import subprocess
import tempfile
from functools import lru_cache
from pathlib import Path
from typing import List

from fastapi import (
    FastAPI,
    HTTPException,
    File,
    UploadFile,
    Form,
)
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field



# REAL DISSERTATION IMPLEMENTATION


from src.predict_food import (
    load_knowledge_base,
    run_kg,
    run_svm,
    hybrid_decision,
    personalised_decision,
)



# 500-PRODUCT RESEARCH CATALOGUE


PRODUCT_FILE = Path(
    "data/processed/ml/gold_test/"
    "gold_test_annotation_completed.csv"
)


@lru_cache(maxsize=1)
def load_products():
    """
    Load the 500 independently reviewed research products.

    IMPORTANT:
    Gold labels are deliberately NOT exposed through
    the /products endpoint.
    """

    if not PRODUCT_FILE.exists():
        raise FileNotFoundError(
            f"Product catalogue not found: {PRODUCT_FILE}"
        )

    products = []

    with PRODUCT_FILE.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as file:

        reader = csv.DictReader(file)

        for row in reader:

            product_code = str(
                row.get("product_code", "")
            ).strip()

            product_name = str(
                row.get("product_name", "")
            ).strip()

            ingredient_text = str(
                row.get("ingredient_text", "")
            ).strip()

            if not (
                product_code
                or product_name
                or ingredient_text
            ):
                continue

            products.append(
                {
                    "id": product_code,
                    "product_code": product_code,
                    "name": product_name,
                    "product_name": product_name,
                    "ingredients": ingredient_text,
                    "ingredient_text": ingredient_text,
                }
            )

    return products



# FASTAPI APPLICATION


app = FastAPI(
    title="P-HAF-KG V2.1 API",
    description=(
        "API wrapper around the implemented P-HAF-KG V2.1 + "
        "TF-IDF/Linear SVM personalised food-analysis pipeline "
        "with Tesseract OCR support and a 500-product research "
        "catalogue."
    ),
    version="1.2.0",
)



# CORS


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)



# REQUEST / RESPONSE MODELS


class AnalyseFoodRequest(BaseModel):
    ingredient_text: str = Field(
        ...,
        min_length=1,
    )

    allergies: List[str] = Field(
        default_factory=list
    )


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



# KNOWLEDGE BASE


@lru_cache(maxsize=1)
def get_knowledge():
    """
    Load the dissertation knowledge base once
    per API process.
    """

    return load_knowledge_base()



# CORE FOOD ANALYSIS


def analyse_food(
    ingredient_text: str,
    allergies: List[str],
):
    """
    Run the actual dissertation prediction pipeline.

    Ingredient text
        ↓
    P-HAF-KG V2.1
        +
    TF-IDF + Linear SVM
        ↓
    Hybrid decision
        ↓
    Personalised decision
    """

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

    
    # HYBRID DECISION
    

    hybrid = hybrid_decision(
        kg,
        svm,
    )

    
    # PERSONALISED DECISION
    
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

    
    # RESPONSE
    

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



# OCR CONFIGURATION


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

    Languages:
        English
        French
        German

    Page segmentation mode:
        6
    """

    suffix = Path(
        filename
    ).suffix.lower()

    if suffix not in SUPPORTED_IMAGE_EXTENSIONS:

        raise ValueError(
            "Unsupported image format. "
            "Use JPG, JPEG, PNG, WEBP, BMP, TIF or TIFF."
        )

    temporary_path = None

    try:

        
        # Save temporary image
        

        with tempfile.NamedTemporaryFile(
            suffix=suffix,
            delete=False,
        ) as temporary_file:

            temporary_file.write(
                image_bytes
            )

            temporary_path = Path(
                temporary_file.name
            )

        
        # Tesseract
        

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

        
        # Basic cleaning
        

        cleaned_lines = []

        for line in (
            result.stdout.splitlines()
        ):

            line = line.strip()

            if line:
                cleaned_lines.append(line)

        return "\n".join(
            cleaned_lines
        ).strip()

    finally:

        if temporary_path is not None:

            try:
                temporary_path.unlink(
                    missing_ok=True
                )
            except Exception:
                pass



# ROOT


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
        "product_catalogue": 500,
    }



# HEALTH


@app.get("/health")
def health():

    try:

        knowledge = get_knowledge()

        products = load_products()

        return {
            "status": "ok",

            "model": "P-HAF-KG V2.1",

            "baseline":
                "TF-IDF + Linear SVM",

            "ocr":
                "Tesseract",

            "ocr_languages":
                "eng+fra+deu",

            "knowledge_relationships_loaded":
                len(knowledge),

            "products_loaded":
                len(products),
        }

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=(
                "Model initialisation failed: "
                f"{exc}"
            ),
        )



# PRODUCT CATALOGUE


@app.get("/products")
def get_products():
    """
    Return the 500 research products.

    IMPORTANT:
    Gold labels are not returned.

    Returned fields are limited to:

        id
        product_code
        name
        product_name
        ingredients
        ingredient_text
    """

    try:

        return load_products()

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=(
                "Product catalogue failed to load: "
                f"{exc}"
            ),
        )



# ANALYZE FOOD


@app.post(
    "/analyze-food",
    response_model=AnalyseFoodResponse,
)
def analyze_food(
    request: AnalyseFoodRequest,
):

    ingredient_text = (
        request.ingredient_text.strip()
    )

    if not ingredient_text:

        raise HTTPException(
            status_code=400,
            detail=(
                "ingredient_text cannot be empty."
            ),
        )

    try:

        return analyse_food(
            ingredient_text,
            request.allergies,
        )

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=(
                "Prediction failed: "
                f"{exc}"
            ),
        )



# OCR + ANALYZE FOOD


@app.post("/ocr-analyze")
async def ocr_analyze(
    file: UploadFile = File(...),
    allergies: str = Form(""),
):
    """
    Image
        ↓
    Tesseract OCR
        ↓
    Ingredient text
        ↓
    P-HAF-KG V2.1
        +
    TF-IDF + Linear SVM
        ↓
    Hybrid reasoning
        ↓
    Personalised decision
    """

    filename = (
        file.filename
        or "food_label.jpg"
    )

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

        
        # No readable text
        

        if not extracted_text:

            return {
                "filename":
                    filename,

                "ocr_text":
                    "",

                "allergies":
                    [],

                "message":
                    "No readable text was detected.",

                "analysis":
                    None,
            }

        
        # Parse allergy profile
        

        allergy_list = [
            item.strip().lower()
            for item in allergies.split(",")
            if item.strip()
        ]

       
        # Run model
        

        analysis = analyse_food(
            extracted_text,
            allergy_list,
        )

        
        # Response
        

        return {

            "filename":
                filename,

            "ocr_text":
                extracted_text,

            "allergies":
                allergy_list,

            "analysis":
                analysis,
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
            detail=(
                "OCR analysis failed: "
                f"{exc}"
            )
        )