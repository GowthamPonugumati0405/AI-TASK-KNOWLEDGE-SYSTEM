"""
One-time setup script:
- creates tables (if not already created by main.py's create_all)
- seeds the 'admin' and 'user' roles
- creates a default admin account (username: admin / password: admin123)

Run with:  python -m scripts.init_db
"""
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import Base, engine, SessionLocal
from app.models.role import Role
from app.models.user import User
from app.core.security import hash_password


def run():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        for role_name in ("admin", "user"):
            if not db.query(Role).filter(Role.name == role_name).first():
                db.add(Role(name=role_name))
        db.commit()

        admin_role = db.query(Role).filter(Role.name == "admin").first()
        if not db.query(User).filter(User.username == "admin").first():
            db.add(
                User(
                    username="admin",
                    email="admin@example.com",
                    hashed_password=hash_password("admin123"),
                    role_id=admin_role.id,
                )
            )
            db.commit()
            print("Created default admin -> username: admin | password: admin123")
        else:
            print("Admin user already exists, skipping.")

        print("Database initialized successfully.")
    finally:
        db.close()


if __name__ == "__main__":
    run()
