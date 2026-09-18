import subprocess
import sys
from pathlib import Path


def run_ocr(image_path, languages="eng+fra+deu"):
    image_path = Path(image_path)

    if not image_path.exists():
        raise FileNotFoundError(f"Image not found: {image_path}")

    command = [
        "tesseract",
        str(image_path),
        "stdout",
        "-l",
        languages,
        "--psm",
        "6",
    ]

    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        raise RuntimeError(result.stderr)

    return result.stdout.strip()


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage:")
        print("python3 src/test_tesseract_ocr.py path/to/image.jpg")
        sys.exit(1)

    image = sys.argv[1]

    print("=" * 60)
    print("P-HAF-KG OCR TEST")
    print("=" * 60)
    print(f"Image: {image}")
    print("Languages: English + French + German")
    print()

    text = run_ocr(image)

    print("===== OCR TEXT =====")
    print(text)
    print()
    print("===== OCR COMPLETE =====")
