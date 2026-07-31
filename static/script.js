console.log("JavaScript Connected Successfully");

function confirmDelete() {

    return confirm(
        "Are you sure you want to delete this student record?"
    );

}

function validateForm() {

    let name = document.getElementById("name").value.trim();

    let age = document.getElementById("age").value;

    let email = document.getElementById("email").value.trim();

    if (name === "") {

        alert("Please enter student name.");

        return false;

    }

    if (age <= 0) {

        alert("Age must be greater than 0.");

        return false;

    }

    let emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

    if (!emailPattern.test(email)) {

        alert("Please enter a valid email address.");

        return false;

    }

    return true;

}
function toggleTheme() {

    document.body.classList.toggle("dark-mode");

    let btn = document.getElementById("themeBtn");

    if (document.body.classList.contains("dark-mode")) {

        localStorage.setItem("theme", "dark");

        if (btn) {
            btn.innerHTML = "☀ Light Mode";
        }

    } else {

        localStorage.setItem("theme", "light");

        if (btn) {
            btn.innerHTML = "🌙 Dark Mode";
        }

    }

}

window.onload = function () {

    if (localStorage.getItem("theme") === "dark") {

        document.body.classList.add("dark-mode");

        let btn = document.getElementById("themeBtn");

        if (btn) {
            btn.innerHTML = "☀ Light Mode";
        }

    }

};

function validateSearch() {

    let id = document.getElementById("search_id").value.trim();

    let name = document.getElementById("search_name").value.trim();

    if (id === "" && name === "") {

        alert("Please enter Student ID or Student Name.");

        return false;

    }

    return true;

}