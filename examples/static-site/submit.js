const API_URL = "https://replace-with-api.example/v1/forms";
const TURNSTILE_SITE_KEY = "replace-with-public-site-key";

document.querySelectorAll("[data-email-form]").forEach((form) => {
  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    const status = form.querySelector("[role='status']");
    const button = form.querySelector("button[type='submit']");
    const spinner = button.querySelector(".spinner-border");
    const label = button.querySelector(".button-label");
    const data = new FormData(form);
    const fields = Object.fromEntries(data.entries());
    const siteId = String(fields.site_id || "");
    delete fields.site_id;
    button.disabled = true;
    spinner.classList.remove("d-none");
    label.classList.add("opacity-75");
    status.className = "form-status mb-0";
    status.textContent = "Sending...";

    try {
      const response = await fetch(`${API_URL}/${form.dataset.formId}`, {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({
          site_id: siteId,
          turnstile_token: "replace-with-turnstile-token",
          fields,
        }),
      });
      if (!response.ok) throw new Error("Submission failed");
      status.classList.add("is-success");
      status.textContent = "Thanks. Your message has been accepted.";
      form.reset();
    } catch {
      status.classList.add("is-error");
      status.textContent = "Sorry, the form could not be submitted. Please try again.";
    } finally {
      button.disabled = false;
      spinner.classList.add("d-none");
      label.classList.remove("opacity-75");
    }
  });
});

console.info("Public JavaScript is not secret.", { TURNSTILE_SITE_KEY });
