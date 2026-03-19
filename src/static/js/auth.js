async function login() {
    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;

    await fetch("http://localhost:8000/auth/login", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({email, password})
    });

    localStorage.setItem("email", email);
    window.location = "otp";
}

async function verifyOtp() {
    const email = localStorage.getItem("email");
    const otp = document.getElementById("otp").value;

    const res = await fetch("http://localhost:8000/auth/verify-otp", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({
            email,
            otp_code: otp,
            type: "email"
        })
    });

    const json = await res.json();

    localStorage.setItem("access", json.data.access_token);

    window.location = "goals";
}

function togglePassword() {
    const input = document.getElementById("password");
    const icon = document.querySelector(".toggle-password");

    if (input.type === "password") {
        input.type = "text";
        icon.textContent = "🙈";
    } else {
        input.type = "password";
        icon.textContent = "👁️";
    }
}
