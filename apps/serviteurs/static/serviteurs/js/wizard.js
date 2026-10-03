document.addEventListener("DOMContentLoaded", function () {
  const panels = Array.from(document.querySelectorAll(".step-panel"));
  const progressSteps = Array.from(document.querySelectorAll(".progress-step"));
  const tabs = Array.from(document.querySelectorAll(".wizard-tab"));
  const prevBtn = document.querySelector(".prev-btn");
  const nextBtn = document.querySelector(".next-btn");
  const submitBtn = document.querySelector(".submit-btn");
  const stepCounter = document.getElementById("step-number");
  const form = document.querySelector(".wizard-form");
  const availabilityFields = Array.from(
    document.querySelectorAll('input[name="disponibilite"]'),
  );
  const availabilityMessage = document.getElementById("availability-message");
  const photoInput = document.getElementById("id_photo");
  const photoPreview = document.getElementById("photoPreview");

  let currentStep = 0;
  const totalSteps = panels.length;

  if (photoInput && photoPreview) {
    photoInput.addEventListener("change", function () {
      const file = this.files && this.files[0];
      if (!file || !file.type.startsWith("image/")) {
        return;
      }

      const reader = new FileReader();
      reader.onload = function (event) {
        photoPreview.innerHTML =
          '<img src="' + event.target.result + '" alt="Aperçu de la photo" />';
      };
      reader.readAsDataURL(file);
    });
  }

  function updateReviewSummary() {
    const reviewFields = {
      nom: "id_nom",
      post_nom: "id_post_nom",
      prenom: "id_prenom",
      telephone: "id_telephone",
      email: "id_email",
      adresse: "id_adresse",
      ministere: "id_ministere",
      champ_apostolique: "id_champ_apostolique",
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

    const selectedAvailability = availabilityFields.find(
      (field) => field.checked,
    );
    const availabilityLabel = selectedAvailability
      ? selectedAvailability.closest("label")
      : null;
    const availabilityValue = document.querySelector(
      '[data-review="disponibilite"]',
    );
    if (availabilityValue) {
      availabilityValue.textContent = availabilityLabel
        ? availabilityLabel.textContent.trim()
        : "-";
    }
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
    const selectedAvailability = availabilityFields.find(
      (field) => field.checked,
    );
    const value = selectedAvailability ? selectedAvailability.value : "";
    if (!availabilityMessage) return;
    if (value === "partielle" || value === "indisponible") {
      availabilityMessage.classList.remove("hidden");
    } else {
      availabilityMessage.classList.add("hidden");
    }
  }

  const curriculumList = document.getElementById("curriculum-list");
  const curriculumTemplate = document.getElementById(
    "curriculum-entry-template",
  );
  const curriculumTotal = document.getElementById("id_curriculum-TOTAL_FORMS");
  const curriculumEmpty = document.getElementById("curriculum-empty");
  const addToggle = document.getElementById("curriculum-add-toggle");
  const addPanel = document.getElementById("curriculum-add-panel");
  const addConfirm = document.getElementById("curriculum-add-confirm");
  const addCancel = document.getElementById("curriculum-add-cancel");
  const addYear = document.getElementById("curriculum-add-year");
  const addTitle = document.getElementById("curriculum-add-title");
  const addDetails = document.getElementById("curriculum-add-details");

  function curriculumField(item, name) {
    return item.querySelector('[name$="-' + name + '"]');
  }

  function updateCurriculumSummary(item) {
    const year = curriculumField(item, "annee").value.trim();
    const title = curriculumField(item, "libelle").value.trim();
    const details = curriculumField(item, "details").value.trim();
    item.querySelector("[data-year]").textContent =
      year || "Année à renseigner";
    item.querySelector("[data-title]").textContent =
      title || "Responsabilité à renseigner";
    item.querySelector("[data-details]").textContent = details;
    item.querySelector("[data-details]").hidden = !details;
  }

  function sortCurriculum() {
    if (!curriculumList) return;
    const entries = Array.from(
      curriculumList.querySelectorAll("[data-curriculum-item]"),
    ).filter((entry) => !entry.hidden);
    entries.sort((first, second) => {
      const firstYear = curriculumField(first, "annee").value.trim();
      const secondYear = curriculumField(second, "annee").value.trim();
      return secondYear.localeCompare(firstYear, undefined, { numeric: true });
    });
    entries.forEach((entry, index) => {
      curriculumList.insertBefore(entry, curriculumEmpty);
      const order = curriculumField(entry, "ordre");
      if (order) order.value = String(index + 1);
      updateCurriculumSummary(entry);
    });
    if (curriculumEmpty) curriculumEmpty.hidden = entries.length > 0;
  }

  function bindCurriculumEntry(item) {
    const fields = item.querySelector(".curriculum-fields");
    const summary = item.querySelector(".curriculum-summary");
    item
      .querySelector(".curriculum-edit")
      .addEventListener("click", function () {
        fields.hidden = false;
        summary.hidden = true;
        curriculumField(item, "annee").focus();
      });
    item
      .querySelector(".curriculum-save")
      .addEventListener("click", function () {
        updateCurriculumSummary(item);
        fields.hidden = true;
        summary.hidden = false;
        sortCurriculum();
      });
    item
      .querySelector(".curriculum-delete")
      .addEventListener("click", function () {
        if (!window.confirm("Supprimer cette expérience ministérielle ?"))
          return;
        const deleteField = curriculumField(item, "DELETE");
        if (deleteField) deleteField.value = "on";
        item.hidden = true;
        sortCurriculum();
      });
  }

  if (curriculumList && curriculumTemplate && curriculumTotal) {
    curriculumList
      .querySelectorAll("[data-curriculum-item]")
      .forEach(bindCurriculumEntry);
    sortCurriculum();

    addToggle.addEventListener("click", function () {
      addPanel.hidden = false;
      addYear.focus();
    });

    addCancel.addEventListener("click", function () {
      addPanel.hidden = true;
      addYear.value = "";
      addTitle.value = "";
      addDetails.value = "";
      addToggle.focus();
    });

    addConfirm.addEventListener("click", function () {
      if (!addYear.reportValidity() || !addTitle.reportValidity()) return;
      const index = Number(curriculumTotal.value);
      const entryTemplate = document.createElement("template");
      entryTemplate.innerHTML = curriculumTemplate.innerHTML.replaceAll(
        "__prefix__",
        String(index),
      );
      const entry = entryTemplate.content.firstElementChild;
      curriculumList.insertBefore(entry, curriculumEmpty);
      curriculumTotal.value = String(index + 1);
      curriculumField(entry, "annee").value = addYear.value;
      curriculumField(entry, "libelle").value = addTitle.value.trim();
      curriculumField(entry, "details").value = addDetails.value.trim();
      bindCurriculumEntry(entry);
      updateCurriculumSummary(entry);
      entry.querySelector(".curriculum-fields").hidden = true;
      entry.querySelector(".curriculum-summary").hidden = false;
      entry.classList.remove("editing");
      sortCurriculum();
      addCancel.click();
    });
  }

  prevBtn.addEventListener("click", function () {
    if (currentStep > 0) showStep(currentStep - 1);
  });

  nextBtn.addEventListener("click", function () {
    if (!validateCurrentStep()) return;
    showStep(currentStep + 1);
  });

  availabilityFields.forEach((field) => {
    field.addEventListener("change", toggleAvailabilityMessage);
  });
  toggleAvailabilityMessage();
  showStep(0);

  form.addEventListener("submit", function (event) {
    sortCurriculum();
    if (!validateCurrentStep()) {
      event.preventDefault();
      return;
    }
  });
});
