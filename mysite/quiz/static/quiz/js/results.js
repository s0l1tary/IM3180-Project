document.addEventListener('DOMContentLoaded', function() {
    // Progress Bar Animation
    const oldProgress = document.getElementById('oldProgress');
    const gainProgress = document.getElementById('gainProgress');
    const prevBadge = document.getElementById('prevBadge');
    const gainBadge = document.getElementById('gainBadge');
    const totalBadge = document.getElementById('totalBadge');
    
    setTimeout(() => {
        // Animate progress bars
        if (oldProgress) {
            const oldWidth = oldProgress.getAttribute('data-width');
            oldProgress.style.width = oldWidth + '%';
        }
        
        if (gainProgress) {
            const gainWidth = gainProgress.getAttribute('data-width');
            gainProgress.style.width = gainWidth + '%';
        }
        
        // Animate badges with stagger
        setTimeout(() => {
            prevBadge.style.opacity = '1';
            prevBadge.style.transform = 'translateY(0)';
        }, 600);
        
        setTimeout(() => {
            gainBadge.style.opacity = '1';
            gainBadge.style.transform = 'translateY(0)';
        }, 900);
        
        setTimeout(() => {
            totalBadge.style.opacity = '1';
            totalBadge.style.transform = 'translateY(0)';
        }, 1200);
        
        // Add glow effect to gain bar when animation completes
        setTimeout(() => {
            if (gainProgress) {
                gainProgress.style.animation = 'glow 2s ease-in-out infinite';
            }
        }, 1700);
        
    }, 200);

    // Explanation Button Handler
    document.querySelectorAll('.explain-btn').forEach(btn => {
        btn.addEventListener('click', () => {

            const questionText = btn.closest('.question-review-card').querySelector('.question-text').textContent.trim();
            const answerText = btn.closest('.question-review-card').querySelector('.correct-answer').textContent.trim();
            const chosenText = btn.closest('.question-review-card').querySelector('.chosen-answer').textContent.trim();

            const cacheKey = questionText + "::" + answerText;
            const container = btn.closest('.question-review-card').querySelector('.explanation-content');
            console.log("Requesting explanation for:", questionText, answerText, chosenText);
            
            if (explanationCache[cacheKey]) {
                container.innerHTML = explanationCache[cacheKey];
                if (window.MathJax) MathJax.typesetPromise([container]);
                return;
            }
            container.innerHTML = "Loading...";
            fetch(explainUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-CSRFToken': csrftoken
                },
                body: `question=${encodeURIComponent(questionText)}&answer=${encodeURIComponent(answerText)}&chosen=${encodeURIComponent(chosenText)}`
            })
            .then(res => res.json())
            .then(data => {
                const explanation = data.explanation || data.error || "No explanation.";
                explanationCache[cacheKey] = explanation;
                container.innerHTML = explanation;
                console.log(data.explanation)

                // 🔹 Trigger MathJax rendering after inserting HTML
                if (window.MathJax) {
                    MathJax.typesetPromise([container]).catch(err => console.error("MathJax error:", err));
                } else {
                    btn.style.display = 'none';
                }
            })
            .catch(e => {
                console.error(e);
                container.innerHTML = "Error fetching explanation.";
            });
        });
    });
});

  // CSRF token helper
  function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
  }
  const csrftoken = getCookie('csrftoken');
  const explanationCache = {};