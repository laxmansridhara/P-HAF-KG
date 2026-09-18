from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch


# ============================================================
# OVERALL SYSTEM ARCHITECTURE
#
# Food data
#     ↓
# Text normalisation
#     ↓
# P-HAF-KG V2.1 + TF-IDF/SVM
#     ↓
# Hybrid evidence fusion
#     ↓
# Personalisation
#     ↓
# Application / user interface
# ============================================================


PROJECT_ROOT = Path(__file__).resolve().parents[1]

OUTPUT_DIR = PROJECT_ROOT / "figures"

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)

OUTPUT_FILE = (
    OUTPUT_DIR
    / "figure_4_1_overall_system_architecture.png"
)


fig, ax = plt.subplots(
    figsize=(15, 10)
)

ax.set_xlim(0, 15)
ax.set_ylim(0, 12)

ax.axis("off")


# ------------------------------------------------------------
# TITLE
# ------------------------------------------------------------

ax.text(
    7.5,
    11.45,
    "Overall System Architecture of the Proposed Food-Analysis System",
    ha="center",
    va="center",
    fontsize=18,
    fontweight="bold"
)


# ------------------------------------------------------------
# BOX FUNCTION
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
        boxstyle="round,pad=0.04",
        linewidth=1.6
    )

    ax.add_patch(box)

    ax.text(
        x + width / 2,
        y + height * 0.70,
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
# LAYER 1 — DATA ACQUISITION
# ------------------------------------------------------------

add_box(
    4.5,
    9.2,
    6.0,
    1.25,
    "1. Data Acquisition",
    "Open Food Facts product records\n"
    "Product name + ingredient text"
)


# ------------------------------------------------------------
# LAYER 2 — TEXT PROCESSING
# ------------------------------------------------------------

add_box(
    4.5,
    7.35,
    6.0,
    1.25,
    "2. Text Processing",
    "Normalisation, accents, punctuation,\n"
    "spacing and phrase-level exceptions"
)


# ------------------------------------------------------------
# LAYER 3 — ALLERGEN ANALYSIS
# ------------------------------------------------------------

add_box(
    0.75,
    4.65,
    5.5,
    1.65,
    "3A. P-HAF-KG V2.1",
    "Structured ingredient–allergen relationships\n"
    "Evidence segmentation\n"
    "Confirmed / potential reasoning"
)


add_box(
    8.75,
    4.65,
    5.5,
    1.65,
    "3B. TF-IDF + Linear SVM",
    "TF-IDF text representation\n"
    "Multilabel supervised prediction\n"
    "Candidate generation"
)


# ------------------------------------------------------------
# LAYER 4 — HYBRID FUSION
# ------------------------------------------------------------

add_box(
    4.5,
    2.45,
    6.0,
    1.35,
    "4. Hybrid Evidence Fusion",
    "Explicit P-HAF-KG evidence has priority\n"
    "SVM-only predictions become review candidates"
)


# ------------------------------------------------------------
# LAYER 5 — PERSONALISATION
# ------------------------------------------------------------

add_box(
    4.5,
    0.65,
    6.0,
    1.25,
    "5. Personalisation / Food Decision",
    "Compare detected allergens with\n"
    "the user's selected allergy profile"
)


# ------------------------------------------------------------
# APPLICATION INTERFACE
# ------------------------------------------------------------

add_box(
    11.0,
    0.65,
    3.0,
    1.25,
    "6. Application Layer",
    "Structured decision output\n"
    "Suitable / risk / review"
)


# ------------------------------------------------------------
# ARROW FUNCTION
# ------------------------------------------------------------

def add_arrow(
    start,
    end
):

    arrow = FancyArrowPatch(
        start,
        end,
        arrowstyle="->",
        mutation_scale=18,
        linewidth=1.6
    )

    ax.add_patch(arrow)


# ------------------------------------------------------------
# DATA → TEXT
# ------------------------------------------------------------

add_arrow(
    (7.5, 9.2),
    (7.5, 8.6)
)


# ------------------------------------------------------------
# TEXT → MODELS
# ------------------------------------------------------------

add_arrow(
    (6.0, 7.35),
    (3.5, 6.3)
)

add_arrow(
    (9.0, 7.35),
    (11.5, 6.3)
)


# ------------------------------------------------------------
# P-HAF → HYBRID
# ------------------------------------------------------------

add_arrow(
    (3.5, 4.65),
    (5.5, 3.8)
)


# ------------------------------------------------------------
# SVM → HYBRID
# ------------------------------------------------------------

add_arrow(
    (11.5, 4.65),
    (9.5, 3.8)
)


# ------------------------------------------------------------
# HYBRID → PERSONALISATION
# ------------------------------------------------------------

add_arrow(
    (7.5, 2.45),
    (7.5, 1.9)
)


# ------------------------------------------------------------
# PERSONALISATION → APPLICATION
# ------------------------------------------------------------

add_arrow(
    (10.5, 1.25),
    (11.0, 1.25)
)


# ------------------------------------------------------------
# KEY PRINCIPLE
# ------------------------------------------------------------

ax.text(
    7.5,
    4.15,
    "Evidence-aware reasoning + complementary statistical prediction",
    ha="center",
    va="center",
    fontsize=9,
    style="italic"
)


# ------------------------------------------------------------
# APPLICATION EXTENSIONS
# ------------------------------------------------------------

ax.text(
    1.0,
    0.35,
    "Application extensions:\nOCR input • API integration",
    ha="left",
    va="center",
    fontsize=8.5
)


# ------------------------------------------------------------
# SAVE
# ------------------------------------------------------------

fig.tight_layout()

fig.savefig(
    OUTPUT_FILE,
    dpi=300,
    bbox_inches="tight"
)

plt.close(fig)


print("\nSUCCESS")
print("=" * 75)

print(
    "Overall system architecture figure generated."
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