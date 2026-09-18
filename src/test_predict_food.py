#!/usr/bin/env python3

from predict_food import (
    load_knowledge_base,
    run_kg,
    run_svm,
    hybrid_decision,
)


def check_case(name, text, expected_confirmed, expected_potential, expected_candidates):
    knowledge = load_knowledge_base()

    kg = run_kg(text, knowledge)
    svm = run_svm(text)
    hybrid = hybrid_decision(kg, svm)

    confirmed = set(hybrid["confirmed"])
    potential = set(hybrid["potential"])
    candidates = set(hybrid["review_candidates"])

    assert confirmed == set(expected_confirmed), (
        f"{name}: confirmed mismatch\n"
        f"Expected: {expected_confirmed}\n"
        f"Actual:   {sorted(confirmed)}"
    )

    assert potential == set(expected_potential), (
        f"{name}: potential mismatch\n"
        f"Expected: {expected_potential}\n"
        f"Actual:   {sorted(potential)}"
    )

    assert candidates == set(expected_candidates), (
        f"{name}: candidate mismatch\n"
        f"Expected: {expected_candidates}\n"
        f"Actual:   {sorted(candidates)}"
    )

    print(f"PASS: {name}")


def main():

    check_case(
        "KG and SVM agreement",
        "wheat flour, milk powder, soy lecithin",
        expected_confirmed=[
            "milk",
            "soy",
            "wheat_gluten",
        ],
        expected_potential=[],
        expected_candidates=[],
    )

    check_case(
        "Precautionary evidence",
        "wheat flour. May contain traces of milk and soy.",
        expected_confirmed=[
            "wheat_gluten",
        ],
        expected_potential=[
            "milk",
            "soy",
        ],
        expected_candidates=[],
    )

    check_case(
        "SVM-only review candidate",
        "coconut milk, almond milk, nutmeg",
        expected_confirmed=[
            "tree_nut",
        ],
        expected_potential=[],
        expected_candidates=[
            "milk",
        ],
    )

    print()
    print("=" * 60)
    print("ALL PREDICTOR TESTS PASSED")
    print("=" * 60)


if __name__ == "__main__":
    main()
