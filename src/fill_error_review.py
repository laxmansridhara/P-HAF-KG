import csv
from pathlib import Path

FILE = Path("data/processed/tfidf_error_review.csv")

REVIEWS = {
    "259": (
        "peanut;milk;soy",
        "tree_nut;wheat_gluten",
        "CHANGE",
        "Peanut and milk are direct ingredients. Soy is present as soy lecithin. Tree nuts and gluten are precautionary."
    ),
    "1003676718": (
        "soy;wheat_gluten",
        "egg;peanut;milk;tree_nut;sesame",
        "KEEP",
        "Soy and wheat are direct. Other listed allergens are precautionary."
    ),
    "49": (
        "egg;milk",
        "",
        "CHANGE",
        "Egg albumin and milk powder are directly present."
    ),
    "37": (
        "",
        "",
        "CHANGE",
        "No confirmed target allergen is present in the ingredient list."
    ),
    "200008423": (
        "soy;wheat_gluten",
        "milk",
        "KEEP",
        "Soy and wheat are directly present. Milk is precautionary."
    ),
    "1422": (
        "milk",
        "soy",
        "KEEP",
        "Milk is directly present. Soy is only mentioned as may contain."
    ),
    "1005400031": (
        "",
        "peanut;tree_nut;milk;soy;wheat_gluten",
        "CHANGE",
        "All target allergens occur only in shared-equipment precautionary wording."
    ),
    "987500001": (
        "soy",
        "peanut;tree_nut;wheat_gluten;sesame",
        "KEEP",
        "Soy is directly present. Other allergens are precautionary."
    ),
    "104": (
        "egg;milk;wheat_gluten",
        "",
        "CHANGE",
        "Egg, milk and wheat are directly present."
    ),
    "12782": (
        "milk;sesame;soy;wheat_gluten",
        "",
        "CHANGE",
        "Milk, sesame, soy and wheat are directly present."
    ),
    "1116103494": (
        "peanut;soy;tree_nut",
        "",
        "KEEP",
        "Cashews are tree nuts; peanut and soybean are explicitly present in the vegetable oil."
    ),
    "380102109": (
        "milk;peanut;tree_nut",
        "",
        "CHANGE",
        "Milk, peanut and almond butter provide direct allergen evidence."
    ),
    "192495165": (
        "tree_nut",
        "milk",
        "KEEP",
        "Almond and hazelnut are direct tree-nut ingredients. Milk is precautionary."
    ),
    "252828288": (
        "egg;milk;peanut;soy;wheat_gluten",
        "",
        "KEEP",
        "Egg, milk, peanut oil, soybean oil and wheat/barley flour are directly present."
    ),
    "105748562": (
        "wheat_gluten",
        "egg",
        "KEEP",
        "Durum wheat semolina is direct. Egg is precautionary."
    ),
    "1000657163": (
        "egg;milk;wheat_gluten",
        "",
        "KEEP",
        "Egg, milk and wheat are directly present."
    ),
    "24": (
        "",
        "peanut;tree_nut;sesame;wheat_gluten",
        "CHANGE",
        "The allergens are associated with factory/shared-use precautionary wording."
    ),
    "224": (
        "egg;milk;wheat_gluten",
        "soy;tree_nut",
        "KEEP",
        "Egg, milk and wheat are direct. Soy and tree nuts are precautionary."
    ),
    "2000012670": (
        "wheat_gluten",
        "milk;egg;sesame;soy",
        "KEEP",
        "Wheat/gluten is directly present. Other listed allergens are precautionary."
    ),
    "1757016092": (
        "milk;soy;tree_nut",
        "",
        "KEEP",
        "Milk, soy and hazelnuts are directly present."
    ),
}


with FILE.open(
    "r",
    encoding="utf-8",
    errors="replace",
    newline=""
) as f:
    rows = list(csv.DictReader(f))


updated = 0
unmatched = []


for row in rows:

    code = row["code"].lstrip("0")

    if code in REVIEWS:

        confirmed, potential, decision, notes = REVIEWS[code]

        row["reviewed_confirmed_allergens"] = confirmed
        row["reviewed_potential_allergens"] = potential
        row["review_decision"] = decision
        row["review_notes"] = notes

        updated += 1

    else:

        unmatched.append(row["code"])


fields = list(rows[0].keys())


with FILE.open(
    "w",
    encoding="utf-8",
    newline=""
) as f:

    writer = csv.DictWriter(
        f,
        fieldnames=fields
    )

    writer.writeheader()
    writer.writerows(rows)


print("===== REVIEW FILE UPDATED =====")
print("Rows updated:", updated)
print("Expected:", len(REVIEWS))

if unmatched:
    print("Unmatched rows:", unmatched)

print("Output:", FILE)
