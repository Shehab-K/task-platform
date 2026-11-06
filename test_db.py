from database import engine

try:
    with engine.connect() as connection:
        print("Successfully connected to the PostgreSQL database in Docker!")
except Exception as e:
    print(f"Failed to connect: {e}")