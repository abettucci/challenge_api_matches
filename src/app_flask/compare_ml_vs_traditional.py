import requests
import csv
import json

API_URL = "http://localhost:5000/items/compare"
CSV_PATH = "../data/data_matches - dataset.csv"

results = []

with open(CSV_PATH, newline='', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        item_a = {"item_id": int(row["ITEM_A"]), "title": row["TITLE_A"].strip()}
        item_b = {"item_id": int(row["ITEM_B"]), "title": row["TITLE_B"].strip()}
        # Sin ML
        resp_no_ml = requests.post(API_URL, json={"item_a": item_a, "item_b": item_b, "use_ml": False})
        score_no_ml = resp_no_ml.json().get("similarity_score", None)
        # Con ML
        resp_ml = requests.post(API_URL, json={"item_a": item_a, "item_b": item_b, "use_ml": True})
        score_ml = resp_ml.json().get("similarity_score", None)
        results.append({
            "item_a": item_a["title"],
            "item_b": item_b["title"],
            "score_no_ml": score_no_ml,
            "score_ml": score_ml,
            "diff": abs((score_ml or 0) - (score_no_ml or 0))
        })

print("\nComparación de resultados ML vs Tradicional:")
for r in results:
    print(f"A: {r['item_a']} | B: {r['item_b']}")
    print(f"  Sin ML: {r['score_no_ml']}, Con ML: {r['score_ml']}, Diferencia: {r['diff']:.3f}")
    print()

positivos_no_ml = sum(1 for r in results if r['score_no_ml'] is not None and r['score_no_ml'] >= 0.7)
positivos_ml = sum(1 for r in results if r['score_ml'] is not None and r['score_ml'] >= 0.7)
print(f"Total positivos sin ML: {positivos_no_ml}")
print(f"Total positivos con ML: {positivos_ml}")
print(f"Diferencia de positivos: {positivos_ml - positivos_no_ml}") 