// static/parser/js/resume_upload.js
const API = {
    upload: "/api/resume/upload/",
    analysis: (id) => `/api/resume/${id}/analysis/`,
    matches:  (id) => `/api/resume/${id}/matches/`,
  };
  
  // Grab DOM nodes once
  const form            = document.getElementById("resumeUploadForm");
  const resultsSection  = document.getElementById("resultsSection");
  const skillsList      = document.getElementById("skillsList");
  const expSummary      = document.getElementById("experienceSummary");
  const improveBox      = document.getElementById("improvementSuggestions");
  const jobList         = document.getElementById("jobMatchesList");
  const analysisLoadBox = document.getElementById("analysisLoading");
  const matchesLoadBox  = document.getElementById("matchesLoading");
  const analysisBlock   = document.getElementById("analysisResults");
  const matchesBlock    = document.getElementById("matchesResults");
  
  // CSRF helper
  function getCookie(name) {
    return document.cookie
      .split("; ")
      .find((row) => row.startsWith(name + "="))
      ?.split("=")[1];
  }
  const csrftoken = getCookie("csrftoken");
  
  // Main submit handler
  form?.addEventListener("submit", async (e) => {
    e.preventDefault();
    if (!form.resume.files.length) return alert("Choose a PDF first!");
  
    // Show the results container & loading spinners
    resultsSection.classList.remove("d-none");
    analysisLoadBox.hidden = false;
    matchesLoadBox.hidden  = false;
    analysisBlock.classList.add("d-none");
    matchesBlock.classList.add("d-none");
  
    try {
      const formData = new FormData(form);
      const resp = await fetch(API.upload, {
        method: "POST",
        headers: { "X-CSRFToken": csrftoken },
        body: formData,
      });
      if (!resp.ok) throw await resp.json();
      const { id } = await resp.json();
  
      // Kick off parallel fetches
      fetchAnalysis(id);
      fetchMatches(id);
    } catch (err) {
      console.error(err);
      alert("Upload failed — check console for details.");
    }
  });
  
  // ---------------- analysis -----------------
  async function fetchAnalysis(id) {
    const resp = await fetch(API.analysis(id));
    if (!resp.ok) return alert("Analysis failed.");
    const { analysis } = await resp.json();
  
    // Example structure expected from your LLM:
    // analysis = { skills: [...], summary: "...", improvements: [...] }
    skillsList.innerHTML = "";
    (analysis.skills || []).forEach((skill) => {
      const li = document.createElement("li");
      li.className = "list-group-item";
      li.textContent = skill;
      skillsList.appendChild(li);
    });
  
    expSummary.textContent = analysis.summary || "—";
    improveBox.innerHTML   = (analysis.improvements || [])
      .map((s) => `<p>• ${s}</p>`)
      .join("");
  
    analysisLoadBox.hidden = true;
    analysisBlock.classList.remove("d-none");
  }
  
  // ---------------- matches ------------------
  async function fetchMatches(id) {
    const resp = await fetch(API.matches(id));
    if (!resp.ok) return alert("Job‑match fetch failed.");
    const { jobs } = await resp.json();
  
    jobList.innerHTML = jobs.length
      ? jobs
          .map(
            (j) => `
            <div class="mb-2">
              <a href="${j.apply_link}" target="_blank">${j.company}</a>
              <span class="badge bg-secondary ms-2">${(
                j.match_score * 100
              ).toFixed(0)}%</span>
            </div>`
          )
          .join("")
      : "<p>No matches found.</p>";
  
    matchesLoadBox.hidden = true;
    matchesBlock.classList.remove("d-none");
  }
  