from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch


# ============================================================
# FIGURE 2.5
# P-HAF-KG V2.1 Confirmed vs Potential Evidence
#
# Based on the actual end-to-end examples documented in the
# dissertation:
#
# Test 1:
# wheat flour, milk powder, soy lecithin
# Selected allergy: milk
# Expected: NOT SUITABLE
#
# Test 2:
# wheat flour.
# May contain traces of milk and soy.
# Selected allergy: milk
# Expected: POTENTIAL RISK
# ============================================================


PROJECT_ROOT = Path(__file__).resolve().parents[1]

OUTPUT_DIR = PROJECT_ROOT / "figures"

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)

OUTPUT_FILE = (
    OUTPUT_DIR
    / "figure_2_5_confirmed_vs_potential_evidence.png"
)


# ------------------------------------------------------------
# FIGURE
# ------------------------------------------------------------

fig, ax = plt.subplots(
    figsize=(15, 9)
)

ax.set_xlim(0, 15)
ax.set_ylim(0, 10)

ax.axis("off")


# ------------------------------------------------------------
# TITLE
# ------------------------------------------------------------

ax.text(
    7.5,
    9.5,
    "P-HAF-KG V2.1: Confirmed vs Potential Allergen Evidence",
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


# ============================================================
# LEFT: DIRECT / CONFIRMED PATH
# ============================================================

add_box(
    0.6,
    6.2,
    3.4,
    1.7,
    "Ingredient Text",
    "wheat flour,\nmilk powder,\nsoy lecithin"
)

add_box(
    4.5,
    6.2,
    3.4,
    1.7,
    "Evidence Match",
    "milk powder\n→ milk allergen"
)

add_box(
    8.4,
    6.2,
    2.5,
    1.7,
    "Evidence State",
    "CONFIRMED"
)

add_box(
    11.5,
    6.0,
    2.8,
    2.1,
    "Decision",
    "NOT SUITABLE\n\n"
    "Confirmed milk\nevidence detected"
)


# ------------------------------------------------------------
# DIRECT PATH ARROWS
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


add_arrow(
    (4.0, 7.05),
    (4.5, 7.05)
)

add_arrow(
    (7.9, 7.05),
    (8.4, 7.05)
)

add_arrow(
    (10.9, 7.05),
    (11.5, 7.05)
)


# ============================================================
# RIGHT / LOWER: PRECAUTIONARY PATH
# ============================================================

add_box(
    0.6,
    2.1,
    3.4,
    1.8,
    "Ingredient / Label Text",
    "wheat flour.\n"
    "May contain traces\n"
    "of milk and soy."
)

add_box(
    4.5,
    2.1,
    3.4,
    1.8,
    "Precautionary Evidence",
    "milk appears in\n"
    "precautionary context"
)

add_box(
    8.4,
    2.1,
    2.5,
    1.8,
    "Evidence State",
    "POTENTIAL"
)

add_box(
    11.5,
    1.9,
    2.8,
    2.2,
    "Decision",
    "POTENTIAL RISK\n\n"
    "Precautionary milk\nevidence detected"
)


# ------------------------------------------------------------
# PRECAUTIONARY ARROWS
# ------------------------------------------------------------

add_arrow(
    (4.0, 3.0),
    (4.5, 3.0)
)

add_arrow(
    (7.9, 3.0),
    (8.4, 3.0)
)

add_arrow(
    (10.9, 3.0),
    (11.5, 3.0)
)


# ------------------------------------------------------------
# CENTRAL PRINCIPLE
# ------------------------------------------------------------

ax.text(
    7.5,
    4.9,
    "Key contribution:",
    ha="center",
    va="center",
    fontsize=11,
    fontweight="bold"
)

ax.text(
    7.5,
    4.45,
    "The system distinguishes the strength and context of allergen evidence",
    ha="center",
    va="center",
    fontsize=10
)

ax.text(
    7.5,
    4.0,
    "rather than converting every lexical match directly into a confirmed allergen.",
    ha="center",
    va="center",
    fontsize=9
)


# ------------------------------------------------------------
# FOOTNOTE
# ------------------------------------------------------------

ax.text(
    7.5,
    0.65,
    "Direct ingredient evidence produces a confirmed state; "
    "precautionary wording produces a potential state.",
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
    "Figure 2.5 confirmed-vs-potential evidence generated."
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