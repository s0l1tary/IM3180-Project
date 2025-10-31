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
            const container = btn.closest('.question-review-card').querySelector('.explanation-content');
            
            // For debug
            console.log("Requesting explanation for:", questionText, answerText, chosenText);

            let conversation = []
            
            container.innerHTML = "Loading...";

            function sendToAI(user_response = null) {
                const payload = {
                    question: questionText,
                    correct_answer: answerText,
                    user_answer: chosenText,
                    user_response: user_response === null ? '' : user_response.trim(),
                    conversation: conversation
                };

                console.log("Sending payload:", payload);
                
                fetch(explainUrl, {
                    method: 'POST',
                    headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrftoken
                    },
                    body: JSON.stringify(payload)
                })
                .then(res => res.json())
                .then(data => {
                    if (data.error) {
                        container.innerHTML = "Error: " + data.error;
                        return;
                    }

                    // Log AI response
                    console.log("AI Response:", data.reply);

                    // Save conversation history
                    conversation = data.conversation;

                    // Render AI response
                    renderAIMessage(data.reply, data.finished);
                })
                .catch(() => {
                    container.innerHTML = "Error fetching AI response.";
                });
            }

            function renderAIMessage(reply, finished) {
                // Parse for options (A., B., etc.)
                const optionMatches = reply.match(/^[A-D]\.\s.*$/gm);

                // Remove options from explanation text before displaying
                let explanationText = reply;
                if (optionMatches) {
                    explanationText = reply.replace(/^[A-D]\.\s.*$/gm, '').trim();
                }

                // Display cleaned explanation text
                container.innerHTML = explanationText;

                // Display options as buttons
                if (optionMatches && !finished) {
                    const optionsDiv = document.createElement('div');
                    optionsDiv.className = 'subquestion-options mt-2';

                    optionMatches.forEach(line => {
                        const btnOption = document.createElement('button');
                        btnOption.innerHTML = line;
                        btnOption.className = 'btn btn-outline-primary btn-sm d-block my-1';
                        btnOption.addEventListener('click', () => {
                            // Disable buttons after one click
                            optionsDiv.querySelectorAll('button').forEach(b => b.disabled = true);
                            sendToAI(line);
                        });
                        optionsDiv.appendChild(btnOption);
                    });
                    container.appendChild(optionsDiv);

                    // Render math expressions
                    if (window.MathJax && window.MathJax.typesetPromise) {
                        MathJax.typesetPromise([container])
                            .then(() => console.log("MathJax rendered"))
                            .catch(err => console.error("MathJax rendering error:", err));
                    }
                } else if (finished) {
                    const endMsg = document.createElement('p');
                    endMsg.textContent = "End of explanation session.";
                    endMsg.className = "text-success mt-2";
                    container.appendChild(endMsg);

                    // Render math expressions for final message too
                    if (window.MathJax && window.MathJax.typesetPromise) {
                        MathJax.typesetPromise([container])
                            .then(() => console.log("MathJax rendered"))
                            .catch(err => console.error("MathJax rendering error:", err));
                    }
                }
            }
            
            sendToAI();
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