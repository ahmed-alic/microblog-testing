#!/bin/bash
# this script is used to boot a Docker container

# Use sqlite3 directly to check if database exists
db_file="/data/app.db"

# Ensure database migrations run
echo "Running database migrations..."
flask db upgrade

# Create a demo user
echo "Checking for existing users..."
python << EOF
from app import create_app, db
from app.models import User
import sqlalchemy as sa

app = create_app()
with app.app_context():
    try:
        # Check if User table exists
        user_count = db.session.scalar(sa.select(sa.func.count()).select_from(User))
        
        if user_count == 0:
            print("Creating demo user...")
            u = User(username='demo', email='demo@example.com')
            u.set_password('demo1234')
            db.session.add(u)
            db.session.commit()
            print('Created demo user: demo / demo1234')
        else:
            print(f'Database already contains {user_count} users')
    except Exception as e:
        print(f"Error: {e}")
        print("Running migrations again...")
        import os
        os.system("flask db upgrade")
        # Try creating user again
        try:
            u = User(username='demo', email='demo@example.com')
            u.set_password('demo1234')
            db.session.add(u)
            db.session.commit()
            print('Created demo user: demo / demo1234')
        except Exception as e2:
            print(f"Second error: {e2}")
EOF

# Run the web server
echo "Starting web server..."
exec gunicorn -b :5000 --access-logfile - --error-logfile - microblog:app
