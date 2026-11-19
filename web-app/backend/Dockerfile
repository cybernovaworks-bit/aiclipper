# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Install system dependencies including FFmpeg
RUN apt-get update && \
    apt-get install -y ffmpeg && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the current directory contents into the container at /app
COPY . .

# Create necessary temp and static directories
RUN mkdir -p temp static/clips

# Make port 7860 available to the world outside this container (Hugging Face default)
ENV PORT=7860
EXPOSE 7860

# Run uvicorn server
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]
