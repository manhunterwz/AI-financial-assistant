import sys
import csv
import os
import random
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from backend.database import SessionLocal, init_db, User, Transaction, Category
from backend.config import EXPENSE_CATEGORIES, INCOME_CATEGORIES

def get_random_time(date_obj):
    hour = random.randint(8, 22)
    minute = random.randint(0, 59)
    second = random.randint(0, 59)
    return date_obj.replace(hour=hour, minute=minute, second=second)

def add_months(sourcedate, months):
    month = sourcedate.month - 1 + months
    year = sourcedate.year + month // 12
    month = month % 12 + 1
    day = min(sourcedate.day, 28) # simplify to avoid exceeding days in month
    return datetime(year, month, day, sourcedate.hour, sourcedate.minute, sourcedate.second)

def generate_transactions(user_id, start_date, end_date):
    transactions = []
    
    current_month_start = start_date.replace(day=1)
    
    month_index = 0
    
    while current_month_start <= end_date:
        year = current_month_start.year
        month = current_month_start.month
        
        spending_multiplier = 1.0 + (month_index * 0.05)
        
        # Salary: 1st of each month
        dt_salary = datetime(year, month, 1, 9, 0, 0)
        transactions.append({
            "user_id": user_id, "amount": 65000.0, "type": "income", "category_name": "Salary",
            "date": dt_salary, "description": "Monthly Salary", "is_recurring": True
        })
        
        # Rent: 5th of each month
        dt_rent = datetime(year, month, 5, 10, 0, 0)
        transactions.append({
            "user_id": user_id, "amount": 12000.0, "type": "expense", "category_name": "Rent",
            "date": dt_rent, "description": "Monthly Rent", "is_recurring": True
        })
        
        # Groceries
        for _ in range(random.randint(8, 12)):
            day = random.randint(1, 28)
            amount = round(random.uniform(200, 2500) * spending_multiplier, 2)
            desc = random.choice(['BigBasket order', 'Vegetables from market', 'D-Mart groceries', 'Milk and bread'])
            transactions.append({
                "user_id": user_id, "amount": amount, "type": "expense", "category_name": "Groceries",
                "date": get_random_time(datetime(year, month, day)), "description": desc, "is_recurring": False
            })
            
        # Food & Dining
        for _ in range(random.randint(15, 25)):
            day = random.randint(1, 28)
            amount = round(random.uniform(100, 2000) * spending_multiplier, 2)
            desc = random.choice(['Swiggy order', 'Zomato delivery', 'Coffee at Starbucks', 'Lunch at office canteen', 'Dinner at restaurant', 'Chai and snacks'])
            transactions.append({
                "user_id": user_id, "amount": amount, "type": "expense", "category_name": "Food & Dining",
                "date": get_random_time(datetime(year, month, day)), "description": desc, "is_recurring": False
            })

        # Transport
        for _ in range(random.randint(10, 20)):
            day = random.randint(1, 28)
            amount = round(random.uniform(30, 800) * spending_multiplier, 2)
            desc = random.choice(['Ola ride', 'Uber to office', 'Metro recharge', 'Petrol', 'Auto rickshaw'])
            transactions.append({
                "user_id": user_id, "amount": amount, "type": "expense", "category_name": "Transport",
                "date": get_random_time(datetime(year, month, day)), "description": desc, "is_recurring": False
            })

        # Shopping
        for _ in range(random.randint(3, 6)):
            day = random.randint(1, 28)
            amount = round(random.uniform(200, 5000) * spending_multiplier, 2)
            desc = random.choice(['Amazon order', 'Flipkart purchase', 'Myntra clothing', 'Reliance Digital'])
            transactions.append({
                "user_id": user_id, "amount": amount, "type": "expense", "category_name": "Shopping",
                "date": get_random_time(datetime(year, month, day)), "description": desc, "is_recurring": False
            })

        # Entertainment
        for _ in range(random.randint(3, 5)):
            day = random.randint(1, 28)
            amount = round(random.uniform(100, 1500) * spending_multiplier, 2)
            desc = random.choice(['Netflix subscription', 'Movie tickets', 'Spotify premium', 'Gaming'])
            transactions.append({
                "user_id": user_id, "amount": amount, "type": "expense", "category_name": "Entertainment",
                "date": get_random_time(datetime(year, month, day)), "description": desc, "is_recurring": False
            })

        # Utilities
        for _ in range(random.randint(3, 5)):
            day = random.randint(1, 28)
            amount = round(random.uniform(200, 3000) * spending_multiplier, 2)
            desc = random.choice(['Electricity bill', 'Water bill', 'Internet bill', 'Phone recharge'])
            transactions.append({
                "user_id": user_id, "amount": amount, "type": "expense", "category_name": "Utilities",
                "date": get_random_time(datetime(year, month, day)), "description": desc, "is_recurring": False
            })
            
        # Healthcare
        for _ in range(random.randint(1, 3)):
            day = random.randint(1, 28)
            amount = round(random.uniform(100, 3000) * spending_multiplier, 2)
            desc = random.choice(['Pharmacy', 'Doctor visit', 'Lab tests'])
            transactions.append({
                "user_id": user_id, "amount": amount, "type": "expense", "category_name": "Healthcare",
                "date": get_random_time(datetime(year, month, day)), "description": desc, "is_recurring": False
            })
            
        # Education
        for _ in range(random.randint(1, 2)):
            day = random.randint(1, 28)
            amount = round(random.uniform(200, 5000) * spending_multiplier, 2)
            desc = random.choice(['Udemy course', 'Books', 'Coursera subscription'])
            transactions.append({
                "user_id": user_id, "amount": amount, "type": "expense", "category_name": "Education",
                "date": get_random_time(datetime(year, month, day)), "description": desc, "is_recurring": False
            })

        # Personal Care
        for _ in range(random.randint(1, 3)):
            day = random.randint(1, 28)
            amount = round(random.uniform(100, 1500) * spending_multiplier, 2)
            desc = random.choice(['Haircut', 'Skincare products'])
            transactions.append({
                "user_id": user_id, "amount": amount, "type": "expense", "category_name": "Personal Care",
                "date": get_random_time(datetime(year, month, day)), "description": desc, "is_recurring": False
            })
            
        # Subscriptions
        for _ in range(random.randint(2, 3)):
            day = random.randint(1, 28)
            amount = round(random.uniform(100, 1000) * spending_multiplier, 2)
            desc = random.choice(['Amazon Prime', 'YouTube Premium', 'iCloud storage'])
            transactions.append({
                "user_id": user_id, "amount": amount, "type": "expense", "category_name": "Subscriptions",
                "date": get_random_time(datetime(year, month, day)), "description": desc, "is_recurring": True
            })

        # Travel
        for _ in range(random.randint(0, 1)):
            day = random.randint(1, 28)
            amount = round(random.uniform(1000, 15000) * spending_multiplier, 2)
            desc = random.choice(['Train tickets', 'Flight booking', 'Hotel booking'])
            transactions.append({
                "user_id": user_id, "amount": amount, "type": "expense", "category_name": "Travel",
                "date": get_random_time(datetime(year, month, day)), "description": desc, "is_recurring": False
            })
            
        # Gifts & Donations
        for _ in range(random.randint(0, 1)):
            day = random.randint(1, 28)
            amount = round(random.uniform(500, 5000) * spending_multiplier, 2)
            desc = random.choice(['Birthday gift', 'Donation', 'Wedding gift'])
            transactions.append({
                "user_id": user_id, "amount": amount, "type": "expense", "category_name": "Gifts & Donations",
                "date": get_random_time(datetime(year, month, day)), "description": desc, "is_recurring": False
            })
            
        # Insurance
        for _ in range(random.randint(0, 1)):
            day = random.randint(1, 28)
            amount = round(random.uniform(1000, 5000) * spending_multiplier, 2)
            desc = random.choice(['Health insurance', 'Term insurance'])
            transactions.append({
                "user_id": user_id, "amount": amount, "type": "expense", "category_name": "Insurance",
                "date": get_random_time(datetime(year, month, day)), "description": desc, "is_recurring": True
            })
            
        # Freelance income
        for _ in range(random.randint(0, 1)):
            day = random.randint(1, 28)
            amount = round(random.uniform(5000, 20000), 2)
            desc = random.choice(['Freelance project', 'Consulting work'])
            transactions.append({
                "user_id": user_id, "amount": amount, "type": "income", "category_name": "Freelance",
                "date": get_random_time(datetime(year, month, day)), "description": desc, "is_recurring": False
            })
            
        # Other Income
        for _ in range(random.randint(0, 1)):
            day = random.randint(1, 28)
            amount = round(random.uniform(1000, 5000), 2)
            desc = random.choice(['Cashback', 'Refund', 'Interest'])
            transactions.append({
                "user_id": user_id, "amount": amount, "type": "income", "category_name": "Other Income",
                "date": get_random_time(datetime(year, month, day)), "description": desc, "is_recurring": False
            })
            
        current_month_start = add_months(current_month_start, 1)
        month_index += 1

    # Intentional anomalies
    anomalies = [
        {"amount": 15000.0, "type": "expense", "category_name": "Shopping", "description": "Luxury Watch", "month_offset": 1, "day": 15},
        {"amount": 8000.0, "type": "expense", "category_name": "Food & Dining", "description": "Fine dining anniversary", "month_offset": 2, "day": 20},
        {"amount": 45000.0, "type": "expense", "category_name": "Travel", "description": "International flight booking", "month_offset": 3, "day": 10},
        {"amount": 25000.0, "type": "expense", "category_name": "Healthcare", "description": "Emergency dental procedure", "month_offset": 4, "day": 5},
        {"amount": 35000.0, "type": "income", "category_name": "Other Income", "description": "Sold old laptop", "month_offset": 5, "day": 12},
    ]

    for a in anomalies:
        d = add_months(start_date, a['month_offset'])
        d = d.replace(day=a['day'])
        transactions.append({
            "user_id": user_id,
            "amount": a['amount'],
            "type": a['type'],
            "category_name": a['category_name'],
            "date": get_random_time(d),
            "description": a['description'],
            "is_recurring": False
        })
        
    return transactions

def main():
    random.seed(42)
    print("Initializing database...")
    init_db()
    
    db = SessionLocal()
    
    try:
        print("Seeding categories...")
        existing_cats = {c.name: c for c in db.query(Category).all()}
        category_map = {}
        
        default_expense_categories = {
            "Rent": "🏠", "Groceries": "🛒", "Food & Dining": "🍔", "Transport": "🚗", 
            "Shopping": "🛍️", "Entertainment": "🎬", "Utilities": "⚡", "Healthcare": "⚕️", 
            "Education": "📚", "Personal Care": "💅", "Subscriptions": "🔁", "Travel": "✈️", 
            "Gifts & Donations": "🎁", "Insurance": "🛡️", "Other Expense": "📝"
        }
        default_income_categories = {
            "Salary": "💵", "Freelance": "💻", "Other Income": "💰"
        }
        
        cats_to_insert = []
        for name, icon in default_expense_categories.items():
            if name not in existing_cats:
                c = Category(name=name, type="expense", icon=icon)
                db.add(c)
                cats_to_insert.append(c)
            else:
                cats_to_insert.append(existing_cats[name])
                
        for name, icon in default_income_categories.items():
            if name not in existing_cats:
                c = Category(name=name, type="income", icon=icon)
                db.add(c)
                cats_to_insert.append(c)
            else:
                cats_to_insert.append(existing_cats[name])
                
        db.commit()
        for c in db.query(Category).all():
            category_map[c.name] = c.id
            
        print("Categories seeded.")

        user = db.query(User).filter_by(email="demo@example.com").first()
        if not user:
            print("Creating Demo User...")
            user = User(
                name="Demo User",
                email="demo@example.com",
                monthly_income=65000.0,
                currency="INR"
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        else:
            print("Demo User already exists.")

        print("Generating 6 months of transactions...")
        start_date = datetime(2026, 3, 1)
        end_date = datetime(2026, 8, 31)
        
        db.query(Transaction).filter_by(user_id=user.id).delete()
        db.commit()
        
        tx_data = generate_transactions(user.id, start_date, end_date)
        print(f"Generated {len(tx_data)} transactions. Saving to DB...")
        
        transactions = []
        for td in tx_data:
            # Ensure category exists in the categories table
            cat_name = td['category_name']
            if cat_name not in category_map:
                c = Category(name=cat_name, type=td['type'], icon="❓")
                db.add(c)
                db.commit()
                db.refresh(c)
                category_map[cat_name] = c.id
                
            tx = Transaction(
                user_id=user.id,
                amount=td['amount'],
                type=td['type'],
                category=cat_name,
                description=td['description'],
                transaction_date=td['date'].date(),
            )
            transactions.append(tx)
            
        db.bulk_save_objects(transactions)
        db.commit()
        print(f"Saved {len(transactions)} transactions to database.")
        
        data_dir = Path(__file__).resolve().parent.parent / "data"
        data_dir.mkdir(parents=True, exist_ok=True)
        csv_path = data_dir / "sample_transactions.csv"
        
        print(f"Exporting to CSV: {csv_path}")
        with open(csv_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["date", "description", "category", "type", "amount"])
            for td in sorted(tx_data, key=lambda x: x['date']):
                writer.writerow([
                    td['date'].strftime('%Y-%m-%d'),
                    td['description'],
                    td['category_name'],
                    td['type'],
                    td['amount'],
                ])
                
        print("Seed data generation complete!")
        
    except Exception as e:
        print(f"Error seeding data: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    main()
