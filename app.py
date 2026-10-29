from flask import Flask, render_template, request, redirect, url_for, session, flash, send_from_directory
from database import init_db, get_db
from werkzeug.utils import secure_filename
from pathlib import Path
from datetime import datetime
from functools import wraps




# =========================================================
# CYBER AWARENESS LESSONS
# =========================================================

lessons = [
    {
        "id": 1,
        "title": "Password Safety",
        "icon": "🔐",
        "description": "Learn how to create strong passwords and protect your accounts.",
        "video": "https://youtube.com/shorts/ENGcqXuUu48?si=ZGsmmkKN-nTx8wFF",
        "points": [
            "Use long and unique passwords.",
            "Do not use your name or birthday.",
            "Use different passwords for different accounts.",
            "Never share your password.",
            "Use two-factor authentication when available."
        ]
    },
    {
        "id": 2,
        "title": "Phishing Awareness",
        "icon": "🎣",
        "description": "Learn how to identify fake messages, emails and suspicious links.",
        "video": "https://youtube.com/shorts/WhEDe8piwNw?si=qdYmsElumopAonfj",
        "points": [
            "Check the sender before opening a message.",
            "Do not click suspicious links.",
            "Be careful with urgent messages.",
            "Check website addresses carefully.",
            "Never share passwords or OTPs."
        ]
    },
    {
        "id": 3,
        "title": "OTP & Banking Fraud",
        "icon": "📱",
        "description": "Learn how to protect your OTP and banking information.",
        "video": "https://youtu.be/K3OfKlbraT4?si=Cqhrkg_B1jA0efeD",
        "points": [
            "Never share your OTP.",
            "Never share your ATM PIN.",
            "Never share your banking password.",
            "Do not install unknown applications.",
            "Report suspicious transactions."
        ]
    },
    {
        "id": 4,
        "title": "Social Media Safety",
        "icon": "🌐",
        "description": "Protect your personal information while using social media.",
        "video": "https://youtube.com/shorts/8YCaeSzYT3E?si=gn5hiJNrspkhcegs",
        "points": [
            "Use suitable privacy settings.",
            "Do not share your home address publicly.",
            "Accept requests from people you know.",
            "Avoid unknown links.",
            "Block and report suspicious accounts."
        ]
    },
    {
        "id": 5,
        "title": "Safe Digital Payments & UPI",
        "icon": "💳",
        "description": "Learn how to make safe UPI and digital payments.",
        "video": "https://youtu.be/K3OfKlbraT4?si=Cqhrkg_B1jA0efeD",
        "points": [
            "Never share your UPI PIN.",
            "Check the receiver's name.",
            "Do not scan unknown QR codes.",
            "Use trusted payment applications.",
            "Verify every payment before confirming."
        ]
    },
    {
        "id": 6,
        "title": "Cyber Safety",
        "icon": "🛡️",
        "description": "Learn basic cyber safety practices and protect yourself online.",
        "video": "https://youtube.com/shorts/ENGcqXuUu48?si=ZGsmmkKN-nTx8wFF",
        "points": [
            "Think before clicking unknown links.",
            "Keep your passwords strong and private.",
            "Never share OTP, PIN or banking passwords.",
            "Keep your phone and computer updated.",
            "Report suspicious cyber activity."
        ]
    }
]


# =========================================================
# FLASK APP
# =========================================================

app = Flask(__name__)

app.secret_key = "cyber-awareness-demo-secret-key"


# =========================================================
# UPLOAD CONFIGURATION
# =========================================================

UPLOAD_FOLDER = Path("static/uploads")
UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


# =========================================================
# DATABASE INITIALIZATION
# =========================================================

init_db()


# =========================================================
# GLOBAL USER INFORMATION
# =========================================================

@app.context_processor
def inject_user():

    return {
        "current_user": session.get("username", "User"),
        "role": session.get("role", "user")
    }


# =========================================================
# ADMIN SECURITY DECORATOR
# =========================================================

def admin_required(function):

    @wraps(function)
    def decorated_function(*args, **kwargs):

        if "username" not in session:
            flash("Please login first.", "error")
            return redirect(url_for("login"))

        if session.get("role") != "admin":
            flash("Admin access required.", "error")
            return redirect(url_for("dashboard"))

        return function(*args, **kwargs)

    return decorated_function


# =========================================================
# HOME
# =========================================================

@app.route("/")
def index():

    if "username" in session:

        if session.get("role") == "admin":
            return redirect(url_for("admin_dashboard"))

        return redirect(url_for("dashboard"))

    return redirect(url_for("login"))


# =========================================================
# LOGIN
# =========================================================

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        if not username or not password:

            flash("Please enter username and password.", "error")
            return render_template("login.html")

        db = get_db()

        user = db.execute(
            """
            SELECT *
            FROM users
            WHERE username=? AND password=?
            """,
            (username, password)
        ).fetchone()

        db.close()

        if user:

            session["username"] = user["username"]
            session["role"] = user["role"]

            flash("Login successful!", "success")

            if user["role"] == "admin":
                return redirect(url_for("admin_dashboard"))

            return redirect(url_for("dashboard"))

        flash("Invalid username or password.", "error")

    return render_template("login.html")


# =========================================================
# REGISTER
# =========================================================

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        full_name = request.form.get("full_name", "").strip()
        email = request.form.get("email", "").strip()
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        if not full_name or not email or not username or not password:

            flash("Please fill in all required fields.", "error")

            return render_template("register.html")

        if password != confirm_password:

            flash("Passwords do not match.", "error")

            return render_template("register.html")

        db = get_db()

        existing_user = db.execute(
            """
            SELECT *
            FROM users
            WHERE username=?
            """,
            (username,)
        ).fetchone()

        if existing_user:

            db.close()

            flash(
                "Username already exists. Please choose another username.",
                "error"
            )

            return render_template("register.html")

        db.execute(
            """
            INSERT INTO users
            (
                username,
                password,
                role,
                full_name,
                email
            )
            VALUES (?, ?, 'user', ?, ?)
            """,
            (
                username,
                password,
                full_name,
                email
            )
        )

        db.commit()
        db.close()

        flash(
            "Account created successfully! Please login.",
            "success"
        )

        return redirect(url_for("login"))

    return render_template("register.html")


# =========================================================
# LOGOUT
# =========================================================

@app.route("/logout")
def logout():

    session.clear()

    flash("You have been logged out successfully.", "success")

    return redirect(url_for("login"))


# =========================================================
# USER DASHBOARD
# =========================================================

@app.route("/dashboard")
def dashboard():

    if "username" not in session:

        return redirect(url_for("login"))

    return render_template("dashboard.html")


# =========================================================
# LEARNING
# =========================================================

@app.route("/learning")
def learning():

    return render_template(
        "learning.html",
        page="home",
        lessons=lessons
    )


@app.route("/lesson/<int:lesson_id>")
def lesson(lesson_id):

    selected = next(
        (item for item in lessons if item["id"] == lesson_id),
        None
    )

    if selected is None:
        return "Lesson not found", 404

    return render_template(
        "learning.html",
        page="lesson",
        selected=selected,
        lessons=lessons
    )


# =========================================================
# HELPLINE
# =========================================================

@app.route("/helpline")
def helpline():

    return render_template("helpline.html")


# =========================================================
# GOVERNMENT RESOURCES
# =========================================================

@app.route("/government")
def government():

    return render_template("government.html")


# =========================================================
# UPCOMING EVENTS
# =========================================================

@app.route("/events")
def events():

    return render_template("events.html")


# =========================================================
# REPORT CYBER SCAM
# =========================================================

@app.route("/report", methods=["GET", "POST"])
def report():

    if request.method == "POST":

        scam_type = request.form.get("scam_type", "").strip()
        incident_date = request.form.get("incident_date", "").strip()
        description = request.form.get("description", "").strip()
        contact = request.form.get("contact", "").strip()
        loss = request.form.get("loss", "").strip()
        notes = request.form.get("notes", "").strip()

        evidence = request.files.get("evidence")

        filename = ""

        # -------------------------------------------------
        # SAVE EVIDENCE FILE
        # -------------------------------------------------

        if evidence and evidence.filename:

            filename = secure_filename(evidence.filename)

            if filename:

                timestamp = datetime.now().strftime("%Y%m%d%H%M%S")

                filename = f"{timestamp}_{filename}"

                evidence.save(
                    app.config["UPLOAD_FOLDER"] / filename
                )

        # -------------------------------------------------
        # INSERT REPORT
        # -------------------------------------------------

        db = get_db()

        db.execute(
            """
            INSERT INTO reports
            (
                username,
                scam_type,
                incident_date,
                description,
                contact,
                financial_loss,
                evidence,
                notes,
                status,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'Pending', ?)
            """,
            (
                session.get("username", "Guest"),
                scam_type,
                incident_date,
                description,
                contact,
                loss,
                filename,
                notes,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            )
        )

        db.commit()
        db.close()

        flash(
            "Your cyber scam report has been submitted successfully.",
            "success"
        )

        return redirect(url_for("report"))

    return render_template("report.html")


# =========================================================
# FEEDBACK & SURVEY
# =========================================================

@app.route("/feedback", methods=["GET", "POST"])
def feedback():

    if request.method == "POST":

        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        message = request.form.get("message", "").strip()
        rating = request.form.get("rating", "5")

        db = get_db()

        db.execute(
            """
            INSERT INTO feedback
            (
                name,
                email,
                message,
                rating,
                created_at
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                name,
                email,
                message,
                rating,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            )
        )

        db.commit()
        db.close()

        flash(
            "Thank you! Your feedback has been submitted.",
            "success"
        )

        return redirect(url_for("feedback"))

    db = get_db()

    recent = db.execute(
        """
        SELECT *
        FROM feedback
        ORDER BY id DESC
        LIMIT 3
        """
    ).fetchall()

    db.close()

    return render_template(
        "feedback.html",
        recent=recent
    )


# =========================================================
# ADMIN DASHBOARD
# =========================================================

@app.route("/admin-dashboard")
@admin_required
def admin_dashboard():

    db = get_db()

    # -----------------------------------------------------
    # ALL REPORTS
    # -----------------------------------------------------
    # Load all reports because the dashboard filters must
    # work across every submitted report, not only the latest 5.

    reports = db.execute(
        """
        SELECT *
        FROM reports
        ORDER BY id DESC
        """
    ).fetchall()

    # -----------------------------------------------------
    # REPORT COUNTS
    # -----------------------------------------------------

    total_reports = db.execute(
        """
        SELECT COUNT(*) AS c
        FROM reports
        """
    ).fetchone()["c"]

    pending = db.execute(
        """
        SELECT COUNT(*) AS c
        FROM reports
        WHERE status='Pending'
        """
    ).fetchone()["c"]

    under_review = db.execute(
        """
        SELECT COUNT(*) AS c
        FROM reports
        WHERE status='Under Review'
        """
    ).fetchone()["c"]

    resolved = db.execute(
        """
        SELECT COUNT(*) AS c
        FROM reports
        WHERE status='Resolved'
        """
    ).fetchone()["c"]

    total_users = db.execute(
        """
        SELECT COUNT(*) AS c
        FROM users
        WHERE role='user'
        """
    ).fetchone()["c"]

    db.close()

    return render_template(
        "admin_dashboard.html",
        reports=reports,
        total_users=total_users,
        total_reports=total_reports,
        pending=pending,
        under_review=under_review,
        resolved=resolved
    )


# =========================================================
# ADMIN - VIEW SINGLE REPORT
# =========================================================

@app.route("/admin-report/<int:report_id>")
@admin_required
def admin_report_details(report_id):

    db = get_db()

    report = db.execute(
        """
        SELECT *
        FROM reports
        WHERE id=?
        """,
        (report_id,)
    ).fetchone()

    if report is None:

        db.close()

        flash(
            "Report not found.",
            "error"
        )

        return redirect(
            url_for("admin_reports")
        )

    # -----------------------------------------------------
    # AUTOMATIC STATUS CHANGE
    # Pending -> Under Review
    # -----------------------------------------------------
    # When an admin opens/seen a pending report, the system
    # automatically marks it as Under Review.

    if report["status"] == "Pending":

        db.execute(
            """
            UPDATE reports
            SET status='Under Review'
            WHERE id=?
            """,
            (report_id,)
        )

        db.commit()

        # Fetch the updated row so the page immediately shows
        # the new Under Review status.
        report = db.execute(
            """
            SELECT *
            FROM reports
            WHERE id=?
            """,
            (report_id,)
        ).fetchone()

    db.close()

    return render_template(
        "admin_report.html",
        report=report
    )


# =========================================================
# ADMIN - OPEN REPORT EVIDENCE
# =========================================================

@app.route("/admin-evidence/<path:filename>")
@admin_required
def admin_evidence(filename):
    return send_from_directory(
        app.config["UPLOAD_FOLDER"],
        filename,
        as_attachment=False
    )


# =========================================================
# ADMIN - UPDATE REPORT STATUS
# =========================================================

@app.route(
    "/update-report-status/<int:report_id>",
    methods=["POST"]
)
@admin_required
def update_report_status(report_id):

    # Under Review is automatic when the report is viewed.
    # This endpoint is only used for the final Resolve action.
    status = request.form.get("status", "").strip()

    if status != "Resolved":
        return redirect(
            url_for(
                "admin_report_details",
                report_id=report_id
            )
        )

    db = get_db()

    report = db.execute(
        """
        SELECT id
        FROM reports
        WHERE id=?
        """,
        (report_id,)
    ).fetchone()

    if report is None:

        db.close()

        return redirect(
            url_for("admin_dashboard")
        )

    db.execute(
        """
        UPDATE reports
        SET status='Resolved'
        WHERE id=?
        """,
        (report_id,)
    )

    db.commit()
    db.close()

    # No flash message is used here so it cannot appear later
    # on the user's Report Cyber Scam page.
    return redirect(
        url_for("admin_dashboard")
    )


# =========================================================
# ADMIN - DELETE REPORT
# =========================================================

@app.route(
    "/admin-report/delete/<int:report_id>",
    methods=["POST"]
)
@admin_required
def delete_report(report_id):

    db = get_db()

    report = db.execute(
        """
        SELECT *
        FROM reports
        WHERE id=?
        """,
        (report_id,)
    ).fetchone()

    if report is None:

        db.close()

        flash(
            "Report not found.",
            "error"
        )

        return redirect(
            url_for("admin_dashboard")
        )

    # -----------------------------------------------------
    # DELETE EVIDENCE FILE
    # -----------------------------------------------------

    if report["evidence"]:

        evidence_path = (
            app.config["UPLOAD_FOLDER"]
            / report["evidence"]
        )

        if evidence_path.exists():

            try:
                evidence_path.unlink()
            except Exception:
                pass

    # -----------------------------------------------------
    # DELETE DATABASE RECORD
    # -----------------------------------------------------

    db.execute(
        """
        DELETE FROM reports
        WHERE id=?
        """,
        (report_id,)
    )

    db.commit()
    db.close()

    flash(
        f"Report #{report_id} deleted successfully.",
        "success"
    )

    return redirect(
        url_for("admin_dashboard")
    )


# =========================================================
# ADMIN - USERS
# =========================================================

@app.route("/admin-users")
@admin_required
def admin_users():

    db = get_db()

    users = db.execute(
        """
        SELECT *
        FROM users
        ORDER BY id DESC
        """
    ).fetchall()

    db.close()

    return render_template(
        "admin_users.html",
        users=users
    )


# =========================================================
# ADMIN - ALL REPORTS
# =========================================================

@app.route("/admin-reports")
@admin_required
def admin_reports():

    db = get_db()

    reports = db.execute(
        """
        SELECT *
        FROM reports
        ORDER BY id DESC
        """
    ).fetchall()

    db.close()

    return render_template(
        "admin_reports.html",
        reports=reports
    )


# =========================================================
# ADMIN - ALL FEEDBACK
# =========================================================

@app.route("/admin-feedback")
@admin_required
def admin_feedback():

    db = get_db()

    feedback_list = db.execute(
        """
        SELECT *
        FROM feedback
        ORDER BY id DESC
        """
    ).fetchall()

    db.close()

    return render_template(
        "admin_feedback.html",
        feedback_list=feedback_list
    )


# =========================================================
# RUN APPLICATION
# =========================================================

if __name__ == "__main__":

    app.run(
        debug=True,
        host="127.0.0.1",
        port=5000
    )