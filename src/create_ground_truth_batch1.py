import csv
from pathlib import Path

INPUT_FILE = Path(
    "data/processed/annotation_batch_01.csv"
)

OUTPUT_FILE = Path(
    "data/processed/ground_truth_batch_01.csv"
)

# Reviewed labels for Products 1-70
LABELS = {
    1:  ("", "", "EXCLUDE", "NO", "EXCLUDE"),
    2:  ("", "", "EXCLUDE", "NO", "EXCLUDE"),
    3:  ("", "", "EXCLUDE", "NO", "EXCLUDE"),
    4:  ("soy;wheat_gluten;tree_nut", "", "DIRECT", "YES", "KEEP"),
    5:  ("milk;egg;wheat_gluten", "", "DIRECT", "YES", "KEEP"),
    6:  ("", "", "EXCLUDE", "NO", "EXCLUDE"),
    7:  ("milk;egg;soy;wheat_gluten", "", "DIRECT", "YES", "KEEP"),
    8:  ("", "", "EXCLUDE", "NO", "EXCLUDE"),
    9:  ("peanut", "", "DIRECT", "YES", "KEEP"),
    10: ("peanut;milk;soy;egg;wheat_gluten",
         "tree_nut", "BOTH", "YES", "KEEP"),
    11: ("milk;soy",
         "peanut;tree_nut;egg;wheat_gluten;sesame",
         "BOTH", "YES", "KEEP"),
    12: ("peanut;milk;egg;wheat_gluten",
         "", "DIRECT", "YES", "KEEP"),
    13: ("peanut;milk;egg;soy;wheat_gluten",
         "", "DIRECT", "YES", "KEEP"),
    14: ("peanut;milk;egg;soy;wheat_gluten;tree_nut",
         "", "DIRECT", "YES", "KEEP"),
    15: ("peanut;milk;tree_nut",
         "", "DIRECT", "YES", "KEEP"),
    16: ("peanut;milk",
         "", "DIRECT", "YES", "KEEP"),
    17: ("", "", "EXCLUDE", "NO", "EXCLUDE"),
    18: ("milk;soy",
         "wheat_gluten;egg;peanut;tree_nut",
         "BOTH", "YES", "KEEP"),
    19: ("milk;soy",
         "peanut;tree_nut",
         "BOTH", "YES", "KEEP"),
    20: ("peanut;milk;soy",
         "", "DIRECT", "YES", "KEEP"),

    21: ("peanut;milk;egg;wheat_gluten",
         "", "DIRECT", "YES", "KEEP"),
    22: ("peanut;milk;soy;tree_nut",
         "egg;tree_nut", "BOTH", "YES", "KEEP"),
    23: ("soy;wheat_gluten",
         "egg;peanut;milk;tree_nut;sesame",
         "BOTH", "YES", "KEEP"),
    24: ("milk;tree_nut",
         "egg;wheat_gluten;peanut;soy",
         "BOTH", "YES", "KEEP"),
    25: ("milk;egg;wheat_gluten",
         "", "DIRECT", "YES", "KEEP"),
    26: ("milk;egg;soy;wheat_gluten",
         "tree_nut", "BOTH", "YES", "KEEP"),
    27: ("milk;egg;soy;wheat_gluten",
         "tree_nut", "BOTH", "YES", "KEEP"),
    28: ("milk;egg",
         "", "DIRECT", "YES", "KEEP"),
    29: ("",
         "tree_nut", "PRECAUTIONARY", "YES", "KEEP"),
    30: ("milk;egg;soy;wheat_gluten;tree_nut",
         "", "DIRECT", "YES", "KEEP"),

    31: ("peanut;soy;wheat_gluten",
         "", "DIRECT", "YES", "KEEP"),
    32: ("peanut;milk;soy",
         "", "DIRECT", "YES", "KEEP"),
    33: ("peanut;milk;soy",
         "", "DIRECT", "YES", "KEEP"),
    34: ("peanut;milk;soy",
         "", "DIRECT", "YES", "KEEP"),
    35: ("peanut;milk;soy;wheat_gluten",
         "", "DIRECT", "YES", "KEEP"),
    36: ("peanut;milk;soy;wheat_gluten",
         "", "DIRECT", "YES", "KEEP"),
    37: ("soy",
         "wheat_gluten;peanut;tree_nut;sesame",
         "BOTH", "YES", "KEEP"),
    38: ("",
         "peanut;milk;soy;wheat_gluten;tree_nut",
         "PRECAUTIONARY", "YES", "KEEP"),
    39: ("peanut;soy;tree_nut",
         "", "DIRECT", "YES", "KEEP"),
    40: ("peanut;milk;soy",
         "", "DIRECT", "YES", "KEEP"),

    41: ("peanut;wheat_gluten",
         "", "DIRECT", "YES", "KEEP"),
    42: ("peanut;milk;soy;wheat_gluten;sesame",
         "", "DIRECT", "YES", "KEEP"),
    43: ("milk;egg;wheat_gluten",
         "", "DIRECT", "YES", "KEEP"),
    44: ("",
         "", "EXCLUDE", "NO", "EXCLUDE"),
    45: ("",
         "", "DIRECT", "YES", "KEEP"),
    46: ("",
         "", "EXCLUDE", "NO", "EXCLUDE"),
    47: ("milk;soy;wheat_gluten",
         "", "DIRECT", "YES", "KEEP"),
    48: ("milk;egg;wheat_gluten",
         "soy;tree_nut", "BOTH", "YES", "KEEP"),
    49: ("milk;egg;soy;wheat_gluten;tree_nut",
         "tree_nut", "BOTH", "YES", "KEEP"),
    50: ("milk;egg;soy;wheat_gluten",
         "", "DIRECT", "YES", "KEEP"),

    51: ("tree_nut",
         "peanut;sesame;tree_nut",
         "BOTH", "YES", "KEEP"),
    52: ("coconut",
         "peanut;tree_nut;sesame",
         "BOTH", "YES", "KEEP"),
    53: ("milk;soy;wheat_gluten;tree_nut",
         "tree_nut;wheat_gluten;sesame;peanut",
         "BOTH", "YES", "KEEP"),
    54: ("wheat_gluten;tree_nut",
         "egg;soy;sesame",
         "BOTH", "YES", "KEEP"),
    55: ("soy;sesame;wheat_gluten",
         "", "DIRECT", "YES", "KEEP"),
    56: ("milk;egg;wheat_gluten",
         "sesame;tree_nut;soy",
         "BOTH", "YES", "KEEP"),
    57: ("soy;sesame",
         "", "DIRECT", "YES", "KEEP"),
    58: ("",
         "tree_nut;peanut;sesame;wheat_gluten",
         "PRECAUTIONARY", "YES", "KEEP"),
    59: ("",
         "tree_nut;peanut;sesame;wheat_gluten",
         "PRECAUTIONARY", "YES", "KEEP"),
    60: ("wheat_gluten",
         "sesame", "BOTH", "YES", "KEEP"),

    61: ("peanut;tree_nut",
         "", "DIRECT", "YES", "KEEP"),
    62: ("peanut;milk;soy;tree_nut",
         "", "DIRECT", "YES", "KEEP"),
    63: ("peanut;tree_nut",
         "", "DIRECT", "YES", "KEEP"),
    64: ("peanut;tree_nut",
         "", "DIRECT", "YES", "KEEP"),
    65: ("peanut;tree_nut",
         "", "DIRECT", "YES", "KEEP"),
    66: ("peanut;tree_nut",
         "", "DIRECT", "YES", "KEEP"),
    67: ("peanut;tree_nut",
         "", "DIRECT", "YES", "KEEP"),
    68: ("milk;tree_nut",
         "", "DIRECT", "YES", "KEEP"),
    69: ("",
         "", "EXCLUDE", "YES", "EXCLUDE"),
    70: ("egg;tree_nut",
         "", "DIRECT", "YES", "KEEP"),
}


with INPUT_FILE.open(
    "r",
    encoding="utf-8",
    errors="replace",
    newline=""
) as f:

    rows = list(csv.DictReader(f))


fields = [
    "code",
    "product_name",
    "ingredients_text",
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
            "candidate_category": row["candidate_category"],
            "confirmed_allergens": confirmed,
            "potential_allergens": potential,
            "evidence_level": evidence,
            "is_food": food,
            "review_status": status,
        })


print("Ground-truth Batch 1 created.")
print("Products:", len(rows))
print("Output:", OUTPUT_FILE)
