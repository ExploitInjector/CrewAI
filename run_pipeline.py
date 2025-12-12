from pathlib import Path
import json
import subprocess
import sys


def run_if_missing(name: str, cmd: list[str], output: Path):
    if output.exists():
        print(f"[SKIP] {name} (output exists: {output})")
        return

    print(f"[RUN ] {name}")
    result = subprocess.run(cmd)
    if result.returncode != 0:
        print(f"[FAIL] {name}")
        sys.exit(1)
    print(f"[DONE] {name}")


def main():
    # ==== Definiáljuk az agenteket sorrendben ====
    steps = [
        (
            "DataCleaner",
            ["python", "src/agents/data_cleaner.py"],
            Path("data/processed/tii_ssrc23_cleaned_full.csv"),
        ),
        (
            "Correlator",
            ["python", "src/agents/correlator_full.py"],
            Path("runs/correlated_events_full.csv"),
        ),
        (
            "Detector",
            ["python", "src/agents/detector_rules.py"],
            Path("runs/detections_top.csv"),
        ),
        (
            "Explainer",
            ["python", "src/agents/explainer.py"],
            Path("runs/explanations_top.json"),
        ),
        (
            "Reporter",
            ["python", "src/agents/reporter.py"],
            Path("runs/incident_cards.json"),
        ),
    ]

    # ==== Pipeline futtatása ====
    print("\n=== IDS PIPELINE START ===")

    for name, cmd, output in steps:
        run_if_missing(name, cmd, output)

    # ==== Emberi összefoglaló ====
    cards_path = Path("runs/incident_cards.json")
    if not cards_path.exists():
        print("\nPipeline finished, but no incident cards found.")
        return

    cards = json.loads(cards_path.read_text(encoding="utf-8"))

    print("\n=== IDS PIPELINE FINISHED ===")
    print(f"Incident cards total: {cards.get('cards_total')}")
    print(f"Incident cards exported: {cards.get('cards_exported')}")
    print("\nHuman-readable report:")
    print("  runs/incident_cards.md\n")

    print("Top suspicious entities:")
    for i, card in enumerate(cards.get("cards", [])[:5], 1):
        print(
            f"  {i}) {card['entity']}={card['value']} | "
            f"events={card['events_count']} | "
            f"max_risk={card['max_risk_score']}"
        )

    print("\nPipeline completed successfully.")
    print("=============================")


if __name__ == "__main__":
    main()
