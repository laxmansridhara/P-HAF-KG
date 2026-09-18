from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch


# ============================================================
# FIGURE 5.15
# OCR-Assisted Food Analysis Workflow
#
# Conceptual representation of the implemented application
# workflow:
#
# Food label image
#       ↓
# Tesseract OCR
#       ↓
# Extracted ingredient text
#       ↓
# P-HAF-KG V2.1 analysis
#       ↓
# Complementary SVM prediction
#       ↓
# Personalised food decision
#
# OCR is shown as an application extension, not as a
# quantitatively evaluated OCR accuracy component.
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
    / "figure_5_15_ocr_assisted_analysis_flow.png"
)


# ------------------------------------------------------------
# 3. FIGURE
# ------------------------------------------------------------

fig, ax = plt.subplots(
    figsize=(12, 10)
)

ax.set_xlim(
    0,
    12
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
    6,
    11.4,
    "OCR-Assisted Food Ingredient Analysis Workflow",
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
        y + height * 0.68,
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
# 6. MAIN WORKFLOW BOXES
# ------------------------------------------------------------

add_box(
    3.5,
    9.25,
    5.0,
    1.25,
    "1. Food Label Image",
    "Uploaded product / ingredient-label image"
)


add_box(
    3.5,
    7.45,
    5.0,
    1.25,
    "2. Tesseract OCR",
    "Image-to-text extraction\nEnglish / French / German support"
)


add_box(
    3.5,
    5.65,
    5.0,
    1.25,
    "3. Ingredient Text",
    "OCR output cleaned and passed to\nfood-analysis pipeline"
)


add_box(
    3.5,
    3.85,
    5.0,
    1.25,
    "4. P-HAF-KG V2.1",
    "Ingredient matching\nEvidence segmentation\nConfirmed / potential reasoning"
)


add_box(
    1.0,
    1.55,
    4.0,
    1.25,
    "5. Complementary SVM",
    "TF-IDF + Linear SVM\nCandidate prediction"
)


add_box(
    7.0,
    1.55,
    4.0,
    1.25,
    "6. Personalised Decision",
    "Allergen-profile filtering\nFood suitability output"
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
        "arc3,rad=0.18"
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
    (6.0, 9.25),
    (6.0, 8.70)
)


add_arrow(
    (6.0, 7.45),
    (6.0, 6.90)
)


add_arrow(
    (6.0, 5.65),
    (6.0, 5.10)
)


# ------------------------------------------------------------
# 9. P-HAF-KG TO SVM
# ------------------------------------------------------------

add_arrow(
    (4.65, 3.85),
    (3.25, 2.80),
    curved=True
)


# ------------------------------------------------------------
# 10. P-HAF-KG TO PERSONALISATION
# ------------------------------------------------------------

add_arrow(
    (7.35, 3.85),
    (8.75, 2.80),
    curved=True
)


# ------------------------------------------------------------
# 11. SVM TO PERSONALISATION
# ------------------------------------------------------------

add_arrow(
    (5.0, 2.18),
    (7.0, 2.18)
)


# ------------------------------------------------------------
# 12. OCR NOTE
# ------------------------------------------------------------

ax.text(
    6,
    7.05,
    "OCR converts the image into text; allergen reasoning is performed downstream.",
    ha="center",
    va="center",
    fontsize=9,
    style="italic"
)


# ------------------------------------------------------------
# 13. APPLICATION LIMITATION NOTE
# ------------------------------------------------------------

ax.text(
    6,
    0.65,
    "OCR functionality was tested as an application extension; "
    "OCR accuracy was not quantitatively evaluated.",
    ha="center",
    va="center",
    fontsize=9
)


# ------------------------------------------------------------
# 14. SAVE
# ------------------------------------------------------------

fig.tight_layout()

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
    "Figure 5.15 OCR-assisted analysis flow generated."
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