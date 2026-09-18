import csv
from pathlib import Path


OUTPUT_FILE = Path(
    "data/processed/ingredient_allergen_knowledge.csv"
)


# ==================================================
# INGREDIENT -> ALLERGEN KNOWLEDGE
# ==================================================

KNOWLEDGE = [

    # ==================================================
    # PEANUT
    # ==================================================

    ("peanut", "peanut"),
    ("peanuts", "peanut"),
    ("peanut flour", "peanut"),
    ("peanut paste", "peanut"),
    ("peanut butter", "peanut"),
    ("peanut oil", "peanut"),
    ("arachis", "peanut"),
    ("arachide", "peanut"),
    ("arachides", "peanut"),
    ("cacahuete", "peanut"),
    ("cacahuetes", "peanut"),
    ("pate d'arachide", "peanut"),
    ("beurre de cacahuete", "peanut"),

    # ==================================================
    # MILK
    # ==================================================

    ("milk", "milk"),
    ("milk powder", "milk"),
    ("skimmed milk", "milk"),
    ("skim milk", "milk"),
    ("whole milk", "milk"),
    ("milk protein", "milk"),
    ("milk protein concentrate", "milk"),
    ("whey", "milk"),
    ("whey protein", "milk"),
    ("whey protein concentrate", "milk"),
    ("casein", "milk"),
    ("caseinate", "milk"),
    ("caseinate de calcium", "milk"),
    ("caseinates", "milk"),
    ("lactose", "milk"),
    ("cream", "milk"),
    ("butter", "milk"),
    ("cheese", "milk"),
    ("yogurt", "milk"),
    ("yoghurt", "milk"),

    # French milk
    ("lait", "milk"),
    ("lait entier", "milk"),
    ("lait ecreme", "milk"),
    ("lait ecreme en poudre", "milk"),
    ("lait en poudre", "milk"),
    ("poudre de lait", "milk"),
    ("proteines de lait", "milk"),
    ("proteine de lait", "milk"),
    ("proteines du lait", "milk"),
    ("lactoserum", "milk"),
    ("proteines de lactoserum", "milk"),
    ("petit lait", "milk"),
    ("beurre concentre", "milk"),
    ("creme fraiche", "milk"),
    ("chocolat au lait", "milk"),
    ("fromage", "milk"),
    ("fromages", "milk"),
    ("ricotta", "milk"),
    ("yaourt", "milk"),
    ("yogourt", "milk"),
    ("caseine", "milk"),

    # ==================================================
    # EGG
    # ==================================================

    ("egg", "egg"),
    ("eggs", "egg"),
    ("egg white", "egg"),
    ("egg whites", "egg"),
    ("egg yolk", "egg"),
    ("egg yolks", "egg"),
    ("albumin", "egg"),
    ("egg albumin", "egg"),
    ("ovalbumin", "egg"),

    # French egg
    ("oeuf", "egg"),
    ("oeufs", "egg"),
    ("blanc d'oeuf", "egg"),
    ("jaune d'oeuf", "egg"),
    ("albumine d'oeuf", "egg"),

    # ==================================================
    # SOY
    # ==================================================

    ("soy", "soy"),
    ("soya", "soy"),
    ("soybean", "soy"),
    ("soybeans", "soy"),
    ("soybean oil", "soy"),
    ("soy oil", "soy"),
    ("soya oil", "soy"),
    ("soy lecithin", "soy"),
    ("soya lecithin", "soy"),
    ("soy protein", "soy"),
    ("soy protein isolate", "soy"),
    ("soy flour", "soy"),
    ("soy sauce", "soy"),
    ("soya sauce", "soy"),
    ("tofu", "soy"),

    # French soy
    ("soja", "soy"),
    ("feves de soja", "soy"),
    ("huile de soja", "soy"),
    ("lecithine de soja", "soy"),
    ("lecithines de soja", "soy"),
    ("proteines de soja", "soy"),
    ("proteine de soja", "soy"),
    ("farine de soja", "soy"),
    ("sauce soja", "soy"),
    ("sauce de soja", "soy"),

    # ==================================================
    # WHEAT / GLUTEN
    # ==================================================

    ("wheat", "wheat_gluten"),
    ("wheat flour", "wheat_gluten"),
    ("wheat protein", "wheat_gluten"),
    ("wheat starch", "wheat_gluten"),
    ("whole wheat", "wheat_gluten"),
    ("durum wheat", "wheat_gluten"),
    ("durum wheat semolina", "wheat_gluten"),
    ("semolina", "wheat_gluten"),
    ("gluten", "wheat_gluten"),
    ("wheat gluten", "wheat_gluten"),
    ("barley", "wheat_gluten"),
    ("rye", "wheat_gluten"),
    ("malt", "wheat_gluten"),
    ("barley malt", "wheat_gluten"),

    # French wheat / gluten
    ("ble", "wheat_gluten"),
    ("farine de ble", "wheat_gluten"),
    ("farine de ble dur", "wheat_gluten"),
    ("ble dur", "wheat_gluten"),
    ("semoule de ble", "wheat_gluten"),
    ("gluten de ble", "wheat_gluten"),
    ("amidon de ble", "wheat_gluten"),
    ("farine de froment", "wheat_gluten"),
    ("orge", "wheat_gluten"),
    ("malt d'orge", "wheat_gluten"),
    ("seigle", "wheat_gluten"),

    # ==================================================
    # SESAME
    # ==================================================

    ("sesame", "sesame"),
    ("sesame seed", "sesame"),
    ("sesame seeds", "sesame"),
    ("sesame oil", "sesame"),
    ("tahini", "sesame"),

    # French sesame
    ("graines de sesame", "sesame"),
    ("huile de sesame", "sesame"),
    ("pate de sesame", "sesame"),

    # ==================================================
    # TREE NUT
    # ==================================================

    ("almond", "tree_nut"),
    ("almonds", "tree_nut"),
    ("almond butter", "tree_nut"),
    ("almond flour", "tree_nut"),
    ("hazelnut", "tree_nut"),
    ("hazelnuts", "tree_nut"),
    ("cashew", "tree_nut"),
    ("cashews", "tree_nut"),
    ("walnut", "tree_nut"),
    ("walnuts", "tree_nut"),
    ("pecan", "tree_nut"),
    ("pecans", "tree_nut"),
    ("pistachio", "tree_nut"),
    ("pistachios", "tree_nut"),
    ("macadamia", "tree_nut"),
    ("brazil nut", "tree_nut"),
    ("brazil nuts", "tree_nut"),

    # French tree nuts
    ("amande", "tree_nut"),
    ("amandes", "tree_nut"),
    ("noisette", "tree_nut"),
    ("noisettes", "tree_nut"),
    ("noix", "tree_nut"),
    ("noix de cajou", "tree_nut"),
    ("cajou", "tree_nut"),
    ("pistache", "tree_nut"),
    ("pistaches", "tree_nut"),
    ("noix de pecan", "tree_nut"),
    ("noix du bresil", "tree_nut"),
    ("fruits a coque", "tree_nut"),
]


# ==================================================
# VALIDATE KNOWLEDGE ENTRIES
# ==================================================

for index, item in enumerate(KNOWLEDGE, start=1):

    if not isinstance(item, tuple):
        raise ValueError(
            f"Knowledge entry {index} is not a tuple: {item!r}"
        )

    if len(item) != 2:
        raise ValueError(
            f"Knowledge entry {index} must contain exactly "
            f"2 values: {item!r}"
        )

    ingredient, allergen = item

    if not isinstance(ingredient, str):
        raise ValueError(
            f"Ingredient at entry {index} is not a string: "
            f"{ingredient!r}"
        )

    if not isinstance(allergen, str):
        raise ValueError(
            f"Allergen at entry {index} is not a string: "
            f"{allergen!r}"
        )


# ==================================================
# REMOVE DUPLICATES
# ==================================================

unique_knowledge = []

seen = set()

for ingredient, allergen in KNOWLEDGE:

    ingredient = ingredient.lower().strip()
    allergen = allergen.lower().strip()

    key = (
        ingredient,
        allergen
    )

    if key in seen:
        continue

    seen.add(key)

    unique_knowledge.append(
        (
            ingredient,
            allergen
        )
    )


# ==================================================
# CREATE OUTPUT DIRECTORY
# ==================================================

OUTPUT_FILE.parent.mkdir(
    parents=True,
    exist_ok=True
)


# ==================================================
# WRITE KNOWLEDGE BASE
# ==================================================

with OUTPUT_FILE.open(
    "w",
    encoding="utf-8",
    newline=""
) as f:

    writer = csv.DictWriter(
        f,
        fieldnames=[
            "ingredient",
            "allergen",
            "evidence_type",
            "confidence"
        ]
    )

    writer.writeheader()

    for ingredient, allergen in unique_knowledge:

        writer.writerow({
            "ingredient": ingredient,
            "allergen": allergen,
            "evidence_type": "direct",
            "confidence": "1.0"
        })


# ==================================================
# SUMMARY
# ==================================================

print(
    "===== P-HAF-KG KNOWLEDGE BASE ====="
)

print(
    "Raw relationships:",
    len(KNOWLEDGE)
)

print(
    "Unique relationships:",
    len(unique_knowledge)
)

print(
    "Output:",
    OUTPUT_FILE
)
