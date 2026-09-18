from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch


# ============================================================
# FIGURE 2.2
# Proposed P-HAF-KG V2.1 Evidence-Aware Output
#
# Concrete example from the dissertation:
#
# Ingredient text:
# wheat flour, milk powder, soy lecithin
#
# Selected allergy:
# milk
#
# Expected outcome:
# NOT SUITABLE
#
# Reason:
# Confirmed milk evidence detected.
# ============================================================


# ------------------------------------------------------------
# 1. PROJECT ROOT
# ------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[1]

OUTPUT_DIR = PROJECT_ROOT / "figures"

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)

OUTPUT_FILE = (
    OUTPUT_DIR
    / "figure_2_2_proposed_model_evidence_output.png"
)


# ------------------------------------------------------------
# 2. FIGURE
# ------------------------------------------------------------

fig, ax = plt.subplots(
    figsize=(15, 9)
)

ax.set_xlim(0, 15)
ax.set_ylim(0, 10)

ax.axis("off")


# ------------------------------------------------------------
# 3. TITLE
# ------------------------------------------------------------

ax.text(
    7.5,
    9.55,
    "P-HAF-KG V2.1 Evidence-Aware Allergen Analysis",
    ha="center",
    va="center",
    fontsize=18,
    fontweight="bold"
)


# ------------------------------------------------------------
# 4. BOX FUNCTION
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
        linewidth=1.6
    )

    ax.add_patch(box)

    ax.text(
        x + width / 2,
        y + height * 0.72,
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
        fontsize=9
    )


# ------------------------------------------------------------
# 5. INPUT
# ------------------------------------------------------------

add_box(
    0.6,
    6.2,
    3.1,
    1.8,
    "Ingredient Input",
    "wheat flour\n"
    "milk powder\n"
    "soy lecithin"
)


# ------------------------------------------------------------
# 6. NORMALISATION
# ------------------------------------------------------------

add_box(
    4.15,
    6.2,
    3.1,
    1.8,
    "Text Normalisation",
    "Standardise case\n"
    "Spacing / punctuation\n"
    "Ingredient terminology"
)


# ------------------------------------------------------------
# 7. KNOWLEDGE MATCHING
# ------------------------------------------------------------

add_box(
    7.7,
    6.2,
    3.1,
    1.8,
    "Ingredient–Allergen\nRelationship Matching",
    "milk powder → milk\n"
    "wheat flour → wheat/gluten\n"
    "soy lecithin → soy"
)


# ------------------------------------------------------------
# 8. EVIDENCE REASONING
# ------------------------------------------------------------

add_box(
    11.25,
    6.2,
    3.1,
    1.8,
    "Evidence State",
    "Direct ingredient evidence\n"
    "→ CONFIRMED"
)


# ------------------------------------------------------------
# 9. USER PROFILE
# ------------------------------------------------------------

add_box(
    2.3,
    2.7,
    3.5,
    1.8,
    "Selected Allergy Profile",
    "User-selected allergy:\n"
    "MILK"
)


# ------------------------------------------------------------
# 10. MATCH
# ------------------------------------------------------------

add_box(
    6.35,
    2.7,
    3.5,
    1.8,
    "Personalised Matching",
    "Confirmed allergen:\n"
    "MILK\n\n"
    "User profile match = YES"
)


# ------------------------------------------------------------
# 11. FINAL DECISION
# ------------------------------------------------------------

add_box(
    10.4,
    2.45,
    3.7,
    2.3,
    "FINAL DECISION",
    "NOT SUITABLE\n\n"
    "Reason:\n"
    "Confirmed milk evidence detected."
)


# ------------------------------------------------------------
# 12. ARROW FUNCTION
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
# 13. TOP PIPELINE
# ------------------------------------------------------------

add_arrow(
    (3.7, 7.1),
    (4.15, 7.1)
)

add_arrow(
    (7.25, 7.1),
    (7.7, 7.1)
)

add_arrow(
    (10.8, 7.1),
    (11.25, 7.1)
)


# ------------------------------------------------------------
# 14. EVIDENCE TO PERSONALISATION
# ------------------------------------------------------------

add_arrow(
    (12.8, 6.2),
    (12.0, 4.75)
)


# ------------------------------------------------------------
# 15. USER PROFILE TO MATCHING
# ------------------------------------------------------------

add_arrow(
    (5.8, 3.6),
    (6.35, 3.6)
)


# ------------------------------------------------------------
# 16. MATCHING TO DECISION
# ------------------------------------------------------------

add_arrow(
    (9.85, 3.6),
    (10.4, 3.6)
)


# ------------------------------------------------------------
# 17. EVIDENCE EXPLANATION
# ------------------------------------------------------------

ax.text(
    7.5,
    5.15,
    "Evidence-aware reasoning preserves WHY the allergen was detected",
    ha="center",
    va="center",
    fontsize=10,
    style="italic"
)


# ------------------------------------------------------------
# 18. CONFIRMED-EVIDENCE NOTE
# ------------------------------------------------------------

ax.text(
    12.8,
    8.55,
    "Direct ingredient evidence",
    ha="center",
    va="center",
    fontsize=9,
    fontweight="bold"
)

ax.text(
    12.8,
    8.2,
    "milk powder → milk",
    ha="center",
    va="center",
    fontsize=9
)


# ------------------------------------------------------------
# 19. SCOPE NOTE
# ------------------------------------------------------------

ax.text(
    7.5,
    0.8,
    "Illustrative evidence-aware decision pathway from the implemented model.",
    ha="center",
    va="center",
    fontsize=9
)


# ------------------------------------------------------------
# 20. SAVE
# ------------------------------------------------------------

fig.tight_layout()

fig.savefig(
    OUTPUT_FILE,
    dpi=300,
    bbox_inches="tight"
)

plt.close(fig)


# ------------------------------------------------------------
# 21. VERIFY
# ------------------------------------------------------------

print("\nSUCCESS")
print("=" * 75)

print(
    "Figure 2.2 proposed-model evidence output generated."
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