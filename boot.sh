#!/bin/bash
# this script is used to boot a Docker container

# Create database directory if it doesn't exist
mkdir -p /app/instance

# Ensure database migrations run
while true; do
    flask db upgrade
    if [[ "$?" == "0" ]]; then
        break
    fi
    echo Deploy command failed, retrying in 5 secs...
    sleep 5
done

# Create a test user if database is empty
python -c "

from app import create_app, db
from app.models import User

app = create_app()
with app.app_context():
    user_count = db.session.query(User).count()
    if user_count == 0:
        u = User(username='demo', email='demo@example.com')
        u.set_password('demo1234')
        db.session.add(u)
        db.session.commit()
        print('Created demo user: demo / demo1234')
    else:
        print(f'Database already contains {user_count} users')
"

# Run the web server
exec gunicorn -b :5000 --access-logfile - --error-logfile - microblog:app
