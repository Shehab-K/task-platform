# 1. Start from an official, lightweight Python 3.12 Linux image
FROM python:3.12-slim

# 2. Prevent Python from buffering stdout/stderr (so worker print() logs show up immediately!)
ENV PYTHONUNBUFFERED=1

# 3. Set the working directory inside the container
WORKDIR /app

# 4. Copy requirements first and install dependencies (cached by Docker unless requirements.txt changes)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copy your application code into /app
COPY . .