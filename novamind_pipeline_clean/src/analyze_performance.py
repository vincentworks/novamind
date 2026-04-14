import json
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

CAMPAIGN_LOG_PATH = DATA_DIR / "campaign_log.json"
PERFORMANCE_LOG_PATH = DATA_DIR / "performance_log.json"


def load_json(path: Path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path: Path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def simulate_metrics(custom_persona: str):
    benchmarks = {
        "Creative Agency Founder": {
            "open_rate": 0.46,
            "click_rate": 0.17,
            "unsubscribe_rate": 0.01
        },
        "Operations Manager": {
            "open_rate": 0.41,
            "click_rate": 0.11,
            "unsubscribe_rate": 0.02
        },
        "Marketing Lead": {
            "open_rate": 0.50,
            "click_rate": 0.20,
            "unsubscribe_rate": 0.01
        }
    }

    return benchmarks.get(custom_persona, {
        "open_rate": 0.40,
        "click_rate": 0.10,
        "unsubscribe_rate": 0.02
    })


def aggregate_results_by_persona(audience_results):
    grouped = {}

    for row in audience_results:
        custom_persona = row["custom_persona"]
        if custom_persona not in grouped:
            grouped[custom_persona] = {
                "custom_persona": custom_persona,
                "open_rate": [],
                "click_rate": [],
                "unsubscribe_rate": []
            }

        grouped[custom_persona]["open_rate"].append(row["open_rate"])
        grouped[custom_persona]["click_rate"].append(row["click_rate"])
        grouped[custom_persona]["unsubscribe_rate"].append(row["unsubscribe_rate"])

    summarized = []
    for custom_persona, values in grouped.items():
        summarized.append({
            "custom_persona": custom_persona,
            "open_rate": round(sum(values["open_rate"]) / len(values["open_rate"]), 2),
            "click_rate": round(sum(values["click_rate"]) / len(values["click_rate"]), 2),
            "unsubscribe_rate": round(sum(values["unsubscribe_rate"]) / len(values["unsubscribe_rate"]), 2)
        })

    return summarized


def generate_summary(results):
    best = max(results, key=lambda x: x["click_rate"])
    worst = min(results, key=lambda x: x["click_rate"])

    return (
        f"{best['custom_persona']} outperformed other segments with a "
        f"{best['click_rate']:.0%} click-through rate, suggesting the messaging was well aligned "
        f"with that audience’s needs. In contrast, {worst['custom_persona']} had the lowest click-through "
        f"rate at {worst['click_rate']:.0%}, which suggests future campaigns should test more tailored "
        f"use cases or clearer value propositions for that segment."
    )


def main():
    campaigns = load_json(CAMPAIGN_LOG_PATH)

    if not campaigns:
        print("No campaigns found in campaign_log.json")
        return

    latest_campaign = campaigns[-1]
    audience = latest_campaign.get("audience", [])

    if not audience:
        print("No audience records found in latest campaign.")
        return

    audience_results = []

    for person in audience:
        custom_persona = (person.get("custom_persona") or person.get("persona") or "Unknown").strip()
        metrics = simulate_metrics(custom_persona)

        audience_results.append({
            "email": person.get("email", ""),
            "custom_persona": custom_persona,
            "open_rate": metrics["open_rate"],
            "click_rate": metrics["click_rate"],
            "unsubscribe_rate": metrics["unsubscribe_rate"]
        })

    persona_results = aggregate_results_by_persona(audience_results)
    summary = generate_summary(persona_results)

    performance_entry = {
        "campaign_id": latest_campaign.get("campaign_id", "unknown_campaign"),
        "campaign_date": latest_campaign.get("campaign_date", datetime.today().strftime("%Y-%m-%d")),
        "channel": latest_campaign.get("channel", "email"),
        "results_by_contact": audience_results,
        "results_by_persona": persona_results,
        "summary": summary
    }

    if PERFORMANCE_LOG_PATH.exists():
        existing = load_json(PERFORMANCE_LOG_PATH)
        if not isinstance(existing, list):
            existing = []
    else:
        existing = []

    existing.append(performance_entry)
    save_json(PERFORMANCE_LOG_PATH, existing)

    print(f"Saved performance log to: {PERFORMANCE_LOG_PATH}")
    print(f"Campaign ID: {performance_entry['campaign_id']}")
    print("Summary:")
    print(summary)


if __name__ == "__main__":
    main()