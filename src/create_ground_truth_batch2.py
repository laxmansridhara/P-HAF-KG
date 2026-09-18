import csv
from pathlib import Path

INPUT_FILE = Path(
    "data/processed/annotation_batch_02.csv"
)

OUTPUT_FILE = Path(
    "data/processed/ground_truth_batch_02.csv"
)

# Batch 2 reviewed annotations
LABELS = {

    1:  ("milk;wheat_gluten",
         "soy;sesame;egg;tree_nut",
         "BOTH", "YES", "KEEP"),

    2:  ("milk;soy;wheat_gluten",
         "egg;sesame;tree_nut",
         "BOTH", "YES", "KEEP"),

    3:  ("sesame",
         "tree_nut;wheat_gluten;egg;soy;milk",
         "BOTH", "YES", "KEEP"),

    4:  ("milk;wheat_gluten;sesame",
         "",
         "DIRECT", "YES", "KEEP"),

    5:  ("wheat_gluten",
         "milk;egg;sesame;soy",
         "BOTH", "YES", "KEEP"),

    6:  ("wheat_gluten",
         "milk;egg;sesame;soy",
         "BOTH", "YES", "KEEP"),

    7:  ("milk;egg;soy;wheat_gluten;sesame",
         "",
         "DIRECT", "YES", "KEEP"),

    8:  ("milk;soy;wheat_gluten;tree_nut",
         "egg;sesame",
         "BOTH", "YES", "KEEP"),

    9:  ("sesame",
         "",
         "DIRECT", "YES", "KEEP"),

    10: ("peanut;soy;wheat_gluten;sesame;tree_nut",
         "",
         "DIRECT", "YES", "KEEP"),

    11: ("wheat_gluten",
         "sesame",
         "BOTH", "YES", "KEEP"),

    12: ("",
         "tree_nut;sesame",
         "PRECAUTIONARY", "YES", "KEEP"),

    13: ("soy;wheat_gluten;sesame",
         "",
         "DIRECT", "YES", "KEEP"),

    14: ("milk;soy;wheat_gluten;sesame",
         "",
         "DIRECT", "YES", "KEEP"),

    15: ("wheat_gluten;tree_nut",
         "egg;soy;sesame",
         "BOTH", "YES", "KEEP"),

    16: ("milk;soy;wheat_gluten;sesame",
         "",
         "DIRECT", "YES", "KEEP"),

    17: ("soy;wheat_gluten;sesame",
         "",
         "DIRECT", "YES", "KEEP"),

    18: ("soy;wheat_gluten;egg",
         "sesame",
         "BOTH", "YES", "KEEP"),

    19: ("milk;wheat_gluten;sesame",
         "",
         "DIRECT", "YES", "KEEP"),

    20: ("milk;soy;wheat_gluten;sesame",
         "",
         "DIRECT", "YES", "KEEP"),

    21: ("peanut;soy;sesame",
         "",
         "DIRECT", "YES", "KEEP"),

    22: ("wheat_gluten",
         "soy;milk;sesame",
         "BOTH", "YES", "KEEP"),

    23: ("wheat_gluten;sesame",
         "egg;soy;milk",
         "BOTH", "YES", "KEEP"),

    24: ("milk;soy;wheat_gluten;tree_nut",
         "sesame;peanut;egg",
         "BOTH", "YES", "KEEP"),

    25: ("wheat_gluten;sesame;soy",
         "",
         "DIRECT", "YES", "KEEP"),

    26: ("tree_nut",
         "peanut;sesame;tree_nut",
         "BOTH", "YES", "KEEP"),

    27: ("egg;wheat_gluten",
         "soy",
         "BOTH", "YES", "KEEP"),

    28: ("milk",
         "wheat_gluten;egg",
         "BOTH", "YES", "KEEP"),

    29: ("milk",
         "wheat_gluten;egg",
         "BOTH", "YES", "KEEP"),

    30: ("milk;egg;soy;wheat_gluten;tree_nut",
         "",
         "DIRECT", "YES", "KEEP"),

    31: ("milk;soy;wheat_gluten",
         "egg;sesame;tree_nut",
         "BOTH", "YES", "KEEP"),

    32: ("milk",
         "wheat_gluten;egg",
         "BOTH", "YES", "KEEP"),

    33: ("wheat_gluten",
         "egg",
         "BOTH", "YES", "KEEP"),

    34: ("",
         "wheat_gluten;egg",
         "PRECAUTIONARY", "YES", "KEEP"),

    35: ("",
         "milk;wheat_gluten;soy",
         "PRECAUTIONARY", "YES", "KEEP"),

    36: ("milk",
         "wheat_gluten;egg",
         "BOTH", "YES", "KEEP"),

    37: ("milk",
         "wheat_gluten;egg",
         "BOTH", "YES", "KEEP"),

    38: ("",
         "milk;wheat_gluten;soy",
         "PRECAUTIONARY", "YES", "KEEP"),

    39: ("milk;egg;soy;wheat_gluten",
         "sesame;tree_nut",
         "BOTH", "YES", "KEEP"),

    40: ("soy;wheat_gluten",
         "milk",
         "BOTH", "YES", "KEEP"),

    41: ("milk",
         "wheat_gluten;egg",
         "BOTH", "YES", "KEEP"),

    42: ("",
         "milk;soy;wheat_gluten",
         "PRECAUTIONARY", "YES", "KEEP"),

    43: ("milk",
         "soy",
         "BOTH", "YES", "KEEP"),

    44: ("tree_nut",
         "milk",
         "BOTH", "YES", "KEEP"),

    45: ("wheat_gluten",
         "milk;egg;tree_nut;soy;sesame",
         "BOTH", "YES", "KEEP"),

    46: ("milk;soy;wheat_gluten;tree_nut",
         "",
         "DIRECT", "YES", "KEEP"),

    47: ("milk;soy",
         "",
         "DIRECT", "YES", "KEEP"),

    48: ("milk;soy;tree_nut",
         "",
         "DIRECT", "YES", "KEEP"),

    49: ("milk;egg;soy;wheat_gluten;tree_nut",
         "",
         "DIRECT", "YES", "KEEP"),

    50: ("milk;wheat_gluten;sesame",
         "",
         "DIRECT", "YES", "KEEP"),

    51: ("milk;egg;wheat_gluten",
         "",
         "DIRECT", "YES", "KEEP"),

    52: ("milk;egg;wheat_gluten",
         "tree_nut",
         "BOTH", "YES", "KEEP"),

    53: ("egg;milk;soy;wheat_gluten;sesame",
         "",
         "DIRECT", "YES", "KEEP"),

    54: ("tree_nut",
         "",
         "DIRECT", "YES", "KEEP"),

    55: ("egg;milk;soy;wheat_gluten;tree_nut",
         "",
         "DIRECT", "YES", "KEEP"),

    56: ("wheat_gluten;tree_nut",
         "",
         "DIRECT", "YES", "KEEP"),

    57: ("egg;milk;soy;wheat_gluten;tree_nut",
         "",
         "DIRECT", "YES", "KEEP"),

    58: ("egg;milk;soy;wheat_gluten",
         "",
         "DIRECT", "YES", "KEEP"),

    59: ("soy;wheat_gluten",
         "",
         "DIRECT", "YES", "KEEP"),

    60: ("milk;soy",
         "",
         "DIRECT", "YES", "KEEP"),

    61: ("milk;wheat_gluten;tree_nut",
         "",
         "DIRECT", "YES", "KEEP"),

    62: ("wheat_gluten",
         "milk;soy",
         "BOTH", "YES", "KEEP"),

    63: ("soy;tree_nut",
         "",
         "DIRECT", "YES", "KEEP"),

    64: ("",
         "milk;soy;wheat_gluten",
         "PRECAUTIONARY", "YES", "KEEP"),

    65: ("milk;egg;soy;wheat_gluten",
         "",
         "DIRECT", "YES", "KEEP"),

    66: ("",
         "",
         "EXCLUDE", "NO", "EXCLUDE"),

    67: ("",
         "",
         "EXCLUDE", "NO", "EXCLUDE"),

    68: ("",
         "",
         "EXCLUDE", "NO", "EXCLUDE"),

    69: ("",
         "",
         "EXCLUDE", "NO", "EXCLUDE"),

    70: ("",
         "",
         "EXCLUDE", "NO", "EXCLUDE"),

    71: ("",
         "",
         "NONE", "YES", "KEEP"),

    72: ("",
         "",
         "NONE", "YES", "KEEP"),

    73: ("",
         "",
         "NONE", "YES", "KEEP"),

    74: ("",
         "",
         "EXCLUDE", "NO", "EXCLUDE"),

    75: ("wheat_gluten;tree_nut",
         "",
         "DIRECT", "YES", "KEEP"),

    76: ("wheat_gluten",
         "",
         "DIRECT", "YES", "KEEP"),

    77: ("",
         "",
         "NONE", "YES", "KEEP"),

    78: ("",
         "",
         "EXCLUDE", "NO", "EXCLUDE"),

    79: ("",
         "",
         "EXCLUDE", "NO", "EXCLUDE"),

    80: ("",
         "",
         "EXCLUDE", "NO", "EXCLUDE"),

    81: ("",
         "",
         "EXCLUDE", "NO", "EXCLUDE"),

    82: ("",
         "",
         "NONE", "YES", "KEEP"),

    83: ("",
         "",
         "EXCLUDE", "NO", "EXCLUDE"),

    84: ("",
         "",
         "NONE", "YES", "KEEP"),

    85: ("",
         "",
         "EXCLUDE", "NO", "EXCLUDE"),
}


with INPUT_FILE.open(
    "r",
    encoding="utf-8",
    errors="replace",
    newline=""
) as f:

    rows = list(csv.DictReader(f))


if len(rows) != 85:
    raise ValueError(
        f"Expected 85 rows, found {len(rows)}"
    )

if len(LABELS) != 85:
    raise ValueError(
        f"Expected 85 labels, found {len(LABELS)}"
    )


fields = [
    "code",
    "product_name",
    "ingredients_text",
    "allergens",
    "allergens_en",
    "additives_en",
    "candidate_category",
    "confirmed_allergens",
    "potential_allergens",
    "evidence_level",
    "is_food",
    "review_status",
]


with OUTPUT_FILE.open(
    "w",
    encoding="utf-8",
    newline=""
) as f:

    writer = csv.DictWriter(
        f,
        fieldnames=fields
    )

    writer.writeheader()

    for i, row in enumerate(rows, 1):

        confirmed, potential, evidence, food, status = LABELS[i]

        writer.writerow({
            "code": row["code"],
            "product_name": row["product_name"],
            "ingredients_text": row["ingredients_text"],
            "allergens": row["allergens"],
            "allergens_en": row["allergens_en"],
            "additives_en": row["additives_en"],
            "candidate_category": row["candidate_category"],
            "confirmed_allergens": confirmed,
            "potential_allergens": potential,
            "evidence_level": evidence,
            "is_food": food,
            "review_status": status,
        })


print("Ground-truth Batch 2 created.")
print("Products:", len(rows))
print("Output:", OUTPUT_FILE)
