import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]

IMAGE_PATH = None

OCR_LANGUAGES = "eng+fra+deu"


def run_tesseract(image_path):
    """
    Run Tesseract OCR on the supplied food-label image.
    """

    image_path = Path(image_path)

    if not image_path.exists():
        raise FileNotFoundError(
            f"Image not found: {image_path}"
        )

    command = [
        "tesseract",
        str(image_path),
        "stdout",
        "-l",
        OCR_LANGUAGES,
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
            f"Tesseract failed:\n{result.stderr}"
        )

    return result.stdout.strip()


def clean_ocr_text(text):
    """
    Basic OCR text cleaning.

    This does NOT perform allergen detection.
    P-HAF-KG remains responsible for that stage.
    """

    lines = []

    for line in text.splitlines():
        line = line.strip()

        if line:
            lines.append(line)

    return "\n".join(lines)


def main():

    print("===== P-HAF-KG IMAGE SCAN =====")

    if len(sys.argv) != 2:
        print()
        print("Usage:")
        print(
            "python3 src/scan_label_ocr.py "
            "data/raw/food_label.jpg"
        )
        sys.exit(1)

    image_path = Path(sys.argv[1])

    print(f"Image: {image_path}")
    print()

    if not image_path.exists():
        print(
            f"ERROR: Image not found: {image_path}"
        )
        sys.exit(1)

    try:

        print("OCR engine: Tesseract")
        print(
            f"OCR languages: "
            f"{OCR_LANGUAGES}"
        )
        print()

        raw_text = run_tesseract(image_path)

        cleaned_text = clean_ocr_text(
            raw_text
        )

        print("===== OCR TEXT =====")

        if cleaned_text:
            print(cleaned_text)
        else:
            print(
                "WARNING: No text was detected."
            )

        print()
        print("===== OCR COMPLETE =====")

    except Exception as error:

        print()
        print(
            f"ERROR: {error}"
        )

        sys.exit(1)


if __name__ == "__main__":
    main()