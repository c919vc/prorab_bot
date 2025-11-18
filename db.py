import json
import os
from datetime import datetime

DATA_DIR = "data"

USERS_FILE = f"{DATA_DIR}/users.json"
EXPENSE_FILE = f"{DATA_DIR}/expenses.json"
CARD_FILE = f"{DATA_DIR}/card.json"
DEBT_FILE = f"{DATA_DIR}/debts.json"


# ================================================================
#                  JSON LOAD / SAVE
# ================================================================
def load_json(path):
    if not os.path.exists(path):
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []


def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)



# ================================================================
#                        USERS
# ================================================================
def add_user(uid, name, username):
    data = load_json(USERS_FILE)

    for u in data:
        if u["id"] == uid:
            return

    data.append({
        "id": uid,
        "name": name,
        "username": username
    })

    save_json(USERS_FILE, data)



# ================================================================
#                       EXPENSES
# ================================================================
def save_expense(category, amount, note):
    data = load_json(EXPENSE_FILE)

    data.append({
        "id": len(data) + 1,
        "category": category,
        "amount": amount,
        "note": note,
        "date": datetime.now().strftime("%Y-%m-%d")
    })

    save_json(EXPENSE_FILE, data)



# ================================================================
#                         CARD
# ================================================================
def save_card(amount, item, photo):
    data = load_json(CARD_FILE)

    data.append({
        "id": len(data) + 1,
        "amount": amount,
        "item": item,
        "photo": photo,
        "date": datetime.now().strftime("%Y-%m-%d")
    })

    save_json(CARD_FILE, data)



# ================================================================
#                        DEBTS
# ================================================================
def save_debt(name, phone, amount, item, deadline):
    data = load_json(DEBT_FILE)

    data.append({
        "id": len(data) + 1,
        "name": name,
        "phone": phone,
        "amount": amount,
        "item": item,
        "deadline": deadline,
        "date": datetime.now().strftime("%Y-%m-%d")
    })

    save_json(DEBT_FILE, data)



def get_debts():
    return load_json(DEBT_FILE)



def get_debt_by_id(did):
    for d in load_json(DEBT_FILE):
        if d["id"] == did:
            return d
    return None



def delete_debt(did):
    data = load_json(DEBT_FILE)
    data = [d for d in data if d["id"] != did]
    save_json(DEBT_FILE, data)



def save_debt_edit(did, name, phone, amount, item, deadline):
    data = load_json(DEBT_FILE)
    for d in data:
        if d["id"] == did:
            d["name"] = name
            d["phone"] = phone
            d["amount"] = amount
            d["item"] = item
            d["deadline"] = deadline
    save_json(DEBT_FILE, data)



# ================================================================
#                       TODAY STATISTICS
# ================================================================
def get_today_statistics():
    today = datetime.now().strftime("%Y-%m-%d")

    expenses = load_json(EXPENSE_FILE)
    cards = load_json(CARD_FILE)

    ovqat = sum(i["amount"] for i in expenses if i["date"] == today and i["category"] == "Ovqat")
    firma = sum(i["amount"] for i in expenses if i["date"] == today and i["category"] == "Firma")
    boshqalar = sum(i["amount"] for i in expenses if i["date"] == today and i["category"] == "Boshqalar")

    card = sum(i["amount"] for i in cards if i["date"] == today)

    return {
        "date": today,
        "ovqat": ovqat,
        "firma": firma,
        "boshqalar": boshqalar,
        "jami_xarajat": ovqat + firma + boshqalar,
        "card_jami": card
    }
