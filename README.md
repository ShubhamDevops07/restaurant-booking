# Restaurant Booking System

A simple table reservation system built with **Python Flask + SQLite** for managing dinner bookings with a calendar view.

---

## File Structure

```
restaurant-booking/
  |-- app.py                 # The brain (Python server)
  |-- restaurant.db          # The memory (database, auto-created)
  |-- templates/
      |-- index.html         # The face (what users see in browser)
```

### What each file does

| File | Purpose |
|---|---|
| **app.py** | The server - receives requests from browser, talks to database, sends responses back |
| **restaurant.db** | SQLite database - stores all bookings permanently (auto-created on first run) |
| **templates/index.html** | The webpage - booking form, calendar, and all visual stuff the user sees |

---

## How It Works

Think of it like a real restaurant:

```
Customer (Browser)  --->  Waiter (app.py)  --->  Notebook (restaurant.db)
   "Book a table"         "Let me write          "Stored permanently"
                           that down"
```

1. User opens browser at `localhost:3000`
2. Browser asks `app.py` for the page
3. `app.py` sends `templates/index.html` to the browser
4. User fills the form and clicks "Reserve Table"
5. Browser sends booking data to `app.py`
6. `app.py` saves it in `restaurant.db`
7. `app.py` tells browser "Booking confirmed!"
8. Calendar refreshes to show the new booking

---

## Features

- **Booking Form** - Takes name, number of guests, date, and dinner time (5 PM - 10 PM)
- **Calendar View** - Monthly calendar showing all bookings with dots on booked dates
- **Day Detail** - Click any day to see the full list of bookings
- **Cancel Bookings** - Remove any booking with one click
- **Permanent Storage** - SQLite database keeps bookings even after server restart
- **Multi-Device** - Any device on the network can access the bookings
- **Responsive Design** - Works on desktop, tablet, and mobile

---

## Setup & Run

### Prerequisites

- Python 3.x
- Flask (`pip install flask`)

### Steps

```bash
# 1. Clone the repo
git clone https://github.com/ShubhamDevops07/restaurant-booking.git
cd restaurant-booking

# 2. Install Flask
pip install flask

# 3. Run the server
python app.py
```

Open your browser and go to **http://localhost:3000**

---

## Tech Stack

| Technology | Used For |
|---|---|
| **Python** | Backend server language |
| **Flask** | Web framework (handles browser requests & responses) |
| **SQLite** | Database (stores bookings in a file, no setup needed) |
| **HTML** | Page structure (form, calendar layout) |
| **CSS** | Styling (dark theme, responsive grid) |
| **JavaScript** | Frontend logic (calendar rendering, AJAX calls, no page reloads) |

---

## Code Explanation

### app.py - The Server

#### Imports
```python
import sqlite3          # To talk to the database
import os               # To handle file paths
from flask import Flask, render_template, request, jsonify
```
- `Flask` = the web framework that handles browser requests
- `render_template` = loads HTML files from the templates/ folder
- `request` = reads data sent by the browser
- `jsonify` = converts Python data to JSON (language browsers understand)

#### Database Setup
```python
def init_db():
    conn.execute("""
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,  -- Unique ID (1, 2, 3...)
            name TEXT NOT NULL,                     -- Customer name
            guests INTEGER NOT NULL,                -- How many people
            date TEXT NOT NULL,                      -- Booking date
            time TEXT NOT NULL,                      -- Dinner time
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
```
Runs once on startup. Creates the bookings table if it doesn't exist — like drawing columns in a new notebook.

#### 4 Routes (API Endpoints)

| Route | Method | What it does |
|---|---|---|
| `/` | GET | Shows the main page with the form and calendar |
| `/book` | POST | Receives booking data, validates it, saves to database |
| `/cancel/<id>` | POST | Deletes a booking by its ID |
| `/api/bookings` | GET | Returns all bookings as JSON (used by calendar to refresh) |

#### Booking Flow
```
Browser sends: {name: "John", guests: 4, date: "2026-04-15", time: "7:00 PM"}
    |
Server validates (checks nothing is empty)
    |
Server saves to SQLite: INSERT INTO bookings VALUES (...)
    |
Server responds: {success: true, message: "Booking confirmed for John"}
```

### templates/index.html - The Webpage

Three main parts:

1. **HTML** - Two-panel layout (booking form on left, calendar on right)
2. **CSS** - Dark theme with colors `#0f0f23` (background), `#1a1a2e` (panels), `#e94560` (accent red)
3. **JavaScript** - Key functions:

| Function | What it does |
|---|---|
| `fetchBookings()` | Calls `/api/bookings`, gets all bookings, renders calendar |
| `renderCalendar()` | Draws the month grid, places dots on days with bookings |
| `selectDay(date)` | Highlights a day, shows its bookings below the calendar |
| `showDay(date)` | Displays booking cards for the selected date |
| `cancelBooking(id)` | Calls `/cancel/id`, then refreshes the calendar |
| Form submit handler | Sends data to `/book` via fetch(), refreshes on success |

---

## Why Python/Flask Over Plain HTML?

```
Plain HTML:  Browser --> localStorage (temporary, single device)
Flask:       Browser --> Server (app.py) --> Database (permanent, any device)
```

The server acts as a **central point** — everyone connects to it, everyone sees the same bookings. That's essential for a real restaurant where multiple staff members need access.

| Feature | Plain HTML/JS | Python Flask |
|---|---|---|
| **Speed** | Instant, no server needed | Slightly slower (server requests) |
| **Data storage** | Browser only (lost if cleared) | SQLite database (permanent) |
| **Multi-device** | Single browser only | Any device on the network |
| **Multi-user** | Single user only | Multiple staff can use it |
| **Scalability** | Limited | Can grow with your restaurant |
