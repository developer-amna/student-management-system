import csv
from fastapi.responses import StreamingResponse
from io import StringIO

import sqlite3
from datetime import datetime
from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi import Request, Query
from typing import Optional

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Database Connection
conn = sqlite3.connect("students.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS students(

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    name TEXT,

    age INTEGER,

    email TEXT,

    created_at TEXT

)
""")
conn.commit()
#cursor.execute("DELETE FROM students")
#cursor.execute("DELETE FROM sqlite_sequence WHERE name='students'")
#conn.commit()


@app.get("/", response_class=HTMLResponse)
def home(request: Request):

    cursor.execute(
        "SELECT COUNT(*) FROM students"
    )

    total_students = cursor.fetchone()[0]

    cursor.execute(
        "SELECT COUNT(*) FROM students WHERE age >= 18"
    )

    adult_students = cursor.fetchone()[0]

    cursor.execute(
        """
        SELECT created_at
        FROM students
        ORDER BY id DESC
        LIMIT 1
        """
    )

    last_student = cursor.fetchone()

    if last_student:

        last_registered = last_student[0]

    else:

        last_registered = "No Records"

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "request": request,
            "total_students": total_students,
            "adult_students": adult_students,
            "last_registered": last_registered
        }
    )
# Save Data
@app.post("/save", response_class=HTMLResponse)
def save(
    name: str = Form(...),
    age: int = Form(...),
    email: str = Form(...)
):
    if name == "":
        return """
        <h2>Name is required</h2>
        <a href="/">Go Back</a>
        """


    if age < 1:
        return """
        <h2>Invalid Age</h2>
        <a href="/">Go Back</a>
        """


    if "@" not in email or "." not in email:
        return """
        <h2>Invalid Email</h2>
        <a href="/">Go Back</a>
        """
    created_at = datetime.now().strftime(
        "%d-%m-%Y %I:%M %p"
    )
    
    cursor.execute(
        """
        INSERT INTO students(
            name,
            age,
            email,
            created_at
        )
        VALUES (?, ?, ?, ?)
        """,
        (
            name,
            age,
            email,
            created_at
        )
    )

    conn.commit()

    return f"""
    <!DOCTYPE html>

    <html>

    <head>

        <title>Success</title>

        <link rel="stylesheet" href="/static/style.css">
        <script src="/static/script.js" defer></script>

    </head>

    <body>

        <div class="container">

            <h2>✅ Student Registered Successfully</h2>

            <p><strong>Name:</strong> {name}</p>

            <p><strong>Age:</strong> {age}</p>

            <p><strong>Email:</strong> {email}</p>

            <br>

            <a href="/">

                <button class="submit-btn">
                    🏠 Back to Home
                </button>

            </a>

        </div>

    </body>

    </html>
    """
@app.get("/students", response_class=HTMLResponse)
def students():

    cursor.execute("SELECT * FROM students")

    records = cursor.fetchall()
    
    if not records:

        return """
    <!DOCTYPE html>

    <html>

    <head>

        <title>Student Records</title>

        <link rel="stylesheet" href="/static/style.css">
        <script src="/static/script.js" defer></script>

    </head>

    <body>

        <div class="container">

            <h2>🎓 Student Records</h2>

            <h3 style="text-align:center;color:#666;">
                📂 No Student Records Found
            </h3>

            <br>

            <a href="/">

                <button class="submit-btn">
                    🏠 Back to Home
                </button>

            </a>

        </div>

    </body>

    </html>
    """

    html = """
    <!DOCTYPE html>
    <html>

    <head>
        <title>Student Records</title>
        <link rel="stylesheet" href="/static/style.css">
        <script src="/static/script.js" defer></script>
    </head>

    <body>

        <div class="container">

            <h2>🎓 Student Records</h2>

            <table class="student-table">

                <tr>

                    <th>ID</th>

                    <th>Name</th>

                    <th>Age</th>

                    <th>Email</th>
                    
                    <th>Registered On</th>

                    <th>Actions</th>

                </tr>
    """

    for row in records:

        html += f"""
        <tr>

            <td>{row[0]}</td>

            <td>{row[1]}</td>

            <td>{row[2]}</td>

            <td>{row[3]}</td>
            
            <td>{row[4]}</td>

            <td>

                <a href="/update?id={row[0]}">

                    <button
                        class="update-btn"
                    >
                        ✏️ Edit
                    </button>

                </a>

                <br><br>

                <a href="/delete?id={row[0]}">

                    <button
                        class="delete-btn"
                    >
                        🗑 Delete
                    </button>

                </a>

            </td>

        </tr>
        """

    html += """
            </table>

            <br>

            <a href="/">
                <button class="submit-btn">
                    🏠 Back to Home
                </button>
            </a>

         </div>

    </body>

    </html>
        """

    return html
@app.get("/update", response_class=HTMLResponse)
def update_page(id: int):
    cursor.execute(
        "SELECT * FROM students WHERE id=?",
        (id,)
    )

    student = cursor.fetchone()

    return f"""
<!DOCTYPE html>

<html>

<head>

    <title>Update Student</title>

    <link rel="stylesheet" href="/static/style.css">
    <script src="/static/script.js" defer></script>

</head>

<body>

    <div class="container">

        <h2>✏️ Update Student</h2>

        <form action="/update_student" method="post">

            <label>🆔 Student ID</label>

            <input
                type="number"
                name="id"
                value="{student[0]}"
                readonly
            >

            <label>👤 Student Name</label>

            <input
                type="text"
                name="name"
                value="{student[1]}"
                required
            >

            <label>🎂 Age</label>

            <input
                type="number"
                name="age"
                value="{student[2]}"
                required
            >

            <label>📧 Email Address</label>

            <input
                type="email"
                name="email"
                value="{student[3]}"
                required
            >

            <button
                type="submit"
                class="update-btn"
            >
                ✏️ Update Student
            </button>

            <a href="/">

                <button
                    type="button"
                    class="submit-btn"
                >
                    🏠 Back to Home
                </button>

            </a>

        </form>

    </div>

</body>

</html>
"""

@app.post("/update_student", response_class=HTMLResponse)
def update_student(
    id: int = Form(...),
    name: str = Form(...),
    age: int = Form(...),
    email: str = Form(...)
):

    cursor.execute(
        """
        UPDATE students
        SET name=?, age=?, email=?
        WHERE id=?
        """,
        (name, age, email, id)
    )

    conn.commit()

    return """
    <!DOCTYPE html>

    <html>

    <head>

        <title>Update Success</title>

        <link rel="stylesheet" href="/static/style.css">
        <script src="/static/script.js" defer></script>

    </head>

    <body>

        <div class="container">

            <h2>✏️ Student Updated Successfully</h2>

            <a href="/">

                <button class="submit-btn">
                    🏠 Back to Home
                </button>

            </a>

        </div>

    </body>

    </html>
    """

@app.get("/delete", response_class=HTMLResponse)
def delete_page(id: int):
        cursor.execute(
            "SELECT * FROM students WHERE id=?",
            (id,)
        )

        student = cursor.fetchone()

        return f"""
<!DOCTYPE html>

<html>

<head>

    <title>Delete Student</title>

    <link rel="stylesheet" href="/static/style.css">
    
    <script src="/static/script.js" defer></script>

</head>

<body>

    <div class="container">

        <h2>🗑 Delete Student</h2>
        <p>
            <strong>Name:</strong> {student[1]}
        </p>

        <p>
            <strong>Age:</strong> {student[2]}
        </p>

        <p>
            <strong>Email:</strong> {student[3]}
        </p>

        <br>

        <form action="/delete_student" method="post" onsubmit="return confirmDelete()">

            <label>🆔 Student ID</label>

            <input
                type="number"
                name="id"
                value="{student[0]}"
                readonly
            >

            <button
                type="submit"
                class="delete-btn"
            >
                🗑 Delete Student
            </button>

            <a href="/">

                <button
                    type="button"
                    class="submit-btn"
                >
                    🏠 Back to Home
                </button>

            </a>

        </form>

    </div>

</body>

</html>
"""

@app.post("/delete_student", response_class=HTMLResponse)
def delete_student(
    id: int = Form(...)
):

    cursor.execute(
        "DELETE FROM students WHERE id=?",
        (id,)
    )

    conn.commit()

    return """
    <!DOCTYPE html>

    <html>

    <head>

        <title>Delete Success</title>

        <link rel="stylesheet" href="/static/style.css">
        <script src="/static/script.js" defer></script>

    </head>

    <body>

        <div class="container">

            <h2>🗑 Student Deleted Successfully</h2>

            <a href="/">

                <button class="submit-btn">
                    🏠 Back to Home
                </button>

            </a>

        </div>

    </body>

    </html>
    """
    
@app.get("/search", response_class=HTMLResponse)
def search_student(

    id: str = Query(""),

    name: str = Query("")

):

    if id.strip():

        cursor.execute(
            "SELECT * FROM students WHERE id=?",
            (int(id),)
        )

    elif name.strip():

        cursor.execute(
            "SELECT * FROM students WHERE name LIKE ?",
            (f"%{name}%",)
        )

    else:

        return """
    <!DOCTYPE html>

    <html>

    <head>

        <title>Search Student</title>

        <link rel="stylesheet" href="/static/style.css">

        <script src="/static/script.js" defer></script>

    </head>

    <body>

        <div class="container">

            <h2>⚠️ Search Required</h2>

            <p style="text-align:center; font-size:18px; color:#555;">
                Please enter Student ID or Student Name.
            </p>

            <br>

            <a href="/">

                <button class="submit-btn">
                    🏠 Back to Home
                </button>

            </a>

        </div>

    </body>

    </html>
    """

    student = cursor.fetchone()

    if student:

        return f"""
<!DOCTYPE html>

<html>

<head>

    <title>Student Found</title>

    <link rel="stylesheet" href="/static/style.css">
    <script src="/static/script.js" defer></script>

</head>

<body>

    <div class="container">

        <h2>🔍 Search Result</h2>

        <table class="student-table">

            <tr>

                <th>ID</th>

                <th>Name</th>

                <th>Age</th>

                <th>Email</th>

                <th>Registered On</th>

            </tr>

            <tr>

                <td>{student[0]}</td>

                <td>{student[1]}</td>

                <td>{student[2]}</td>

                <td>{student[3]}</td>

                <td>{student[4]}</td>

            </tr>

        </table>

        <br>
        <a href="/">

            <button class="submit-btn">
                🏠 Back to Home
            </button>

        </a>

    </div>

</body>

</html>
"""

    return """
<!DOCTYPE html>

<html>

<head>

    <title>Not Found</title>

    <link rel="stylesheet" href="/static/style.css">
    <script src="/static/script.js" defer></script>

</head>

<body>

    <div class="container">

        <h2>❌ Student Not Found</h2>

        <a href="/">

            <button class="submit-btn">
                🏠 Back to Home
            </button>

        </a>

    </div>

</body>

</html>
"""

@app.get("/export")
def export_students():

    cursor.execute(
        "SELECT * FROM students"
    )

    students = cursor.fetchall()

    output = StringIO()

    writer = csv.writer(output)

    writer.writerow([
        "ID",
        "Name",
        "Age",
        "Email",
        "Registered On"
    ])

    writer.writerows(students)

    output.seek(0)

    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={
            "Content-Disposition": "attachment; filename=students.csv"
        }
    )