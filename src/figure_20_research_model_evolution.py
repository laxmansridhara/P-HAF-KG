from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch


# ============================================================
# FIGURE 2.1
# Research Model Evolution:
# Keyword Matching → Supervised ML → P-HAF-KG V2.1
# ============================================================


PROJECT_ROOT = Path(__file__).resolve().parents[1]

OUTPUT_DIR = PROJECT_ROOT / "figures"

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)

OUTPUT_FILE = (
    OUTPUT_DIR
    / "figure_2_1_research_model_evolution.png"
)


# ------------------------------------------------------------
# FIGURE
# ------------------------------------------------------------

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
    11.5,
    "Evolution of the Proposed Food Allergen Analysis Approach",
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
    description,
    title_size=12,
    body_size=9
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
        y + height * 0.72,
        title,
        ha="center",
        va="center",
        fontsize=title_size,
        fontweight="bold"
    )

    ax.text(
        x + width / 2,
        y + height * 0.32,
        description,
        ha="center",
        va="center",
        fontsize=body_size
    )


# ------------------------------------------------------------
# 1. KEYWORD MATCHING
# ------------------------------------------------------------

add_box(
    0.6,
    8.0,
    3.7,
    2.0,
    "Traditional Keyword Matching",
    "Ingredient term → allergen label\n\n"
    "Simple lexical matching\n"
    "Easy to implement and audit"
)


# ------------------------------------------------------------
# 2. LIMITATIONS
# ------------------------------------------------------------

add_box(
    0.6,
    4.9,
    3.7,
    2.0,
    "Observed Limitations",
    "Context ambiguity\n"
    "Phrase-level exceptions\n"
    "Precautionary wording\n"
    "Multilingual terminology"
)


# ------------------------------------------------------------
# 3. SUPERVISED ML
# ------------------------------------------------------------

add_box(
    5.3,
    8.0,
    3.7,
    2.0,
    "Supervised AI / ML",
    "TF-IDF + Linear SVM\n\n"
    "Statistical text classification\n"
    "Learns patterns from labelled data"
)


# ------------------------------------------------------------
# 4. ML LIMITATIONS
# ------------------------------------------------------------

add_box(
    5.3,
    4.9,
    3.7,
    2.0,
    "Remaining Limitations",
    "Prediction does not explicitly\n"
    "represent ingredient–allergen\n"
    "evidence or evidence strength"
)


# ------------------------------------------------------------
# 5. PROPOSED MODEL
# ------------------------------------------------------------

add_box(
    10.0,
    6.8,
    4.4,
    3.2,
    "Proposed P-HAF-KG V2.1",
    "Text normalisation\n"
    "Structured ingredient–allergen relationships\n"
    "Evidence segmentation\n"
    "Phrase/context exclusions\n"
    "Confirmed vs potential states\n"
    "Deterministic and auditable reasoning",
    title_size=13,
    body_size=9
)


# ------------------------------------------------------------
# 6. HYBRID OUTPUT
# ------------------------------------------------------------

add_box(
    5.3,
    1.1,
    4.4,
    2.2,
    "Hybrid Personalised Framework",
    "P-HAF-KG V2.1\n"
    "+ complementary SVM\n"
    "+ user allergen profile\n\n"
    "Food suitability / review decision"
)


# ------------------------------------------------------------
# ARROW FUNCTION
# ------------------------------------------------------------

def arrow(
    start,
    end
):

    patch = FancyArrowPatch(
        start,
        end,
        arrowstyle="->",
        mutation_scale=18,
        linewidth=1.6
    )

    ax.add_patch(patch)


# ------------------------------------------------------------
# FLOW
# ------------------------------------------------------------

arrow(
    (2.45, 8.0),
    (2.45, 6.9)
)


arrow(
    (4.3, 9.0),
    (5.3, 9.0)
)


arrow(
    (7.15, 8.0),
    (7.15, 6.9)
)


arrow(
    (9.0, 8.9),
    (10.0, 8.9)
)


arrow(
    (12.2, 6.8),
    (9.7, 2.9)
)


# ------------------------------------------------------------
# KEY RESEARCH CONTRIBUTION
# ------------------------------------------------------------

ax.text(
    12.2,
    5.4,
    "Primary research contribution",
    ha="center",
    va="center",
    fontsize=10,
    fontweight="bold"
)


ax.text(
    12.2,
    4.8,
    "Evidence-aware ingredient-level\n"
    "allergen interpretation",
    ha="center",
    va="center",
    fontsize=9
)


# ------------------------------------------------------------
# IMPORTANT POSITIONING
# ------------------------------------------------------------

ax.text(
    7.5,
    0.35,
    "P-HAF-KG V2.1 is the primary research model; "
    "the SVM is a complementary statistical component.",
    ha="center",
    va="center",
    fontsize=9
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
    "Figure 2.1 research-model evolution generated."
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