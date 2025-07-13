# Use an official Python runtime as a parent image
FROM python:3.10-slim-buster

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# application code into the container at /app

# .
# ├── main.py
# ├── .env
# ├── database/
# │   ├── __init__.py
# │   ├── engine.py
# │   ├── models.py
# │   └── db_interface.py
# └── operations/
#     ├── __init__.py
#     ├── models.py
#     └── stats_monitor.py
COPY . .

CMD ["python", "main.py"]
