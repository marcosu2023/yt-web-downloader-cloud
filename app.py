import os
from flask import Flask, render_template, request, redirect, url_for, send_from_directory, session, flash
import yt_dlp

APP_TITLE = "YTD Web Downloader"

# Allow overriding the download directory via env var for cloud volumes
DOWNLOAD_DIR = os.environ.get("DOWNLOAD_DIR") or os.path.join(os.path.dirname(__file__), "downloads")
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("FLASK_SECRET", "dev-secret-change-me")
PASSWORD = os.environ.get("APP_PASSWORD", "changeme")

def login_required(fn):
    from functools import wraps
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not session.get("logged_in"):
            return redirect(url_for("login", next=request.path))
        return fn(*args, **kwargs)
    return wrapper

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if request.form.get("password", "") == PASSWORD:
            session["logged_in"] = True
            flash("Login successful.", "ok")
            return redirect(request.args.get("next") or url_for("index"))
        flash("Wrong password.", "err")
    return render_template("login.html", title=APP_TITLE)

@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out.", "ok")
    return redirect(url_for("login"))

@app.route("/")
@login_required
def index():
    files = sorted([f for f in os.listdir(DOWNLOAD_DIR) if os.path.isfile(os.path.join(DOWNLOAD_DIR, f))])
    return render_template("index.html", title=APP_TITLE, files=files, download_dir=DOWNLOAD_DIR)

@app.route("/files/<path:filename>")
@login_required
def files(filename):
    return send_from_directory(DOWNLOAD_DIR, filename, as_attachment=True)

@app.route("/download", methods=["POST"])
@login_required
def download():
    url = request.form.get("url", "").strip()
    max_height = request.form.get("max_height", "1080")
    force_mp4 = request.form.get("force_mp4") == "on"

    if not url:
        flash("Please paste a video URL.", "err")
        return redirect(url_for("index"))

    fmt = f"bv*[height<={max_height}]+ba/best"
    ydl_opts = {
        "outtmpl": os.path.join(DOWNLOAD_DIR, "%(uploader)s_%(id)s.%(ext)s"),
        "restrictfilenames": True,
        "noplaylist": True,
        "format": fmt,
        "quiet": False,
        "nocheckcertificate": True,
    }

    if force_mp4:
        ydl_opts.setdefault("postprocessors", []).append({
            "key": "FFmpegVideoConvertor",
            "preferedformat": "mp4"
        })

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            # Determine final file name
            if "requested_downloads" in info and info["requested_downloads"]:
                last = info["requested_downloads"][-1]
                filename = ydl.prepare_filename(last)
            else:
                filename = ydl.prepare_filename(info)
        base_noext, _ = os.path.splitext(filename)
        final_candidate = base_noext + ".mp4"
        if os.path.exists(final_candidate):
            final_name = os.path.basename(final_candidate)
        elif os.path.exists(filename):
            final_name = os.path.basename(filename)
        else:
            final_name = None

        if final_name:
            flash(f"✅ Downloaded: {final_name}", "ok")
        else:
            flash("Downloaded, but file not found. Check server folder.", "err")
    except Exception as e:
        flash(f"❌ Error: {e}", "err")

    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
