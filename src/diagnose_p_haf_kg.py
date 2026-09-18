import csv
import re
from pathlib import Path


TEST_FILE = Path(
    "data/processed/test.csv"
)

KNOWLEDGE_FILE = Path(
    "data/processed/ingredient_allergen_knowledge.csv"
)

OUTPUT_FILE = Path(
    "data/processed/p_haf_kg_diagnostics.csv"
)


def normalize_text(text):

    text = text.lower()

    replacements = {
        "é": "e",
        "è": "e",
        "ê": "e",
        "ë": "e",
        "à": "a",
        "â": "a",
        "ä": "a",
        "á": "a",
        "î": "i",
        "ï": "i",
        "ô": "o",
        "ö": "o",
        "ù": "u",
        "û": "u",
        "ü": "u",
        "ç": "c",
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    text = re.sub(
        r"\s+",
        " ",
        text
    ).strip()

    return text


PRECAUTIONARY_PATTERNS = [
    r"\bmay contain\b",
    r"\bmay contain traces\b",
    r"\bcan contain\b",
    r"\btraces of\b",
    r"\btrace of\b",
    r"\bpossible presence\b",
    r"\bpossibly contains\b",
    r"\bshared equipment\b",
    r"\bshared equipment with\b",
    r"\bmanufactured on equipment\b",
    r"\bmanufactured in a facility\b",
    r"\bproduced in a facility\b",
    r"\bmade in a facility\b",
    r"\bcross[- ]contact\b",
]


def is_precautionary(text):

    for pattern in PRECAUTIONARY_PATTERNS:

        if re.search(
            pattern,
            text
        ):
            return True

    return False


with KNOWLEDGE_FILE.open(
    "r",
    encoding="utf-8",
    errors="replace",
    newline=""
) as f:

    knowledge = list(
        csv.DictReader(f)
    )


knowledge.sort(
    key=lambda x: len(
        x["ingredient"]
    ),
    reverse=True
)


with TEST_FILE.open(
    "r",
    encoding="utf-8",
    errors="replace",
    newline=""
) as f:

    products = list(
        csv.DictReader(f)
    )


diagnostics = []


for product in products:

    text = normalize_text(
        product["ingredients_text"]
    )

    for item in knowledge:

        ingredient = normalize_text(
            item["ingredient"]
        )

        if not ingredient:
            continue

        pattern = (
            r"(?<![a-z0-9])"
            + re.escape(ingredient)
            + r"(?![a-z0-9])"
        )

        for match in re.finditer(
            pattern,
            text
        ):

            # Use a smaller local context
            # for diagnosis.
            start = max(
                0,
                match.start() - 60
            )

            end = min(
                len(text),
                match.end() + 60
            )

            context = text[
                start:end
            ]

            if is_precautionary(
                context
            ):

                evidence = "potential"

            else:

                evidence = "direct"


            diagnostics.append({

                "code":
                    product["code"],

                "product_name":
                    product["product_name"],

                "matched_ingredient":
                    item["ingredient"],

                "allergen":
                    item["allergen"],

                "evidence":
                    evidence,

                "context":
                    context,

            })


with OUTPUT_FILE.open(
    "w",
    encoding="utf-8",
    newline=""
) as f:

    writer = csv.DictWriter(
        f,
        fieldnames=[
            "code",
            "product_name",
            "matched_ingredient",
            "allergen",
            "evidence",
            "context",
        ]
    )

    writer.writeheader()
    writer.writerows(
        diagnostics
    )


print(
    "===== P-HAF-KG DIAGNOSTICS ====="
)

print(
    "Products:",
    len(products)
)

print(
    "Matches:",
    len(diagnostics)
)

print(
    "Output:",
    OUTPUT_FILE
)


print(
    "\n===== FIRST 20 MATCHES ====="
)

for row in diagnostics[:20]:

    print(
        "\nProduct:",
        row["product_name"]
    )

    print(
        "Ingredient:",
        row["matched_ingredient"]
    )

    print(
        "Allergen:",
        row["allergen"]
    )

    print(
        "Evidence:",
        row["evidence"]
    )

    print(
        "Context:",
        row["context"]
    )
