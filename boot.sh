#!/bin/bash
# This script boots the Docker container with direct database initialization

# Set up error handling
set -e

# Define database file location
db_file="/data/app.db"
db_dir="/data"

# Ensure data directory exists with proper permissions
echo "Checking data directory permissions..."
mkdir -p "$db_dir"
chmod 777 "$db_dir"

# Function to check if the user table exists
check_user_table() {
    if sqlite3 "$db_file" "SELECT name FROM sqlite_master WHERE type='table' AND name='user';" | grep -q user; then
        return 0  # Success - table exists
    else
        return 1  # Failure - table doesn't exist
    fi
}

# Database initialization strategy
echo "=== DATABASE INITIALIZATION STRATEGY ==="

# Step 1: Try the direct SQLAlchemy initialization approach
echo "1. Initializing database directly with SQLAlchemy..." 
python create_db.py

# Step 2: Check if that worked
if ! check_user_table; then
    echo "Direct initialization failed, trying flask db upgrade..."
    
    # Step 3: Try using Flask-Migrate as a fallback
    echo "2. Attempting database migrations..."
    flask db upgrade
    
    # Step 4: Final fallback - create tables with raw SQL
    if ! check_user_table; then
        echo "3. Creating minimal tables with raw SQL..."
        
        # Create the absolute minimum tables needed for the app to function
        sqlite3 "$db_file" <<EOF
CREATE TABLE IF NOT EXISTS user (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(64) UNIQUE,
    email VARCHAR(120) UNIQUE,
    password_hash VARCHAR(128),
    about_me VARCHAR(140),
    last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_message_read_time TIMESTAMP,
    token VARCHAR(32),
    token_expiration TIMESTAMP
);

CREATE TABLE IF NOT EXISTS post (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    body VARCHAR(140),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    user_id INTEGER,
    language VARCHAR(5),
    FOREIGN KEY (user_id) REFERENCES user (id)
);
EOF
    fi
fi

# Create a demo user if database exists but no users
echo "Creating demo user if needed..."
python << EOF
from app import create_app, db
from app.models import User
import sqlalchemy as sa

app = create_app()
with app.app_context():
    try:
        # Check if we can connect to the database at all
        db.session.execute(sa.text('SELECT 1'))
        print("Database connection successful")
        
        # Try to create a demo user
        try:
            user_exists = db.session.execute(sa.text("SELECT id FROM user WHERE username='demo' LIMIT 1")).scalar() is not None
            if not user_exists:
                print("Creating demo user...")
                db.session.execute(sa.text("INSERT INTO user (username, email, password_hash) VALUES ('demo', 'demo@example.com', 'pbkdf2:sha256:600000$pvYRR36e$c0d92fcc530d244be251d21c76dc444a31ccade3fbddce6bf2aa5ed5fcaa2365')"))
                db.session.commit()
                print('Created demo user: demo / demo1234')
            else:
                print('Demo user already exists')
        except Exception as e:
            print(f"Error creating demo user: {e}")
    except Exception as e:
        print(f"Database connection error: {e}")
EOF

# Final verification
if check_user_table; then
    echo "Database initialization successful!"
else
    echo "ERROR: Failed to initialize database properly!"
    echo "Please check the logs for errors."
fi

# Start the Gunicorn web server
echo "Starting web server..."
exec gunicorn -b :5000 --access-logfile - --error-logfile - --capture-output microblog:app
