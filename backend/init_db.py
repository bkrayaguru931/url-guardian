from app.db.database import engine
from app.db.models import Base

def init_db():
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✅ Database initialized!")

if __name__ == "__main__":
    init_db()