from app.database import SessionLocal
from app.models import User
from app.auth_utils import get_password_hash

def ensure_admin():
    db = SessionLocal()
    try:
        # Check if user 'admin' exists
        admin_user = db.query(User).filter(User.username == "admin").first()
        if not admin_user:
            print("Creating default admin user...")
            new_admin = User(
                username="admin",
                email="admin@sajhilosewa.com",
                first_name="Admin",
                last_name="User",
                hashed_password=get_password_hash("admin"),
                is_active=True
            )
            db.add(new_admin)
            db.commit()
            print("Default admin user created successfully.")
        else:
            print("Admin user already exists.")
    except Exception as e:
        print(f"Error ensuring admin: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    ensure_admin()
