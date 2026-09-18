from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch


# ============================================================
# FIGURE 5.8
# Application Decision Outcomes
#
# Exact dissertation logic:
#
# Detected allergen evidence
#          |
#     +----+------------------+
#     |                       |
# Confirmed user-        Potential / review
# relevant allergen       level information
#     |                       |
# NOT SUITABLE        +-------+--------+
#                     |                |
#              Potential risk   SVM-only / ambiguous
#                                      |
#                              REVIEW RECOMMENDED
#
# The application distinguishes confirmed evidence from
# potential and review-level information.
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


# ------------------------------------------------------------
# 3. OUTPUT FILE
# ------------------------------------------------------------

OUTPUT_FILE = (
    OUTPUT_DIR
    / "figure_5_8_application_decision_outcomes.png"
)


# ------------------------------------------------------------
# 4. FIGURE
# ------------------------------------------------------------

fig, ax = plt.subplots(
    figsize=(13, 9)
)

ax.set_xlim(0, 13)
ax.set_ylim(0, 10)

ax.axis("off")


# ------------------------------------------------------------
# 5. TITLE
# ------------------------------------------------------------

ax.text(
    6.5,
    9.45,
    "Application Decision Logic",
    ha="center",
    va="center",
    fontsize=18,
    fontweight="bold"
)


# ------------------------------------------------------------
# 6. BOX FUNCTION
# ------------------------------------------------------------

def add_box(
    x,
    y,
    width,
    height,
    title,
    description="",
    title_size=12,
    body_size=9
):

    box = FancyBboxPatch(
        (x, y),
        width,
        height,
        boxstyle="round,pad=0.04",
        linewidth=1.6
    )

    ax.add_patch(box)

    if description:

        ax.text(
            x + width / 2,
            y + height * 0.68,
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

    else:

        ax.text(
            x + width / 2,
            y + height / 2,
            title,
            ha="center",
            va="center",
            fontsize=title_size,
            fontweight="bold"
        )


# ------------------------------------------------------------
# 7. MAIN INPUT
# ------------------------------------------------------------

add_box(
    4.25,
    7.55,
    4.5,
    1.15,
    "Detected Allergen Evidence",
    "Evidence produced by P-HAF-KG V2.1\n"
    "and complementary prediction signals"
)


# ------------------------------------------------------------
# 8. CONFIRMED PATH
# ------------------------------------------------------------

add_box(
    0.75,
    4.95,
    3.6,
    1.35,
    "Confirmed User-Relevant Allergen",
    "Confirmed evidence matches\n"
    "the selected user allergy"
)


add_box(
    0.75,
    2.55,
    3.6,
    1.35,
    "NOT SUITABLE",
    "Confirmed allergen evidence\n"
    "detected for the user"
)


# ------------------------------------------------------------
# 9. POTENTIAL PATH
# ------------------------------------------------------------

add_box(
    4.7,
    4.95,
    3.6,
    1.35,
    "Potential Evidence",
    "Precautionary or uncertain\n"
    "allergen evidence"
)


add_box(
    4.7,
    2.55,
    3.6,
    1.35,
    "POTENTIAL RISK",
    "Further checking is appropriate"
)


# ------------------------------------------------------------
# 10. REVIEW PATH
# ------------------------------------------------------------

add_box(
    8.65,
    4.95,
    3.6,
    1.35,
    "SVM-Only / Ambiguous Candidate",
    "Machine-learning candidate without\n"
    "equivalent confirmed KG evidence"
)


add_box(
    8.65,
    2.55,
    3.6,
    1.35,
    "REVIEW RECOMMENDED",
    "Candidate requires further\n"
    "verification"
)


# ------------------------------------------------------------
# 11. ARROW FUNCTION
# ------------------------------------------------------------

def add_arrow(
    start,
    end,
    label=None
):

    arrow = FancyArrowPatch(
        start,
        end,
        arrowstyle="->",
        mutation_scale=18,
        linewidth=1.6
    )

    ax.add_patch(arrow)

    if label:

        x = (
            start[0] + end[0]
        ) / 2

        y = (
            start[1] + end[1]
        ) / 2

        ax.text(
            x,
            y + 0.18,
            label,
            ha="center",
            va="center",
            fontsize=9
        )


# ------------------------------------------------------------
# 12. INPUT → THREE EVIDENCE STATES
# ------------------------------------------------------------

add_arrow(
    (5.1, 7.55),
    (2.55, 6.30),
    "confirmed"
)


add_arrow(
    (6.5, 7.55),
    (6.5, 6.30),
    "potential"
)


add_arrow(
    (7.9, 7.55),
    (10.45, 6.30),
    "SVM-only / ambiguous"
)


# ------------------------------------------------------------
# 13. EVIDENCE STATES → OUTCOMES
# ------------------------------------------------------------

add_arrow(
    (2.55, 4.95),
    (2.55, 3.90)
)


add_arrow(
    (6.5, 4.95),
    (6.5, 3.90)
)


add_arrow(
    (10.45, 4.95),
    (10.45, 3.90)
)


# ------------------------------------------------------------
# 14. KEY PRINCIPLE
# ------------------------------------------------------------

ax.text(
    6.5,
    1.30,
    "The application does not treat all predictions as equivalent.",
    ha="center",
    va="center",
    fontsize=11,
    fontweight="bold"
)


ax.text(
    6.5,
    0.78,
    "Confirmed evidence → NOT SUITABLE   |   "
    "Potential evidence → POTENTIAL RISK   |   "
    "SVM-only / ambiguous → REVIEW RECOMMENDED",
    ha="center",
    va="center",
    fontsize=9
)


# ------------------------------------------------------------
# 15. SAVE
# ------------------------------------------------------------

fig.tight_layout()

fig.savefig(
    OUTPUT_FILE,
    dpi=300,
    bbox_inches="tight"
)

plt.close(fig)


# ------------------------------------------------------------
# 16. VERIFY
# ------------------------------------------------------------

print("\nSUCCESS")
print("=" * 75)

print(
    "Figure 5.8 application decision outcomes generated."
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