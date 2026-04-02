const structuredInput = document.getElementById("structured-file");
const unstructuredInput = document.getElementById("unstructured-file");
const compareButton = document.getElementById("compare-button");
const resultContainer = document.getElementById("result");
const tableContainer = document.getElementById("matches-table-container");
const loadingIndicator = document.getElementById("loading-indicator");

function setLoading(isLoading) {
  if (isLoading) {
    loadingIndicator.style.display = "block";
    compareButton.disabled = true;
  } else {
    loadingIndicator.style.display = "none";
    compareButton.disabled = false;
  }
}

function confidenceClass(score) {
  if (score >= 0.8) return "conf-high";
  if (score >= 0.6) return "conf-med";
  return "conf-low";
}

function renderMatches(matches) {
  if (!matches || matches.length === 0) {
    tableContainer.innerHTML = "<p>No matches found.</p>";
    return;
  }

  let html = `
    <table class="matches-table">
      <thead>
        <tr>
          <th>Structured Field</th>
          <th>Best Unstructured Match</th>
          <th>Confidence</th>
          <th>Details</th>
        </tr>
      </thead>
      <tbody>
  `;

  matches.forEach((m, idx) => {
    const best = m.best_match || {};
    const score = best.score ?? 0;
    const cls = confidenceClass(score);
    const components = best.components || {};
    const alt = m.alternatives || [];

    html += `
      <tr class="${cls}">
        <td>${m.structured_field}</td>
        <td>${best.unstructured_field ?? "-"}</td>
        <td>${score.toFixed(3)}</td>
        <td>
          <button class="toggle-details" data-row="${idx}">View</button>
        </td>
      </tr>
      <tr class="details-row" id="details-${idx}" style="display:none;">
        <td colspan="4">
          <div class="details-block">
            <strong>Components</strong><br/>
            Semantic: ${(components.semantic ?? 0).toFixed(3)}<br/>
            Fuzzy: ${(components.fuzzy ?? 0).toFixed(3)}<br/>
            Token Jaccard: ${(components.token_jaccard ?? 0).toFixed(3)}<br/><br/>
            <strong>Alternatives</strong><br/>
            ${
              alt.length === 0
                ? "None"
                : `
              <ul>
                ${alt
                  .map(
                    (a) => `
                  <li>
                    ${a.unstructured_field} — score: ${a.score.toFixed(3)}
                  </li>
                `
                  )
                  .join("")}
              </ul>
            `
            }
          </div>
        </td>
      </tr>
    `;
  });

  html += "</tbody></table>";
  tableContainer.innerHTML = html;

  // Wire up detail toggles
  document.querySelectorAll(".toggle-details").forEach((btn) => {
    btn.addEventListener("click", () => {
      const rowId = btn.getAttribute("data-row");
      const detailsRow = document.getElementById(`details-${rowId}`);
      if (detailsRow.style.display === "none") {
        detailsRow.style.display = "table-row";
        btn.textContent = "Hide";
      } else {
        detailsRow.style.display = "none";
        btn.textContent = "View";
      }
    });
  });
}

compareButton.addEventListener("click", async () => {
  const file1 = structuredInput.files[0];
  const file2 = unstructuredInput.files[0];

  if (!file1 || !file2) {
    alert("Please select both files.");
    return;
  }

  const formData = new FormData();
  formData.append("file1", file1);
  formData.append("file2", file2);

  setLoading(true);
  resultContainer.textContent = "";
  tableContainer.innerHTML = "";

  try {
    const response = await fetch("/compare", {
      method: "POST",
      body: formData,
    });

    const data = await response.json();

    if (!response.ok || data.error) {
      resultContainer.textContent =
        data.error || "An error occurred while comparing.";
      return;
    }

    resultContainer.textContent = data.message || "Comparison complete.";
    renderMatches(data.matches);
  } catch (err) {
    console.error(err);
    resultContainer.textContent = "Network or server error.";
  } finally {
    setLoading(false);
  }
});
