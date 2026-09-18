"""
generate_data.py
-----------------
Creates a synthetic but realistic transaction dataset to train/evaluate the
expense categorizer and the spending forecaster. In a real deployment you'd
replace this with the user's actual transaction history (bank statement,
UPI export, etc.) - the rest of the pipeline doesn't change.
"""
import random
import csv
from datetime import date, timedelta

random.seed(42)

# category -> (list of description templates, typical amount range in INR)
CATALOG = {
    "Food": (
        ["Swiggy order", "Zomato order", "Dominos pizza", "Campus canteen lunch",
         "Chai and snacks", "Grocery - BigBasket", "Grocery - local store",
         "Dinner with friends", "Starbucks coffee", "Biryani order",
         "Bakery - birthday cake", "Milk and bread"],
        (60, 900),
    ),
    "Transport": (
        ["Uber ride", "Ola cab", "Auto fare", "Petrol - bike", "Metro card recharge",
         "Bus pass", "Train ticket booking", "Rapido bike ride", "Parking fee",
         "Cab to airport"],
        (30, 1500),
    ),
    "Shopping": (
        ["Amazon purchase", "Flipkart order", "Myntra clothes", "New headphones",
         "Shoes - Decathlon", "Mobile phone cover", "Stationery shopping",
         "Gift for friend", "Home decor items", "Electronics - USB cable"],
        (150, 5000),
    ),
    "Bills & Utilities": (
        ["Electricity bill", "Mobile recharge - Jio", "Mobile recharge - Airtel",
         "Wifi bill - ACT Fibernet", "DTH recharge", "Water bill",
         "Gas cylinder booking", "Maintenance charges", "Laundry service"],
        (150, 2500),
    ),
    "Entertainment": (
        ["Netflix subscription", "Spotify premium", "Movie tickets - PVR",
         "Amazon Prime subscription", "Gaming - Steam purchase", "Concert ticket",
         "YouTube Premium", "Bowling with friends", "Hotstar subscription"],
        (100, 1200),
    ),
    "Health": (
        ["Pharmacy - medicines", "Doctor consultation fee", "Hospital visit",
         "Gym membership", "Protein supplement", "Dental checkup",
         "Health insurance premium", "Diagnostic lab test"],
        (150, 3000),
    ),
    "Education": (
        ["College semester fees", "Udemy course purchase", "Textbook purchase",
         "Coaching class fees", "Printing and Xerox", "Exam registration fee",
         "Online certification - Coursera", "Library fine", "Lab equipment purchase"],
        (100, 8000),
    ),
    "Other": (
        ["ATM cash withdrawal", "Bank service charge", "Donation", "Salon haircut",
         "Miscellaneous expense", "Courier charges", "Mobile repair",
         "Photocopy and binding", "SIM card purchase"],
        (50, 2000),
    ),
}

INCOME_DESCRIPTIONS = [
    "Monthly allowance from home", "Part-time tutoring payment", "Freelance project payment",
    "Scholarship credit", "Internship stipend", "Cashback credited", "Gift money - birthday",
]

def random_date_within(months_back=6):
    today = date.today()
    start = today - timedelta(days=30 * months_back)
    delta_days = (today - start).days
    return start + timedelta(days=random.randint(0, delta_days))

def generate(n_expense=220, n_income=28):
    rows = []
    categories = list(CATALOG.keys())
    for _ in range(n_expense):
        cat = random.choice(categories)
        templates, (lo, hi) = CATALOG[cat]
        desc = random.choice(templates)
        amount = round(random.uniform(lo, hi), 2)
        d = random_date_within()
        rows.append({"date": d.isoformat(), "description": desc, "amount": amount,
                      "type": "expense", "category": cat})
    for _ in range(n_income):
        desc = random.choice(INCOME_DESCRIPTIONS)
        amount = round(random.uniform(1000, 15000), 2)
        d = random_date_within()
        rows.append({"date": d.isoformat(), "description": desc, "amount": amount,
                      "type": "income", "category": "Income"})
    rows.sort(key=lambda r: r["date"])
    return rows

if __name__ == "__main__":
    rows = generate()
    out_path = "data/transactions_sample.csv"
    with open(out_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["date", "description", "amount", "type", "category"])
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {len(rows)} rows to {out_path}")
