from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import sqlite3
from datetime import datetime, timedelta
import os

app = Flask(__name__)
app.secret_key = os.environ.get(
    "SECRET_KEY", "your-secret-key-here"
)  # Use environment variable in production


# Helper functions for 3-year rolling period system
def calculate_expiration_date(reserved_date, last_usage_year=None):
    """
    Calculate expiration date based on 3-year rolling period rules

    Args:
        reserved_date (str): Original reservation date (YYYY-MM-DD)
        last_usage_year (int): Last usage year or None

    Returns:
        tuple: (expiration_date, is_active_in_period)
    """
    # Handle None or empty reserved_date
    if not reserved_date:
        return None, False

    try:
        reserved_dt = datetime.strptime(reserved_date, "%Y-%m-%d")
        reserved_year = reserved_dt.year
        current_year = datetime.now().year

        # Calculate original expiration date (3 years from reserved date)
        original_expiration_year = reserved_year + 3

        if last_usage_year:
            # Ensure last_usage_year is an integer
            try:
                last_usage_year = int(last_usage_year)
            except (ValueError, TypeError):
                print(
                    f"⚠️  Error calculating expiration date: invalid usage year '{last_usage_year}'"
                )
                return None, False

            # Start with original expiration
            current_expiration = original_expiration_year

            # Calculate how many 3-year periods have passed since original expiration
            # Each period with usage extends the expiration by 3 years
            if last_usage_year > original_expiration_year:
                # Calculate periods passed
                years_since_original = last_usage_year - original_expiration_year
                # Each period is 3 years, so calculate how many periods have passed
                periods_passed = (
                    years_since_original + 5
                ) // 3  # Round up to get 2 periods for 2024
                # Extend by 3 years for each period
                current_expiration += periods_passed * 3
            else:
                # Usage within original period, extend by 3 years
                current_expiration += 3

            expiration_year = current_expiration
        else:
            # If no usage, expiration is the original 3 years from reserved year
            expiration_year = original_expiration_year

        expiration_date = f"{expiration_year}-01-01"

        # Check if still active (current year <= expiration year)
        is_active = current_year <= expiration_year

        return expiration_date, is_active

    except ValueError as e:
        print(f"⚠️  Error calculating expiration date: {e}")
        return None, False


def update_usage_for_registration(registration_id, usage_year=None):
    """
    Update usage information for a registration

    Args:
        registration_id (int): The registration ID
        usage_year (int): Usage year or None for current year
    """
    if usage_year is None:
        usage_year = datetime.now().year

    db_path = app.config.get("DATABASE", "car_numbers.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Get current registration info
        cursor.execute(
            """
            SELECT reserved_date, last_usage_year, usage_count 
            FROM car_registrations 
            WHERE id = ?
        """,
            (registration_id,),
        )

        result = cursor.fetchone()
        if not result:
            print(f"❌ Registration {registration_id} not found")
            return False

        reserved_date, current_last_usage_year, current_usage_count = result

        # Update usage information
        new_usage_count = current_usage_count + 1

        # Calculate new expiration date
        expiration_date, is_active = calculate_expiration_date(
            reserved_date, usage_year
        )

        # Update the record
        cursor.execute(
            """
            UPDATE car_registrations 
            SET last_usage_year = ?, usage_count = ?, expiration_date = ?, is_active_in_period = ?
            WHERE id = ?
        """,
            (usage_year, new_usage_count, expiration_date, is_active, registration_id),
        )

        conn.commit()
        print(
            f"✅ Updated usage for registration {registration_id} (year: {usage_year})"
        )
        return True

    except Exception as e:
        print(f"❌ Error updating usage: {e}")
        conn.rollback()
        return False

    finally:
        conn.close()


def remove_usage_for_registration(registration_id):
    """
    Remove usage information for a registration

    Args:
        registration_id (int): The registration ID
    """
    db_path = app.config.get("DATABASE", "car_numbers.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Get current registration info
        cursor.execute(
            """
            SELECT reserved_date 
            FROM car_registrations 
            WHERE id = ?
        """,
            (registration_id,),
        )

        result = cursor.fetchone()
        if not result:
            print(f"❌ Registration {registration_id} not found")
            return False

        reserved_date = result[0]

        # Calculate new expiration date (no usage)
        expiration_date, is_active = calculate_expiration_date(reserved_date, None)

        # Update the record (clear usage)
        cursor.execute(
            """
            UPDATE car_registrations 
            SET last_usage_year = NULL, usage_count = 0, expiration_date = ?, is_active_in_period = ?
            WHERE id = ?
        """,
            (expiration_date, is_active, registration_id),
        )

        conn.commit()
        print(f"✅ Removed usage for registration {registration_id}")
        return True

    except Exception as e:
        print(f"❌ Error removing usage: {e}")
        conn.rollback()
        return False

    finally:
        conn.close()


# Database initialization
def init_db(db_path="car_numbers.db"):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS car_registrations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            car_number TEXT NOT NULL,
            sort_order INTEGER,
            car_make TEXT,
            car_model TEXT,
            car_year INTEGER,
            car_color TEXT,
            reserved_date DATE,
            reserved_for_year INTEGER DEFAULT 2025,
            status TEXT DEFAULT 'Active',
            notes TEXT,
            last_usage_year INTEGER,
            expiration_date DATE,
            usage_count INTEGER DEFAULT 0,
            is_active_in_period BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """
    )
    conn.commit()
    conn.close()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/search")
def search():
    query = request.args.get("q", "")
    number = request.args.get("number", "")
    show_all = request.args.get("show_all", "")

    # Use configured database path or default
    db_path = app.config.get("DATABASE", "car_numbers.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    if query and not show_all:
        # Search by name
        cursor.execute(
            """
            SELECT * FROM car_registrations 
            WHERE first_name LIKE ? OR last_name LIKE ? OR (first_name || ' ' || last_name) LIKE ?
            ORDER BY sort_order, car_number
        """,
            (f"%{query}%", f"%{query}%", f"%{query}%"),
        )
    elif number and not show_all:
        # Search by car number - try multiple formats and numeric matching
        try:
            # Convert to integer for numeric matching
            search_int = int(number)

            # Search by sort_order (numeric matching) and also try common formats
            cursor.execute(
                """
                SELECT * FROM car_registrations 
                WHERE sort_order = ? OR car_number = ? OR car_number = ? OR car_number = ?
                ORDER BY sort_order, car_number
            """,
                (
                    search_int,
                    str(search_int),
                    str(search_int).zfill(2),
                    str(search_int).zfill(3),
                ),
            )
        except ValueError:
            # If not a valid number, search by exact car_number match
            cursor.execute(
                """
                SELECT * FROM car_registrations 
                WHERE car_number = ?
                ORDER BY sort_order, car_number
            """,
                (number,),
            )
    else:
        # Show all registrations (when show_all=1 or no search criteria)
        cursor.execute(
            "SELECT * FROM car_registrations ORDER BY sort_order, car_number"
        )

    registrations = cursor.fetchall()
    conn.close()

    return render_template(
        "search.html",
        registrations=registrations,
        query=query,
        number=number,
        show_all=show_all,
    )


@app.route("/add", methods=["GET", "POST"])
def add_registration():
    if request.method == "POST":
        first_name = request.form["first_name"].strip()
        last_name = request.form["last_name"].strip()
        car_number = request.form["car_number"]
        car_make = request.form["car_make"].strip()
        car_model = request.form["car_model"].strip()
        car_year = request.form["car_year"]
        car_color = request.form["car_color"].strip()
        reserved_date = request.form["reserved_date"]
        notes = request.form["notes"].strip()

        # Validation
        if not first_name or not last_name or not car_number:
            flash("First name, last name, and car number are required!", "error")
            return render_template("add.html")

        try:
            # Convert car number to string and pad with leading zeros
            car_number = str(int(car_number)).zfill(
                3
            )  # Ensure 3 digits with leading zeros
            if car_year:
                car_year = int(car_year)
        except ValueError:
            flash("Car number and year must be valid numbers!", "error")
            return render_template("add.html")

        # Use configured database path or default
        db_path = app.config.get("DATABASE", "car_numbers.db")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Check if car number is already taken
        cursor.execute(
            "SELECT * FROM car_registrations WHERE car_number = ?", (car_number,)
        )
        if cursor.fetchone():
            flash(f"Car number {car_number} is already taken!", "error")
            conn.close()
            return render_template("add.html")

        # Calculate expiration date for new registration
        expiration_date = None
        is_active_in_period = True

        if reserved_date:
            expiration_date, is_active_in_period = calculate_expiration_date(
                reserved_date
            )

        # Calculate sort_order from car_number
        try:
            sort_order = int(car_number)
        except ValueError:
            sort_order = 0

        # Insert new registration
        cursor.execute(
            """
            INSERT INTO car_registrations 
            (first_name, last_name, car_number, sort_order, car_make, car_model, car_year, car_color, reserved_date, notes, expiration_date, is_active_in_period)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                first_name,
                last_name,
                car_number,
                sort_order,
                car_make,
                car_model,
                car_year,
                car_color,
                reserved_date,
                notes,
                expiration_date,
                is_active_in_period,
            ),
        )

        conn.commit()
        conn.close()

        flash(
            f"Registration added successfully for {first_name} {last_name} with car number {car_number}!",
            "success",
        )
        return redirect(url_for("search", show_all="1"))

    return render_template("add.html")


@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit_registration(id):
    # Use configured database path or default
    db_path = app.config.get("DATABASE", "car_numbers.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    if request.method == "POST":
        first_name = request.form["first_name"].strip()
        last_name = request.form["last_name"].strip()
        car_number = request.form["car_number"]
        car_make = request.form["car_make"].strip()
        car_model = request.form["car_model"].strip()
        car_year = request.form["car_year"]
        car_color = request.form["car_color"].strip()
        reserved_date = request.form["reserved_date"]
        status = request.form["status"]
        notes = request.form["notes"].strip()

        # Validation
        if not first_name or not last_name or not car_number:
            flash("First name, last name, and car number are required!", "error")
            return render_template("edit.html", registration=None)

        try:
            # Convert car number to string and pad with leading zeros
            car_number = str(int(car_number)).zfill(
                3
            )  # Ensure 3 digits with leading zeros
            if car_year:
                car_year = int(car_year)
        except ValueError:
            flash("Car number and year must be valid numbers!", "error")
            return render_template("edit.html", registration=None)

        # Check if car number is already taken by someone else
        cursor.execute(
            "SELECT * FROM car_registrations WHERE car_number = ? AND id != ?",
            (car_number, id),
        )
        if cursor.fetchone():
            flash(f"Car number {car_number} is already taken!", "error")
            conn.close()
            return render_template("edit.html", registration=None)

        # Calculate new expiration date if reserved_date changed
        expiration_date = None
        is_active_in_period = True

        if reserved_date:
            # Get current last_usage_year to calculate expiration
            cursor.execute(
                "SELECT last_usage_year FROM car_registrations WHERE id = ?", (id,)
            )
            current_usage = cursor.fetchone()
            last_usage_year = current_usage[0] if current_usage else None

            expiration_date, is_active_in_period = calculate_expiration_date(
                reserved_date, last_usage_year
            )

        # Calculate sort_order from car_number
        try:
            sort_order = int(car_number)
        except ValueError:
            sort_order = 0

        # Update registration
        cursor.execute(
            """
            UPDATE car_registrations 
            SET first_name=?, last_name=?, car_number=?, sort_order=?, car_make=?, car_model=?, car_year=?, 
                car_color=?, reserved_date=?, status=?, notes=?, expiration_date=?, is_active_in_period=?, updated_at=CURRENT_TIMESTAMP
            WHERE id=?
        """,
            (
                first_name,
                last_name,
                car_number,
                sort_order,
                car_make,
                car_model,
                car_year,
                car_color,
                reserved_date,
                status,
                notes,
                expiration_date,
                is_active_in_period,
                id,
            ),
        )

        conn.commit()
        conn.close()

        flash("Registration updated successfully!", "success")
        return redirect(url_for("search", show_all="1"))

    # Get registration for editing
    cursor.execute("SELECT * FROM car_registrations WHERE id = ?", (id,))
    registration = cursor.fetchone()
    conn.close()

    if not registration:
        flash("Registration not found!", "error")
        return redirect(url_for("search", show_all="1"))

    return render_template("edit.html", registration=registration)


@app.route("/delete/<int:id>", methods=["POST"])
def delete_registration(id):
    # Use configured database path or default
    db_path = app.config.get("DATABASE", "car_numbers.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT first_name, last_name, car_number FROM car_registrations WHERE id = ?",
        (id,),
    )
    registration = cursor.fetchone()

    if registration:
        cursor.execute("DELETE FROM car_registrations WHERE id = ?", (id,))
        conn.commit()
        flash(
            f"Registration for {registration[0]} {registration[1]} (Car #{registration[2]}) deleted successfully!",
            "success",
        )
    else:
        flash("Registration not found!", "error")

    conn.close()
    return redirect(url_for("search", show_all="1"))


@app.route("/api/check_number/<int:number>")
def check_number(number):
    # Use configured database path or default
    db_path = app.config.get("DATABASE", "car_numbers.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    # Convert to string and pad with leading zeros
    search_number = str(number).zfill(3)
    cursor.execute(
        "SELECT * FROM car_registrations WHERE car_number = ?", (search_number,)
    )
    registration = cursor.fetchone()
    conn.close()

    if registration:
        return jsonify(
            {
                "available": False,
                "driver": f"{registration[1]} {registration[2]}",
                "car_info": f"{registration[4]} {registration[5]} {registration[6]} {registration[7]}",
            }
        )
    else:
        return jsonify({"available": True})


@app.route("/api/record_usage/<int:id>", methods=["POST"])
def record_usage(id):
    """Record usage for a car number registration"""
    try:
        usage_year = request.form.get("usage_year")
        if usage_year:
            usage_year = int(usage_year)
        else:
            usage_year = datetime.now().year

        if update_usage_for_registration(id, usage_year):
            flash(f"Usage recorded successfully for {usage_year}!", "success")
        else:
            flash("Failed to record usage!", "error")

    except Exception as e:
        flash(f"Error recording usage: {str(e)}", "error")

    # Preserve search context from form or referer
    query = request.form.get("search_query", "")
    number = request.form.get("search_number", "")
    show_all = request.form.get("search_show_all", "")

    # If no form parameters, try to extract from referer
    if not query and not number and not show_all:
        referer = request.headers.get("Referer", "")
        if referer and "search?" in referer:
            from urllib.parse import urlparse, parse_qs

            parsed = urlparse(referer)
            params = parse_qs(parsed.query)
            query = params.get("q", [""])[0]
            number = params.get("number", [""])[0]
            show_all = params.get("show_all", [""])[0]

    # Build redirect URL preserving search context
    redirect_params = {}
    if query:
        redirect_params["q"] = query
    if number:
        redirect_params["number"] = number
    if show_all:
        redirect_params["show_all"] = show_all

    return redirect(url_for("search", **redirect_params))


@app.route("/api/remove_usage/<int:id>", methods=["POST"])
def remove_usage(id):
    """Remove usage for a car number registration"""
    try:
        if remove_usage_for_registration(id):
            flash("Usage removed successfully!", "success")
        else:
            flash("Failed to remove usage!", "error")

    except Exception as e:
        flash(f"Error removing usage: {str(e)}", "error")

    # Preserve search context from form or referer
    query = request.form.get("search_query", "")
    number = request.form.get("search_number", "")
    show_all = request.form.get("search_show_all", "")

    # If no form parameters, try to extract from referer
    if not query and not number and not show_all:
        referer = request.headers.get("Referer", "")
        if referer and "search?" in referer:
            from urllib.parse import urlparse, parse_qs

            parsed = urlparse(referer)
            params = parse_qs(parsed.query)
            query = params.get("q", [""])[0]
            number = params.get("number", [""])[0]
            show_all = params.get("show_all", [""])[0]

    # Build redirect URL preserving search context
    redirect_params = {}
    if query:
        redirect_params["q"] = query
    if number:
        redirect_params["number"] = number
    if show_all:
        redirect_params["show_all"] = show_all

    return redirect(url_for("search", **redirect_params))


@app.route("/api/export")
def export_data():
    """Export all registration data as JSON"""
    try:
        # Use configured database path or default
        db_path = app.config.get("DATABASE", "car_numbers.db")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Get all registrations
        cursor.execute("SELECT * FROM car_registrations")
        rows = cursor.fetchall()

        # Get column names
        columns = [description[0] for description in cursor.description]

        # Convert to list of dictionaries
        registrations = []
        for row in rows:
            registration = dict(zip(columns, row))
            registrations.append(registration)

        # Create export data structure
        export_data = {
            "export_date": datetime.now().isoformat(),
            "total_registrations": len(registrations),
            "registrations": registrations,
        }

        conn.close()

        return jsonify(export_data)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/stats")
def stats():
    # Use configured database path or default
    db_path = app.config.get("DATABASE", "car_numbers.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Total registrations
    cursor.execute("SELECT COUNT(*) FROM car_registrations")
    total = cursor.fetchone()[0]

    # Active registrations
    cursor.execute('SELECT COUNT(*) FROM car_registrations WHERE status = "Active"')
    active = cursor.fetchone()[0]

    # Retired registrations
    cursor.execute('SELECT COUNT(*) FROM car_registrations WHERE status = "Retired"')
    retired = cursor.fetchone()[0]

    # Highest car number (convert string numbers to integers for comparison)
    cursor.execute("SELECT MAX(CAST(car_number AS INTEGER)) FROM car_registrations")
    max_number = cursor.fetchone()[0] or 0

    # Most common car makes
    cursor.execute(
        """
        SELECT car_make, COUNT(*) as count 
        FROM car_registrations 
        WHERE car_make IS NOT NULL AND car_make != '' 
        GROUP BY car_make 
        ORDER BY count DESC 
        LIMIT 5
    """
    )
    common_makes = cursor.fetchall()

    # Expiring registrations (within next 30 days)
    cursor.execute(
        """
        SELECT COUNT(*) FROM car_registrations 
        WHERE expiration_date IS NOT NULL 
        AND expiration_date <= date('now', '+30 days')
        AND expiration_date > date('now')
        AND status = 'Active'
    """
    )
    expiring_soon = cursor.fetchone()[0]

    # Expired registrations
    cursor.execute(
        """
        SELECT COUNT(*) FROM car_registrations 
        WHERE expiration_date IS NOT NULL 
        AND expiration_date < date('now')
        AND status = 'Active'
    """
    )
    expired = cursor.fetchone()[0]

    # Active in current period
    cursor.execute(
        "SELECT COUNT(*) FROM car_registrations WHERE is_active_in_period = 1"
    )
    active_in_period = cursor.fetchone()[0]

    conn.close()

    return render_template(
        "stats.html",
        total=total,
        active=active,
        retired=retired,
        max_number=max_number,
        common_makes=common_makes,
        expiring_soon=expiring_soon,
        expired=expired,
        active_in_period=active_in_period,
    )


if __name__ == "__main__":
    init_db()
    # Use environment variable for port (Google Cloud Run uses 8080)
    port = int(os.environ.get("PORT", 5001))
    app.run(debug=False, host="0.0.0.0", port=port)
