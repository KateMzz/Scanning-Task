# Use the Playwright image as the base image
FROM mcr.microsoft.com/playwright/python:v1.39.0-jammy

# Install Poetry
ADD . /app
WORKDIR app/scraper_logic

RUN pip install --no-cache-dir poetry==1.5.1 \
    && poetry config virtualenvs.create false


# Set the working directory in the container


# Copy the poetry files and install dependencies
COPY pyproject.toml /app
RUN poetry install --no-root ; mkdir /app/logs

# Copy your Python script and other necessary files
COPY . .

# Run your Python script
CMD ["python", "main.py"]


