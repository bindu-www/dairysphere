from flask import Flask, render_template, request, redirect, session
from werkzeug.security import generate_password_hash, check_password_hash

from database import get_db_connection, create_table


app = Flask(__name__)

app.secret_key = "dairysphere_secret_key"


# --------------------------------
# CREATE DATABASE TABLE
# --------------------------------

create_table()


# --------------------------------
# HOME
# --------------------------------

@app.route("/")
def home():
    return redirect("/login")


# --------------------------------
# LOGIN
# --------------------------------

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")

        connection = get_db_connection()

        user = connection.execute(
            "SELECT * FROM users WHERE username = ?",
            (username,)
        ).fetchone()

        connection.close()

        if user and check_password_hash(
            user["password"],
            password
        ):

            session["username"] = user["username"]

            return redirect("/dashboard")

        return render_template(
            "login.html",
            error="Invalid username or password"
        )

    return render_template("login.html")


# --------------------------------
# REGISTER
# --------------------------------

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")

        # Check password
        if password != confirm_password:

            return render_template(
                "register.html",
                error="Passwords do not match"
            )

        # Check empty fields
        if not username or not password:

            return render_template(
                "register.html",
                error="Please fill all fields"
            )

        # Hash password
        hashed_password = generate_password_hash(password)

        try:

            connection = get_db_connection()

            connection.execute(
                """
                INSERT INTO users
                (username, password)
                VALUES (?, ?)
                """,
                (username, hashed_password)
            )

            connection.commit()
            connection.close()

            return redirect("/login")

        except Exception:

            return render_template(
                "register.html",
                error="Username already exists"
            )

    return render_template("register.html")


# --------------------------------
# DASHBOARD
# --------------------------------

@app.route("/dashboard")
def dashboard():

    if "username" not in session:
        return redirect("/login")

    return render_template(
        "dashboard.html",
        username=session["username"]
    )


# --------------------------------
# BRANDS
# --------------------------------

@app.route("/brands")
def brands():

    if "username" not in session:
        return redirect("/login")

    connection = get_db_connection()

    brands = connection.execute(
        "SELECT * FROM brands ORDER BY id DESC"
    ).fetchall()

    connection.close()

    return render_template(
        "brands.html",
        brands=brands,
        username=session["username"]
    )


# --------------------------------
# ADD BRAND
# --------------------------------

@app.route("/brands/add", methods=["POST"])
def add_brand():

    if "username" not in session:
        return redirect("/login")

    name = request.form.get("name")
    company_type = request.form.get("company_type")
    headquarters = request.form.get("headquarters")
    description = request.form.get("description")

    connection = get_db_connection()

    connection.execute(
        """
        INSERT INTO brands
        (name, company_type, headquarters, description)
        VALUES (?, ?, ?, ?)
        """,
        (
            name,
            company_type,
            headquarters,
            description
        )
    )

    connection.commit()
    connection.close()

    return redirect("/brands")


# --------------------------------
# DELETE BRAND
# --------------------------------

@app.route("/brands/delete/<int:brand_id>")
def delete_brand(brand_id):

    if "username" not in session:
        return redirect("/login")

    connection = get_db_connection()

    connection.execute(
        "DELETE FROM brands WHERE id = ?",
        (brand_id,)
    )

    connection.commit()
    connection.close()

    return redirect("/brands")


# --------------------------------
# PRODUCTS
# --------------------------------

@app.route("/products")
def products():

    if "username" not in session:
        return redirect("/login")

    connection = get_db_connection()

    products = connection.execute(
        """
        SELECT
            products.id,
            products.name,
            products.category,
            products.quantity,
            products.unit,
            products.description,
            brands.name AS brand_name

        FROM products

        JOIN brands
        ON products.brand_id = brands.id

        ORDER BY products.id DESC
        """
    ).fetchall()

    brands = connection.execute(
        """
        SELECT *
        FROM brands
        ORDER BY name
        """
    ).fetchall()

    connection.close()

    return render_template(
        "products.html",
        products=products,
        brands=brands,
        username=session["username"]
    )

# --------------------------------
# ADD PRODUCT
# --------------------------------

@app.route("/products/add", methods=["POST"])
def add_product():

    if "username" not in session:
        return redirect("/login")

    name = request.form.get("name")
    brand_id = request.form.get("brand_id")
    category = request.form.get("category")
    quantity = request.form.get("quantity")
    unit = request.form.get("unit")
    description = request.form.get("description")

    connection = get_db_connection()

    connection.execute(
        """
        INSERT INTO products
        (name, brand_id, category, quantity, unit, description)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            name,
            brand_id,
            category,
            quantity,
            unit,
            description
        )
    )

    connection.commit()
    connection.close()

    return redirect("/products")




# --------------------------------
# PRODUCTION
# --------------------------------

@app.route("/production")
def production():

    if "username" not in session:
        return redirect("/login")

    connection = get_db_connection()

    # Get production records
    production_data = connection.execute("""
        SELECT *
        FROM production
        ORDER BY id DESC
    """).fetchall()

    # Get products for dropdown
    products_data = connection.execute("""
        SELECT id, name
        FROM products
        ORDER BY name
    """).fetchall()

    # Total production
    total_quantity = connection.execute("""
        SELECT COALESCE(SUM(quantity), 0)
        FROM production
    """).fetchone()[0]

    # Number of production units
    production_units = connection.execute("""
        SELECT COUNT(DISTINCT location)
        FROM production
    """).fetchone()[0]

    connection.close()

    return render_template(
        "production.html",
        production=production_data,
        products_data=products_data,
        total_quantity=total_quantity,
        production_units=production_units,
        username=session["username"]
    )


# --------------------------------
# ADD PRODUCTION
# --------------------------------

@app.route("/production/add", methods=["POST"])
def add_production():

    if "username" not in session:
        return redirect("/login")

    product_name = request.form.get("product_name")
    location = request.form.get("location")
    quantity = request.form.get("quantity")
    production_date = request.form.get("production_date")
    batch_number = request.form.get("batch_number")
    status = request.form.get("status")

    connection = get_db_connection()

    connection.execute("""
        INSERT INTO production
        (
            product_name,
            location,
            quantity,
            production_date,
            batch_number,
            status
        )
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        product_name,
        location,
        quantity,
        production_date,
        batch_number,
        status
    ))

    connection.commit()
    connection.close()

    return redirect("/production")
# --------------------------------
# QUALITY
# --------------------------------

@app.route("/quality")
def quality():

    if "username" not in session:
        return redirect("/login")

    connection = get_db_connection()

    # Get all quality records
    quality_data = connection.execute("""
        SELECT *
        FROM quality
        ORDER BY id DESC
    """).fetchall()

    # Get all products for Product dropdown
    products_data = connection.execute("""
        SELECT *
        FROM products
        ORDER BY name
    """).fetchall()

    # Total quality tests
    total_tests = connection.execute("""
        SELECT COUNT(*)
        FROM quality
    """).fetchone()[0]

    # Approved tests
    approved_tests = connection.execute("""
        SELECT COUNT(*)
        FROM quality
        WHERE result = 'Approved'
    """).fetchone()[0]

    # Calculate quality rate
    if total_tests > 0:
        quality_rate = round((approved_tests / total_tests) * 100)
    else:
        quality_rate = 0

    connection.close()

    return render_template(
        "quality.html",
        quality=quality_data,
        products=products_data,
        total_tests=total_tests,
        approved_tests=approved_tests,
        quality_rate=quality_rate,
        username=session["username"]
    )

# --------------------------------
# ADD QUALITY TEST
# --------------------------------

@app.route("/quality/add", methods=["POST"])
def add_quality():

    if "username" not in session:
        return redirect("/login")

    product_name = request.form.get("product_name")
    batch_number = request.form.get("batch_number")
    fat = request.form.get("fat")
    snf = request.form.get("snf")
    test_date = request.form.get("test_date")
    result = request.form.get("result")
    remarks = request.form.get("remarks")

    connection = get_db_connection()

    connection.execute("""
        INSERT INTO quality
        (
            product_name,
            batch_number,
            fat,
            snf,
            test_date,
            result,
            remarks
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        product_name,
        batch_number,
        fat,
        snf,
        test_date,
        result,
        remarks
    ))

    connection.commit()
    connection.close()

    return redirect("/quality")

# --------------------------------
# PROCESSING
# --------------------------------

@app.route("/processing")
def processing():

    if "username" not in session:
        return redirect("/login")

    connection = get_db_connection()

    processing_data = connection.execute(
        """
        SELECT *
        FROM processing
        ORDER BY id DESC
        """
    ).fetchall()

    products_data = connection.execute(
        """
        SELECT id, name
        FROM products
        ORDER BY name
        """
    ).fetchall()

    total_records = connection.execute(
        """
        SELECT COUNT(*)
        FROM processing
        """
    ).fetchone()[0]

    total_input = connection.execute(
        """
        SELECT COALESCE(SUM(input_quantity), 0)
        FROM processing
        """
    ).fetchone()[0]

    total_output = connection.execute(
        """
        SELECT COALESCE(SUM(output_quantity), 0)
        FROM processing
        """
    ).fetchone()[0]

    connection.close()

    return render_template(
        "processing.html",
        processing=processing_data,
        products=products_data,
        total_records=total_records,
        total_input=total_input,
        total_output=total_output,
        username=session["username"]
    )


# --------------------------------
# ADD PROCESSING
# --------------------------------

@app.route("/processing/add", methods=["POST"])
def add_processing():

    if "username" not in session:
        return redirect("/login")

    product_name = request.form.get("product_name")
    process_type = request.form.get("process_type")
    input_quantity = request.form.get("input_quantity")
    output_quantity = request.form.get("output_quantity")
    processing_date = request.form.get("processing_date")
    facility = request.form.get("facility")
    description = request.form.get("description")

    connection = get_db_connection()

    connection.execute(
        """
        INSERT INTO processing
        (
            product_name,
            process_type,
            input_quantity,
            output_quantity,
            processing_date,
            facility,
            description
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            product_name,
            process_type,
            input_quantity,
            output_quantity,
            processing_date,
            facility,
            description
        )
    )

    connection.commit()
    connection.close()

    return redirect("/processing")


# --------------------------------
# PACKAGING
# --------------------------------

@app.route("/packaging")
def packaging():

    if "username" not in session:
        return redirect("/login")

    connection = get_db_connection()

    packaging_data = connection.execute(
        """
        SELECT *
        FROM packaging
        ORDER BY id DESC
        """
    ).fetchall()

    products_data = connection.execute(
        """
        SELECT id, name
        FROM products
        ORDER BY name
        """
    ).fetchall()

    total_records = connection.execute(
        """
        SELECT COUNT(*)
        FROM packaging
        """
    ).fetchone()[0]

    total_quantity = connection.execute(
        """
        SELECT COALESCE(SUM(quantity), 0)
        FROM packaging
        """
    ).fetchone()[0]

    connection.close()

    return render_template(
        "packaging.html",
        packaging=packaging_data,
        products=products_data,
        total_records=total_records,
        total_quantity=total_quantity,
        username=session["username"]
    )


# --------------------------------
# ADD PACKAGING
# --------------------------------

@app.route("/packaging/add", methods=["POST"])
def add_packaging():

    if "username" not in session:
        return redirect("/login")

    product_name = request.form.get("product_name")
    package_type = request.form.get("package_type")
    package_size = request.form.get("package_size")
    quantity = request.form.get("quantity")
    packaging_date = request.form.get("packaging_date")
    packaging_unit = request.form.get("packaging_unit")
    description = request.form.get("description")

    connection = get_db_connection()

    connection.execute(
        """
        INSERT INTO packaging
        (
            product_name,
            package_type,
            package_size,
            quantity,
            packaging_date,
            packaging_unit,
            description
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            product_name,
            package_type,
            package_size,
            quantity,
            packaging_date,
            packaging_unit,
            description
        )
    )

    connection.commit()
    connection.close()

    return redirect("/packaging")

# --------------------------------
# DISTRIBUTION
# --------------------------------

@app.route("/distribution")
def distribution():

    if "username" not in session:
        return redirect("/login")

    connection = get_db_connection()

    distribution_data = connection.execute(
        """
        SELECT *
        FROM distribution
        ORDER BY id DESC
        """
    ).fetchall()

    products_data = connection.execute(
        """
        SELECT id, name
        FROM products
        ORDER BY name
        """
    ).fetchall()

    total_records = connection.execute(
        """
        SELECT COUNT(*)
        FROM distribution
        """
    ).fetchone()[0]

    total_quantity = connection.execute(
        """
        SELECT COALESCE(SUM(quantity), 0)
        FROM distribution
        """
    ).fetchone()[0]

    connection.close()

    return render_template(
        "distribution.html",
        distribution=distribution_data,
        products=products_data,
        total_records=total_records,
        total_quantity=total_quantity,
        username=session["username"]
    )


# --------------------------------
# ADD DISTRIBUTION
# --------------------------------

@app.route("/distribution/add", methods=["POST"])
def add_distribution():

    if "username" not in session:
        return redirect("/login")

    product_name = request.form.get("product_name")
    quantity = request.form.get("quantity")
    unit = request.form.get("unit")
    source = request.form.get("source")
    destination = request.form.get("destination")
    dispatch_date = request.form.get("dispatch_date")
    transport = request.form.get("transport")
    description = request.form.get("description")

    connection = get_db_connection()

    connection.execute(
        """
        INSERT INTO distribution
        (
            product_name,
            quantity,
            unit,
            source,
            destination,
            dispatch_date,
            transport,
            description
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            product_name,
            quantity,
            unit,
            source,
            destination,
            dispatch_date,
            transport,
            description
        )
    )

    connection.commit()
    connection.close()

    return redirect("/distribution")
# --------------------------------
# RETAIL
# --------------------------------

@app.route("/retail")
def retail():

    if "username" not in session:
        return redirect("/login")

    connection = get_db_connection()

    # Get all retail records
    retail_data = connection.execute("""
        SELECT *
        FROM retail
        ORDER BY id DESC
    """).fetchall()

    # Get products for dropdown
    products_data = connection.execute("""
        SELECT id, name
        FROM products
        ORDER BY name
    """).fetchall()

    # Total retail quantity
    total_retail = connection.execute("""
        SELECT COALESCE(SUM(quantity), 0)
        FROM retail
    """).fetchone()[0]

    # Number of retail outlets
    retail_outlets = connection.execute("""
        SELECT COUNT(DISTINCT outlet)
        FROM retail
    """).fetchone()[0]

    # Number of retail regions
    retail_regions = connection.execute("""
        SELECT COUNT(DISTINCT location)
        FROM retail
    """).fetchone()[0]

    connection.close()

    return render_template(
        "retail.html",
        retail=retail_data,
        products=products_data,
        total_retail=total_retail,
        retail_outlets=retail_outlets,
        retail_regions=retail_regions,
        username=session["username"]
    )


# --------------------------------
# ADD RETAIL
# --------------------------------

@app.route("/retail/add", methods=["POST"])
def add_retail():

    if "username" not in session:
        return redirect("/login")

    product_name = request.form.get("product_name")
    brand = request.form.get("brand")
    quantity = request.form.get("quantity")
    unit = request.form.get("unit")
    outlet = request.form.get("outlet")
    location = request.form.get("location")
    retail_date = request.form.get("retail_date")
    description = request.form.get("description")

    connection = get_db_connection()

    connection.execute("""
        INSERT INTO retail
        (
            product_name,
            brand,
            quantity,
            unit,
            outlet,
            location,
            retail_date,
            description
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        product_name,
        brand,
        quantity,
        unit,
        outlet,
        location,
        retail_date,
        description
    ))

    connection.commit()
    connection.close()

    return redirect("/retail")
# --------------------------------
# INDIA MAP
# --------------------------------

@app.route("/india-map")
def india_map():

    if "username" not in session:
        return redirect("/login")

    connection = get_db_connection()

    # Production data
    production_locations = connection.execute("""
        SELECT
            location,
            SUM(quantity) AS total_quantity,
            COUNT(*) AS total_records
        FROM production
        GROUP BY location
        ORDER BY total_quantity DESC
    """).fetchall()

    # Processing data
    processing_locations = connection.execute("""
        SELECT
            facility,
            SUM(input_quantity) AS total_input,
            SUM(output_quantity) AS total_output,
            COUNT(*) AS total_records
        FROM processing
        GROUP BY facility
        ORDER BY total_input DESC
    """).fetchall()

    # Distribution data
    distribution_locations = connection.execute("""
        SELECT
            destination,
            SUM(quantity) AS total_quantity,
            COUNT(*) AS total_records
        FROM distribution
        GROUP BY destination
        ORDER BY total_quantity DESC
    """).fetchall()

    # Retail data
    retail_locations = connection.execute("""
        SELECT
            location,
            SUM(quantity) AS total_quantity,
            COUNT(*) AS total_records
        FROM retail
        GROUP BY location
        ORDER BY total_quantity DESC
    """).fetchall()

    # Total production
    total_production = connection.execute("""
        SELECT COALESCE(SUM(quantity), 0)
        FROM production
    """).fetchone()[0]

    # Total processing input
    total_processing = connection.execute("""
        SELECT COALESCE(SUM(input_quantity), 0)
        FROM processing
    """).fetchone()[0]

    # Total distribution
    total_distribution = connection.execute("""
        SELECT COALESCE(SUM(quantity), 0)
        FROM distribution
    """).fetchone()[0]

    # Total retail
    total_retail = connection.execute("""
        SELECT COALESCE(SUM(quantity), 0)
        FROM retail
    """).fetchone()[0]

    # Number of production locations
    production_count = connection.execute("""
        SELECT COUNT(DISTINCT location)
        FROM production
    """).fetchone()[0]

    # Number of processing facilities
    processing_count = connection.execute("""
        SELECT COUNT(DISTINCT facility)
        FROM processing
    """).fetchone()[0]

    # Number of distribution destinations
    distribution_count = connection.execute("""
        SELECT COUNT(DISTINCT destination)
        FROM distribution
    """).fetchone()[0]

    connection.close()

    return render_template(
        "india_map.html",

        production_locations=production_locations,
        processing_locations=processing_locations,
        distribution_locations=distribution_locations,
        retail_locations=retail_locations,

        total_production=total_production,
        total_processing=total_processing,
        total_distribution=total_distribution,
        total_retail=total_retail,

        production_count=production_count,
        processing_count=processing_count,
        distribution_count=distribution_count,

        username=session["username"]
    )

# --------------------------------
# ANALYTICS
# --------------------------------

@app.route("/analytics")
def analytics():

    if "username" not in session:
        return redirect("/login")

    connection = get_db_connection()

    # --------------------------------
    # BRANDS
    # --------------------------------

    total_brands = connection.execute("""
        SELECT COUNT(*)
        FROM brands
    """).fetchone()[0]


    # --------------------------------
    # PRODUCTS
    # --------------------------------

    total_products = connection.execute("""
        SELECT COUNT(*)
        FROM products
    """).fetchone()[0]


    # --------------------------------
    # PRODUCTION
    # --------------------------------

    total_production = connection.execute("""
        SELECT COALESCE(SUM(quantity), 0)
        FROM production
    """).fetchone()[0]

    production_records = connection.execute("""
        SELECT COUNT(*)
        FROM production
    """).fetchone()[0]


    # --------------------------------
    # QUALITY
    # --------------------------------

    total_quality_tests = connection.execute("""
        SELECT COUNT(*)
        FROM quality
    """).fetchone()[0]

    passed_quality = connection.execute("""
        SELECT COUNT(*)
        FROM quality
        WHERE result IN ('Passed', 'Approved')
    """).fetchone()[0]

    failed_quality = connection.execute("""
        SELECT COUNT(*)
        FROM quality
        WHERE result = 'Failed'
    """).fetchone()[0]

    if total_quality_tests > 0:
        quality_rate = round(
            (passed_quality / total_quality_tests) * 100,
            1
        )
    else:
        quality_rate = 0


    # --------------------------------
    # PROCESSING
    # --------------------------------

    processing_records = connection.execute("""
        SELECT COUNT(*)
        FROM processing
    """).fetchone()[0]

    total_processing_input = connection.execute("""
        SELECT COALESCE(SUM(input_quantity), 0)
        FROM processing
    """).fetchone()[0]

    total_processing_output = connection.execute("""
        SELECT COALESCE(SUM(output_quantity), 0)
        FROM processing
    """).fetchone()[0]


    # --------------------------------
    # PACKAGING
    # --------------------------------

    packaging_records = connection.execute("""
        SELECT COUNT(*)
        FROM packaging
    """).fetchone()[0]

    total_packaging = connection.execute("""
        SELECT COALESCE(SUM(quantity), 0)
        FROM packaging
    """).fetchone()[0]


    # --------------------------------
    # DISTRIBUTION
    # --------------------------------

    distribution_records = connection.execute("""
        SELECT COUNT(*)
        FROM distribution
    """).fetchone()[0]

    total_distribution = connection.execute("""
        SELECT COALESCE(SUM(quantity), 0)
        FROM distribution
    """).fetchone()[0]

    distribution_destinations = connection.execute("""
        SELECT COUNT(DISTINCT destination)
        FROM distribution
    """).fetchone()[0]


    # --------------------------------
    # RETAIL
    # --------------------------------

    retail_records = connection.execute("""
        SELECT COUNT(*)
        FROM retail
    """).fetchone()[0]

    total_retail = connection.execute("""
        SELECT COALESCE(SUM(quantity), 0)
        FROM retail
    """).fetchone()[0]

    retail_outlets = connection.execute("""
        SELECT COUNT(DISTINCT outlet)
        FROM retail
    """).fetchone()[0]


    # --------------------------------
    # RECENT PRODUCTION
    # --------------------------------

    recent_production = connection.execute("""
        SELECT
            product_name,
            quantity,
            production_date,
            location,
            status
        FROM production
        ORDER BY id DESC
        LIMIT 5
    """).fetchall()


    # --------------------------------
    # RECENT QUALITY
    # --------------------------------

    recent_quality = connection.execute("""
        SELECT
            product_name,
            batch_number,
            fat,
            snf,
            result,
            test_date
        FROM quality
        ORDER BY id DESC
        LIMIT 5
    """).fetchall()


    # --------------------------------
    # RECENT DISTRIBUTION
    # --------------------------------

    recent_distribution = connection.execute("""
        SELECT
            product_name,
            quantity,
            unit,
            source,
            destination,
            dispatch_date
        FROM distribution
        ORDER BY id DESC
        LIMIT 5
    """).fetchall()


    # --------------------------------
    # RECENT RETAIL
    # --------------------------------

    recent_retail = connection.execute("""
        SELECT
            product_name,
            brand,
            quantity,
            unit,
            outlet,
            location,
            retail_date
        FROM retail
        ORDER BY id DESC
        LIMIT 5
    """).fetchall()


    connection.close()


    return render_template(
        "analytics.html",

        username=session["username"],

        # Main totals
        total_brands=total_brands,
        total_products=total_products,

        total_production=total_production,
        production_records=production_records,

        total_quality_tests=total_quality_tests,
        passed_quality=passed_quality,
        failed_quality=failed_quality,
        quality_rate=quality_rate,

        processing_records=processing_records,
        total_processing_input=total_processing_input,
        total_processing_output=total_processing_output,

        packaging_records=packaging_records,
        total_packaging=total_packaging,

        distribution_records=distribution_records,
        total_distribution=total_distribution,
        distribution_destinations=distribution_destinations,

        retail_records=retail_records,
        total_retail=total_retail,
        retail_outlets=retail_outlets,

        # Recent records
        recent_production=recent_production,
        recent_quality=recent_quality,
        recent_distribution=recent_distribution,
        recent_retail=recent_retail
    )
# --------------------------------
# REPORTS
# --------------------------------

@app.route("/reports", methods=["GET", "POST"])
def reports():

    if "username" not in session:
        return redirect("/login")

    report_data = []
    report_type = ""
    region = "All India"
    from_date = ""
    to_date = ""

    if request.method == "POST":

        report_type = request.form.get("report_type")
        region = request.form.get("region", "All India")
        from_date = request.form.get("from_date", "")
        to_date = request.form.get("to_date", "")

        connection = get_db_connection()

        # --------------------------------
        # PRODUCTION REPORT
        # --------------------------------

        if report_type == "Production":

            query = """
                SELECT
                    product_name,
                    location,
                    quantity,
                    production_date,
                    batch_number,
                    status
                FROM production
                WHERE 1=1
            """

            params = []

            if region != "All India":
                query += " AND location LIKE ?"
                params.append("%" + region + "%")

            if from_date:
                query += " AND production_date >= ?"
                params.append(from_date)

            if to_date:
                query += " AND production_date <= ?"
                params.append(to_date)

            query += " ORDER BY id DESC"

            report_data = connection.execute(
                query, params
            ).fetchall()


        # --------------------------------
        # QUALITY REPORT
        # --------------------------------

        elif report_type == "Quality":

            query = """
                SELECT
                    product_name,
                    batch_number,
                    fat,
                    snf,
                    test_date,
                    result,
                    remarks
                FROM quality
                WHERE 1=1
            """

            params = []

            if from_date:
                query += " AND test_date >= ?"
                params.append(from_date)

            if to_date:
                query += " AND test_date <= ?"
                params.append(to_date)

            query += " ORDER BY id DESC"

            report_data = connection.execute(
                query, params
            ).fetchall()


        # --------------------------------
        # PROCESSING REPORT
        # --------------------------------

        elif report_type == "Processing":

            query = """
                SELECT
                    product_name,
                    process_type,
                    input_quantity,
                    output_quantity,
                    processing_date,
                    facility,
                    description
                FROM processing
                WHERE 1=1
            """

            params = []

            if from_date:
                query += " AND processing_date >= ?"
                params.append(from_date)

            if to_date:
                query += " AND processing_date <= ?"
                params.append(to_date)

            query += " ORDER BY id DESC"

            report_data = connection.execute(
                query, params
            ).fetchall()


        # --------------------------------
        # PACKAGING REPORT
        # --------------------------------

        elif report_type == "Packaging":

            query = """
                SELECT
                    product_name,
                    package_type,
                    package_size,
                    quantity,
                    packaging_date,
                    packaging_unit,
                    description
                FROM packaging
                WHERE 1=1
            """

            params = []

            if from_date:
                query += " AND packaging_date >= ?"
                params.append(from_date)

            if to_date:
                query += " AND packaging_date <= ?"
                params.append(to_date)

            query += " ORDER BY id DESC"

            report_data = connection.execute(
                query, params
            ).fetchall()


        # --------------------------------
        # DISTRIBUTION REPORT
        # --------------------------------

        elif report_type == "Distribution":

            query = """
                SELECT
                    product_name,
                    quantity,
                    unit,
                    source,
                    destination,
                    dispatch_date,
                    transport,
                    description
                FROM distribution
                WHERE 1=1
            """

            params = []

            if region != "All India":
                query += " AND destination LIKE ?"
                params.append("%" + region + "%")

            if from_date:
                query += " AND dispatch_date >= ?"
                params.append(from_date)

            if to_date:
                query += " AND dispatch_date <= ?"
                params.append(to_date)

            query += " ORDER BY id DESC"

            report_data = connection.execute(
                query, params
            ).fetchall()


        # --------------------------------
        # RETAIL REPORT
        # --------------------------------

        elif report_type == "Retail":

            query = """
                SELECT
                    product_name,
                    brand,
                    quantity,
                    unit,
                    outlet,
                    location,
                    retail_date,
                    description
                FROM retail
                WHERE 1=1
            """

            params = []

            if region != "All India":
                query += " AND location LIKE ?"
                params.append("%" + region + "%")

            if from_date:
                query += " AND retail_date >= ?"
                params.append(from_date)

            if to_date:
                query += " AND retail_date <= ?"
                params.append(to_date)

            query += " ORDER BY id DESC"

            report_data = connection.execute(
                query, params
            ).fetchall()


        # --------------------------------
        # COMPLETE REPORT
        # --------------------------------

        elif report_type == "Complete":

            report_data = {

                "production": connection.execute("""
                    SELECT *
                    FROM production
                    ORDER BY id DESC
                """).fetchall(),

                "quality": connection.execute("""
                    SELECT *
                    FROM quality
                    ORDER BY id DESC
                """).fetchall(),

                "processing": connection.execute("""
                    SELECT *
                    FROM processing
                    ORDER BY id DESC
                """).fetchall(),

                "packaging": connection.execute("""
                    SELECT *
                    FROM packaging
                    ORDER BY id DESC
                """).fetchall(),

                "distribution": connection.execute("""
                    SELECT *
                    FROM distribution
                    ORDER BY id DESC
                """).fetchall(),

                "retail": connection.execute("""
                    SELECT *
                    FROM retail
                    ORDER BY id DESC
                """).fetchall()
            }

        connection.close()

    return render_template(
        "reports.html",
        username=session["username"],
        report_data=report_data,
        report_type=report_type,
        region=region,
        from_date=from_date,
        to_date=to_date
    )
# --------------------------------
# LOGOUT
# --------------------------------

@app.route("/logout")
def logout():

    session.clear()

    return redirect("/login")
# --------------------------------
# RUN APPLICATION
# --------------------------------

if __name__ == "__main__":
    app.run(debug=True)