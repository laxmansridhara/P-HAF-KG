import csv
import re
import tkinter as tk
from pathlib import Path
from tkinter import ttk, messagebox

# ============================================================
# FILES
# ============================================================

ORIGINAL_INPUT_FILE = Path(
    "data/processed/ml/gold_test/gold_test_annotation.csv"
)

OUTPUT_FILE = Path(
    "data/processed/ml/gold_test/gold_test_annotation_completed.csv"
)

# We use the completed file for resume functionality.
INPUT_FILE = OUTPUT_FILE if OUTPUT_FILE.exists() else ORIGINAL_INPUT_FILE

csv.field_size_limit(10_000_000)


# ============================================================
# ALLERGENS
# ============================================================

ALLERGENS = [
    "celery",
    "crustaceans",
    "egg",
    "fish",
    "lupin",
    "milk",
    "molluscs",
    "mustard",
    "peanut",
    "sesame",
    "soy",
    "tree_nut",
    "wheat_gluten",
]


EVIDENCE_LEVELS = [
    "direct",
    "precautionary",
    "mixed",
    "none",
    "ambiguous",
]


# ============================================================
# DIRECT ALLERGEN PATTERNS
# ============================================================

DIRECT_PATTERNS = {

    "celery": [
        r"\bcelery\b",
        r"\bceleriac\b",
        r"\bsellerie\b",
        r"\bceleri\b",
    ],

    "crustaceans": [
        r"\bcrustacean(s)?\b",
        r"\bshrimp(s)?\b",
        r"\bprawn(s)?\b",
        r"\bcrab(s)?\b",
        r"\blobster(s)?\b",
        r"\bkrill\b",
        r"\bcrustacé",
    ],

    "egg": [
        r"\begg(s)?\b",
        r"\begg white\b",
        r"\bovalbumin\b",
        r"\balbumen\b",
        r"\boeuf\b",
        r"\boeufs\b",
    ],

    "fish": [
        r"\bfish\b",
        r"\bancho(vy|vies)\b",
        r"\bcod\b",
        r"\bsalmon\b",
        r"\btuna\b",
        r"\btrout\b",
        r"\bsardine(s)?\b",
        r"\bpoisson\b",
    ],

    "lupin": [
        r"\blupin\b",
        r"\blupine\b",
        r"\blupinen\b",
    ],

    "milk": [
        r"\bmilk\b",
        r"\bmilk powder\b",
        r"\bwhey\b",
        r"\bcasein\b",
        r"\bcaseinate\b",
        r"\blactose\b",
        r"\bbutter\b",
        r"\bcream\b",
        r"\bcheese\b",
        r"\byogurt\b",
        r"\byoghurt\b",
        r"\blait\b",
        r"\bleite\b",
        r"\bmilch\b",
    ],

    "molluscs": [
        r"\bmollusc(s)?\b",
        r"\boctopus\b",
        r"\bsquid\b",
        r"\bcalamari\b",
        r"\bmussel(s)?\b",
        r"\boyster(s)?\b",
        r"\bclam(s)?\b",
        r"\bmollusque\b",
    ],

    "mustard": [
        r"\bmustard\b",
        r"\bmustard seed\b",
        r"\bmoutarde\b",
        r"\bsenf\b",
        r"\bmosterd\b",
    ],

    "peanut": [
        r"\bpeanut(s)?\b",
        r"\bgroundnut(s)?\b",
        r"\barachide(s)?\b",
        r"\berdnuss\b",
    ],

    "sesame": [
        r"\bsesame\b",
        r"\bsesame seed(s)?\b",
        r"\bsésame\b",
        r"\bsesam\b",
    ],

    "soy": [
        r"\bsoy\b",
        r"\bsoya\b",
        r"\bsoybean(s)?\b",
        r"\bsoya bean(s)?\b",
        r"\bsoy lecithin\b",
        r"\bsoja\b",
    ],

    "tree_nut": [
        r"\balmond(s)?\b",
        r"\bhazelnut(s)?\b",
        r"\bwalnut(s)?\b",
        r"\bcashew(s)?\b",
        r"\bpistachio(s)?\b",
        r"\bpecan(s)?\b",
        r"\bmacadamia\b",
        r"\bbrazil nut(s)?\b",
        r"\bchestnut(s)?\b",
        r"\bfruits? à coque\b",
        r"\bfruits? a coque\b",
        r"\bnoix\b",
        r"\bnüsse\b",
    ],

    "wheat_gluten": [
        r"\bwheat\b",
        r"\bgluten\b",
        r"\bwheat flour\b",
        r"\bbarley\b",
        r"\brye\b",
        r"\bspelt\b",
        r"\bmalt(ed)?\b",
        r"\bsemolina\b",
        r"\bbl[eé]\b",
        r"\borge\b",
        r"\bseigle\b",
        r"\bweizen\b",
        r"\bgerste\b",
        r"\broggen\b",
    ],
}


# ============================================================
# PRECAUTIONARY MARKERS
# ============================================================

PRECAUTIONARY_MARKERS = [
    r"\bmay contain\b",
    r"\bmay contain traces?\b",
    r"\btraces? of\b",
    r"\bcan contain\b",
    r"\bcontains? traces?\b",
    r"\bpeut contenir\b",
    r"\btraces? de\b",
    r"\bfabriqué dans un atelier utilisant\b",
    r"\bfabrique dans un atelier utilisant\b",
    r"\bspuren von\b",
    r"\bkann spuren von\b",
    r"\btraces may be present\b",
]


# ============================================================
# TEXT HELPERS
# ============================================================

def norm(text):
    return re.sub(r"\s+", " ", (text or "").lower()).strip()


def has_precautionary_marker(text):
    t = norm(text)
    return any(
        re.search(pattern, t, re.I)
        for pattern in PRECAUTIONARY_MARKERS
    )


def suggest(text):
    """
    Rule-assisted annotation helper.

    0 = no suggestion
    1 = direct evidence
    2 = precautionary evidence
    """

    t = norm(text)

    out = {
        allergen: 0
        for allergen in ALLERGENS
    }

    reasons = {
        allergen: []
        for allergen in ALLERGENS
    }

    for allergen, patterns in DIRECT_PATTERNS.items():

        for pattern in patterns:

            for match in re.finditer(pattern, t, re.I):

                start = max(0, match.start() - 100)
                end = min(len(t), match.end() + 100)

                window = t[start:end]

                precautionary = any(
                    re.search(marker, window, re.I)
                    for marker in PRECAUTIONARY_MARKERS
                )

                value = 2 if precautionary else 1

                if value > out[allergen]:
                    out[allergen] = value

                reasons[allergen].append(
                    match.group(0)
                )

    return out, reasons


def split_labels(s):
    return {
        x.strip()
        for x in (s or "").split(";")
        if x.strip()
    }


# ============================================================
# SAVE
# ============================================================

def save_rows(rows):

    fields = [
        "gold_id",
        "product_code",
        "product_name",
        "ingredient_text",
        "gold_confirmed_allergens",
        "gold_potential_allergens",
        "gold_evidence_level",
        "review_notes",
        "reviewer",
        "review_status",
    ]

    with OUTPUT_FILE.open(
        "w",
        encoding="utf-8",
        newline=""
    ) as f:

        writer = csv.DictWriter(
            f,
            fieldnames=fields
        )

        writer.writeheader()
        writer.writerows(rows)


# ============================================================
# APPLICATION
# ============================================================

class App:

    def __init__(self, root):

        self.root = root

        self.root.title(
            "P-HAF-KG V2.1 — Gold Annotation"
        )

        self.root.geometry(
            "1450x900"
        )

        self.root.minsize(
            1100,
            700
        )

        # ----------------------------------------------------
        # LOAD DATA
        # ----------------------------------------------------

        self.rows = self.load_rows()

        # ----------------------------------------------------
        # RESUME FROM FIRST UNREVIEWED PRODUCT
        # ----------------------------------------------------

        reviewed_indices = [
            idx
            for idx, row in enumerate(self.rows)
            if (
                (row.get("review_status", "") or "")
                .strip()
                .lower()
                == "reviewed"
            )
        ]

        unfinished_indices = [
            idx
            for idx in range(len(self.rows))
            if idx not in reviewed_indices
        ]

        if unfinished_indices:

            self.i = unfinished_indices[0]

        else:

            self.i = 0

        # ----------------------------------------------------
        # VARIABLES
        # ----------------------------------------------------

        self.vars = {
            allergen: tk.IntVar(value=0)
            for allergen in ALLERGENS
        }

        self.evidence = tk.StringVar(
            value=""
        )

        self.reviewer = tk.StringVar(
            value=""
        )

        self.status = tk.StringVar(
            value="not_started"
        )

        self.progress = tk.StringVar(
            value=""
        )

        self.info_var = tk.StringVar(
            value=""
        )

        self.reason_labels = {}

        # ----------------------------------------------------
        # BUILD UI
        # ----------------------------------------------------

        self.build()

        # ----------------------------------------------------
        # LOAD FIRST UNFINISHED PRODUCT
        # ----------------------------------------------------

        self.load(self.i)

    # ========================================================
    # LOAD ROWS
    # ========================================================

    def load_rows(self):

        # Prefer completed file if it exists.
        if OUTPUT_FILE.exists():

            path = OUTPUT_FILE

        elif ORIGINAL_INPUT_FILE.exists():

            path = ORIGINAL_INPUT_FILE

        else:

            raise FileNotFoundError(
                "Neither the original nor completed annotation file exists:\n"
                f"{ORIGINAL_INPUT_FILE}\n"
                f"{OUTPUT_FILE}"
            )

        with path.open(
            "r",
            encoding="utf-8",
            newline=""
        ) as f:

            rows = list(
                csv.DictReader(f)
            )

        # Make sure expected columns exist.
        expected_fields = [
            "gold_id",
            "product_code",
            "product_name",
            "ingredient_text",
            "gold_confirmed_allergens",
            "gold_potential_allergens",
            "gold_evidence_level",
            "review_notes",
            "reviewer",
            "review_status",
        ]

        for row in rows:

            for field in expected_fields:

                if field not in row:
                    row[field] = ""

        return rows

    # ========================================================
    # BUILD UI
    # ========================================================

    def build(self):

        outer = ttk.Frame(
            self.root,
            padding=10
        )

        outer.pack(
            fill="both",
            expand=True
        )

        # ----------------------------------------------------
        # TOP BAR
        # ----------------------------------------------------

        top = ttk.Frame(
            outer
        )

        top.pack(
            fill="x",
            pady=(0, 8)
        )

        ttk.Label(
            top,
            text="P-HAF-KG V2.1 — Gold Annotation",
            font=("Arial", 18, "bold")
        ).pack(
            side="left"
        )

        ttk.Label(
            top,
            textvariable=self.progress,
            font=("Arial", 12, "bold")
        ).pack(
            side="right"
        )

        # ----------------------------------------------------
        # INFO BAR
        # ----------------------------------------------------

        info_frame = ttk.Frame(
            outer
        )

        info_frame.pack(
            fill="x",
            pady=(0, 8)
        )

        ttk.Label(
            info_frame,
            textvariable=self.info_var,
            font=("Arial", 11)
        ).pack(
            side="left"
        )

        # ----------------------------------------------------
        # MAIN PANED AREA
        # ----------------------------------------------------

        paned = ttk.PanedWindow(
            outer,
            orient=tk.HORIZONTAL
        )

        paned.pack(
            fill="both",
            expand=True
        )

        # ====================================================
        # LEFT SIDE — PRODUCT
        # ====================================================

        left = ttk.Frame(
            paned,
            padding=8
        )

        paned.add(
            left,
            weight=2
        )

        ttk.Label(
            left,
            text="Product",
            font=("Arial", 14, "bold")
        ).pack(
            anchor="w",
            pady=(0, 5)
        )

        self.product_name_label = ttk.Label(
            left,
            text="",
            font=("Arial", 14, "bold"),
            wraplength=600
        )

        self.product_name_label.pack(
            anchor="w",
            fill="x",
            pady=(0, 10)
        )

        ttk.Label(
            left,
            text="Product code:",
            font=("Arial", 10, "bold")
        ).pack(
            anchor="w"
        )

        self.product_code_label = ttk.Label(
            left,
            text="",
            wraplength=600
        )

        self.product_code_label.pack(
            anchor="w",
            pady=(0, 10)
        )

        ttk.Label(
            left,
            text="Ingredient text",
            font=("Arial", 12, "bold")
        ).pack(
            anchor="w"
        )

        ingredient_frame = ttk.Frame(
            left
        )

        ingredient_frame.pack(
            fill="both",
            expand=True,
            pady=(5, 0)
        )

        self.ingredient_text = tk.Text(
            ingredient_frame,
            wrap="word",
            font=("Arial", 11),
            height=25
        )

        self.ingredient_text.pack(
            side="left",
            fill="both",
            expand=True
        )

        ingredient_scroll = ttk.Scrollbar(
            ingredient_frame,
            orient="vertical",
            command=self.ingredient_text.yview
        )

        ingredient_scroll.pack(
            side="right",
            fill="y"
        )

        self.ingredient_text.configure(
            yscrollcommand=ingredient_scroll.set
        )

        # ====================================================
        # RIGHT SIDE — ANNOTATION
        # ====================================================

        right = ttk.Frame(
            paned,
            padding=8
        )

        paned.add(
            right,
            weight=1
        )

        ttk.Label(
            right,
            text="Allergen Annotation",
            font=("Arial", 14, "bold")
        ).pack(
            anchor="w",
            pady=(0, 5)
        )

        ttk.Label(
            right,
            text="0 = No evidence    1 = Confirmed/direct    2 = Potential/precautionary",
            font=("Arial", 10, "bold")
        ).pack(
            anchor="w",
            pady=(0, 10)
        )

        # ----------------------------------------------------
        # ALLERGEN SCROLL AREA
        # ----------------------------------------------------

        canvas_frame = ttk.Frame(
            right
        )

        canvas_frame.pack(
            fill="both",
            expand=True
        )

        canvas = tk.Canvas(
            canvas_frame,
            highlightthickness=0
        )

        scrollbar = ttk.Scrollbar(
            canvas_frame,
            orient="vertical",
            command=canvas.yview
        )

        allergen_frame = ttk.Frame(
            canvas
        )

        allergen_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.create_window(
            (0, 0),
            window=allergen_frame,
            anchor="nw"
        )

        canvas.configure(
            yscrollcommand=scrollbar.set
        )

        canvas.pack(
            side="left",
            fill="both",
            expand=True
        )

        scrollbar.pack(
            side="right",
            fill="y"
        )

        # ----------------------------------------------------
        # ALLERGEN ROWS
        # ----------------------------------------------------

        for row_index, allergen in enumerate(ALLERGENS):

            row = ttk.Frame(
                allergen_frame
            )

            row.grid(
                row=row_index,
                column=0,
                sticky="ew",
                pady=3
            )

            row.columnconfigure(
                1,
                weight=1
            )

            ttk.Label(
                row,
                text=allergen,
                width=15,
                font=("Arial", 10, "bold")
            ).grid(
                row=0,
                column=0,
                sticky="w"
            )

            combo = ttk.Combobox(
                row,
                textvariable=self.vars[allergen],
                values=[0, 1, 2],
                state="readonly",
                width=6
            )

            combo.grid(
                row=0,
                column=1,
                sticky="w",
                padx=(5, 8)
            )

            reason_label = ttk.Label(
                row,
                text="no suggestion",
                wraplength=230
            )

            reason_label.grid(
                row=0,
                column=2,
                sticky="w"
            )

            self.reason_labels[allergen] = reason_label

        # ====================================================
        # EVIDENCE / REVIEWER / STATUS
        # ====================================================

        details = ttk.Frame(
            right
        )

        details.pack(
            fill="x",
            pady=(8, 5)
        )

        ttk.Label(
            details,
            text="Evidence:"
        ).grid(
            row=0,
            column=0,
            sticky="w",
            padx=(0, 5)
        )

        self.evidence_combo = ttk.Combobox(
            details,
            textvariable=self.evidence,
            values=EVIDENCE_LEVELS,
            state="readonly",
            width=16
        )

        self.evidence_combo.grid(
            row=0,
            column=1,
            sticky="w"
        )

        ttk.Label(
            details,
            text="Reviewer:"
        ).grid(
            row=1,
            column=0,
            sticky="w",
            pady=(6, 0)
        )

        ttk.Entry(
            details,
            textvariable=self.reviewer,
            width=20
        ).grid(
            row=1,
            column=1,
            sticky="w",
            pady=(6, 0)
        )

        ttk.Label(
            details,
            text="Status:"
        ).grid(
            row=2,
            column=0,
            sticky="w",
            pady=(6, 0)
        )

        self.status_combo = ttk.Combobox(
            details,
            textvariable=self.status,
            values=[
                "not_started",
                "reviewed"
            ],
            state="readonly",
            width=16
        )

        self.status_combo.grid(
            row=2,
            column=1,
            sticky="w",
            pady=(6, 0)
        )

        # ====================================================
        # NOTES
        # ====================================================

        ttk.Label(
            right,
            text="Review notes:"
        ).pack(
            anchor="w",
            pady=(5, 2)
        )

        self.notes = tk.Text(
            right,
            height=4,
            wrap="word"
        )

        self.notes.pack(
            fill="x",
            pady=(0, 8)
        )

        # ====================================================
        # BUTTON BAR
        # ====================================================

        buttons = ttk.Frame(
            right
        )

        buttons.pack(
            fill="x",
            pady=(0, 5)
        )

        ttk.Button(
            buttons,
            text="Previous",
            command=self.previous
        ).pack(
            side="left",
            padx=(0, 5)
        )

        ttk.Button(
            buttons,
            text="Save",
            command=self.save_current
        ).pack(
            side="left",
            padx=5
        )

        ttk.Button(
            buttons,
            text="Save & Next",
            command=self.save_next
        ).pack(
            side="left",
            padx=5
        )

        ttk.Button(
            buttons,
            text="Next",
            command=self.next
        ).pack(
            side="left",
            padx=5
        )

        ttk.Button(
            buttons,
            text="Exit",
            command=self.root.destroy
        ).pack(
            side="right"
        )

        # ----------------------------------------------------
        # KEYBOARD SHORTCUTS
        # ----------------------------------------------------

        self.root.bind(
            "<Control-s>",
            lambda event: self.save_current()
        )

        self.root.bind(
            "<Command-s>",
            lambda event: self.save_current()
        )

    # ========================================================
    # LOAD PRODUCT
    # ========================================================

    def load(self, i):

        if not self.rows:
            return

        i = max(
            0,
            min(i, len(self.rows) - 1)
        )

        self.i = i

        row = self.rows[i]

        # ----------------------------------------------------
        # PRODUCT INFORMATION
        # ----------------------------------------------------

        self.product_name_label.config(
            text=row.get("product_name", "") or "(No product name)"
        )

        self.product_code_label.config(
            text=row.get("product_code", "") or "(No product code)"
        )

        ingredient = (
            row.get("ingredient_text", "")
            or ""
        )

        self.ingredient_text.delete(
            "1.0",
            "end"
        )

        self.ingredient_text.insert(
            "1.0",
            ingredient
        )

        # ----------------------------------------------------
        # ASSISTED SUGGESTIONS
        # ----------------------------------------------------

        suggestions, reasons = suggest(
            ingredient
        )

        confirmed = split_labels(
            row.get(
                "gold_confirmed_allergens",
                ""
            )
        )

        potential = split_labels(
            row.get(
                "gold_potential_allergens",
                ""
            )
        )

        # ----------------------------------------------------
        # LOAD EXISTING ANNOTATIONS
        # ----------------------------------------------------

        for allergen in ALLERGENS:

            value = (
                1
                if allergen in confirmed
                else (
                    2
                    if allergen in potential
                    else 0
                )
            )

            self.vars[allergen].set(
                value
            )

            reason_text = ", ".join(
                dict.fromkeys(
                    reasons[allergen][:3]
                )
            )

            if suggestions[allergen] == 1:

                shown = (
                    f"suggested direct: {reason_text}"
                    if reason_text
                    else "suggested direct"
                )

            elif suggestions[allergen] == 2:

                shown = (
                    f"suggested potential: {reason_text}"
                    if reason_text
                    else "suggested potential"
                )

            else:

                shown = "no suggestion"

            self.reason_labels[allergen].config(
                text=shown[:45]
            )

        # ----------------------------------------------------
        # OTHER FIELDS
        # ----------------------------------------------------

        self.evidence.set(
            row.get(
                "gold_evidence_level",
                ""
            )
            or ""
        )

        self.reviewer.set(
            row.get(
                "reviewer",
                ""
            )
            or ""
        )

        self.status.set(
            row.get(
                "review_status",
                ""
            )
            or "not_started"
        )

        self.notes.delete(
            "1.0",
            "end"
        )

        self.notes.insert(
            "1.0",
            row.get(
                "review_notes",
                ""
            )
            or ""
        )

        # ----------------------------------------------------
        # PROGRESS
        # ----------------------------------------------------

        reviewed = sum(
            1
            for r in self.rows
            if (
                (r.get("review_status", "") or "")
                .strip()
                .lower()
                == "reviewed"
            )
        )

        self.progress.set(
            f"Product {i + 1} of {len(self.rows)}   |   Reviewed: {reviewed}"
        )

        gold_id = row.get(
            "gold_id",
            ""
        )

        if gold_id:

            self.info_var.set(
                f"{gold_id}"
            )

        else:

            self.info_var.set(
                f"Record {i + 1}"
            )

    # ========================================================
    # COLLECT CURRENT ANNOTATION
    # ========================================================

    def collect(self):

        confirmed = []
        potential = []

        for allergen in ALLERGENS:

            value = self.vars[allergen].get()

            if value == 1:

                confirmed.append(
                    allergen
                )

            elif value == 2:

                potential.append(
                    allergen
                )

        return (
            confirmed,
            potential,
            self.evidence.get().strip(),
            self.notes.get(
                "1.0",
                "end"
            ).strip(),
            self.reviewer.get().strip(),
            self.status.get().strip(),
        )

    # ========================================================
    # SAVE CURRENT
    # ========================================================

    def save_current(self):

        if not self.rows:
            return

        confirmed, potential, evidence, notes, reviewer, status = (
            self.collect()
        )

        row = self.rows[self.i]

        row["gold_confirmed_allergens"] = ";".join(
            confirmed
        )

        row["gold_potential_allergens"] = ";".join(
            potential
        )

        row["gold_evidence_level"] = evidence

        row["review_notes"] = notes

        row["reviewer"] = reviewer

        row["review_status"] = status

        save_rows(
            self.rows
        )

        # Update progress immediately.
        reviewed = sum(
            1
            for r in self.rows
            if (
                (r.get("review_status", "") or "")
                .strip()
                .lower()
                == "reviewed"
            )
        )

        self.progress.set(
            f"Product {self.i + 1} of {len(self.rows)}   |   Reviewed: {reviewed}"
        )

        self.info_var.set(
            f"{row.get('gold_id', '')} saved successfully."
        )

    # ========================================================
    # SAVE & NEXT
    # ========================================================

    def save_next(self):

        self.save_current()

        if self.i < len(self.rows) - 1:

            self.load(
                self.i + 1
            )

        else:

            messagebox.showinfo(
                "Complete",
                "All products have been reached."
            )

    # ========================================================
    # NEXT
    # ========================================================

    def next(self):

        if self.i < len(self.rows) - 1:

            self.load(
                self.i + 1
            )

    # ========================================================
    # PREVIOUS
    # ========================================================

    def previous(self):

        if self.i > 0:

            self.load(
                self.i - 1
            )


# ============================================================
# MAIN
# ============================================================

def main():

    root = tk.Tk()

    app = App(
        root
    )

    root.mainloop()


if __name__ == "__main__":
    main()