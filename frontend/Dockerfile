FROM python:3.11-slim

# Non-interactive so that installations do not ask for input
ENV debian_frontend=noninteractive

# Install linux packages
# RUN apt-get update && apt-get install -y \
#     vim \
#     && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Copy python requirements and pip install
COPY requirements.txt requirements.txt 
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy the rest of the files
COPY . .

EXPOSE 8501

# Run the python script
CMD ["streamlit", "run", "src/app.py"]