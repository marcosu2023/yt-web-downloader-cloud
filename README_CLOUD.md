# YTD Web Downloader — Cloud Deployment

This folder contains a cloud-ready version of the tiny Flask app that wraps **yt-dlp**. It includes a Dockerfile (with FFmpeg) and an example `render.yaml` for easy deployment.

> Use responsibly — only download content you have the right to download. Some sites' Terms of Service may prohibit downloading.

## Option A — Deploy to Render (recommended for beginners)

1. **Push** this folder to a new GitHub repo.
2. In **Render Dashboard** → *New* → *Web Service* → *Build from a repository* → select your repo.
3. When Render detects the **Dockerfile**, it will build automatically.
4. In the service settings:
   - **Advanced → Disks**: add a disk (e.g., 10 GB) and set **Mount Path**: `/data`.
   - **Environment variables**:
     - `APP_PASSWORD`: set your own strong password.
     - `FLASK_SECRET`: any long random string.
     - `DOWNLOAD_DIR`: `/data/downloads`
5. Click **Create Web Service** and wait for deploy to finish.
6. Open the Render URL, log in with your password, paste a video URL, and download. Files persist on the attached disk.

## Option B — Deploy to Railway

1. Create a new project and service from your GitHub repo.
2. Add a **Volume** and mount it at `/data` (size as needed).
3. Set env vars:
   - `APP_PASSWORD` (your password)
   - `FLASK_SECRET` (random string)
   - `DOWNLOAD_DIR` = `/data/downloads`
4. Deploy and use the generated public URL.

## Option C — Self-host on a VPS (Docker)

```bash
docker build -t ytd-web .
docker run -d --name ytd-web -p 80:5000 -e APP_PASSWORD=YourSecret ^
  -v /opt/ytd-data:/data ytd-web
```

Files will be on the server in `/opt/ytd-data/downloads`.

## Notes

- The app runs downloads **server-side**. Your personal computer can be off; the server handles everything.
- Persistent storage is required to keep files between redeploys/restarts.
- For large/long downloads, a background worker & queue would be more robust; this simple app performs downloads synchronously per request (works fine for short/medium videos).
- Security: change the default password immediately, and consider IP allowlists or extra auth if exposing to the public internet.
