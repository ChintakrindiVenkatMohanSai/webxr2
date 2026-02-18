from flask import Flask, render_template, request, redirect, send_from_directory, abort
import sqlite3
import os

app = Flask(__name__)

# ---------- CONFIG ----------
UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"glb", "jpg", "jpeg", "png", "pdf"}
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# ---------- DATABASE ----------
def init_db():
    with sqlite3.connect("products.db") as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS products(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                file TEXT NOT NULL,
                type TEXT NOT NULL
            )
        """)

init_db()


# ---------- FILE CHECK ----------
def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


# ---------- HOME ----------
@app.route("/")
def home():
    with sqlite3.connect("products.db") as conn:
        products = conn.execute("SELECT * FROM products").fetchall()
    return render_template("index.html", products=products)


# ---------- ADMIN PAGE ----------
@app.route("/admin")
def admin():
    return render_template("admin.html")


# ---------- IMAGE AR ----------
@app.route("/image-ar/<filename>")
def image_ar(filename):
    path = os.path.join(UPLOAD_FOLDER, filename)
    if not os.path.exists(path):
        abort(404)
    return render_template("image_ar_pro.html", img=filename)


# ---------- 3D AR ----------
@app.route("/pro-ar/<filename>")
def pro_ar(filename):
    path = os.path.join(UPLOAD_FOLDER, filename)
    if not os.path.exists(path):
        abort(404)
    return render_template("pro_ar.html", file=filename)


# ---------- FILE UPLOAD ----------
@app.route("/upload-model", methods=["POST"])
def upload_model():
    name = request.form.get("name")
    file_type = request.form.get("type")
    file = request.files.get("file")

    if not name or not file_type or not file:
        return "Missing form data"

    if file.filename == "":
        return "No file selected"

    if not allowed_file(file.filename):
        return "Unsupported file format"

    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)

    with sqlite3.connect("products.db") as conn:
        conn.execute(
            "INSERT INTO products(name,file,type) VALUES(?,?,?)",
            (name, file.filename, file_type)
        )

    return redirect("/")


# ---------- SERVE UPLOAD FILE ----------
@app.route("/uploads/<filename>")
def uploaded_file(filename):
    path = os.path.join(UPLOAD_FOLDER, filename)
    if not os.path.exists(path):
        abort(404)
    return send_from_directory(UPLOAD_FOLDER, filename)


# ---------- OPTIONAL: HANDLE /uploads/ ROOT ----------
@app.route("/uploads/")
def uploads_root():
    return "Specify a file name like /uploads/example.png"


# ---------- RUN SERVER ----------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)