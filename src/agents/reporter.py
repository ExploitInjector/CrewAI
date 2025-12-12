from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from collections import defaultdict


@dataclass
class ReporterConfig:
    input_json: Path = Path("runs/explanations_top.json")
    output_json: Path = Path("runs/incident_cards.json")
    output_md: Path = Path("runs/incident_cards.md")
    group_by: str = "src_ip"   # src_ip / dst_ip
    top_n_cards: int = 50


def main() -> None:
    cfg = ReporterConfig()
    cfg.output_json.parent.mkdir(parents=True, exist_ok=True)

    payload = json.loads(cfg.input_json.read_text(encoding="utf-8"))
    items = payload.get("items", [])

    # group_by mező kinyerése a raw-ból
    groups = defaultdict(list)
    for it in items:
        raw = it.get("raw", {})
        key = raw.get(cfg.group_by) or "UNKNOWN"
        groups[key].append(it)

    # kártyák összeállítása
    cards = []
    for key, lst in groups.items():
        lst_sorted = sorted(lst, key=lambda x: int(x.get("risk_score", 0)), reverse=True)
        max_score = int(lst_sorted[0].get("risk_score", 0)) if lst_sorted else 0

        # rövid „mi történt” + összesített okok
        reasons_all = []
        for it in lst_sorted:
            reasons_all.extend(it.get("reasons", []))

        # top okok gyakoriság szerint
        reason_counts = defaultdict(int)
        for r in reasons_all:
            reason_counts[r] += 1
        top_reasons = sorted(reason_counts.items(), key=lambda x: x[1], reverse=True)[:5]

        cards.append({
            "entity": cfg.group_by,
            "value": key,
            "events_count": len(lst),
            "max_risk_score": max_score,
            "top_reasons": [{"reason": r, "count": c} for r, c in top_reasons],
            "top_events": lst_sorted[:10],  # első 10 esemény a kártyán
        })

    # rendezés: legtöbb esemény, majd max score
    cards.sort(key=lambda c: (c["events_count"], c["max_risk_score"]), reverse=True)

    cards_out = cards[:cfg.top_n_cards]

    out = {
        "group_by": cfg.group_by,
        "cards_total": len(cards),
        "cards_exported": len(cards_out),
        "cards": cards_out,
    }

    cfg.output_json.write_text(json.dumps(out, indent=2), encoding="utf-8")

    # Markdown export
    lines = []
    lines.append(f"# Incident Cards (grouped by {cfg.group_by})")
    lines.append(f"- total cards: {len(cards)}")
    lines.append(f"- exported: {len(cards_out)}")
    lines.append("")

    for i, c in enumerate(cards_out, 1):
        lines.append(f"## {i}. {c['entity']} = {c['value']}")
        lines.append(f"- events_count: {c['events_count']}")
        lines.append(f"- max_risk_score: {c['max_risk_score']}")
        lines.append(f"- top_reasons:")
        for tr in c["top_reasons"]:
            lines.append(f"  - {tr['reason']} (count={tr['count']})")
        lines.append(f"- top_events:")
        for e in c["top_events"]:
            lines.append(f"  - {e['summary']} (risk_score={e['risk_score']})")
        lines.append("")

    cfg.output_md.write_text("\n".join(lines), encoding="utf-8")

    print("Reporter done.")
    print(f"Wrote: {cfg.output_json} and {cfg.output_md}")


if __name__ == "__main__":
    main()
