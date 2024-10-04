# Use the official Python image as the base image
FROM python:3.12.3

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy the rest of the application code
COPY . .

# Run dbt commands
ENTRYPOINT ["dbt"]
CMD ["build"]