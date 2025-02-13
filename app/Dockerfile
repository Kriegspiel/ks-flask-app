# Use the official Python image
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# Install dependencies
COPY requirements.txt requirements.txt
RUN python -m pip install --upgrade pip
RUN pip install -r requirements.txt
RUN pip install gunicorn

# Copy the rest of the app code
COPY . /app
COPY boot.sh ./
RUN chmod a+x boot.sh

# Expose the port the app runs on
EXPOSE 5000

# Run the Flask app
# CMD ["python", "app.py"]
ENTRYPOINT ["sh", "./boot.sh"]
