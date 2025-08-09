# syntax=docker/dockerfile:1
FROM python:3.11-slim

# Install ffmpeg (for yt-dlp merge/recode)
RUN apt-get update && apt-get install -y --no-install-recommends ffmpeg && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app/

# Default envs
ENV PORT=5000 \
    FLASK_SECRET=change-me-in-env \
    APP_PASSWORD=changeme \
    DOWNLOAD_DIR=/data/downloads

# Create mount point for persistent volume
RUN mkdir -p /data/downloads && mkdir -p /app/downloads

EXPOSE 5000

# Start with gunicorn
CMD ["gunicorn", "-w", "2", "-b", "0.0.0.0:5000", "app:app"]
