let currentUser = null;

function showScreen(screen) {
    document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
    if (screen === 'main') {
        document.getElementById('main-card').classList.add('active');
    } else if (screen === 'history') {
        document.getElementById('history-card').classList.add('active');
    }
}

async function handleAuth(url, body) {
    try {
        const res = await fetch(url, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(body)
        });
        const data = await res.json();

        if (data.ok) {
            currentUser = { email: body.email, name: data.name };
            localStorage.setItem("user", JSON.stringify(currentUser));
            document.getElementById('auth-card').style.display = 'none';
            showScreen('main');
        } else {
            alert(data.error || "Failed");
        }
    } catch (err) {
        alert("Server error. Make sure app.py is running.");
    }
}

async function register() {
    const email = document.getElementById("email").value.trim();
    const password = document.getElementById("password").value;
    const name = document.getElementById("name").value.trim();

    if (!email || !password || !name) return alert("All fields required");
    await handleAuth("/api/register", {email, password, name});
}

async function login() {
    const email = document.getElementById("email").value.trim();
    const password = document.getElementById("password").value;

    if (!email || !password) return alert("Email and password required");
    await handleAuth("/api/login", {email, password});
}

async function googleLogin() {
    const email = prompt("Enter your Gmail:");
    if (!email) return;
    await handleAuth("/api/google-login", {email});
}

async function startDownload() {
    const url = document.getElementById("url").value.trim();
    if (!url) return alert("Paste a link first!");

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
    evt.onmessage = (e) => {
        const job = JSON.parse(e.data);
        document.getElementById("title").textContent = job.title || "Downloading...";
        document.getElementById("progress").style.width = (job.progress * 100) + "%";
        document.getElementById("status").textContent = `${job.status} ${job.speed} ${job.eta}`;

        const log = document.getElementById("log");
        log.innerHTML = job.log.map(l => `<div>${l}</div>`).join("");
        log.scrollTop = log.scrollHeight;

        if (job.done) evt.close();
    };
}

async function showHistory() {
    if (!currentUser) return alert("Login first");
    const res = await fetch(`/api/history?user=${currentUser.email}`);
    const data = await res.json();

    let html = "";
    data.forEach(item => {
        html += `
            <div style="background:#252525; padding:12px; margin:10px 0; border-radius:12px;">
                <strong>${item.title}</strong><br>
                <small>${new Date(item.time).toLocaleString()}</small><br>
                <a href="/downloads/${encodeURIComponent(item.filename)}" download>Download Again</a>
            </div>`;
    });
    document.getElementById("history-list").innerHTML = html || "<p>No downloads yet.</p>";
    showScreen('history');
}

function backToMain() {
    showScreen('main');
}

// Auto login
if (localStorage.getItem("user")) {
    currentUser = JSON.parse(localStorage.getItem("user"));
    document.getElementById('auth-card').style.display = 'none';
    showScreen('main');
}
