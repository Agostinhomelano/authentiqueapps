document.addEventListener("DOMContentLoaded", function () {
  const panels = Array.from(document.querySelectorAll(".step-panel"));
  const progressSteps = Array.from(document.querySelectorAll(".progress-step"));
  const tabs = Array.from(document.querySelectorAll(".wizard-tab"));
  const prevBtn = document.querySelector(".prev-btn");
  const nextBtn = document.querySelector(".next-btn");
  const submitBtn = document.querySelector(".submit-btn");
  const stepCounter = document.getElementById("step-number");
  const form = document.querySelector(".wizard-form");
  const availabilitySelect = document.getElementById("id_disponibilite");
  const availabilityMessage = document.getElementById("availability-message");

  let currentStep = 0;
  const totalSteps = panels.length;

  function updateReviewSummary() {
    const reviewFields = {
      nom: "id_nom",
      prenom: "id_prenom",
      telephone: "id_telephone",
      email: "id_email",
      ministere: "id_ministere",
      champ_apostolique: "id_champ_apostolique",
      disponibilite: "id_disponibilite",
      lieu_remplissage: "id_lieu_remplissage",
    };

    Object.entries(reviewFields).forEach(([key, fieldId]) => {
      const field = document.getElementById(fieldId);
      const valueNode = document.querySelector('[data-review="' + key + '"]');
      if (field && valueNode) {
        const value = field.value ? field.value : "-";
        valueNode.textContent = value;
      }
    });
  }

  function showStep(stepIndex) {
    currentStep = Math.max(0, Math.min(stepIndex, totalSteps - 1));

    panels.forEach((panel, index) => {
      panel.classList.toggle("active", index === currentStep);
    });

    progressSteps.forEach((step, index) => {
      step.classList.toggle("active", index === currentStep);
      step.classList.toggle("done", index < currentStep);
    });

    tabs.forEach((tab, index) => {
      tab.classList.toggle("active", index === currentStep);
    });

    stepCounter.textContent = String(currentStep + 1);
    prevBtn.style.visibility = currentStep === 0 ? "hidden" : "visible";
    nextBtn.classList.toggle("hidden", currentStep === totalSteps - 1);
    submitBtn.classList.toggle("hidden", currentStep !== totalSteps - 1);

    if (currentStep === totalSteps - 1) {
      updateReviewSummary();
    }
  }

  function validateCurrentStep() {
    const currentPanel = panels[currentStep];
    const fields = currentPanel.querySelectorAll("input, select, textarea");

    for (const field of fields) {
      if (field.disabled || field.type === "hidden") continue;

      if (field.required && !field.value.trim()) {
        field.focus();
        field.reportValidity();
        return false;
      }
    }

    return true;
  }

  function toggleAvailabilityMessage() {
    if (!availabilitySelect) return;
    const value = availabilitySelect.value;
    if (value === "partielle" || value === "indisponible") {
      availabilityMessage.classList.remove("hidden");
    } else {
      availabilityMessage.classList.add("hidden");
    }
  }

  prevBtn.addEventListener("click", function () {
    if (currentStep > 0) showStep(currentStep - 1);
  });

  nextBtn.addEventListener("click", function () {
    if (!validateCurrentStep()) return;
    showStep(currentStep + 1);
  });

  availabilitySelect.addEventListener("change", toggleAvailabilityMessage);
  toggleAvailabilityMessage();
  showStep(0);

  form.addEventListener("submit", function (event) {
    if (!validateCurrentStep()) {
      event.preventDefault();
      return;
    }
  });
});
