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

# Create directory for database with proper permissions
RUN mkdir -p /data && chown -R 1000:1000 /data && chmod 777 /data

# Set working directory
WORKDIR /app

# Install Python dependencies
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir gunicorn pymysql cryptography

# Copy application files
COPY app app
COPY migrations migrations
COPY microblog.py config.py boot.sh create_db.py ./
RUN chmod a+x boot.sh

# Set environment variables
ENV FLASK_APP=microblog.py
ENV FLASK_DEBUG=0
ENV MAIL_SERVER=
ENV MAIL_ADMIN=admin@example.com
ENV DATABASE_URL=sqlite:////data/app.db
ENV LOG_TO_STDOUT=1

RUN flask translate compile

# Create volume for database persistence
VOLUME /data

EXPOSE 5000
ENTRYPOINT ["./boot.sh"]
