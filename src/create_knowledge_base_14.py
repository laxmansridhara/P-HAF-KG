import csv
from pathlib import Path


OUTPUT_FILE = Path(
    "data/processed/ingredient_allergen_knowledge_14.csv"
)


# ============================================================
# P-HAF-KG V2
# UK 14 REGULATED ALLERGENS
# ============================================================

ALLERGENS = [
    "celery",
    "wheat_gluten",
    "crustaceans",
    "egg",
    "fish",
    "lupin",
    "milk",
    "molluscs",
    "mustard",
    "peanut",
    "sesame",
    "soy",
    "sulphites",
    "tree_nut",
]


# ============================================================
# KNOWLEDGE BASE
#
# Format:
# ingredient,
# allergen,
# evidence_type,
# confidence,
# language
# ============================================================

KNOWLEDGE = [

    # ========================================================
    # CELERY
    # ========================================================

    ("celery", "celery", "direct", 1.0, "en"),
    ("celery root", "celery", "direct", 1.0, "en"),
    ("celeriac", "celery", "direct", 1.0, "en"),
    ("celeri", "celery", "direct", 1.0, "fr"),
    ("celeri rave", "celery", "direct", 1.0, "fr"),
    ("sellerie", "celery", "direct", 1.0, "de"),


    # ========================================================
    # CEREALS CONTAINING GLUTEN
    # ========================================================

    # English

    ("wheat", "wheat_gluten", "direct", 1.0, "en"),
    ("wheat flour", "wheat_gluten", "direct", 1.0, "en"),
    ("whole wheat", "wheat_gluten", "direct", 1.0, "en"),
    ("whole wheat flour", "wheat_gluten", "direct", 1.0, "en"),
    ("wheat protein", "wheat_gluten", "direct", 1.0, "en"),
    ("wheat starch", "wheat_gluten", "direct", 1.0, "en"),
    ("durum wheat", "wheat_gluten", "direct", 1.0, "en"),
    ("semolina", "wheat_gluten", "direct", 1.0, "en"),
    ("barley", "wheat_gluten", "direct", 1.0, "en"),
    ("barley flour", "wheat_gluten", "direct", 1.0, "en"),
    ("barley malt", "wheat_gluten", "direct", 1.0, "en"),
    ("barley malt extract", "wheat_gluten", "direct", 1.0, "en"),
    ("rye", "wheat_gluten", "direct", 1.0, "en"),
    ("rye flour", "wheat_gluten", "direct", 1.0, "en"),
    ("oat", "wheat_gluten", "direct", 1.0, "en"),
    ("oats", "wheat_gluten", "direct", 1.0, "en"),
    ("oat flour", "wheat_gluten", "direct", 1.0, "en"),
    ("gluten", "wheat_gluten", "direct", 1.0, "en"),

    # French

    ("ble", "wheat_gluten", "direct", 1.0, "fr"),
    ("farine de ble", "wheat_gluten", "direct", 1.0, "fr"),
    ("farine de ble tendre", "wheat_gluten", "direct", 1.0, "fr"),
    ("farine de ble complet", "wheat_gluten", "direct", 1.0, "fr"),
    ("semoule de ble", "wheat_gluten", "direct", 1.0, "fr"),
    ("semoule de ble dur", "wheat_gluten", "direct", 1.0, "fr"),
    ("orge", "wheat_gluten", "direct", 1.0, "fr"),
    ("malt d orge", "wheat_gluten", "direct", 1.0, "fr"),
    ("seigle", "wheat_gluten", "direct", 1.0, "fr"),
    ("avoine", "wheat_gluten", "direct", 1.0, "fr"),
    ("gluten", "wheat_gluten", "direct", 1.0, "fr"),

    # German

    ("weizen", "wheat_gluten", "direct", 1.0, "de"),
    ("weizenmehl", "wheat_gluten", "direct", 1.0, "de"),
    ("weizenmehltyp", "wheat_gluten", "direct", 1.0, "de"),
    ("weizenvollkornmehl", "wheat_gluten", "direct", 1.0, "de"),
    ("weizengries", "wheat_gluten", "direct", 1.0, "de"),
    ("weizenprotein", "wheat_gluten", "direct", 1.0, "de"),
    ("weizenstarke", "wheat_gluten", "direct", 1.0, "de"),
    ("gerste", "wheat_gluten", "direct", 1.0, "de"),
    ("gerstenmalz", "wheat_gluten", "direct", 1.0, "de"),
    ("gerstenmalzextrakt", "wheat_gluten", "direct", 1.0, "de"),
    ("malz", "wheat_gluten", "direct", 1.0, "de"),
    ("roggen", "wheat_gluten", "direct", 1.0, "de"),
    ("roggenmehl", "wheat_gluten", "direct", 1.0, "de"),
    ("hafer", "wheat_gluten", "direct", 1.0, "de"),
    ("hafermehl", "wheat_gluten", "direct", 1.0, "de"),
    ("gluten", "wheat_gluten", "direct", 1.0, "de"),


    # ========================================================
    # CRUSTACEANS
    # ========================================================

    ("crustaceans", "crustaceans", "direct", 1.0, "en"),
    ("shrimp", "crustaceans", "direct", 1.0, "en"),
    ("prawn", "crustaceans", "direct", 1.0, "en"),
    ("prawns", "crustaceans", "direct", 1.0, "en"),
    ("crab", "crustaceans", "direct", 1.0, "en"),
    ("lobster", "crustaceans", "direct", 1.0, "en"),
    ("langoustine", "crustaceans", "direct", 1.0, "en"),
    ("crevette", "crustaceans", "direct", 1.0, "fr"),
    ("crevettes", "crustaceans", "direct", 1.0, "fr"),
    ("crabe", "crustaceans", "direct", 1.0, "fr"),
    ("homard", "crustaceans", "direct", 1.0, "fr"),
    ("garnelen", "crustaceans", "direct", 1.0, "de"),
    ("krabbe", "crustaceans", "direct", 1.0, "de"),
    ("hummer", "crustaceans", "direct", 1.0, "de"),


    # ========================================================
    # EGG
    # ========================================================

    ("egg", "egg", "direct", 1.0, "en"),
    ("eggs", "egg", "direct", 1.0, "en"),
    ("egg albumin", "egg", "direct", 1.0, "en"),
    ("albumin", "egg", "direct", 1.0, "en"),
    ("egg white", "egg", "direct", 1.0, "en"),
    ("egg yolk", "egg", "direct", 1.0, "en"),
    ("oeuf", "egg", "direct", 1.0, "fr"),
    ("oeufs", "egg", "direct", 1.0, "fr"),
    ("jaune d oeuf", "egg", "direct", 1.0, "fr"),
    ("ei", "egg", "direct", 1.0, "de"),
    ("eier", "egg", "direct", 1.0, "de"),
    ("eiprotein", "egg", "direct", 1.0, "de"),
    ("eigelb", "egg", "direct", 1.0, "de"),
    ("eiweiss", "egg", "direct", 1.0, "de"),


    # ========================================================
    # FISH
    # ========================================================

    ("fish", "fish", "direct", 1.0, "en"),
    ("fish protein", "fish", "direct", 1.0, "en"),
    ("salmon", "fish", "direct", 1.0, "en"),
    ("tuna", "fish", "direct", 1.0, "en"),
    ("cod", "fish", "direct", 1.0, "en"),
    ("haddock", "fish", "direct", 1.0, "en"),
    ("trout", "fish", "direct", 1.0, "en"),
    ("saumon", "fish", "direct", 1.0, "fr"),
    ("thon", "fish", "direct", 1.0, "fr"),
    ("morue", "fish", "direct", 1.0, "fr"),
    ("lachs", "fish", "direct", 1.0, "de"),
    ("thunfisch", "fish", "direct", 1.0, "de"),
    ("kabeljau", "fish", "direct", 1.0, "de"),


    # ========================================================
    # LUPIN
    # ========================================================

    ("lupin", "lupin", "direct", 1.0, "en"),
    ("lupin flour", "lupin", "direct", 1.0, "en"),
    ("lupine", "lupin", "direct", 1.0, "fr"),
    ("farine de lupin", "lupin", "direct", 1.0, "fr"),
    ("lupinen", "lupin", "direct", 1.0, "de"),


    # ========================================================
    # MILK
    # ========================================================

    ("milk", "milk", "direct", 1.0, "en"),
    ("milk powder", "milk", "direct", 1.0, "en"),
    ("milk protein", "milk", "direct", 1.0, "en"),
    ("milk proteins", "milk", "direct", 1.0, "en"),
    ("skimmed milk", "milk", "direct", 1.0, "en"),
    ("skim milk", "milk", "direct", 1.0, "en"),
    ("whole milk", "milk", "direct", 1.0, "en"),
    ("whey", "milk", "direct", 1.0, "en"),
    ("whey protein", "milk", "direct", 1.0, "en"),
    ("casein", "milk", "direct", 1.0, "en"),
    ("caseinate", "milk", "direct", 1.0, "en"),
    ("butter", "milk", "direct", 1.0, "en"),
    ("cream", "milk", "direct", 1.0, "en"),
    ("lactose", "milk", "direct", 1.0, "en"),

    # French

    ("lait", "milk", "direct", 1.0, "fr"),
    ("lait ecreme", "milk", "direct", 1.0, "fr"),
    ("lait entier", "milk", "direct", 1.0, "fr"),
    ("poudre de lait", "milk", "direct", 1.0, "fr"),
    ("proteines de lait", "milk", "direct", 1.0, "fr"),
    ("lactoserum", "milk", "direct", 1.0, "fr"),
    ("proteines de lactoserum", "milk", "direct", 1.0, "fr"),
    ("caseinate de calcium", "milk", "direct", 1.0, "fr"),
    ("beurre", "milk", "direct", 1.0, "fr"),
    ("creme", "milk", "direct", 1.0, "fr"),
    ("fromage", "milk", "direct", 1.0, "fr"),
    ("fromages", "milk", "direct", 1.0, "fr"),

    # German

    ("milch", "milk", "direct", 1.0, "de"),
    ("milchpulver", "milk", "direct", 1.0, "de"),
    ("milchprotein", "milk", "direct", 1.0, "de"),
    ("milchproteine", "milk", "direct", 1.0, "de"),
    ("molke", "milk", "direct", 1.0, "de"),
    ("molkenprotein", "milk", "direct", 1.0, "de"),
    ("sahne", "milk", "direct", 1.0, "de"),
    ("butter", "milk", "direct", 1.0, "de"),


    # ========================================================
    # MOLLUSCS
    # ========================================================

    ("molluscs", "molluscs", "direct", 1.0, "en"),
    ("mussel", "molluscs", "direct", 1.0, "en"),
    ("mussels", "molluscs", "direct", 1.0, "en"),
    ("oyster", "molluscs", "direct", 1.0, "en"),
    ("oysters", "molluscs", "direct", 1.0, "en"),
    ("squid", "molluscs", "direct", 1.0, "en"),
    ("octopus", "molluscs", "direct", 1.0, "en"),
    ("moule", "molluscs", "direct", 1.0, "fr"),
    ("moules", "molluscs", "direct", 1.0, "fr"),
    ("huitre", "molluscs", "direct", 1.0, "fr"),
    ("calmar", "molluscs", "direct", 1.0, "fr"),
    ("muschel", "molluscs", "direct", 1.0, "de"),
    ("muscheln", "molluscs", "direct", 1.0, "de"),


    # ========================================================
    # MUSTARD
    # ========================================================

    ("mustard", "mustard", "direct", 1.0, "en"),
    ("mustard seed", "mustard", "direct", 1.0, "en"),
    ("mustard seeds", "mustard", "direct", 1.0, "en"),
    ("moutarde", "mustard", "direct", 1.0, "fr"),
    ("graines de moutarde", "mustard", "direct", 1.0, "fr"),
    ("senf", "mustard", "direct", 1.0, "de"),
    ("senfsamen", "mustard", "direct", 1.0, "de"),


    # ========================================================
    # PEANUT
    # ========================================================

    ("peanut", "peanut", "direct", 1.0, "en"),
    ("peanuts", "peanut", "direct", 1.0, "en"),
    ("peanut flour", "peanut", "direct", 1.0, "en"),
    ("peanut paste", "peanut", "direct", 1.0, "en"),
    ("peanut butter", "peanut", "direct", 1.0, "en"),
    ("peanut oil", "peanut", "direct", 1.0, "en"),
    ("arachis", "peanut", "direct", 1.0, "en"),

    ("arachide", "peanut", "direct", 1.0, "fr"),
    ("arachides", "peanut", "direct", 1.0, "fr"),
    ("pate d arachide", "peanut", "direct", 1.0, "fr"),
    ("cacahuete", "peanut", "direct", 1.0, "fr"),
    ("cacahuetes", "peanut", "direct", 1.0, "fr"),

    ("erdnuss", "peanut", "direct", 1.0, "de"),
    ("erdnusse", "peanut", "direct", 1.0, "de"),
    ("erdnussol", "peanut", "direct", 1.0, "de"),
    ("erdnussbutter", "peanut", "direct", 1.0, "de"),


    # ========================================================
    # SESAME
    # ========================================================

    ("sesame", "sesame", "direct", 1.0, "en"),
    ("sesame seed", "sesame", "direct", 1.0, "en"),
    ("sesame seeds", "sesame", "direct", 1.0, "en"),
    ("sesame oil", "sesame", "direct", 1.0, "en"),
    ("tahini", "sesame", "direct", 1.0, "en"),

    ("sesame", "sesame", "direct", 1.0, "fr"),
    ("sésame", "sesame", "direct", 1.0, "fr"),
    ("graines de sesame", "sesame", "direct", 1.0, "fr"),
    ("graines de sésame", "sesame", "direct", 1.0, "fr"),
    ("huile de sesame", "sesame", "direct", 1.0, "fr"),

    ("sesam", "sesame", "direct", 1.0, "de"),
    ("sesamsamen", "sesame", "direct", 1.0, "de"),
    ("sesamol", "sesame", "direct", 1.0, "de"),


    # ========================================================
    # SOY
    # ========================================================

    ("soy", "soy", "direct", 1.0, "en"),
    ("soybean", "soy", "direct", 1.0, "en"),
    ("soybeans", "soy", "direct", 1.0, "en"),
    ("soy protein", "soy", "direct", 1.0, "en"),
    ("soy lecithin", "soy", "direct", 1.0, "en"),
    ("soy flour", "soy", "direct", 1.0, "en"),

    ("soja", "soy", "direct", 1.0, "fr"),
    ("soja sauce", "soy", "direct", 1.0, "fr"),
    ("farine de soja", "soy", "direct", 1.0, "fr"),
    ("lecithine de soja", "soy", "direct", 1.0, "fr"),

    ("sojabohne", "soy", "direct", 1.0, "de"),
    ("sojabohnen", "soy", "direct", 1.0, "de"),
    ("sojaprotein", "soy", "direct", 1.0, "de"),
    ("sojalecithin", "soy", "direct", 1.0, "de"),


    # ========================================================
    # SULPHITES
    # ========================================================

    (
        "sulphites",
        "sulphites",
        "special_threshold",
        1.0,
        "en"
    ),

    (
        "sulfites",
        "sulphites",
        "special_threshold",
        1.0,
        "en"
    ),

    (
        "sulfites",
        "sulphites",
        "special_threshold",
        1.0,
        "fr"
    ),

    (
        "sulphite",
        "sulphites",
        "special_threshold",
        1.0,
        "en"
    ),

    (
        "sulfite",
        "sulphites",
        "special_threshold",
        1.0,
        "en"
    ),

    (
        "schwefeldioxid",
        "sulphites",
        "special_threshold",
        1.0,
        "de"
    ),

    (
        "sulfit",
        "sulphites",
        "special_threshold",
        1.0,
        "de"
    ),


    # ========================================================
    # TREE NUTS
    # ========================================================

    ("tree nuts", "tree_nut", "direct", 1.0, "en"),
    ("almond", "tree_nut", "direct", 1.0, "en"),
    ("almonds", "tree_nut", "direct", 1.0, "en"),
    ("hazelnut", "tree_nut", "direct", 1.0, "en"),
    ("hazelnuts", "tree_nut", "direct", 1.0, "en"),
    ("walnut", "tree_nut", "direct", 1.0, "en"),
    ("walnuts", "tree_nut", "direct", 1.0, "en"),
    ("pistachio", "tree_nut", "direct", 1.0, "en"),
    ("pistachios", "tree_nut", "direct", 1.0, "en"),
    ("cashew", "tree_nut", "direct", 1.0, "en"),
    ("cashews", "tree_nut", "direct", 1.0, "en"),
    ("pecan", "tree_nut", "direct", 1.0, "en"),
    ("macadamia", "tree_nut", "direct", 1.0, "en"),

    ("amande", "tree_nut", "direct", 1.0, "fr"),
    ("noisette", "tree_nut", "direct", 1.0, "fr"),
    ("noix", "tree_nut", "direct", 1.0, "fr"),
    ("pistache", "tree_nut", "direct", 1.0, "fr"),
    ("pistaches", "tree_nut", "direct", 1.0, "fr"),
    ("fruits a coque", "tree_nut", "direct", 1.0, "fr"),

    ("mandel", "tree_nut", "direct", 1.0, "de"),
    ("mandeln", "tree_nut", "direct", 1.0, "de"),
    ("haselnuss", "tree_nut", "direct", 1.0, "de"),
    ("haselnusse", "tree_nut", "direct", 1.0, "de"),
    ("walnuss", "tree_nut", "direct", 1.0, "de"),
    ("walnusse", "tree_nut", "direct", 1.0, "de"),
    ("pistazie", "tree_nut", "direct", 1.0, "de"),
    ("pistazien", "tree_nut", "direct", 1.0, "de"),
    ("cashew", "tree_nut", "direct", 1.0, "de"),
    ("cashews", "tree_nut", "direct", 1.0, "de"),
]


# ============================================================
# NORMALISATION
# ============================================================

def normalize_term(text):

    text = str(text).strip().lower()

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

        "ß": "ss",
    }

    for old, new in replacements.items():
        text = text.replace(
            old,
            new
        )

    return text


# ============================================================
# VALIDATE KNOWLEDGE
# ============================================================

valid_rows = []

seen = set()

for item in KNOWLEDGE:

    if len(item) != 5:
        raise ValueError(
            f"Invalid knowledge entry: {item}"
        )

    ingredient = normalize_term(
        item[0]
    )

    allergen = item[1]
    evidence_type = item[2]
    confidence = item[3]
    language = item[4]

    if allergen not in ALLERGENS:
        raise ValueError(
            f"Invalid allergen: {allergen}"
        )

    if not ingredient:
        raise ValueError(
            f"Empty ingredient: {item}"
        )

    key = (
        ingredient,
        allergen
    )

    if key in seen:
        continue

    seen.add(key)

    valid_rows.append({

        "ingredient":
            ingredient,

        "allergen":
            allergen,

        "evidence_type":
            evidence_type,

        "confidence":
            confidence,

        "language":
            language,

    })


# ============================================================
# SORT
# ============================================================

valid_rows.sort(
    key=lambda x: (
        x["allergen"],
        -len(x["ingredient"]),
        x["ingredient"]
    )
)


# ============================================================
# SAVE
# ============================================================

OUTPUT_FILE.parent.mkdir(
    parents=True,
    exist_ok=True
)


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
            "confidence",
            "language",
        ]
    )

    writer.writeheader()

    writer.writerows(
        valid_rows
    )


# ============================================================
# SUMMARY
# ============================================================

counts = {
    allergen: 0
    for allergen in ALLERGENS
}

for row in valid_rows:
    counts[
        row["allergen"]
    ] += 1


print(
    "===== P-HAF-KG V2 KNOWLEDGE BASE ====="
)

print(
    "Raw relationships:",
    len(KNOWLEDGE)
)

print(
    "Unique relationships:",
    len(valid_rows)
)

print(
    "\n===== RELATIONSHIPS BY ALLERGEN ====="
)

for allergen in ALLERGENS:

    print(
        f"{allergen:<18}: "
        f"{counts[allergen]}"
    )


print(
    "\nOutput:"
)

print(
    OUTPUT_FILE
)