import os
import time
import smtplib
from email.mime.text import MIMEText
from flask import Flask, request, jsonify
from celery import Celery
from celery.result import AsyncResult

# -----------------------------------------------------------------------------
# Flask app
# -----------------------------------------------------------------------------
app = Flask(__name__)

# -----------------------------------------------------------------------------
# Config: lấy từ biến môi trường
# -----------------------------------------------------------------------------
CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", CELERY_BROKER_URL)

celery = Celery(
    app.import_name,
    broker=CELERY_BROKER_URL,
    backend=CELERY_RESULT_BACKEND,
)
celery.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
)

# -----------------------------------------------------------------------------
# Tasks
# -----------------------------------------------------------------------------
@celery.task(name="tasks.heavy_job")
def heavy_job(seconds: int = 5):
    """Giả lập tác vụ nặng bằng cách ngủ 'seconds' giây."""
    time.sleep(max(1, seconds))
    return {"status": "done", "slept": seconds}

@celery.task(name="tasks.send_email_smtp")
def send_email_smtp(to: str, subject: str, body: str):
    """Gửi email thật qua SMTP (ví dụ Gmail)."""
    sender = os.getenv("SMTP_USER")
    password = os.getenv("SMTP_PASS")
    smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", "465"))

    msg = MIMEText(body, "plain", "utf-8")
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = to

    try:
        with smtplib.SMTP_SSL(smtp_host, smtp_port) as server:
            server.login(sender, password)
            server.sendmail(sender, [to], msg.as_string())
        return {"status": "sent", "to": to}
    except Exception as e:
        return {"status": "error", "error": str(e)}

# -----------------------------------------------------------------------------
# Routes
# -----------------------------------------------------------------------------
@app.route("/", methods=["GET"])
def health():
    return jsonify({"ok": True, "service": "flask+celery+redis"}), 200

@app.route("/run-heavy", methods=["POST"])
def run_heavy():
    data = request.get_json(silent=True) or {}
    seconds = int(data.get("seconds", 5))
    task = heavy_job.delay(seconds)
    return jsonify({"message": "Task accepted", "task_id": task.id}), 202

@app.route("/send-email-smtp", methods=["POST"])
def send_email_smtp_route():
    data = request.get_json(silent=True) or {}
    to = data.get("to")
    subject = data.get("subject", "(No subject)")
    body = data.get("body", "")
    if not to:
        return jsonify({"error": "Missing 'to'"}), 400
    task = send_email_smtp.delay(to, subject, body)
    return jsonify({"message": "Email queued (SMTP)", "task_id": task.id}), 202

@app.route("/task-status/<task_id>", methods=["GET"])
def task_status(task_id):
    res: AsyncResult = celery.AsyncResult(task_id)
    response = {
        "task_id": task_id,
        "state": res.state,
        "ready": res.ready(),
    }
    if res.ready():
        response["result"] = res.result
    return jsonify(response), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")), debug=True)