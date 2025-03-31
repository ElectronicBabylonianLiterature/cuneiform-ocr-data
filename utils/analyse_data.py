import json
from collections import defaultdict

def generate_statistics(metadata):
    stats = defaultdict(int)
    summary = dict()
    for d in metadata:
        sign = d["sign"]
        stats[sign] += 1
    summary["num_of_diff_signs"] = len(stats.keys())
    summary["sign_total"] = sum(stats.values())
    return stats, summary

def load_json_metadata():
    with open("naive_data/crops_metadata.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        return data

if __name__ == '__main__':
    metadata = load_json_metadata()
    stats, summary = generate_statistics(metadata)
    breakpoint()
