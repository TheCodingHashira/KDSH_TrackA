FROM python:3.10-slim

WORKDIR /app

# 1️⃣ System dependencies (cached)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 2️⃣ Python dependencies (cached unless requirements.txt changes)
COPY requirements.txt .
RUN pip install --upgrade pip \
    && pip install -r requirements.txt

# 3️⃣ Copy SOURCE CODE (changes often)
COPY code/ code/

# 4️⃣ Copy DATA (changes rarely, but MUST exist)
COPY data/ data/

CMD ["python", "code/main.py"]
