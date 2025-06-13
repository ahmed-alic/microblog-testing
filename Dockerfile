FROM python:3.9-slim

# Install required dependencies for building packages
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    g++ \
    libpq-dev \
    python3-dev \
    sqlite3 \
    && rm -rf /var/lib/apt/lists/*

# Create directory for database and set permissions
RUN mkdir -p /data && chmod 777 /data

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
RUN pip install gunicorn pymysql cryptography

COPY app app
COPY migrations migrations
COPY microblog.py config.py boot.sh ./
RUN chmod a+x boot.sh

# Set environment variables
ENV FLASK_APP=microblog.py
ENV MAIL_SERVER=
ENV MAIL_ADMIN=admin@example.com
ENV DATABASE_URL=sqlite:////data/app.db

RUN flask translate compile

# Create volume for database persistence
VOLUME /data

EXPOSE 5000
ENTRYPOINT ["./boot.sh"]
