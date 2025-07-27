# Base image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy all files
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose no ports (Telegram bots don’t need incoming HTTP)
# EXPOSE 8000

# Run the bot
CMD ["python", "bot.py"]
