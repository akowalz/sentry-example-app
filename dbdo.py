from app import db

print("Dropping database.")

db.drop_all()
db.create_all()

print("Database created successfully.")
