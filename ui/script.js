// script.js

const form = document.getElementById("compare-form");
const statusEl = document.getElementById("status");
const resultsEl = document.getElementById("results");
const overallScoreEl = document.getElementById("overall-score");
const resultsBodyEl = document.getElementById("results-body");

// CHANGE THIS to your Render URL in production
// e.g. const API_BASE = "https://mortgage-matcher.onrender.com";
const API_BASE = "https://mortgage-matcher-1.onrender.com/";

form.addEventListener("submit", async (e) => {
  e.preventDefault();
  statusEl.textContent = "Comparing...";
  statusEl.classList.remove("error");
  resultsEl.classList.add("hidden");
  resultsBodyEl.innerHTML = "";

  const structuredFile = document.getElementById("structured").files[0];
  const unstructuredFile = document.getElementById("unstructured").files[0];

  if (!structuredFile || !unstructuredFile) {
    statusEl.textContent = "Please select both JSON files.";
    statusEl.classList.add("error");
    return;
  }

  const formData = new FormData();
  formData.append("structured", structuredFile);
  formData.append("unstructured", unstructuredFile);

  try {
    const res = await fetch(`${API_BASE}/compare`, {
      method: "POST",
      body: formData,
    });

    if (!res.ok) {
      const text = await res.text();
      statusEl.textContent = `Server error (${res.status}): ${text}`;
      statusEl.classList.add("error");
      return;
    }

    const data = await res.json();

    if (data.error) {
      statusEl.textContent = data.error;
      statusEl.classList.add("error");
      return;
    }

    statusEl.textContent = "Comparison complete.";
    overallScoreEl.textContent = data.overall_score;

    data.field_results.forEach((row) => {
      const tr = document.createElement("tr");

      const tdField = document.createElement("td");
      tdField.textContent = row.field;

      const tdStruct = document.createElement("td");
      tdStruct.textContent = row.structured_value;

      const tdUnstruct = document.createElement("td");
      tdUnstruct.textContent = row.unstructured_value;

      const tdScore = document.createElement("td");
      tdScore.textContent = row.score;

      tr.appendChild(tdField);
      tr.appendChild(tdStruct);
      tr.appendChild(tdUnstruct);
      tr.appendChild(tdScore);

      resultsBodyEl.appendChild(tr);
    });

    resultsEl.classList.remove("hidden");
  } catch (err) {
    statusEl.textContent = `Request failed: ${err.message}`;
    statusEl.classList.add("error");
  }
});
