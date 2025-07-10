# Use an official Python runtime as a parent image
FROM python:3.10-slim-buster

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container at /app
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application code into the container at /app
# Assuming your project structure is:
# .
# ├── main.py
# ├── .env
# ├── database/
# │   ├── __init__.py
# │   ├── engine.py
# │   ├── models.py
# │   └── db_interface.py
# └── operations/
#     ├── __init__.py
#     ├── models.py
#     └── stats_monitor.py
COPY . .

# Command to run the application
# This will execute your main.py script
CMD ["python", "main.py"]
