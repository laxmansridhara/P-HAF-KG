import csv
import tkinter as tk
from pathlib import Path
from tkinter import messagebox, ttk


# ============================================================
# P-HAF-KG V2.1
# GOLD TEST ANNOTATION APPLICATION
# ============================================================
#
# PURPOSE
# -------
# Manually annotate the independently selected 500-product
# gold-test candidate set.
#
# IMPORTANT
# ---------
# This application reads ONLY the blinded annotation CSV.
# It does NOT load:
# - SVM predictions
# - P-HAF-KG predictions
# - disagreement categories
#
# Therefore the annotation remains blinded.
# ============================================================


# ============================================================
# FILES
# ============================================================

INPUT_FILE = Path(
    "data/processed/ml/gold_test/"
    "gold_test_annotation.csv"
)

OUTPUT_FILE = Path(
    "data/processed/ml/gold_test/"
    "gold_test_annotation_completed.csv"
)


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


# ============================================================
# ANNOTATION VALUES
# ============================================================

ANNOTATION_VALUES = {
    0: "No evidence",
    1: "Confirmed / direct",
    2: "Potential / precautionary",
}


EVIDENCE_LEVELS = [
    "direct",
    "precautionary",
    "mixed",
    "none",
    "ambiguous",
]


# ============================================================
# CSV SAFETY
# ============================================================

csv.field_size_limit(10_000_000)


# ============================================================
# LOAD CSV
# ============================================================

def load_products(path):
    """
    Load the blinded annotation CSV.

    Returns
    -------
    list[dict]
        Product records.
    """

    if not path.exists():
        raise FileNotFoundError(
            f"Input file not found:\n{path}"
        )

    with path.open(
        "r",
        encoding="utf-8",
        newline=""
    ) as f:

        reader = csv.DictReader(f)

        required_columns = {
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
        }

        actual_columns = set(
            reader.fieldnames or []
        )

        missing = (
            required_columns -
            actual_columns
        )

        if missing:
            raise ValueError(
                "Missing required columns:\n"
                + "\n".join(
                    sorted(missing)
                )
            )

        products = list(reader)

    return products


# ============================================================
# SAVE CSV
# ============================================================

def save_products(path, products):
    """
    Save all annotation records.
    """

    fieldnames = [
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

    with path.open(
        "w",
        encoding="utf-8",
        newline=""
    ) as f:

        writer = csv.DictWriter(
            f,
            fieldnames=fieldnames
        )

        writer.writeheader()

        writer.writerows(products)


# ============================================================
# APPLICATION
# ============================================================

class GoldAnnotationApp:

    def __init__(self, root):

        self.root = root

        self.root.title(
            "P-HAF-KG V2.1 — Gold Test Annotation"
        )

        self.root.geometry(
            "1350x900"
        )

        self.root.minsize(
            1000,
            700
        )


        # ----------------------------------------------------
        # Load products
        # ----------------------------------------------------

        try:

            self.products = load_products(
                INPUT_FILE
            )

        except Exception as exc:

            messagebox.showerror(
                "Loading Error",
                str(exc)
            )

            self.root.destroy()

            return


        # ----------------------------------------------------
        # Application state
        # ----------------------------------------------------

        self.current_index = 0

        self.loading_record = False


        # ----------------------------------------------------
        # Tk variables
        # ----------------------------------------------------

        self.allergen_vars = {}

        for allergen in ALLERGENS:

            self.allergen_vars[
                allergen
            ] = tk.IntVar(
                value=0
            )


        self.evidence_level_var = (
            tk.StringVar(
                value=""
            )
        )


        self.reviewer_var = (
            tk.StringVar(
                value=""
            )
        )


        self.status_var = (
            tk.StringVar(
                value=""
            )
        )


        self.progress_var = (
            tk.StringVar(
                value=""
            )
        )


        self.product_info_var = (
            tk.StringVar(
                value=""
            )
        )


        # ----------------------------------------------------
        # Build interface
        # ----------------------------------------------------

        self.build_interface()

        self.load_record(
            0
        )


        # ----------------------------------------------------
        # Keyboard shortcuts
        # ----------------------------------------------------

        self.root.bind(
            "<Control-s>",
            lambda event:
                self.save_current()
        )

        self.root.bind(
            "<Command-s>",
            lambda event:
                self.save_current()
        )

        self.root.bind(
            "<Right>",
            lambda event:
                self.next_record()
        )

        self.root.bind(
            "<Left>",
            lambda event:
                self.previous_record()
        )


    # ========================================================
    # BUILD UI
    # ========================================================

    def build_interface(self):

        # ----------------------------------------------------
        # Main container
        # ----------------------------------------------------

        main = ttk.Frame(
            self.root,
            padding=15
        )

        main.pack(
            fill="both",
            expand=True
        )


        # ----------------------------------------------------
        # Header
        # ----------------------------------------------------

        header = ttk.Frame(
            main
        )

        header.pack(
            fill="x",
            pady=(0, 10)
        )


        title = ttk.Label(
            header,
            text=(
                "P-HAF-KG V2.1 — "
                "Gold Test Annotation"
            ),
            font=(
                "Arial",
                20,
                "bold"
            )
        )

        title.pack(
            side="left"
        )


        progress = ttk.Label(
            header,
            textvariable=self.progress_var,
            font=(
                "Arial",
                12,
                "bold"
            )
        )

        progress.pack(
            side="right"
        )


        # ----------------------------------------------------
        # Product information
        # ----------------------------------------------------

        info_frame = ttk.LabelFrame(
            main,
            text="Product Information",
            padding=10
        )

        info_frame.pack(
            fill="x",
            pady=(0, 10)
        )


        info = ttk.Label(
            info_frame,
            textvariable=self.product_info_var,
            font=(
                "Arial",
                12
            ),
            justify="left"
        )

        info.pack(
            fill="x"
        )


        # ----------------------------------------------------
        # Ingredient text
        # ----------------------------------------------------

        ingredient_frame = ttk.LabelFrame(
            main,
            text="Ingredient Text — Read This Carefully",
            padding=8
        )

        ingredient_frame.pack(
            fill="both",
            expand=True,
            pady=(0, 10)
        )


        text_container = ttk.Frame(
            ingredient_frame
        )

        text_container.pack(
            fill="both",
            expand=True
        )


        scrollbar = ttk.Scrollbar(
            text_container,
            orient="vertical"
        )

        scrollbar.pack(
            side="right",
            fill="y"
        )


        self.ingredient_text = tk.Text(
            text_container,
            wrap="word",
            font=(
                "Arial",
                12
            ),
            yscrollcommand=(
                scrollbar.set
            ),
            padx=10,
            pady=10
        )

        self.ingredient_text.pack(
            side="left",
            fill="both",
            expand=True
        )

        scrollbar.config(
            command=self.ingredient_text.yview
        )


        # ----------------------------------------------------
        # Allergen annotation
        # ----------------------------------------------------

        allergen_frame = ttk.LabelFrame(
            main,
            text=(
                "Allergen Annotation "
                "(0 = No evidence, "
                "1 = Confirmed, "
                "2 = Potential)"
            ),
            padding=10
        )

        allergen_frame.pack(
            fill="x",
            pady=(0, 10)
        )


        # Create four columns.
        for column in range(4):

            allergen_frame.columnconfigure(
                column,
                weight=1
            )


        for index, allergen in enumerate(
            ALLERGENS
        ):

            row = index // 4
            column = index % 4


            cell = ttk.Frame(
                allergen_frame
            )

            cell.grid(
                row=row,
                column=column,
                sticky="w",
                padx=10,
                pady=4
            )


            label = ttk.Label(
                cell,
                text=allergen,
                width=16
            )

            label.pack(
                side="left"
            )


            combo = ttk.Combobox(
                cell,
                textvariable=(
                    self.allergen_vars[
                        allergen
                    ]
                ),
                values=[
                    0,
                    1,
                    2
                ],
                state="readonly",
                width=5
            )

            combo.pack(
                side="left"
            )


        # ----------------------------------------------------
        # Evidence level
        # ----------------------------------------------------

        lower_frame = ttk.Frame(
            main
        )

        lower_frame.pack(
            fill="x",
            pady=(0, 10)
        )


        evidence_frame = ttk.LabelFrame(
            lower_frame,
            text="Evidence Level",
            padding=8
        )

        evidence_frame.pack(
            side="left",
            fill="x",
            expand=True,
            padx=(0, 5)
        )


        self.evidence_combo = ttk.Combobox(
            evidence_frame,
            textvariable=(
                self.evidence_level_var
            ),
            values=EVIDENCE_LEVELS,
            state="readonly",
            width=20
        )

        self.evidence_combo.pack(
            anchor="w"
        )


        reviewer_frame = ttk.LabelFrame(
            lower_frame,
            text="Reviewer",
            padding=8
        )

        reviewer_frame.pack(
            side="left",
            fill="x",
            expand=True,
            padx=(5, 0)
        )


        self.reviewer_entry = ttk.Entry(
            reviewer_frame,
            textvariable=(
                self.reviewer_var
            ),
            width=30
        )

        self.reviewer_entry.pack(
            anchor="w"
        )


        # ----------------------------------------------------
        # Notes
        # ----------------------------------------------------

        notes_frame = ttk.LabelFrame(
            main,
            text="Review Notes",
            padding=8
        )

        notes_frame.pack(
            fill="x",
            pady=(0, 10)
        )


        self.notes_entry = tk.Text(
            notes_frame,
            height=4,
            wrap="word",
            font=(
                "Arial",
                11
            )
        )

        self.notes_entry.pack(
            fill="x"
        )


        # ----------------------------------------------------
        # Status
        # ----------------------------------------------------

        status_frame = ttk.Frame(
            main
        )

        status_frame.pack(
            fill="x",
            pady=(0, 10)
        )


        status_label = ttk.Label(
            status_frame,
            text="Status:"
        )

        status_label.pack(
            side="left"
        )


        self.status_combo = ttk.Combobox(
            status_frame,
            textvariable=(
                self.status_var
            ),
            values=[
                "not_started",
                "reviewed"
            ],
            state="readonly",
            width=20
        )

        self.status_combo.pack(
            side="left",
            padx=10
        )


        # ----------------------------------------------------
        # Buttons
        # ----------------------------------------------------

        buttons = ttk.Frame(
            main
        )

        buttons.pack(
            fill="x"
        )


        self.previous_button = ttk.Button(
            buttons,
            text="← Previous",
            command=self.previous_record
        )

        self.previous_button.pack(
            side="left",
            padx=(0, 5)
        )


        self.save_button = ttk.Button(
            buttons,
            text="Save",
            command=self.save_current
        )

        self.save_button.pack(
            side="left",
            padx=5
        )


        self.next_button = ttk.Button(
            buttons,
            text="Save & Next →",
            command=self.save_and_next
        )

        self.next_button.pack(
            side="left",
            padx=5
        )


        self.jump_entry = ttk.Entry(
            buttons,
            width=12
        )

        self.jump_entry.pack(
            side="right",
            padx=5
        )


        self.jump_button = ttk.Button(
            buttons,
            text="Jump to GOLD ID",
            command=self.jump_to_id
        )

        self.jump_button.pack(
            side="right"
        )


        # ----------------------------------------------------
        # Instructions
        # ----------------------------------------------------

        instruction = ttk.Label(
            main,
            text=(
                "Read only the product and ingredient text. "
                "Do not use machine-generated predictions. "
                "Use Previous/Next to navigate. "
                "Progress is saved to the completed CSV."
            ),
            font=(
                "Arial",
                10
            )
        )

        instruction.pack(
            fill="x",
            pady=(10, 0)
        )


    # ========================================================
    # LOAD RECORD
    # ========================================================

    def load_record(
        self,
        index
    ):

        if not (
            0 <= index <
            len(self.products)
        ):

            return


        self.current_index = index

        record = self.products[
            index
        ]


        self.loading_record = True


        # ----------------------------------------------------
        # Product information
        # ----------------------------------------------------

        self.product_info_var.set(
            f"Gold ID: {record['gold_id']}\n"
            f"Product Code: {record['product_code']}\n"
            f"Product Name: "
            f"{record['product_name'] or '(blank)'}"
        )


        # ----------------------------------------------------
        # Ingredient text
        # ----------------------------------------------------

        self.ingredient_text.config(
            state="normal"
        )

        self.ingredient_text.delete(
            "1.0",
            "end"
        )

        self.ingredient_text.insert(
            "1.0",
            record[
                "ingredient_text"
            ]
        )

        self.ingredient_text.config(
            state="disabled"
        )

        self.ingredient_text.yview_moveto(
            0
        )


        # ----------------------------------------------------
        # Allergen values
        # ----------------------------------------------------

        confirmed = {
            x.strip()
            for x in (
                record[
                    "gold_confirmed_allergens"
                ] or ""
            ).split(";")
            if x.strip()
        }


        potential = {
            x.strip()
            for x in (
                record[
                    "gold_potential_allergens"
                ] or ""
            ).split(";")
            if x.strip()
        }


        for allergen in ALLERGENS:

            if allergen in confirmed:

                value = 1

            elif allergen in potential:

                value = 2

            else:

                value = 0


            self.allergen_vars[
                allergen
            ].set(value)


        # ----------------------------------------------------
        # Other fields
        # ----------------------------------------------------

        self.evidence_level_var.set(
            record[
                "gold_evidence_level"
            ] or ""
        )


        self.reviewer_var.set(
            record[
                "reviewer"
            ] or ""
        )


        self.status_var.set(
            record[
                "review_status"
            ]
            or "not_started"
        )


        self.notes_entry.delete(
            "1.0",
            "end"
        )

        self.notes_entry.insert(
            "1.0",
            record[
                "review_notes"
            ] or ""
        )


        # ----------------------------------------------------
        # Update progress
        # ----------------------------------------------------

        reviewed = sum(
            1
            for item in self.products
            if (
                item.get(
                    "review_status",
                    ""
                )
                == "reviewed"
            )
        )


        self.progress_var.set(
            f"Product {index + 1} "
            f"of {len(self.products)}   |   "
            f"Reviewed: {reviewed}"
        )


        # ----------------------------------------------------
        # Enable / disable navigation
        # ----------------------------------------------------

        if index == 0:

            self.previous_button.config(
                state="disabled"
            )

        else:

            self.previous_button.config(
                state="normal"
            )


        if index == (
            len(self.products) - 1
        ):

            self.next_button.config(
                text="Save"
            )

        else:

            self.next_button.config(
                text="Save & Next →"
            )


        self.loading_record = False


    # ========================================================
    # GET CURRENT ANNOTATION
    # ========================================================

    def collect_current_annotation(self):

        confirmed = []
        potential = []


        for allergen in ALLERGENS:

            value = self.allergen_vars[
                allergen
            ].get()


            if value == 1:

                confirmed.append(
                    allergen
                )

            elif value == 2:

                potential.append(
                    allergen
                )


        evidence_level = (
            self.evidence_level_var
            .get()
            .strip()
        )


        reviewer = (
            self.reviewer_var
            .get()
            .strip()
        )


        notes = (
            self.notes_entry
            .get(
                "1.0",
                "end"
            )
            .strip()
        )


        status = (
            self.status_var
            .get()
            .strip()
        )


        return (
            confirmed,
            potential,
            evidence_level,
            reviewer,
            notes,
            status,
        )


    # ========================================================
    # VALIDATE ANNOTATION
    # ========================================================

    def validate_annotation(
        self
    ):

        (
            confirmed,
            potential,
            evidence_level,
            reviewer,
            notes,
            status,
        ) = self.collect_current_annotation()


        # ----------------------------------------------------
        # Prevent both states for same allergen.
        #
        # This should already be impossible because each
        # allergen has exactly one dropdown, but we retain
        # this validation for data integrity.
        # ----------------------------------------------------

        overlap = (
            set(confirmed) &
            set(potential)
        )


        if overlap:

            messagebox.showerror(
                "Invalid Annotation",
                "An allergen cannot be both "
                "confirmed and potential:\n\n"
                + ", ".join(
                    sorted(overlap)
                )
            )

            return False


        # ----------------------------------------------------
        # Evidence level required when reviewed.
        # ----------------------------------------------------

        if status == "reviewed":

            if not evidence_level:

                messagebox.showwarning(
                    "Evidence Level Required",
                    "Select an evidence level "
                    "before marking this product "
                    "as reviewed."
                )

                return False


            # ------------------------------------------------
            # Check evidence-level consistency.
            # ------------------------------------------------

            if (
                evidence_level
                == "direct"
                and not confirmed
            ):

                messagebox.showwarning(
                    "Check Annotation",
                    "Evidence level is 'direct' "
                    "but no confirmed allergens "
                    "are selected."
                )

                return False


            if (
                evidence_level
                == "precautionary"
                and not potential
            ):

                messagebox.showwarning(
                    "Check Annotation",
                    "Evidence level is "
                    "'precautionary' but no "
                    "potential allergens are selected."
                )

                return False


            if (
                evidence_level
                == "mixed"
                and (
                    not confirmed
                    or not potential
                )
            ):

                messagebox.showwarning(
                    "Check Annotation",
                    "Evidence level is 'mixed'. "
                    "You should normally have "
                    "both confirmed and potential "
                    "allergens."
                )

                return False


            if (
                evidence_level
                == "none"
                and (
                    confirmed
                    or potential
                )
            ):

                messagebox.showwarning(
                    "Check Annotation",
                    "Evidence level is 'none' "
                    "but allergens are selected."
                )

                return False


            if (
                evidence_level
                == "ambiguous"
                and not notes
            ):

                messagebox.showwarning(
                    "Review Note Required",
                    "For an ambiguous case, "
                    "please explain the reason "
                    "in Review Notes."
                )

                return False


        # ----------------------------------------------------
        # Reviewer required for completed review.
        # ----------------------------------------------------

        if (
            status == "reviewed"
            and not reviewer
        ):

            messagebox.showwarning(
                "Reviewer Required",
                "Enter the reviewer name or "
                "identifier before marking "
                "the product as reviewed."
            )

            return False


        return True


    # ========================================================
    # SAVE CURRENT
    # ========================================================

    def save_current(
        self,
        show_message=True
    ):

        if not self.validate_annotation():

            return False


        (
            confirmed,
            potential,
            evidence_level,
            reviewer,
            notes,
            status,
        ) = self.collect_current_annotation()


        record = self.products[
            self.current_index
        ]


        # ----------------------------------------------------
        # Save labels
        # ----------------------------------------------------

        record[
            "gold_confirmed_allergens"
        ] = ";".join(
            sorted(confirmed)
        )


        record[
            "gold_potential_allergens"
        ] = ";".join(
            sorted(potential)
        )


        record[
            "gold_evidence_level"
        ] = evidence_level


        record[
            "review_notes"
        ] = notes


        record[
            "reviewer"
        ] = reviewer


        record[
            "review_status"
        ] = status


        # ----------------------------------------------------
        # Write complete CSV
        # ----------------------------------------------------

        try:

            save_products(
                OUTPUT_FILE,
                self.products
            )

        except Exception as exc:

            messagebox.showerror(
                "Save Error",
                str(exc)
            )

            return False


        if show_message:

            messagebox.showinfo(
                "Saved",
                f"{record['gold_id']} saved.\n\n"
                f"File:\n{OUTPUT_FILE}"
            )


        # ----------------------------------------------------
        # Refresh progress
        # ----------------------------------------------------

        reviewed = sum(
            1
            for item in self.products
            if (
                item.get(
                    "review_status",
                    ""
                )
                == "reviewed"
            )
        )


        self.progress_var.set(
            f"Product "
            f"{self.current_index + 1} "
            f"of "
            f"{len(self.products)}"
            f"   |   Reviewed: "
            f"{reviewed}"
        )


        return True


    # ========================================================
    # SAVE AND NEXT
    # ========================================================

    def save_and_next(self):

        saved = self.save_current(
            show_message=False
        )

        if not saved:

            return


        if (
            self.current_index
            < len(self.products) - 1
        ):

            self.load_record(
                self.current_index + 1
            )

        else:

            messagebox.showinfo(
                "Completed",
                "This is the final product."
            )


    # ========================================================
    # PREVIOUS
    # ========================================================

    def previous_record(self):

        # Save current first.
        saved = self.save_current(
            show_message=False
        )

        if not saved:

            return


        if self.current_index > 0:

            self.load_record(
                self.current_index - 1
            )


    # ========================================================
    # JUMP TO ID
    # ========================================================

    def jump_to_id(self):

        value = (
            self.jump_entry
            .get()
            .strip()
            .upper()
        )


        if not value:

            return


        if not value.startswith(
            "GOLD_"
        ):

            value = (
                "GOLD_"
                + value
            )


        # Save current before jumping.
        saved = self.save_current(
            show_message=False
        )

        if not saved:

            return


        for index, record in enumerate(
            self.products
        ):

            if (
                record[
                    "gold_id"
                ].upper()
                == value
            ):

                self.load_record(
                    index
                )

                self.jump_entry.delete(
                    0,
                    "end"
                )

                return


        messagebox.showwarning(
            "Not Found",
            f"{value} was not found."
        )


# ============================================================
# MAIN
# ============================================================

def main():

    root = tk.Tk()

    try:

        app = GoldAnnotationApp(
            root
        )

    except Exception as exc:

        messagebox.showerror(
            "Application Error",
            str(exc)
        )

        root.destroy()

        return


    root.mainloop()


if __name__ == "__main__":
    main()
