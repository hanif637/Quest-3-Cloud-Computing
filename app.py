import os
from datetime import datetime
from zoneinfo import ZoneInfo

from flask import Flask, render_template, jsonify
from prometheus_flask_exporter import PrometheusMetrics

app = Flask(__name__)
metrics = PrometheusMetrics(app, path="/metrics", group_by="endpoint")
metrics.info(
    "smart_city_jember_app_info",
    "Smart City Jember Flask application information",
    version=os.getenv("APP_VERSION", "1.0.0"),
)


@app.get("/")
def dashboard():
    # NIM diambil dari environment variable yang diberikan saat docker run.
    nim = os.getenv("NIM", "Belum diatur")
    waktu_update = datetime.now(ZoneInfo("Asia/Jakarta")).strftime("%d %B %Y, %H:%M:%S WIB")

    # Data berikut adalah data contoh untuk demonstrasi tugas, bukan pembacaan sensor nyata.
    sensor = [
        {
            "nama": "Titik Pantau Pusat Kota",
            "kode": "JBR-001",
            "suhu": 29.4,
            "kelembapan": 76,
            "status": "Normal",
        },
        {
            "nama": "Titik Pantau Area Perkantoran",
            "kode": "JBR-002",
            "suhu": 30.1,
            "kelembapan": 71,
            "status": "Normal",
        },
    ]

    return render_template(
        "index.html",
        nim=nim,
        waktu_update=waktu_update,
        sensor=sensor,
    )


@app.get("/health")
def health():
    return jsonify({"status": "ok", "app": "Smart City Jember Sensor Dashboard"})


if __name__ == "__main__":
    port = int(os.getenv("PORT", "5000"))
    app.run(host="0.0.0.0", port=port)
