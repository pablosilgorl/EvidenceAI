# Use the official Python image
FROM python:3.9

# Set the working directory in the container
#WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install dependencies
RUN pip install -r requirements.txt

# Copy the rest of the application code into the container
COPY . .

# Expose the port your app will run on
EXPOSE 5000

# Define the command to run your app
CMD ["python", "convos.py"]
