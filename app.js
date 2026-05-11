let currentUser = null;

function saveUser(user) {
    currentUser = user;
    localStorage.setItem("user", JSON.stringify(user));
    document.getElementById("auth-section").style.display = "none";
    document.getElementById("main-section").style.display = "block";
}

async function handleAuth(endpoint, data) {
    const authSection = document.getElementById("auth-section");
    try {
        const res = await fetch(endpoint, {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify(data)
        });
        const result = await res.json();

        if (result.ok) {
            saveUser({email: data.email, name: result.name || data.name});
        } else {
            authSection.classList.add("shake");
            setTimeout(() => authSection.classList.remove("shake"), 600);
            alert(result.error || "Something went wrong");
        }
    } catch (e) {
        alert("Connection error. Make sure the server is running.");
    }
}

async function register() {
    const email = document.getElementById("email").value.trim();
    const password = document.getElementById("password").value;
    const name = document.getElementById("name").value.trim();

    if (!email || !password || !name) return alert("All fields are required!");
    await handleAuth("/api/register", {email, password, name});
}

async function login() {
    const email = document.getElementById("email").value.trim();
    const password = document.getElementById("password").value;

    if (!email || !password) return alert("Email and Password required!");
    await handleAuth("/api/login", {email, password});
}

async function googleLogin() {
    const email = prompt("Enter your Gmail address:");
    if (!email) return;
    await handleAuth("/api/google-login", {email});
}

async function startDownload() {
    const url = document.getElementById("url").value.trim();
    if (!url) return alert("Please paste a URL!");

    const res = await fetch("/api/download", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({url, user: currentUser ? currentUser.email : ""})
    });

    const data = await res.json();
    if (data.job_id) {
        document.getElementById("progress-section").style.display = "block";
        watchProgress(data.job_id);
    }
}

function watchProgress(job_id) {
    const evtSource = new EventSource(`/api/progress/${job_id}`);
    evtSource.onmessage = function(e) {
        const job = JSON.parse(e.data);
        document.getElementById("title").textContent = job.title || "Downloading...";
        document.getElementById("progress").style.width = (job.progress * 100) + "%";
        document.getElementById("status").textContent = `${job.status} • ${job.speed || ''} • ${job.eta || ''}`;

        const logDiv = document.getElementById("log");
        logDiv.innerHTML = job.log.map(l => `<div>${l}</div>`).join('');
        logDiv.scrollTop = logDiv.scrollHeight;

        if (job.done) {
            evtSource.close();
            if (job.status === "done") {
                setTimeout(() => alert("✅ Download Completed!"), 500);
            }
        }
    };
}

async function showHistory() {
    if (!currentUser) return alert("Please login first!");
    // ... (same as before)
    const res = await fetch(`/api/history?user=${currentUser.email}`);
    const history = await res.json();
    let html = "";
    history.forEach(item => {
        html += `<div class="history-item"><strong>${item.title}</strong><br><small>${new Date(item.time).toLocaleString()}</small><br><a href="/downloads/${encodeURIComponent(item.filename)}" download>⬇ Download Again</a></div>`;
    });
    document.getElementById("history-list").innerHTML = html || "<p>No history yet.</p>";
    document.getElementById("history-section").style.display = "block";
    document.getElementById("main-section").style.display = "none";
}

function backToMain() {
    document.getElementById("history-section").style.display = "none";
    document.getElementById("main-section").style.display = "block";
}

// Auto login
if (localStorage.getItem("user")) {
    currentUser = JSON.parse(localStorage.getItem("user"));
    document.getElementById("auth-section").style.display = "none";
    document.getElementById("main-section").style.display = "block";
}
