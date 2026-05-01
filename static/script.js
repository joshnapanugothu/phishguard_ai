let currentRequest = null

function showDashboard() {
    const dash = document.getElementById("dashboard")
    dash.classList.remove("hidden")
    dash.style.display = "block"
    dash.scrollIntoView({ behavior: "smooth" })
}

function setInput(val) {
    document.getElementById("url").value = val
}

function formatResult(risk, confidence, reasons = [], type = "") {

    let title = "Safe"
    let message = "No phishing indicators detected"

    if (risk === "High") {
        title = "Phishing"
        message = "Strong phishing indicators found"
    } 
    else if (risk === "Medium") {
        title = "Suspicious"
        message = "Potential phishing patterns detected"
    }

    let reasonHTML = reasons.length
        ? `<small>Detected: ${reasons.join(", ")}</small>`
        : ""

    let typeLabel = type
        ? `<small style="color:#888;">Type: ${type}</small>`
        : ""

    return `
        <div>
            <h3>${title}</h3>
            <p>${message}</p>
            ${typeLabel}
            ${reasonHTML}
        </div>
    `
}

function detectType(text) {
    if (text.includes("@")) return "Email"
    if (text.includes("http") || text.includes("www")) return "URL"
    return "Text"
}

async function analyze(event) {

    const input = document.getElementById("url").value.trim()
    const btn = event.target
    const box = document.getElementById("result")

    if (!input) {
        box.innerText = "Please enter something"
        return
    }

    if (currentRequest) currentRequest.abort()
    currentRequest = new AbortController()

    box.className = "result-box"
    box.innerText = "Analyzing..."

    let dots = 0
    const interval = setInterval(() => {
        dots = (dots + 1) % 4
        box.innerText = "Analyzing" + ".".repeat(dots)
    }, 300)

    btn.disabled = true
    btn.innerText = "Analyzing..."

    try {

        const type = detectType(input)

        const res = await fetch("/analyze", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ input: input }),
            signal: currentRequest.signal
        })

        const data = await res.json()

        clearInterval(interval)

        let cssClass = "safe"
        if (data.risk === "High") cssClass = "risk"
        else if (data.risk === "Medium") cssClass = "medium"

        box.className = "result-box " + cssClass

        box.innerHTML = formatResult(
            data.risk,
            data.confidence,
            data.reasons,
            type
        )

    } catch (error) {
        clearInterval(interval)
        box.innerText = "Something went wrong"
        console.error(error)
    }

    btn.disabled = false
    btn.innerText = "Analyze"
}

window.addEventListener("scroll", () => {
    const nav = document.querySelector(".navbar")

    if (window.scrollY > 50) {
        nav.classList.add("scrolled")
    } else {
        nav.classList.remove("scrolled")
    }
})