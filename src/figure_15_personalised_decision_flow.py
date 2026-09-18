from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch


# ============================================================
# FIGURE 5.14
# Personalised Food-Decision Flow
#
# Conceptual representation of the implemented application
# workflow:
#
# Ingredient input
#       ↓
# P-HAF-KG evidence analysis
#       ↓
# Confirmed / potential allergen evidence
#       ↓
# Complementary SVM prediction
#       ↓
# Hybrid review decision
#       ↓
# User-specific allergen filtering
#       ↓
# Personalised food decision
# ============================================================


# ------------------------------------------------------------
# 1. PROJECT ROOT
# ------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[1]


# ------------------------------------------------------------
# 2. OUTPUT FOLDER
# ------------------------------------------------------------

OUTPUT_DIR = PROJECT_ROOT / "figures"

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)


OUTPUT_FILE = (
    OUTPUT_DIR
    / "figure_5_14_personalised_decision_flow.png"
)


# ------------------------------------------------------------
# 3. FIGURE
# ------------------------------------------------------------

fig, ax = plt.subplots(
    figsize=(13, 10)
)

ax.set_xlim(
    0,
    13
)

ax.set_ylim(
    0,
    12
)

ax.axis("off")


# ------------------------------------------------------------
# 4. TITLE
# ------------------------------------------------------------

ax.text(
    6.5,
    11.5,
    "Personalised Food Analysis and Decision Flow",
    ha="center",
    va="center",
    fontsize=18,
    fontweight="bold"
)


# ------------------------------------------------------------
# 5. BOX FUNCTION
# ------------------------------------------------------------

def add_box(
    x,
    y,
    width,
    height,
    title,
    description
):

    box = FancyBboxPatch(
        (x, y),
        width,
        height,
        boxstyle="round,pad=0.03",
        linewidth=1.5
    )

    ax.add_patch(box)

    ax.text(
        x + width / 2,
        y + height * 0.67,
        title,
        ha="center",
        va="center",
        fontsize=11,
        fontweight="bold"
    )

    ax.text(
        x + width / 2,
        y + height * 0.30,
        description,
        ha="center",
        va="center",
        fontsize=8.5
    )


# ------------------------------------------------------------
# 6. MAIN PIPELINE BOXES
# ------------------------------------------------------------

boxes = [
    (
        4.5,
        9.65,
        "Ingredient Input",
        "Product ingredient text\nor OCR-extracted text"
    ),

    (
        4.5,
        7.95,
        "P-HAF-KG V2.1 Evidence Analysis",
        "Ingredient normalisation\nEvidence segmentation\nKnowledge-base matching"
    ),

    (
        4.5,
        6.25,
        "Evidence Result",
        "Confirmed allergens\nPotential allergens\nEvidence-aware reasoning"
    ),

    (
        1.0,
        3.65,
        "Complementary SVM",
        "TF-IDF representation\nLinear SVM prediction"
    ),

    (
        8.0,
        3.65,
        "Hybrid Review Layer",
        "KG evidence retained\nSVM-only signals become review candidates"
    ),

    (
        4.5,
        1.70,
        "Personalised User Filtering",
        "Compare detected allergens\nwith the user's allergen profile"
    ),

    (
        4.5,
        0.05,
        "Personalised Food Decision",
        "Suitable / unsuitable / review-oriented output"
    )
]


for box in boxes:

    add_box(
        box[0],
        box[1],
        3.5,
        1.15,
        box[2],
        box[3]
    )


# ------------------------------------------------------------
# 7. ARROW FUNCTION
# ------------------------------------------------------------

def add_arrow(
    start,
    end,
    curved=False
):

    connection = (
        "arc3,rad=0.20"
        if curved
        else "arc3,rad=0"
    )

    arrow = FancyArrowPatch(
        start,
        end,
        arrowstyle="->",
        mutation_scale=18,
        linewidth=1.5,
        connectionstyle=connection
    )

    ax.add_patch(arrow)


# ------------------------------------------------------------
# 8. MAIN VERTICAL FLOW
# ------------------------------------------------------------

add_arrow(
    (6.25, 9.65),
    (6.25, 9.10)
)


add_arrow(
    (6.25, 7.95),
    (6.25, 7.40)
)


add_arrow(
    (6.25, 6.25),
    (6.25, 5.45)
)


# ------------------------------------------------------------
# 9. EVIDENCE RESULT TO SVM
# ------------------------------------------------------------

add_arrow(
    (4.90, 6.25),
    (2.75, 4.80),
    curved=True
)


# ------------------------------------------------------------
# 10. EVIDENCE RESULT TO HYBRID
# ------------------------------------------------------------

add_arrow(
    (7.60, 6.25),
    (9.55, 4.80),
    curved=True
)


# ------------------------------------------------------------
# 11. SVM TO HYBRID
# ------------------------------------------------------------

add_arrow(
    (4.50, 4.22),
    (8.00, 4.22)
)


# ------------------------------------------------------------
# 12. HYBRID TO PERSONALISATION
# ------------------------------------------------------------

add_arrow(
    (9.75, 3.65),
    (7.55, 2.85),
    curved=True
)


# ------------------------------------------------------------
# 13. SVM TO PERSONALISATION
# ------------------------------------------------------------

add_arrow(
    (3.50, 3.65),
    (5.45, 2.85),
    curved=True
)


# ------------------------------------------------------------
# 14. PERSONALISATION TO FINAL DECISION
# ------------------------------------------------------------

add_arrow(
    (6.25, 1.70),
    (6.25, 1.20)
)


# ------------------------------------------------------------
# 15. DECISION NOTES
# ------------------------------------------------------------

ax.text(
    6.5,
    5.05,
    "Primary evidence-aware pathway",
    ha="center",
    va="center",
    fontsize=9,
    style="italic"
)


ax.text(
    2.75,
    3.10,
    "Complementary prediction",
    ha="center",
    va="center",
    fontsize=8.5,
    style="italic"
)


ax.text(
    9.75,
    3.10,
    "Review / candidate generation",
    ha="center",
    va="center",
    fontsize=8.5,
    style="italic"
)


# ------------------------------------------------------------
# 16. FOOTNOTE
# ------------------------------------------------------------

ax.text(
    6.5,
    -0.35,
    "P-HAF-KG V2.1 remains the primary allergen-evidence layer; "
    "the SVM provides complementary predictions and review candidates.",
    ha="center",
    va="center",
    fontsize=9
)


# ------------------------------------------------------------
# 17. SAVE
# ------------------------------------------------------------

fig.tight_layout()

fig.savefig(
    OUTPUT_FILE,
    dpi=300,
    bbox_inches="tight"
)

plt.close(fig)


# ------------------------------------------------------------
# 18. VERIFY
# ------------------------------------------------------------

print("\nSUCCESS")
print("=" * 75)

print(
    "Figure 5.14 personalised decision flow generated."
)

print("\nSaved to:")
print(OUTPUT_FILE)

print(
    "\nFile exists:",
    OUTPUT_FILE.exists()
)

if OUTPUT_FILE.exists():

    print(
        "File size:",
        OUTPUT_FILE.stat().st_size,
        "bytes"
    )

print("=" * 75)