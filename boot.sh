#!/bin/bash
# This script boots the Docker container with proper database initialization

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

# Try database migrations with retries
echo "Running database migrations..."
max_retries=5
retry_count=0
success=false

while [ $retry_count -lt $max_retries ] && [ "$success" = false ]; do
    echo "Migration attempt $(($retry_count + 1))/$max_retries"
    
    if flask db upgrade; then
        echo "Migration succeeded!"
        success=true
    else
        retry_count=$(($retry_count + 1))
        echo "Migration failed, retrying in 2 seconds..."
        sleep 2
    fi
done

# Check if user table exists after migrations
if ! check_user_table; then
    echo "WARNING: User table doesn't exist after migrations."
    echo "Creating tables manually with basic schema..."
    
    # Create basic user table if it doesn't exist
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
EOF
    
    echo "Basic user table created."
fi

# Create a demo user if no users exist
echo "Checking for existing users..."
python << EOF
from app import create_app, db
from app.models import User
import sqlalchemy as sa

app = create_app()
with app.app_context():
    try:
        # Check if User table exists and if there are any users
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
