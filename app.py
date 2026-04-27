import csv
import io
import sqlite3
import os
from datetime import datetime
from flask import Flask, render_template, request, jsonify, Response

app = Flask(__name__)
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "restaurant.db")


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            guests INTEGER NOT NULL,
            date TEXT NOT NULL,
            time TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()


@app.route("/")
def index():
    conn = get_db()
    bookings = conn.execute("SELECT * FROM bookings ORDER BY date, time").fetchall()
    conn.close()
    return render_template("index.html", bookings=bookings)


@app.route("/book", methods=["POST"])
def book():
    data = request.get_json()
    name = data.get("name", "").strip()
    guests = data.get("guests")
    date = data.get("date", "").strip()
    time_slot = data.get("time", "").strip()

    if not name:
        return jsonify({"error": "Name is required"}), 400
    if not guests or int(guests) < 1:
        return jsonify({"error": "At least 1 guest required"}), 400
    if int(guests) > 20:
        return jsonify({"error": "Maximum 20 guests per booking"}), 400
    if not date:
        return jsonify({"error": "Date is required"}), 400
    if not time_slot:
        return jsonify({"error": "Time slot is required"}), 400

    conn = get_db()
    conn.execute(
        "INSERT INTO bookings (name, guests, date, time) VALUES (?, ?, ?, ?)",
        (name, int(guests), date, time_slot),
    )
    conn.commit()
    conn.close()
    return jsonify({"success": True, "message": f"Booking confirmed for {name}"})


@app.route("/cancel/<int:booking_id>", methods=["POST"])
def cancel(booking_id):
    conn = get_db()
    row = conn.execute("SELECT * FROM bookings WHERE id = ?", (booking_id,)).fetchone()
    if not row:
        conn.close()
        return jsonify({"error": "Booking not found"}), 404
    conn.execute("DELETE FROM bookings WHERE id = ?", (booking_id,))
    conn.commit()
    conn.close()
    return jsonify({"success": True, "message": "Booking cancelled"})


@app.route("/api/bookings")
def api_bookings():
    conn = get_db()
    bookings = conn.execute("SELECT * FROM bookings ORDER BY date, time").fetchall()
    conn.close()
    result = [
        {
            "id": b["id"],
            "name": b["name"],
            "guests": b["guests"],
            "date": b["date"],
            "time": b["time"],
        }
        for b in bookings
    ]
    return jsonify(result)


@app.route("/api/stats")
def api_stats():
    conn = get_db()
    total = conn.execute("SELECT COUNT(*) as c FROM bookings").fetchone()["c"]
    upcoming = conn.execute(
        "SELECT COUNT(*) as c FROM bookings WHERE date >= ?",
        (datetime.now().strftime("%Y-%m-%d"),),
    ).fetchone()["c"]
    total_guests = conn.execute(
        "SELECT COALESCE(SUM(guests), 0) as s FROM bookings"
    ).fetchone()["s"]
    popular_time = conn.execute(
        "SELECT time, COUNT(*) as c FROM bookings GROUP BY time ORDER BY c DESC LIMIT 1"
    ).fetchone()
    busiest_day = conn.execute(
        "SELECT date, COUNT(*) as c FROM bookings GROUP BY date ORDER BY c DESC LIMIT 1"
    ).fetchone()
    conn.close()
    return jsonify({
        "total_bookings": total,
        "upcoming_bookings": upcoming,
        "total_guests": total_guests,
        "popular_time": popular_time["time"] if popular_time else None,
        "busiest_day": busiest_day["date"] if busiest_day else None,
    })


@app.route("/api/bookings/export")
def export_bookings():
    conn = get_db()
    bookings = conn.execute("SELECT * FROM bookings ORDER BY date, time").fetchall()
    conn.close()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["ID", "Name", "Guests", "Date", "Time", "Created At"])
    for b in bookings:
        writer.writerow([b["id"], b["name"], b["guests"], b["date"], b["time"], b["created_at"]])

    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment; filename=bookings_{datetime.now().strftime('%Y%m%d')}.csv"},
    )


@app.route("/health")
def health():
    status = {"status": "healthy", "timestamp": datetime.utcnow().isoformat() + "Z"}
    try:
        conn = get_db()
        conn.execute("SELECT 1")
        conn.close()
        status["database"] = "connected"
    except Exception:
        status["status"] = "degraded"
        status["database"] = "disconnected"
    return jsonify(status)


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=3000, debug=True)
