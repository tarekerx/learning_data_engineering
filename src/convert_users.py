import csv
import json
import os

with open("data/users.json", "r", encoding="utf-8") as file:
    users = json.load(file)

# Flatten each user object to match the CSV fieldnames
flattened_users = []
for user in users:
    flattened_users.append(
        {
            "customer_id": user.get("id"),
            "customer_name": user.get("name"),
            "email": user.get("email"),
            "phone": user.get("phone"),
            "city": user.get("address", {}).get("city"),
            "zipcode": user.get("address", {}).get("zipcode"),
            "company_name": user.get("company", {}).get("name"),
        }
    )

with open("data/users.csv", "w", newline="", encoding="utf-8") as file:
    fieldnames = [
        "customer_id",
        "customer_name",
        "email",
        "phone",
        "city",
        "zipcode",
        "company_name",
    ]
    writer = csv.DictWriter(file, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(flattened_users)