let currentUser = null;
let isLoginMode = true;

function toggleMode() {
    isLoginMode = !isLoginMode;
    document.getElementById("auth-title").textContent = isLoginMode ? "Login" : "Register";
    document.getElementById("main-btn").textContent = isLoginMode ? "Login" : "Register";
    document.getElementById("name").style.display = isLoginMode ? "none" : "block";
    document.getElementById("switch-text").innerHTML = isLoginMode 
        ? `Don't have an account? <span onclick="toggleMode()">Register</span>` 
        : `Already have account? <span onclick="toggleMode()">Login</span>`;
}

async function submitAuth() {
    const email = document.getElementById("email").value.trim();
    const password = document.getElementById("password").value;
    const name = document.getElementById("name").value.trim();

    if (!email || !password) return alert("Email and Password are required!");

    const endpoint = isLoginMode ? "/api/login" : "/api/register";
    const body = isLoginMode ? {email, password} : {email, password, name};

    try {
        const res = await fetch(endpoint, {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify(body)
        });
        const data = await res.json();

        if (data.ok) {
            currentUser = {email: email, name: data.name || name};
            localStorage.setItem("user", JSON.stringify(currentUser));
            document.getElementById("auth-card").style.display = "none";
            document.getElementById("main-app").style.display = "block";
        } else {
            alert(data.error || "Failed");
        }
    } catch(e) {
        alert("Cannot connect to server. Is app.py running?");
    }
}

async function googleLogin() {
    const email = prompt("Enter your Gmail address:");
    if (!email) return;

    try {
        const res = await fetch("/api/google-login", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({email})
        });
        const data = await res.json();

        if (data.ok) {
            currentUser = {email: email, name: data.name};
            localStorage.setItem("user", JSON.stringify(currentUser));
            document.getElementById("auth-card").style.display = "none";
            document.getElementById("main-app").style.display = "block";
        } else {
            alert(data.error);
        }
    } catch(e) {
        alert("Server error");
    }
}

// Rest of functions (startDownload, watchProgress, etc.)
async function startDownload() {
    const url = document.getElementById("url").value.trim();
    if (!url) return alert("Paste URL first!");

    const res = await fetch("/api/download", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({url, user: currentUser ? currentUser.email : ""})
    });
    const data = await res.json();
    if (data.job_id) {
        document.getElementById("progress-area").style.display = "block";
        watchProgress(data.job_id);
    }
}

function watchProgress(job_id) {
    const evt = new EventSource(`/api/progress/${job_id}`);
    evt.onmessage = e => {
        const job = JSON.parse(e.data);
        document.getElementById("title").textContent = job.title || "Downloading...";
        document.getElementById("progress").style.width = (job.progress * 100) + "%";
        document.getElementById("status").textContent = `${job.status} ${job.speed || ''} ${job.eta || ''}`;
        
        const log = document.getElementById("log");
        log.innerHTML = job.log.map(l => `<div>${l}</div>`).join('');
        log.scrollTop = log.scrollHeight;
    };
}

async function showHistory() {
    // You can implement later if needed
    alert("History feature coming soon");
}

// Auto login
if (localStorage.getItem("user")) {
    currentUser = JSON.parse(localStorage.getItem("user"));
    document.getElementById("auth-card").style.display = "none";
    document.getElementById("main-app").style.display = "block";
}
