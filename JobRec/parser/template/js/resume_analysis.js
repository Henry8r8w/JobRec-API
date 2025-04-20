// Function to get resume analysis
window.getResumeAnalysis = function(resumeId) {
    const analysisLoading = document.getElementById('analysisLoading');
    const analysisResults = document.getElementById('analysisResults');
    
    // Verify elements exist
    if (!analysisLoading || !analysisResults) return;
    
    fetch(`/api/parser/resume-analysis/${resumeId}/`, {
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
        analysisLoading.classList.add('d-none');
        analysisResults.classList.remove('d-none');
        
        // Display skills
        const skillsList = document.getElementById('skillsList');
        if (skillsList) {
            skillsList.innerHTML = '';
            if (data.skills && data.skills.length > 0) {
                data.skills.forEach(skill => {
                    const li = document.createElement('li');
                    li.className = 'list-group-item';
                    li.textContent = skill;
                    skillsList.appendChild(li);
                });
            } else {
                skillsList.innerHTML = '<li class="list-group-item">No skills identified</li>';
            }
        }
        
        // Display experience summary
        const experienceSummary = document.getElementById('experienceSummary');
        if (experienceSummary) {
            experienceSummary.innerHTML = data.experience_summary || 'No experience summary available';
        }
        
        // Display improvement suggestions
        const improvementSuggestions = document.getElementById('improvementSuggestions');
        if (improvementSuggestions) {
            if (data.improvement_suggestions) {
                improvementSuggestions.innerHTML = data.improvement_suggestions;
            } else {
                improvementSuggestions.innerHTML = 'No improvement suggestions available';
            }
        }
    })
    .catch(error => {
        console.error('Error:', error);
        analysisLoading.classList.add('d-none');
        
      
        analysisResults.innerHTML = '<div class="alert alert-danger">Error loading analysis. Please try again.</div>';
        analysisResults.classList.remove('d-none');
    });
};

// Helper function to get CSRF token
function getCsrfToken() {
    return document.querySelector('[name=csrfmiddlewaretoken]').value;
}