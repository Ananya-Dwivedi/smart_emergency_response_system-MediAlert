// ── Form submit handling (all forms)
document.addEventListener("DOMContentLoaded", function () {
  const forms = document.querySelectorAll(".form");

  forms.forEach((form) => {
    form.addEventListener("submit", function () {
      const btn = form.querySelector(".submit-btn");
      if (btn) {
        btn.disabled = true;

        // Change button text based on form type
        if (this.action === "/predict") {
          btn.textContent = "Sending to hospital...";
        } else if (this.action === "/login") {
          btn.textContent = "Logging in...";
        } else if (this.action === "/signup") {
          btn.textContent = "Creating account...";
        }
      }
    });
  });
});

// Live countdown from predicted ETA
const etaEl = document.getElementById("eta-display");
if (etaEl) {
  let seconds = parseFloat(etaEl.textContent) * 60;
  const interval = setInterval(() => {
    seconds--;
    if (seconds <= 0) {
      clearInterval(interval);
      etaEl.innerHTML = "Arriving <span>now</span>";
      return;
    }
    const m = Math.floor(seconds / 60);
    const s = Math.floor(seconds % 60);
    etaEl.innerHTML = `${m}:${s.toString().padStart(2, "0")} <span>remaining</span>`;
  }, 1000);
}
