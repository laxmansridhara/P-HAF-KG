import csv
from pathlib import Path


BASELINE_FILE = Path(
    "data/processed/p_haf_kg_evidence_14_baseline.csv"
)

V2_FILE = Path(
    "data/processed/p_haf_kg_evidence_14_v2.csv"
)

OUTPUT_FILE = Path(
    "data/processed/p_haf_kg_14_version_comparison.csv"
)


def split_labels(value):

    return set(
        x.strip()
        for x in str(value).split(";")
        if x.strip()
    )


with BASELINE_FILE.open(
    "r",
    encoding="utf-8",
    errors="replace",
    newline=""
) as f:

    baseline_rows = {
        row["code"]: row
        for row in csv.DictReader(f)
    }


with V2_FILE.open(
    "r",
    encoding="utf-8",
    errors="replace",
    newline=""
) as f:

    v2_rows = {
        row["code"]: row
        for row in csv.DictReader(f)
    }


rows = []

changed_products = 0


for code in baseline_rows:

    baseline = baseline_rows[
        code
    ]

    v2 = v2_rows.get(code)

    if v2 is None:
        continue


    baseline_confirmed = split_labels(
        baseline[
            "confirmed_allergens"
        ]
    )

    v2_confirmed = split_labels(
        v2[
            "confirmed_allergens"
        ]
    )


    baseline_potential = split_labels(
        baseline[
            "potential_allergens"
        ]
    )

    v2_potential = split_labels(
        v2[
            "potential_allergens"
        ]
    )


    confirmed_added = (
        v2_confirmed
        - baseline_confirmed
    )

    confirmed_removed = (
        baseline_confirmed
        - v2_confirmed
    )

    potential_added = (
        v2_potential
        - baseline_potential
    )

    potential_removed = (
        baseline_potential
        - v2_potential
    )


    changed = any([
        confirmed_added,
        confirmed_removed,
        potential_added,
        potential_removed,
    ])


    if changed:
        changed_products += 1


    rows.append({

        "code":
            code,

        "product_name":
            v2["product_name"],

        "baseline_confirmed":
            ";".join(
                sorted(
                    baseline_confirmed
                )
            ),

        "v2_confirmed":
            ";".join(
                sorted(
                    v2_confirmed
                )
            ),

        "confirmed_added":
            ";".join(
                sorted(
                    confirmed_added
                )
            ),

        "confirmed_removed":
            ";".join(
                sorted(
                    confirmed_removed
                )
            ),

        "baseline_potential":
            ";".join(
                sorted(
                    baseline_potential
                )
            ),

        "v2_potential":
            ";".join(
                sorted(
                    v2_potential
                )
            ),

        "potential_added":
            ";".join(
                sorted(
                    potential_added
                )
            ),

        "potential_removed":
            ";".join(
                sorted(
                    potential_removed
                )
            ),

        "changed":
            "YES" if changed else "NO",

    })


with OUTPUT_FILE.open(
    "w",
    encoding="utf-8",
    newline=""
) as f:

    fieldnames = [
        "code",
        "product_name",
        "baseline_confirmed",
        "v2_confirmed",
        "confirmed_added",
        "confirmed_removed",
        "baseline_potential",
        "v2_potential",
        "potential_added",
        "potential_removed",
        "changed",
    ]

    writer = csv.DictWriter(
        f,
        fieldnames=fieldnames
    )

    writer.writeheader()
    writer.writerows(rows)


print(
    "===== P-HAF-KG VERSION COMPARISON ====="
)

print(
    "Baseline products:",
    len(baseline_rows)
)

print(
    "V2 products:",
    len(v2_rows)
)

print(
    "Products compared:",
    len(rows)
)

print(
    "Products changed:",
    changed_products
)

print(
    "Output:",
    OUTPUT_FILE
)


print(
    "\n===== CHANGED PRODUCTS ====="
)

for row in rows:

    if row["changed"] == "YES":

        print(
            "\nCode:",
            row["code"]
        )

        print(
            "Product:",
            row["product_name"]
        )

        print(
            "Baseline confirmed:",
            row["baseline_confirmed"]
        )

        print(
            "V2 confirmed:",
            row["v2_confirmed"]
        )

        print(
            "Confirmed added:",
            row["confirmed_added"]
        )

        print(
            "Confirmed removed:",
            row["confirmed_removed"]
        )

        print(
            "Baseline potential:",
            row["baseline_potential"]
        )

        print(
            "V2 potential:",
            row["v2_potential"]
        )

        print(
            "Potential added:",
            row["potential_added"]
        )

        print(
            "Potential removed:",
            row["potential_removed"]
        )
