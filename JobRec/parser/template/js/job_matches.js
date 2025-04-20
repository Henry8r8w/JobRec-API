// Function to get job matches
window.getJobMatches = function(resumeId) {
    const matchesLoading = document.getElementById('matchesLoading');
    const matchesResults = document.getElementById('matchesResults');
    
    // Verify elements exist
    if (!matchesLoading || !matchesResults) return;
    
    fetch(`/api/parser/job-matches/${resumeId}/`, {
        method: 'GET',
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken': getCsrfToken()
        }
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        // Hide loading indicator
        matchesLoading.classList.add('d-none');
        matchesResults.classList.remove('d-none');
        
        // Display job matches
        const jobMatchesList = document.getElementById('jobMatchesList');
        if (!jobMatchesList) return;
        
        jobMatchesList.innerHTML = '';
        
        if (data.matches && data.matches.length > 0) {
            data.matches.forEach(job => {
                const jobCard = createJobCard(job);
                jobMatchesList.appendChild(jobCard);
            });
        } else {
            jobMatchesList.innerHTML = '<div class="alert alert-info">No job matches found. Please refine your resume or check back later.</div>';
        }
    })
    .catch(error => {
        console.error('Error:', error);
        matchesLoading.classList.add('d-none');
        
        // Show error message
        matchesResults.innerHTML = '<div class="alert alert-danger">Error loading job matches. Please try again.</div>';
        matchesResults.classList.remove('d-none');
    });
};

// Helper function to create a job card
function createJobCard(job) {
    const jobCard = document.createElement('div');
    jobCard.className = 'card mb-3';
    
    const jobCardBody = document.createElement('div');
    jobCardBody.className = 'card-body';
    
    const jobTitle = document.createElement('h5');
    jobTitle.className = 'card-title';
    jobTitle.textContent = job.title;
    
    const jobCompany = document.createElement('h6');
    jobCompany.className = 'card-subtitle mb-2 text-muted';
    jobCompany.textContent = job.company;
    
    const jobDescription = document.createElement('p');
    jobDescription.className = 'card-text';
    jobDescription.textContent = job.description;
    
    const matchScore = document.createElement('div');
    matchScore.className = 'progress mb-3';
    matchScore.innerHTML = `
        <div class="progress-bar" role="progressbar" style="width: ${job.match_percentage}%;" 
             aria-valuenow="${job.match_percentage}" aria-valuemin="0" aria-valuemax="100">
            ${job.match_percentage}% Match
        </div>
    `;
    
    const applyButton = document.createElement('a');
    applyButton.href = job.application_url;
    applyButton.className = 'btn btn-primary';
    applyButton.textContent = 'Apply Now';
    applyButton.target = '_blank';
    
    jobCardBody.appendChild(jobTitle);
    jobCardBody.appendChild(jobCompany);
    jobCardBody.appendChild(matchScore);
    jobCardBody.appendChild(jobDescription);
    jobCardBody.appendChild(applyButton);
    
    jobCard.appendChild(jobCardBody);
    return jobCard;
}

// Helper function to get CSRF token
function getCsrfToken() {
    return document.querySelector('[name=csrfmiddlewaretoken]').value;
}