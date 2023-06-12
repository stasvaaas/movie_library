FROM python:3.9

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file
COPY requirements.txt .

# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

RUN pip install waitress
RUN pip install flask_sqlalchemy
RUN pip install flask_login
RUN pip install psycopg2
COPY . /app
# Set the entry point command
CMD ["python", "app.py"]
