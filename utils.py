from datetime import datetime, timedelta
import json
import os

def cleanup_old_data():
    DATA_FILES = ["data/debts.json", "data/expenses.json"]

    now = datetime.now()
    limit = now - timedelta(days=5)

    for file in DATA_FILES:
        if not os.path.exists(file):
            continue

        with open(file, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except:
                data = []

        new_data = []
        for item in data:
            created = item.get("created_at")
            if not created:
                new_data.append(item)
                continue

            created_date = datetime.strptime(created, "%Y-%m-%d")
            if created_date >= limit:
                new_data.append(item)

        with open(file, "w", encoding="utf-8") as f:
            json.dump(new_data, f, indent=4, ensure_ascii=False)
