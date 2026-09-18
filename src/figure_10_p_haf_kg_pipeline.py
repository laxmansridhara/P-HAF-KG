from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch


# ============================================================
# FIGURE
# P-HAF-KG V2.1 Processing Pipeline
#
# Conceptual pipeline based on the implemented project workflow.
# No performance values are manually entered.
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
    / "figure_4_1_p_haf_kg_v2_1_processing_pipeline.png"
)


# ------------------------------------------------------------
# 3. PIPELINE STAGES
# ------------------------------------------------------------

stages = [
    (
        "1. Ingredient Input",
        "Product ingredient text\nor OCR-extracted text"
    ),
    (
        "2. Text Normalisation",
        "Lowercase\nAccent / punctuation handling\nWhitespace normalisation"
    ),
    (
        "3. Evidence Segmentation",
        "Direct ingredient evidence\nPrecautionary statements\nContext separation"
    ),
    (
        "4. Lexical Matching",
        "Knowledge-base terms\nLongest-term matching\nBoundary-safe matching"
    ),
    (
        "5. P-HAF-KG Reasoning",
        "Confirmed evidence\nPotential evidence\nExclusions / context rules"
    ),
    (
        "6. SVM Complement",
        "TF-IDF representation\nLinear SVM candidate prediction"
    ),
    (
        "7. Hybrid Review",
        "Evidence-confirmed result\nor review candidate"
    ),
    (
        "8. Personalised Decision",
        "Allergen filtering\nUser preference\nFood suitability output"
    ),
]


# ------------------------------------------------------------
# 4. FIGURE
# ------------------------------------------------------------

fig, ax = plt.subplots(
    figsize=(16, 9)
)


ax.set_xlim(
    0,
    16
)

ax.set_ylim(
    0,
    10
)

ax.axis("off")


# ------------------------------------------------------------
# 5. TITLE
# ------------------------------------------------------------

ax.text(
    8,
    9.5,
    "P-HAF-KG V2.1 Evidence-Aware Food Analysis Pipeline",
    ha="center",
    va="center",
    fontsize=18,
    fontweight="bold"
)


# ------------------------------------------------------------
# 6. BOX POSITIONS
# ------------------------------------------------------------

positions = [
    (0.5, 7.3),
    (4.5, 7.3),
    (8.5, 7.3),
    (12.5, 7.3),

    (0.5, 3.2),
    (4.5, 3.2),
    (8.5, 3.2),
    (12.5, 3.2),
]


box_width = 3.0

box_height = 1.7


# ------------------------------------------------------------
# 7. DRAW BOXES
# ------------------------------------------------------------

for (
    (title, description),
    (x, y)
) in zip(
    stages,
    positions
):

    box = FancyBboxPatch(
        (
            x,
            y
        ),
        box_width,
        box_height,

        boxstyle="round,pad=0.03",

        linewidth=1.5
    )

    ax.add_patch(box)


    ax.text(
        x + box_width / 2,
        y + 1.25,

        title,

        ha="center",
        va="center",

        fontsize=10.5,
        fontweight="bold"
    )


    ax.text(
        x + box_width / 2,
        y + 0.65,

        description,

        ha="center",
        va="center",

        fontsize=8.5
    )


# ------------------------------------------------------------
# 8. TOP ROW ARROWS
# ------------------------------------------------------------

for i in range(3):

    x_start = positions[i][0] + box_width

    x_end = positions[i + 1][0]

    y = positions[i][1] + box_height / 2

    arrow = FancyArrowPatch(
        (
            x_start + 0.05,
            y
        ),
        (
            x_end - 0.05,
            y
        ),

        arrowstyle="->",

        mutation_scale=18,

        linewidth=1.5
    )

    ax.add_patch(arrow)


# ------------------------------------------------------------
# 9. CONNECT TOP ROW TO LOWER ROW
# ------------------------------------------------------------

arrow = FancyArrowPatch(
    (
        positions[3][0] + box_width / 2,
        positions[3][1]
    ),
    (
        positions[7][0] + box_width / 2,
        positions[7][1] + box_height
    ),

    arrowstyle="->",

    mutation_scale=18,

    linewidth=1.5,

    connectionstyle="arc3,rad=0.25"
)

ax.add_patch(arrow)


# ------------------------------------------------------------
# 10. LOWER ROW ARROWS
# ------------------------------------------------------------

for i in range(4, 7):

    x_start = positions[i][0] + box_width

    x_end = positions[i + 1][0]

    y = positions[i][1] + box_height / 2

    arrow = FancyArrowPatch(
        (
            x_start + 0.05,
            y
        ),
        (
            x_end - 0.05,
            y
        ),

        arrowstyle="->",

        mutation_scale=18,

        linewidth=1.5
    )

    ax.add_patch(arrow)


# ------------------------------------------------------------
# 11. SVM COMPLEMENT ANNOTATION
# ------------------------------------------------------------

ax.text(
    6.0,
    5.55,

    "Complementary supervised ML pathway",

    ha="center",
    va="center",

    fontsize=9,
    style="italic"
)


# ------------------------------------------------------------
# 12. EVIDENCE-REASONING ANNOTATION
# ------------------------------------------------------------

ax.text(
    10.0,
    5.55,

    "Evidence-aware reasoning remains the primary decision layer",

    ha="center",
    va="center",

    fontsize=9,
    style="italic"
)


# ------------------------------------------------------------
# 13. FOOTNOTE
# ------------------------------------------------------------

ax.text(
    8,
    0.65,

    "Implemented as a structured ingredient–allergen relationship knowledge base "
    "with deterministic evidence-reasoning rules.",

    ha="center",
    va="center",

    fontsize=9
)


# ------------------------------------------------------------
# 14. SAVE
# ------------------------------------------------------------

fig.savefig(
    OUTPUT_FILE,
    dpi=300,
    bbox_inches="tight"
)

plt.close(fig)


# ------------------------------------------------------------
# 15. VERIFY
# ------------------------------------------------------------

print("\nSUCCESS")
print("=" * 75)

print(
    "P-HAF-KG V2.1 processing pipeline figure generated."
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