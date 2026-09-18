import csv
import re
import time
from pathlib import Path
csv.field_size_limit(10_000_000)


# ============================================================
# P-HAF-KG V2.1 LARGE-SCALE STREAMING TEST
# ============================================================

# Purpose:
#   Test the frozen P-HAF-KG V2.1 evidence layer against
#   a large Open Food Facts TSV without loading the dataset
#   into RAM.

# Large-scale experiment:
#   MAX_ROWS controls the number of rows processed.

# IMPORTANT:
#   This preserves the V2.1 matching logic:
#   - text normalisation
#   - phrase-level exclusions
#   - precautionary detection
#   - knowledge-base matching
#   - confirmed/potential separation
#   - confirmed overrides potential


# ============================================================
# CONFIGURATION
# ============================================================

INPUT_FILE = Path(
    "data/en.openfoodfacts.org.products (1).csv"
)

KNOWLEDGE_FILE = Path(
    "data/processed/ingredient_allergen_knowledge_14.csv"
)

MAX_ROWS = 4_535_553

OUTPUT_FILE = Path(
    f"data/processed/scan/p_haf_kg_v2_1_large_scale_{MAX_ROWS}.csv"
)


# ============================================================
# 1. TEXT NORMALISATION
# ============================================================

def normalize_text(text):

    text = str(text).lower()

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
        "œ": "oe",
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    text = re.sub(
        r"[^a-z0-9\s]",
        " ",
        text
    )

    text = re.sub(
        r"\s+",
        " ",
        text
    ).strip()

    return text


# ============================================================
# 2. PHRASE-LEVEL EXCLUSIONS
# ============================================================

PHRASE_EXCLUSIONS = {

    "noix de muscade": {
        "tree_nut"
    },

    "noix de coco": {
        "tree_nut"
    },

    "lait d amande": {
        "milk"
    },

    "lait damande": {
        "milk"
    },

    "lait de soja": {
        "milk"
    },

    "lait de coco": {
        "milk"
    },

    "lait de noisette": {
        "milk"
    },

    "lait d avoine": {
        "milk"
    },

    "lait de riz": {
        "milk"
    },
}


def is_excluded_match(
    ingredient,
    allergen,
    text,
    start,
    end
):

    for phrase, excluded_allergens in (
        PHRASE_EXCLUSIONS.items()
    ):

        if allergen not in excluded_allergens:
            continue

        phrase_pattern = (
            r"(?<![a-z0-9])"
            + re.escape(phrase)
            + r"(?![a-z0-9])"
        )

        for phrase_match in re.finditer(
            phrase_pattern,
            text
        ):

            phrase_start = phrase_match.start()
            phrase_end = phrase_match.end()

            if (
                start >= phrase_start
                and end <= phrase_end
            ):
                return True

    return False


# ============================================================
# 3. PRECAUTIONARY PATTERNS
# ============================================================

PRECAUTIONARY_PATTERNS = [

    # English
    r"\bmay contain\b",
    r"\bmay contain traces\b",
    r"\bmay contain traces of\b",
    r"\bcan contain\b",
    r"\bcan contain traces\b",
    r"\bcan contain traces of\b",
    r"\bcontains traces\b",
    r"\bcontains traces of\b",
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
    r"\bcross contact\b",
    r"\bcross contact with\b",
    r"\bcross contamination\b",
    r"\bfactory where\b",
    r"\bfactory in which\b",
    r"\bwhere .* are used\b",

    # French
    r"\bpeut contenir\b",
    r"\bpeut contenir des traces\b",
    r"\bpeut contenir des traces de\b",
    r"\bcontient des traces\b",
    r"\bcontient des traces de\b",
    r"\btraces de\b",
    r"\btrace de\b",
    r"\btraces eventuelles\b",
    r"\btrace eventuelle\b",
    r"\bpourrait contenir\b",
    r"\bpourrait contenir des traces\b",
    r"\bpresence possible\b",
    r"\bfabrique dans une usine\b",
    r"\bfabrique dans un atelier\b",
    r"\bproduit dans une usine\b",
    r"\bproduit dans un atelier\b",
    r"\bfabrique ou\b",
    r"\bdans une fabrique\b",
    r"\bdans une usine\b",

    # German
    r"\bkann spuren enthalten\b",
    r"\bkann spuren von\b",
    r"\bspuren von\b",
    r"\bspuren enthalten\b",
]


def is_precautionary_sentence(sentence):

    sentence = normalize_text(
        sentence
    )

    for pattern in PRECAUTIONARY_PATTERNS:

        if re.search(
            pattern,
            sentence
        ):
            return True

    return False


# ============================================================
# 4. EVIDENCE SEGMENTATION
# ============================================================

def split_evidence_segments(text):

    text = str(text)

    segments = re.split(
        r"(?<=[\.\!\?;])\s+|\n+",
        text
    )

    cleaned = []

    for segment in segments:

        segment = segment.strip()

        if not segment:
            continue

        cleaned.append(segment)

    return cleaned


# ============================================================
# 5. LOAD KNOWLEDGE BASE
# ============================================================

print("=" * 70)
print("P-HAF-KG V2.1 LARGE-SCALE STREAMING TEST")
print("=" * 70)

print()
print("Input:")
print(INPUT_FILE)

print()
print("Knowledge base:")
print(KNOWLEDGE_FILE)

print()
print("Maximum rows:")
print(f"{MAX_ROWS:,}")


with KNOWLEDGE_FILE.open(
    "r",
    encoding="utf-8",
    errors="replace",
    newline=""
) as f:

    knowledge_raw = list(
        csv.DictReader(f)
    )


knowledge = []

seen = set()

for item in knowledge_raw:

    ingredient_original = (
        item["ingredient"].strip()
    )

    ingredient = normalize_text(
        ingredient_original
    )

    allergen = (
        item["allergen"].strip()
    )

    evidence_type = (
        item["evidence_type"].strip()
    )

    confidence = (
        item["confidence"].strip()
    )

    language = (
        item["language"].strip()
    )

    if not ingredient:
        continue

    key = (
        ingredient,
        allergen,
        evidence_type,
        language
    )

    if key in seen:
        continue

    seen.add(key)

    knowledge.append({

        "ingredient": ingredient,

        "ingredient_original":
            ingredient_original,

        "allergen": allergen,

        "evidence_type":
            evidence_type,

        "confidence":
            confidence,

        "language":
            language,
    })


knowledge.sort(
    key=lambda x: len(
        x["ingredient"]
    ),
    reverse=True
)


print()
print(
    "Knowledge relationships:",
    len(knowledge)
)


# ============================================================
# 6. OUTPUT DIRECTORY
# ============================================================

OUTPUT_FILE.parent.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# 7. STREAM OPEN FOOD FACTS
# ============================================================

start_time = time.time()

rows_read = 0
rows_with_ingredients = 0
rows_processed = 0

confirmed_product_count = 0
potential_product_count = 0

confirmed_counts = {}
potential_counts = {}


output_file = OUTPUT_FILE.open(
    "w",
    encoding="utf-8",
    newline=""
)


writer = csv.DictWriter(
    output_file,
    fieldnames=[
        "code",
        "product_name",
        "confirmed_allergens",
        "potential_allergens",
        "direct_matches",
        "precautionary_matches",
        "special_threshold_matches",
    ]
)

writer.writeheader()


try:

    with INPUT_FILE.open(
        "r",
        encoding="utf-8",
        errors="replace",
        newline=""
    ) as f:

        reader = csv.DictReader(
            f,
            delimiter="\t"
        )

        for row in reader:

            rows_read += 1

            if rows_read > MAX_ROWS:
                break

            original_text = (
                row.get(
                    "ingredients_text"
                )
                or ""
            ).strip()

            if not original_text:
                continue

            rows_with_ingredients += 1
            rows_processed += 1

            confirmed_allergens = set()
            potential_allergens = set()
            direct_matches = set()
            precautionary_matches = set()
            special_threshold_matches = set()


            # ------------------------------------------------
            # Split into evidence segments
            # ------------------------------------------------

            segments = split_evidence_segments(
                original_text
            )


            # ------------------------------------------------
            # Process segments
            # ------------------------------------------------

            for segment in segments:

                normalized_segment = normalize_text(
                    segment
                )

                if not normalized_segment:
                    continue

                precautionary_segment = (
                    is_precautionary_sentence(
                        segment
                    )
                )


                # ------------------------------------------------
                # Match knowledge relationships
                # ------------------------------------------------

                for item in knowledge:

                    ingredient = item[
                        "ingredient"
                    ]

                    allergen = item[
                        "allergen"
                    ]

                    evidence_type = item[
                        "evidence_type"
                    ]

                    if not ingredient:
                        continue

                    pattern = (
                        r"(?<![a-z0-9])"
                        + re.escape(ingredient)
                        + r"(?![a-z0-9])"
                    )

                    matches = re.finditer(
                        pattern,
                        normalized_segment
                    )


                    for match in matches:

                        # ----------------------------------------
                        # Phrase-level exclusion
                        # ----------------------------------------

                        if is_excluded_match(
                            ingredient,
                            allergen,
                            normalized_segment,
                            match.start(),
                            match.end()
                        ):
                            continue


                        match_string = (
                            f"{item['ingredient_original']}"
                            f" -> "
                            f"{allergen}"
                        )


                        # ----------------------------------------
                        # Special threshold
                        # ----------------------------------------

                        if (
                            evidence_type
                            == "special_threshold"
                        ):

                            special_threshold_matches.add(
                                match_string
                            )

                            continue


                        # ----------------------------------------
                        # Precautionary
                        # ----------------------------------------

                        if precautionary_segment:

                            potential_allergens.add(
                                allergen
                            )

                            precautionary_matches.add(
                                match_string
                            )

                        else:

                            confirmed_allergens.add(
                                allergen
                            )

                            direct_matches.add(
                                match_string
                            )


            # ------------------------------------------------
            # Confirmed overrides potential
            # ------------------------------------------------

            potential_allergens -= (
                confirmed_allergens
            )


            # ------------------------------------------------
            # Update statistics
            # ------------------------------------------------

            if confirmed_allergens:
                confirmed_product_count += 1

            if potential_allergens:
                potential_product_count += 1


            for allergen in confirmed_allergens:

                confirmed_counts[allergen] = (
                    confirmed_counts.get(
                        allergen,
                        0
                    ) + 1
                )


            for allergen in potential_allergens:

                potential_counts[allergen] = (
                    potential_counts.get(
                        allergen,
                        0
                    ) + 1
                )


            # ------------------------------------------------
            # Write immediately
            # ------------------------------------------------

            writer.writerow({

                "code":
                    row.get("code", ""),

                "product_name":
                    row.get(
                        "product_name",
                        ""
                    ),

                "confirmed_allergens":
                    ";".join(
                        sorted(
                            confirmed_allergens
                        )
                    ),

                "potential_allergens":
                    ";".join(
                        sorted(
                            potential_allergens
                        )
                    ),

                "direct_matches":
                    ";".join(
                        sorted(
                            direct_matches
                        )
                    ),

                "precautionary_matches":
                    ";".join(
                        sorted(
                            precautionary_matches
                        )
                    ),

                "special_threshold_matches":
                    ";".join(
                        sorted(
                            special_threshold_matches
                        )
                    ),
            })


            # ------------------------------------------------
            # Progress
            # ------------------------------------------------

            if rows_read % 10_000 == 0:

                elapsed = (
                    time.time()
                    - start_time
                )

                rate = (
                    rows_read / elapsed
                    if elapsed > 0
                    else 0
                )

                print(
                    f"Processed {rows_read:,} "
                    f"/ {MAX_ROWS:,} rows | "
                    f"Ingredients: "
                    f"{rows_with_ingredients:,} | "
                    f"Rate: {rate:,.0f} rows/sec"
                )


finally:

    output_file.close()


# ============================================================
# 8. FINAL REPORT
# ============================================================

elapsed = (
    time.time()
    - start_time
)

rate = (
    rows_read / elapsed
    if elapsed > 0
    else 0
)


print()
print("=" * 70)
print("LARGE-SCALE TEST COMPLETE")
print("=" * 70)

print()
print(
    f"Rows scanned:           {rows_read:,}"
)

print(
    f"Rows with ingredients:  "
    f"{rows_with_ingredients:,}"
)

print(
    f"Products analysed:      "
    f"{rows_processed:,}"
)

print(
    f"Products with confirmed "
    f"allergens:              "
    f"{confirmed_product_count:,}"
)

print(
    f"Products with potential "
    f"allergens:              "
    f"{potential_product_count:,}"
)

print()
print(
    f"Processing time:        "
    f"{elapsed:.2f} seconds"
)

print(
    f"Rows/second:            "
    f"{rate:,.0f}"
)

print()
print("Confirmed allergen counts:")

for allergen, count in sorted(
    confirmed_counts.items(),
    key=lambda x: (-x[1], x[0])
):

    print(
        f"  {allergen:20} {count:,}"
    )


print()
print("Potential allergen counts:")

for allergen, count in sorted(
    potential_counts.items(),
    key=lambda x: (-x[1], x[0])
):

    print(
        f"  {allergen:20} {count:,}"
    )


print()
print("Output:")
print(OUTPUT_FILE)

print()
print("=" * 70)
print("END")
print("=" * 70)