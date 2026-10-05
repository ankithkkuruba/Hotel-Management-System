from flask import Flask, request, redirect, session
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

app = Flask(__name__)

app.secret_key = "grand_horizon_2026"

DB = "hotel.db"


# =========================================================
# DATABASE
# =========================================================

def db():
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    return con


def setup():

    con = db()

    # USERS TABLE
    con.execute("""
        CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT DEFAULT 'customer'
        )
    """)

    # ROOMS TABLE
    con.execute("""
        CREATE TABLE IF NOT EXISTS rooms(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            number TEXT UNIQUE NOT NULL,
            type TEXT NOT NULL,
            price REAL NOT NULL,
            capacity INTEGER NOT NULL,
            description TEXT
        )
    """)

    # BOOKINGS TABLE
    con.execute("""
        CREATE TABLE IF NOT EXISTS bookings(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            room_id INTEGER,
            check_in TEXT,
            check_out TEXT,
            guests INTEGER,
            total REAL
        )
    """)

    # CREATE DEFAULT ADMIN
    admin = con.execute(
        "SELECT * FROM users WHERE email=?",
        ("admin@grandhorizon.com",)
    ).fetchone()

    if not admin:

        con.execute("""
            INSERT INTO users(name,email,password,role)
            VALUES(?,?,?,?)
        """, (
            "Administrator",
            "admin@grandhorizon.com",
            generate_password_hash("admin123"),
            "admin"
        ))

    # CREATE DEFAULT ROOMS
    if con.execute("SELECT COUNT(*) FROM rooms").fetchone()[0] == 0:

        rooms = [

            (
                "101",
                "Deluxe Room",
                4500,
                2,
                "A comfortable and elegant room with modern facilities, a cozy bed and a relaxing atmosphere."
            ),

            (
                "201",
                "Executive Suite",
                7500,
                3,
                "A spacious executive suite designed for business travelers and guests looking for extra comfort."
            ),

            (
                "301",
                "Luxury Suite",
                12000,
                4,
                "Our premium suite offering elegant interiors, spacious accommodation and a luxurious experience."
            ),

            (
                "401",
                "Family Room",
                6500,
                4,
                "A large and comfortable room specially designed for families and group travelers."
            )

        ]

        con.executemany("""
            INSERT INTO rooms(
                number,
                type,
                price,
                capacity,
                description
            )
            VALUES(?,?,?,?,?)
        """, rooms)

    con.commit()
    con.close()


# =========================================================
# DESIGN
# =========================================================

CSS = """
<style>

* {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
}

body {
    font-family: Arial, Helvetica, sans-serif;
    background: #f7f5f0;
    color: #222;
    line-height: 1.6;
}

nav {
    height: 75px;
    background: #111;
    color: white;
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0 7%;
    position: sticky;
    top: 0;
    z-index: 1000;
}

.logo {
    font-size: 25px;
    font-weight: bold;
    color: #d4af37;
    letter-spacing: 1px;
}

.nav-links {
    display: flex;
    align-items: center;
    gap: 25px;
}

.nav-links a {
    color: white;
    text-decoration: none;
    font-size: 15px;
    transition: 0.3s;
}

.nav-links a:hover {
    color: #d4af37;
}

.nav-btn {
    border: 1px solid #d4af37;
    padding: 8px 17px;
    border-radius: 5px;
}

.hero {
    min-height: 600px;

    background:
        linear-gradient(
            rgba(0,0,0,0.58),
            rgba(0,0,0,0.58)
        ),
        url('/static/images/hotel.jpg') center/cover;

    display: flex;
    align-items: center;
    justify-content: center;
    text-align: center;
    color: white;
}

.hero-content {
    max-width: 850px;
    padding: 30px;
}

.hero small {
    color: #d4af37;
    font-size: 17px;
    letter-spacing: 3px;
    text-transform: uppercase;
}

.hero h1 {
    font-size: 58px;
    margin: 20px 0;
    line-height: 1.1;
}

.hero p {
    font-size: 20px;
    margin-bottom: 30px;
    color: #eee;
}

.btn {
    display: inline-block;
    background: #c19a32;
    color: white;
    padding: 12px 24px;
    border-radius: 5px;
    text-decoration: none;
    border: none;
    cursor: pointer;
    font-size: 15px;
    transition: 0.3s;
}

.btn:hover {
    background: #a68120;
    transform: translateY(-2px);
}

.btn-dark {
    background: #111;
}

.btn-danger {
    background: #a83232;
}

.container {
    width: 90%;
    max-width: 1150px;
    margin: 70px auto;
}

.section-title {
    text-align: center;
    margin-bottom: 45px;
}

.section-title small {
    color: #b18b28;
    font-weight: bold;
    letter-spacing: 2px;
    text-transform: uppercase;
}

.section-title h1 {
    font-size: 38px;
    margin-top: 10px;
}

.section-title p {
    color: #777;
    max-width: 650px;
    margin: 10px auto;
}

.grid {
    display: grid;
    grid-template-columns: repeat(
        auto-fit,
        minmax(250px, 1fr)
    );
    gap: 28px;
}

.card {
    background: white;
    border-radius: 10px;
    overflow: hidden;
    box-shadow: 0 5px 25px rgba(0,0,0,0.08);
    transition: 0.3s;
}

.card:hover {
    transform: translateY(-6px);
    box-shadow: 0 12px 30px rgba(0,0,0,0.13);
}

.card-content {
    padding: 25px;
}

.card h2 {
    margin-bottom: 10px;
}

.card p {
    color: #666;
    margin: 7px 0;
}

.room-price {
    color: #b18b28 !important;
    font-size: 21px;
    font-weight: bold;
    margin: 15px 0 !important;
}

.room-image {
    width: 100%;
    height: 220px;
    object-fit: cover;
}

.feature-section {
    background: #111;
    color: white;
    padding: 70px 5%;
}

.feature {
    text-align: center;
    padding: 25px;
}

.feature-icon {
    font-size: 42px;
    margin-bottom: 15px;
}

.feature h3 {
    margin-bottom: 10px;
    color: #d4af37;
}

.feature p {
    color: #bbb;
}

.info-box {
    background: white;
    padding: 40px;
    border-radius: 10px;
    box-shadow: 0 5px 25px rgba(0,0,0,0.07);
}

form {
    background: white;
    padding: 40px;
    border-radius: 12px;
    max-width: 560px;
    margin: 60px auto;
    box-shadow: 0 8px 30px rgba(0,0,0,0.08);
}

form h1 {
    text-align: center;
    margin-bottom: 25px;
}

label {
    font-weight: bold;
    display: block;
    margin-top: 10px;
}

input,
select,
textarea {
    width: 100%;
    padding: 13px;
    margin: 8px 0 18px;
    border: 1px solid #ddd;
    border-radius: 6px;
    font-size: 15px;
}

input:focus,
select:focus,
textarea:focus {
    outline: none;
    border-color: #c19a32;
}

textarea {
    min-height: 120px;
    resize: vertical;
}

.form-footer {
    text-align: center;
    margin-top: 20px;
}

.form-footer a {
    color: #a68120;
    font-weight: bold;
}

.error {
    background: #ffe1e1;
    color: #9b1c1c;
    padding: 12px;
    border-radius: 6px;
    margin-bottom: 15px;
}

.success {
    background: #ddf7df;
    color: #176b20;
    padding: 12px;
    border-radius: 6px;
    margin-bottom: 15px;
}

.dashboard-header {
    background: #111;
    color: white;
    padding: 50px;
    border-radius: 12px;
    margin-bottom: 35px;
}

.dashboard-header h1 {
    font-size: 35px;
}

.stats {
    display: grid;
    grid-template-columns:
        repeat(auto-fit, minmax(200px,1fr));
    gap: 20px;
    margin-bottom: 35px;
}

.stat {
    background: white;
    padding: 30px;
    border-radius: 10px;
    box-shadow: 0 5px 20px rgba(0,0,0,0.07);
}

.stat h2 {
    color: #b18b28;
    font-size: 32px;
}

.stat p {
    color: #777;
}

table {
    width: 100%;
    background: white;
    border-collapse: collapse;
    border-radius: 10px;
    overflow: hidden;
    box-shadow: 0 5px 20px rgba(0,0,0,0.06);
}

th {
    background: #111;
    color: white;
}

th,
td {
    padding: 15px;
    border-bottom: 1px solid #eee;
    text-align: left;
}

td .btn {
    padding: 7px 12px;
    font-size: 13px;
}

.admin-actions {
    margin-bottom: 25px;
}

footer {
    background: #111;
    color: #aaa;
    text-align: center;
    padding: 35px 20px;
    margin-top: 80px;
}

footer strong {
    color: #d4af37;
}

@media(max-width: 768px) {

    nav {
        height: auto;
        padding: 18px 5%;
        flex-direction: column;
        gap: 15px;
    }

    .nav-links {
        gap: 12px;
        flex-wrap: wrap;
        justify-content: center;
    }

    .hero {
        min-height: 500px;
    }

    .hero h1 {
        font-size: 38px;
    }

    .hero p {
        font-size: 17px;
    }

    .container {
        margin: 45px auto;
    }

    .section-title h1 {
        font-size: 30px;
    }

    table {
        display: block;
        overflow-x: auto;
    }
}

</style>
"""


# =========================================================
# PAGE TEMPLATE
# =========================================================

def page(title, body):

    nav = """
    <nav>

        <div class="logo">
            GRAND HORIZON
        </div>

        <div class="nav-links">

            <a href="/">
                Home
            </a>

            <a href="/rooms">
                Rooms
            </a>

            <a href="/about">
                About
            </a>

            <a href="/contact">
                Contact
            </a>
    """

    if session.get("role") == "admin":

        nav += """
            <a href="/admin">
                Admin Dashboard
            </a>

            <a class="nav-btn" href="/logout">
                Logout
            </a>
        """

    elif session.get("user_id"):

        nav += """
            <a href="/dashboard">
                Dashboard
            </a>

            <a href="/booking">
                Book Now
            </a>

            <a class="nav-btn" href="/logout">
                Logout
            </a>
        """

    else:

        nav += """
            <a href="/login">
                Login
            </a>

            <a class="nav-btn" href="/register">
                Register
            </a>
        """

    nav += """
        </div>
    </nav>
    """

    return f"""
    <!DOCTYPE html>

    <html>

    <head>

        <meta charset="UTF-8">

        <meta name="viewport"
              content="width=device-width, initial-scale=1.0">

        <title>
            {title} | Grand Horizon Hotel
        </title>

        {CSS}

    </head>

    <body>

        {nav}

        {body}

        <footer>

            <strong>
                GRAND HORIZON HOTEL
            </strong>

            <br>

            Luxury • Comfort • Hospitality

            <br><br>

            © 2026 Grand Horizon Hotel.
            All Rights Reserved.

        </footer>

    </body>

    </html>
    """


# =========================================================
# HOME
# =========================================================

@app.route("/")
def home():

    con = db()

    rooms = con.execute(
        "SELECT * FROM rooms LIMIT 4"
    ).fetchall()

    con.close()

    cards = ""

    for r in rooms:

        cards += f"""
        <div class="card">

            <div class="card-content">

                <h2>
                    {r['type']}
                </h2>

                <p>
                    <strong>
                        Room {r['number']}
                    </strong>
                </p>

                <p>
                    👥 Capacity:
                    {r['capacity']} guests
                </p>

                <p class="room-price">
                    ₹{r['price']:,.0f} / night
                </p>

                <a class="btn"
                   href="/room/{r['id']}">
                    View Details
                </a>

            </div>

        </div>
        """

    return page(
        "Home",
        f"""

        <section class="hero">

            <div class="hero-content">

                <small>
                    Welcome to Grand Horizon
                </small>

                <h1>
                    Experience Luxury.
                    <br>
                    Experience Comfort.
                </h1>

                <p>
                    Discover an unforgettable stay
                    with exceptional hospitality
                    and elegant rooms.
                </p>

                <a class="btn" href="/rooms">
                    Explore Our Rooms
                </a>

            </div>

        </section>


        <div class="container">

            <div class="section-title">

                <small>
                    Accommodation
                </small>

                <h1>
                    Our Featured Rooms
                </h1>

                <p>
                    Choose from our carefully designed
                    rooms and suites for a comfortable
                    and memorable stay.
                </p>

            </div>

            <div class="grid">

                {cards}

            </div>

        </div>


        <section class="feature-section">

            <div class="grid">

                <div class="feature">

                    <div class="feature-icon">
                        🏨
                    </div>

                    <h3>
                        Luxury Rooms
                    </h3>

                    <p>
                        Elegant rooms designed
                        for your comfort.
                    </p>

                </div>


                <div class="feature">

                    <div class="feature-icon">
                        ⭐
                    </div>

                    <h3>
                        Premium Service
                    </h3>

                    <p>
                        Exceptional hospitality
                        throughout your stay.
                    </p>

                </div>


                <div class="feature">

                    <div class="feature-icon">
                        🔐
                    </div>

                    <h3>
                        Secure Booking
                    </h3>

                    <p>
                        Simple and reliable
                        online room booking.
                    </p>

                </div>

            </div>

        </section>

        """
    )


# =========================================================
# ROOMS
# =========================================================

@app.route("/rooms")
def rooms():

    con = db()

    rooms = con.execute(
        "SELECT * FROM rooms"
    ).fetchall()

    con.close()

    cards = ""

    for r in rooms:

        cards += f"""
        <div class="card">

            <div class="card-content">

                <h2>
                    {r['type']}
                </h2>

                <p>
                    Room Number:
                    {r['number']}
                </p>

                <p>
                    {r['description']}
                </p>

                <p>
                    👥 {r['capacity']} Guests
                </p>

                <p class="room-price">
                    ₹{r['price']:,.0f} / night
                </p>

                <a class="btn"
                   href="/room/{r['id']}">
                    View Room
                </a>

            </div>

        </div>
        """

    return page(
        "Rooms",
        f"""

        <div class="container">

            <div class="section-title">

                <small>
                    Stay With Us
                </small>

                <h1>
                    Our Rooms & Suites
                </h1>

                <p>
                    Find the perfect room for your
                    stay at Grand Horizon Hotel.
                </p>

            </div>

            <div class="grid">

                {cards}

            </div>

        </div>

        """
    )


# =========================================================
# ROOM DETAILS
# =========================================================

@app.route("/room/<int:room_id>")
def room(room_id):

    con = db()

    r = con.execute(
        "SELECT * FROM rooms WHERE id=?",
        (room_id,)
    ).fetchone()

    con.close()

    if not r:
        return "Room not found", 404

    return page(
        r["type"],
        f"""

        <div class="container">

            <div class="info-box">

                <div class="section-title">

                    <small>
                        Room Details
                    </small>

                    <h1>
                        {r['type']}
                    </h1>

                </div>

                <h2>
                    Room {r['number']}
                </h2>

                <br>

                <p>
                    {r['description']}
                </p>

                <br>

                <p>
                    👥 Maximum Capacity:
                    <strong>
                        {r['capacity']} guests
                    </strong>
                </p>

                <p class="room-price">
                    ₹{r['price']:,.0f} / night
                </p>

                <br>

                <a class="btn"
                   href="/booking?room={r['id']}">
                    Book This Room
                </a>

                <a class="btn btn-dark"
                   href="/rooms">
                    Back to Rooms
                </a>

            </div>

        </div>

        """
    )


# =========================================================
# REGISTER
# =========================================================

@app.route("/register", methods=["GET", "POST"])
def register():

    error = ""

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]

        con = db()

        try:

            con.execute("""
                INSERT INTO users(
                    name,
                    email,
                    password
                )
                VALUES(?,?,?)
            """, (
                name,
                email,
                generate_password_hash(password)
            ))

            con.commit()
            con.close()

            return redirect("/login")

        except sqlite3.IntegrityError:

            error = "This email is already registered."

            con.close()

    return page(
        "Register",
        f"""

        <form method="POST">

            <h1>
                Create Account
            </h1>

            <p style="text-align:center;color:#777;margin-bottom:25px;">
                Join Grand Horizon Hotel today
            </p>

            {f'<div class="error">{error}</div>' if error else ''}

            <label>
                Full Name
            </label>

            <input
                type="text"
                name="name"
                placeholder="Enter your full name"
                required
            >

            <label>
                Email Address
            </label>

            <input
                type="email"
                name="email"
                placeholder="Enter your email"
                required
            >

            <label>
                Password
            </label>

            <input
                type="password"
                name="password"
                placeholder="Create a password"
                required
            >

            <button class="btn"
                    style="width:100%;">
                Create Account
            </button>

            <div class="form-footer">

                Already have an account?

                <a href="/login">
                    Login here
                </a>

            </div>

        </form>

        """
    )


# =========================================================
# LOGIN
# =========================================================

@app.route("/login", methods=["GET", "POST"])
def login():

    error = ""

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        con = db()

        user = con.execute(
            "SELECT * FROM users WHERE email=?",
            (email,)
        ).fetchone()

        con.close()

        if user and check_password_hash(
            user["password"],
            password
        ):

            session["user_id"] = user["id"]
            session["name"] = user["name"]
            session["role"] = user["role"]

            if user["role"] == "admin":
                return redirect("/admin")

            return redirect("/dashboard")

        error = "Invalid email or password."

    return page(
        "Login",
        f"""

        <form method="POST">

            <h1>
                Welcome Back
            </h1>

            <p style="text-align:center;color:#777;margin-bottom:25px;">
                Login to continue
            </p>

            {f'<div class="error">{error}</div>' if error else ''}

            <label>
                Email Address
            </label>

            <input
                type="email"
                name="email"
                placeholder="Enter your email"
                required
            >

            <label>
                Password
            </label>

            <input
                type="password"
                name="password"
                placeholder="Enter your password"
                required
            >

            <button class="btn"
                    style="width:100%;">
                Login
            </button>

            <div class="form-footer">

                Don't have an account?

                <a href="/register">
                    Create one
                </a>

            </div>

        </form>

        """
    )


# =========================================================
# LOGOUT
# =========================================================

@app.route("/logout")
def logout():

    session.clear()

    return redirect("/")


# =========================================================
# CUSTOMER DASHBOARD
# =========================================================

@app.route("/dashboard")
def dashboard():

    if not session.get("user_id"):
        return redirect("/login")

    con = db()

    bookings = con.execute("""
        SELECT
            bookings.*,
            rooms.number,
            rooms.type
        FROM bookings

        JOIN rooms
        ON bookings.room_id = rooms.id

        WHERE bookings.user_id=?

        ORDER BY bookings.id DESC
    """, (
        session["user_id"],
    )).fetchall()

    con.close()

    rows = ""

    for b in bookings:

        rows += f"""
        <tr>

            <td>
                #{b['id']}
            </td>

            <td>
                {b['type']}
                <br>
                <small>
                    Room {b['number']}
                </small>
            </td>

            <td>
                {b['check_in']}
            </td>

            <td>
                {b['check_out']}
            </td>

            <td>
                {b['guests']}
            </td>

            <td>
                ₹{b['total']:,.0f}
            </td>

        </tr>
        """

    if not rows:

        rows = """
        <tr>

            <td colspan="6"
                style="text-align:center;">

                You have no bookings yet.

            </td>

        </tr>
        """

    return page(
        "Dashboard",
        f"""

        <div class="container">

            <div class="dashboard-header">

                <p style="color:#d4af37;">
                    CUSTOMER DASHBOARD
                </p>

                <h1>
                    Welcome,
                    {session['name']}!
                </h1>

                <p style="color:#bbb;">
                    Manage your bookings and plan
                    your next stay.
                </p>

            </div>


            <div class="stats">

                <div class="stat">

                    <p>
                        Total Bookings
                    </p>

                    <h2>
                        {len(bookings)}
                    </h2>

                </div>


                <div class="stat">

                    <p>
                        Hotel
                    </p>

                    <h2>
                        Grand
                    </h2>

                </div>


                <div class="stat">

                    <p>
                        Booking
                    </p>

                    <h2>
                        Online
                    </h2>

                </div>

            </div>


            <div class="info-box">

                <h2>
                    My Bookings
                </h2>

                <br>

                <table>

                    <tr>

                        <th>
                            ID
                        </th>

                        <th>
                            Room
                        </th>

                        <th>
                            Check-in
                        </th>

                        <th>
                            Check-out
                        </th>

                        <th>
                            Guests
                        </th>

                        <th>
                            Total
                        </th>

                    </tr>

                    {rows}

                </table>

                <br>

                <a class="btn"
                   href="/rooms">
                    Book Another Room
                </a>

            </div>

        </div>

        """
    )


# =========================================================
# BOOKING
# =========================================================

@app.route("/booking", methods=["GET", "POST"])
def booking():

    if not session.get("user_id"):
        return redirect("/login")

    con = db()

    rooms = con.execute(
        "SELECT * FROM rooms"
    ).fetchall()

    error = ""

    if request.method == "POST":

        try:

            room_id = int(
                request.form["room_id"]
            )

            check_in = request.form["check_in"]

            check_out = request.form["check_out"]

            guests = int(
                request.form["guests"]
            )

            # FIND ROOM
            room = con.execute(
                "SELECT * FROM rooms WHERE id=?",
                (room_id,)
            ).fetchone()

            if not room:

                con.close()

                return "Room not found", 404

            # CHECK GUEST CAPACITY
            if guests > room["capacity"]:

                error = (
                    "Number of guests exceeds "
                    "room capacity."
                )

            else:

                # CONVERT DATES
                d1 = datetime.strptime(
                    check_in,
                    "%Y-%m-%d"
                )

                d2 = datetime.strptime(
                    check_out,
                    "%Y-%m-%d"
                )

                nights = (d2 - d1).days

                # CHECK VALID DATES
                if nights <= 0:

                    error = (
                        "Check-out must be after "
                        "check-in."
                    )

                else:

                    # CHECK ROOM AVAILABILITY
                    overlapping = con.execute("""
                        SELECT id
                        FROM bookings
                        WHERE room_id=?
                        AND check_in < ?
                        AND check_out > ?
                    """, (
                        room_id,
                        check_out,
                        check_in
                    )).fetchone()

                    if overlapping:

                        error = (
                            "This room is already "
                            "booked for the selected dates."
                        )

                    else:

                        total = room["price"] * nights

                        con.execute("""
                            INSERT INTO bookings(
                                user_id,
                                room_id,
                                check_in,
                                check_out,
                                guests,
                                total
                            )
                            VALUES(?,?,?,?,?,?)
                        """, (
                            session["user_id"],
                            room_id,
                            check_in,
                            check_out,
                            guests,
                            total
                        ))

                        con.commit()
                        con.close()

                        return redirect("/dashboard")

        except ValueError:

            error = "Please enter valid booking details."

    options = ""

    selected = request.args.get("room")

    for r in rooms:

        is_selected = (
            "selected"
            if selected == str(r["id"])
            else ""
        )

        options += f"""
        <option value="{r['id']}" {is_selected}>

            Room {r['number']} -
            {r['type']} -
            ₹{r['price']:,.0f}/night

        </option>
        """

    con.close()

    return page(
        "Book a Room",
        f"""

        <form method="POST">

            <h1>
                Reserve Your Stay
            </h1>

            <p style="text-align:center;color:#777;margin-bottom:25px;">
                Complete the details below to
                make your reservation.
            </p>

            {f'<div class="error">{error}</div>' if error else ''}

            <label>
                Select Room
            </label>

            <select name="room_id"
                    required>

                {options}

            </select>


            <label>
                Check-in Date
            </label>

            <input
                type="date"
                name="check_in"
                required
            >


            <label>
                Check-out Date
            </label>

            <input
                type="date"
                name="check_out"
                required
            >


            <label>
                Number of Guests
            </label>

            <input
                type="number"
                name="guests"
                min="1"
                value="1"
                required
            >


            <button class="btn"
                    style="width:100%;">

                Confirm Reservation

            </button>

        </form>

        """
    )


# =========================================================
# ADMIN DASHBOARD
# =========================================================

@app.route("/admin")
def admin():

    if session.get("role") != "admin":
        return redirect("/login")

    con = db()

    rooms = con.execute(
        "SELECT * FROM rooms"
    ).fetchall()

    customers = con.execute(
        "SELECT COUNT(*) FROM users WHERE role='customer'"
    ).fetchone()[0]

    bookings = con.execute(
        "SELECT COUNT(*) FROM bookings"
    ).fetchone()[0]

    con.close()

    rows = ""

    for r in rooms:

        rows += f"""
        <tr>

            <td>
                <strong>
                    Room {r['number']}
                </strong>
            </td>

            <td>
                {r['type']}
            </td>

            <td>
                ₹{r['price']:,.0f}
            </td>

            <td>
                {r['capacity']}
            </td>

            <td>

                <a class="btn"
                   href="/admin/edit/{r['id']}">
                    Edit
                </a>

                <a class="btn btn-danger"
                   href="/admin/delete/{r['id']}"
                   onclick="return confirm('Delete this room?')">
                    Delete
                </a>

            </td>

        </tr>
        """

    return page(
        "Admin Dashboard",
        f"""

        <div class="container">

            <div class="dashboard-header">

                <p style="color:#d4af37;">
                    ADMINISTRATION
                </p>

                <h1>
                    Hotel Management Dashboard
                </h1>

                <p style="color:#bbb;">
                    Manage rooms and monitor
                    your hotel system.
                </p>

            </div>


            <div class="stats">

                <div class="stat">

                    <p>
                        Total Customers
                    </p>

                    <h2>
                        {customers}
                    </h2>

                </div>


                <div class="stat">

                    <p>
                        Total Rooms
                    </p>

                    <h2>
                        {len(rooms)}
                    </h2>

                </div>


                <div class="stat">

                    <p>
                        Total Bookings
                    </p>

                    <h2>
                        {bookings}
                    </h2>

                </div>

            </div>


            <div class="admin-actions">

                <a class="btn"
                   href="/admin/add">

                    + Add New Room

                </a>

            </div>


            <div class="info-box">

                <h2>
                    Room Management
                </h2>

                <br>

                <table>

                    <tr>

                        <th>
                            Room
                        </th>

                        <th>
                            Type
                        </th>

                        <th>
                            Price
                        </th>

                        <th>
                            Capacity
                        </th>

                        <th>
                            Actions
                        </th>

                    </tr>

                    {rows}

                </table>

            </div>

        </div>

        """
    )


# =========================================================
# ADD ROOM
# =========================================================

@app.route("/admin/add", methods=["GET", "POST"])
def add_room():

    if session.get("role") != "admin":
        return redirect("/login")

    error = ""

    if request.method == "POST":

        con = db()

        try:

            con.execute("""
                INSERT INTO rooms(
                    number,
                    type,
                    price,
                    capacity,
                    description
                )
                VALUES(?,?,?,?,?)
            """, (
                request.form["number"],
                request.form["type"],
                float(request.form["price"]),
                int(request.form["capacity"]),
                request.form["description"]
            ))

            con.commit()
            con.close()

            return redirect("/admin")

        except sqlite3.IntegrityError:

            error = "Room number already exists."

            con.close()

    return page(
        "Add Room",
        f"""

        <form method="POST">

            <h1>
                Add New Room
            </h1>

            {f'<div class="error">{error}</div>' if error else ''}

            <label>
                Room Number
            </label>

            <input
                name="number"
                placeholder="Example: 501"
                required
            >


            <label>
                Room Type
            </label>

            <input
                name="type"
                placeholder="Example: Premium Suite"
                required
            >


            <label>
                Price Per Night
            </label>

            <input
                type="number"
                name="price"
                placeholder="Example: 8500"
                min="1"
                required
            >


            <label>
                Guest Capacity
            </label>

            <input
                type="number"
                name="capacity"
                min="1"
                placeholder="Example: 3"
                required
            >


            <label>
                Description
            </label>

            <textarea
                name="description"
                placeholder="Describe the room..."
            ></textarea>


            <button class="btn"
                    style="width:100%;">

                Add Room

            </button>

        </form>

        """
    )


# =========================================================
# EDIT ROOM
# =========================================================

@app.route(
    "/admin/edit/<int:room_id>",
    methods=["GET", "POST"]
)
def edit_room(room_id):

    if session.get("role") != "admin":
        return redirect("/login")

    con = db()

    room = con.execute(
        "SELECT * FROM rooms WHERE id=?",
        (room_id,)
    ).fetchone()

    if not room:

        con.close()

        return "Room not found", 404

    error = ""

    if request.method == "POST":

        try:

            con.execute("""
                UPDATE rooms

                SET
                    number=?,
                    type=?,
                    price=?,
                    capacity=?,
                    description=?

                WHERE id=?
            """, (
                request.form["number"],
                request.form["type"],
                float(request.form["price"]),
                int(request.form["capacity"]),
                request.form["description"],
                room_id
            ))

            con.commit()
            con.close()

            return redirect("/admin")

        except sqlite3.IntegrityError:

            error = (
                "Another room already uses "
                "this room number."
            )

            con.close()

            return page(
                "Error",
                f"""

                <div class="container">

                    <div class="error">
                        {error}
                    </div>

                    <a class="btn"
                       href="/admin/edit/{room_id}">
                        Go Back
                    </a>

                </div>

                """
            )

    con.close()

    return page(
        "Edit Room",
        f"""

        <form method="POST">

            <h1>
                Edit Room
            </h1>

            <label>
                Room Number
            </label>

            <input
                name="number"
                value="{room['number']}"
                required
            >


            <label>
                Room Type
            </label>

            <input
                name="type"
                value="{room['type']}"
                required
            >


            <label>
                Price Per Night
            </label>

            <input
                type="number"
                name="price"
                value="{room['price']}"
                min="1"
                required
            >


            <label>
                Guest Capacity
            </label>

            <input
                type="number"
                name="capacity"
                value="{room['capacity']}"
                min="1"
                required
            >


            <label>
                Description
            </label>

            <textarea
                name="description"
            >{room['description']}</textarea>


            <button class="btn"
                    style="width:100%;">

                Update Room

            </button>

        </form>

        """
    )


# =========================================================
# DELETE ROOM
# =========================================================

@app.route("/admin/delete/<int:room_id>")
def delete_room(room_id):

    if session.get("role") != "admin":
        return redirect("/login")

    con = db()

    # Check if the room has bookings
    booking = con.execute("""
        SELECT id
        FROM bookings
        WHERE room_id=?
        LIMIT 1
    """, (room_id,)).fetchone()

    if booking:

        con.close()

        return page(
            "Cannot Delete Room",
            """

            <div class="container">

                <div class="error">

                    This room cannot be deleted
                    because it has existing bookings.

                </div>

                <a class="btn"
                   href="/admin">

                    Back to Dashboard

                </a>

            </div>

            """
        )

    con.execute(
        "DELETE FROM rooms WHERE id=?",
        (room_id,)
    )

    con.commit()
    con.close()

    return redirect("/admin")


# =========================================================
# ABOUT
# =========================================================

@app.route("/about")
def about():

    return page(
        "About Us",
        """

        <div class="container">

            <div class="section-title">

                <small>
                    About Us
                </small>

                <h1>
                    Welcome to Grand Horizon
                </h1>

                <p>
                    A place where comfort meets elegance.
                </p>

            </div>


            <div class="info-box">

                <h2>
                    Our Hotel
                </h2>

                <br>

                <p>
                    Grand Horizon Hotel is a modern
                    hotel management system designed
                    to provide guests with a simple
                    and convenient way to explore
                    rooms and make reservations online.
                </p>

                <br>

                <p>
                    Our platform provides customers
                    with easy registration, secure
                    login, room browsing, online
                    booking and booking history.
                </p>

                <br>

                <p>
                    Administrators can manage room
                    information through a dedicated
                    administration dashboard.
                </p>

            </div>

        </div>

        """
    )


# =========================================================
# CONTACT
# =========================================================

@app.route("/contact")
def contact():

    return page(
        "Contact Us",
        """

        <div class="container">

            <div class="section-title">

                <small>
                    Get In Touch
                </small>

                <h1>
                    Contact Grand Horizon
                </h1>

                <p>
                    We are here to help you
                    with your stay.
                </p>

            </div>


            <div class="grid">

                <div class="info-box">

                    <h2>
                        📍 Address
                    </h2>

                    <p>

                        Grand Horizon Hotel
                        <br>

                        Bengaluru, Karnataka
                        <br>

                        India

                    </p>

                </div>


                <div class="info-box">

                    <h2>
                        📞 Phone
                    </h2>

                    <p>
                        +91 98765 43210
                    </p>

                    <br>

                    <h2>
                        ✉️ Email
                    </h2>

                    <p>
                        info@grandhorizon.com
                    </p>

                </div>

            </div>

        </div>

        """
    )


# =========================================================
# RUN APPLICATION
# =========================================================

if __name__ == "__main__":

    setup()

    app.run(
        debug=True,
        host="127.0.0.1",
        port=5000
    )