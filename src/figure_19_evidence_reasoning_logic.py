from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch


# ============================================================
# FIGURE 5.18
# P-HAF-KG V2.1 Evidence-State Reasoning Logic
#
# Conceptual representation of the implemented reasoning:
#
# Ingredient text
#      ↓
# Evidence segmentation
#      ↓
# Relationship matching
#      ↓
# ┌───────────────┬─────────────────┐
# │ Direct match  │ Precautionary   │
# │               │ match           │
# └───────────────┴─────────────────┘
#      ↓                  ↓
# Confirmed            Potential
#      └──────────┬───────────┘
#                 ↓
#       Context / exclusion rules
#                 ↓
#       Final evidence-aware state
#
# Confirmed evidence takes precedence over potential evidence.
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
    / "figure_5_18_evidence_reasoning_logic.png"
)


# ------------------------------------------------------------
# 3. FIGURE
# ------------------------------------------------------------

fig, ax = plt.subplots(
    figsize=(14, 10)
)

ax.set_xlim(0, 14)
ax.set_ylim(0, 12)

ax.axis("off")


# ------------------------------------------------------------
# 4. TITLE
# ------------------------------------------------------------

ax.text(
    7,
    11.45,
    "P-HAF-KG V2.1 Evidence-State Reasoning Logic",
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
# 6. MAIN BOXES
# ------------------------------------------------------------

add_box(
    4.75,
    9.35,
    4.5,
    1.2,
    "Ingredient Text",
    "Normalised ingredient / label text"
)


add_box(
    4.75,
    7.55,
    4.5,
    1.2,
    "Evidence Segmentation",
    "Direct ingredient evidence\nPrecautionary statements"
)


add_box(
    4.75,
    5.75,
    4.5,
    1.2,
    "Knowledge-Base Matching",
    "Ingredient–allergen relationships\nBoundary-safe term matching"
)


# ------------------------------------------------------------
# 7. EVIDENCE BOXES
# ------------------------------------------------------------

add_box(
    0.9,
    3.55,
    4.2,
    1.35,
    "Direct Evidence",
    "Explicit allergen ingredient\n→ Confirmed evidence"
)


add_box(
    8.9,
    3.55,
    4.2,
    1.35,
    "Precautionary Evidence",
    "May contain / traces / shared facility\n→ Potential evidence"
)


# ------------------------------------------------------------
# 8. CONTEXT RULES
# ------------------------------------------------------------

add_box(
    4.75,
    1.55,
    4.5,
    1.25,
    "Context and Exclusion Rules",
    "Phrase exclusions\nPlant-milk context\nMultilingual precautionary cues"
)


# ------------------------------------------------------------
# 9. FINAL STATE
# ------------------------------------------------------------

add_box(
    4.25,
    -0.15,
    5.5,
    1.25,
    "Final Evidence-Aware Allergen State",
    "Confirmed / Potential / No retained evidence"
)


# ------------------------------------------------------------
# 10. ARROW FUNCTION
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
        linewidth=1.5
    )

    ax.add_patch(arrow)


# ------------------------------------------------------------
# 11. MAIN FLOW
# ------------------------------------------------------------

add_arrow(
    (7.0, 9.35),
    (7.0, 8.75)
)


add_arrow(
    (7.0, 7.55),
    (7.0, 6.95)
)


# ------------------------------------------------------------
# 12. MATCHING TO DIRECT EVIDENCE
# ------------------------------------------------------------

add_arrow(
    (5.65, 5.75),
    (3.0, 4.90)
)


# ------------------------------------------------------------
# 13. MATCHING TO PRECAUTIONARY EVIDENCE
# ------------------------------------------------------------

add_arrow(
    (8.35, 5.75),
    (11.0, 4.90)
)


# ------------------------------------------------------------
# 14. EVIDENCE STATES TO CONTEXT RULES
# ------------------------------------------------------------

add_arrow(
    (3.0, 3.55),
    (5.85, 2.80)
)


add_arrow(
    (11.0, 3.55),
    (8.15, 2.80)
)


# ------------------------------------------------------------
# 15. CONTEXT TO FINAL STATE
# ------------------------------------------------------------

add_arrow(
    (7.0, 1.55),
    (7.0, 1.10)
)


# ------------------------------------------------------------
# 16. PRIORITY RULE
# ------------------------------------------------------------

ax.text(
    7,
    5.05,
    "Evidence priority: confirmed evidence overrides potential evidence",
    ha="center",
    va="center",
    fontsize=10,
    style="italic"
)


# ------------------------------------------------------------
# 17. OUTPUT NOTE
# ------------------------------------------------------------

ax.text(
    7,
    -0.85,
    "The final state is used by the downstream personalised food-decision layer.",
    ha="center",
    va="center",
    fontsize=9
)


# ------------------------------------------------------------
# 18. SAVE
# ------------------------------------------------------------

fig.tight_layout()

fig.savefig(
    OUTPUT_FILE,
    dpi=300,
    bbox_inches="tight"
)

plt.close(fig)


# ------------------------------------------------------------
# 19. VERIFY
# ------------------------------------------------------------

print("\nSUCCESS")
print("=" * 75)

print(
    "Figure 5.18 evidence-state reasoning logic generated."
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