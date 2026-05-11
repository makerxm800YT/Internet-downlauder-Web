let currentUser = null;

function saveUser(user) {
    currentUser = user;
    localStorage.setItem("user", JSON.stringify(user));
    document.getElementById("auth-section").style.display = "none";
    document.getElementById("main-section").style.display = "block";
}

async function register() {
    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;
    const name = document.getElementById("name").value;

    const res = await fetch("/api/register", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({email, password, name})
    });
    const data = await res.json();
    if (data.ok) saveUser({email, name});
    else alert(data.error || "Register failed");
}

async function login() {
    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;

    const res = await fetch("/api/login", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({email, password})
    });
    const data = await res.json();
    if (data.ok) saveUser({email, name: data.name});
    else alert(data.error || "Login failed");
}

async function googleLogin() {
    const email = prompt("Enter your Gmail address:");
    if (!email) return;
    const res = await fetch("/api/google-login", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({email})
    });
    const data = await res.json();
    if (data.ok) saveUser({email, name: data.name});
    else alert(data.error);
}

async function startDownload() {
    const url = document.getElementById("url").value.trim();
    if (!url) return alert("Paste a URL first!");

    const res = await fetch("/api/download", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({url, user: currentUser.email})
    });
    const {job_id} = await res.json();

    document.getElementById("progress-section").style.display = "block";
    watchProgress(job_id);
}

function watchProgress(job_id) {
    const evtSource = new EventSource(`/api/progress/${job_id}`);
    evtSource.onmessage = function(e) {
        const job = JSON.parse(e.data);
        
        document.getElementById("title").textContent = job.title || "Downloading...";
        document.getElementById("progress").style.width = (job.progress * 100) + "%";
        document.getElementById("status").textContent = `${job.status} • ${job.speed} • ${job.eta}`;
        
        const logDiv = document.getElementById("log");
        logDiv.innerHTML = job.log.map(l => `<div>${l}</div>`).join('');
        logDiv.scrollTop = logDiv.scrollHeight;

        if (job.done) {
            evtSource.close();
            if (job.status === "done") {
                alert("✅ Download Completed! Check Downloads folder.");
            }
        }
    };
}

async function showHistory() {
    if (!currentUser) return;
    const res = await fetch(`/api/history?user=${currentUser.email}`);
    const history = await res.json();

    let html = "";
    history.forEach(item => {
        html += `
            <div class="history-item">
                <strong>${item.title}</strong><br>
                <small>${new Date(item.time).toLocaleString()}</small><br>
                <a href="/downloads/${item.filename}" download>⬇ Download Again</a>
            </div>`;
    });
    document.getElementById("history-list").innerHTML = html || "<p>No downloads yet.</p>";
    document.getElementById("history-section").style.display = "block";
    document.getElementById("main-section").style.display = "none";
}

function backToMain() {
    document.getElementById("history-section").style.display = "none";
    document.getElementById("main-section").style.display = "block";
}

// Auto login if saved
if (localStorage.getItem("user")) {
    currentUser = JSON.parse(localStorage.getItem("user"));
    document.getElementById("auth-section").style.display = "none";
    document.getElementById("main-section").style.display = "block";
}
