"""
Database initialization script that directly creates tables using SQLAlchemy
"""

from app import create_app, db
from app.models import User, Post, Message, Notification, Task, followers

def init_db():
    """Initialize the database by creating all tables"""
    print("Creating database tables directly with SQLAlchemy...")
    app = create_app()
    
    with app.app_context():
        # Create all tables
        try:
            db.create_all()
            print("Successfully created all database tables.")
            
            # Check if we need to create a demo user
            from app.models import User
            import sqlalchemy as sa
            
            try:
                user_count = db.session.scalar(sa.select(sa.func.count()).select_from(User))
                print(f"Found {user_count} existing users")
                
                if user_count == 0:
                    print("Creating demo user...")
                    u = User(username='demo', email='demo@example.com')
                    u.set_password('demo1234')
                    db.session.add(u)
                    db.session.commit()
                    print('Created demo user: demo / demo1234')
                else:
                    print('Using existing user accounts')
            except Exception as e:
                print(f"Error checking users: {e}")
                
        except Exception as e:
            print(f"Error creating tables: {e}")
            return False
            
        # Verify tables were created
        try:
            tables = db.engine.table_names()
            print(f"Created tables: {', '.join(tables)}")
            return 'user' in tables
        except Exception as e:
            print(f"Error verifying tables: {e}")
            return False
    
if __name__ == '__main__':
    init_db()
