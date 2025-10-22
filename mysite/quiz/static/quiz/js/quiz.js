document.addEventListener("DOMContentLoaded", () => {
  const questions = JSON.parse(
    document.getElementById("questions-data").textContent
  );

  let currentIndex = 0;
  let answered = false;
  const answers = {}; // <-- store question_id : selected_option_id

  const questionText = document.getElementById("question-text");
  const difficultyTag = document.getElementById("difficulty-tag")
  const nextBtn = document.getElementById("next-btn");
  const optionsContainer = document.getElementById("options-container");

  // Load first question
  loadQuestion(currentIndex);

  // Next button click
  nextBtn.addEventListener("click", () => {
    currentIndex++;
    if (currentIndex < questions.length) {
      loadQuestion(currentIndex);
    } else {
      // No more questions -> submit via AJAX
      fetch(submitUrl, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": getCookie("csrftoken"),
        },
        body: JSON.stringify({ answers }),
      })
      .then((response) => response.json())
      .then((data) => {
        alert(`Quiz complete! Your score: ${data.score.toFixed(1)}%`);
        window.location.href = resultsUrl;
      });
    }
  });
  

  function loadQuestion(index) {
    answered = false;
    nextBtn.disabled = true;

    // Load question text
    questionText.textContent = questions[index].text;

    // Load difficulty
    difficultyTag.textContent = questions[index].difficulty;
    difficultyTag.className = `position-absolute top-0 start-0 m-4 badge rounded-pill px-3 py-2 fs-6 ${questions[index].difficulty.toLowerCase()}`;

    // Rebuild form options
    optionsContainer.innerHTML = "";

    questions[index].options.forEach(option => {
      const btn = document.createElement("button");
      btn.type = "button";
      btn.className = "btn btn-outline-primary mb-2 option-btn";
      btn.textContent = option.text;
      btn.dataset.optionId = option.id;

      btn.addEventListener("click", () => {
        if (answered) return; //second click does not do anyth
        answered = true;
        nextBtn.disabled = false;

        const correctOption = questions[index].options.find(opt => opt.is_correct).id
        const selectedOptionId = parseInt(btn.dataset.optionId)

        // Save question id and chose option to the answers dictionary
        answers[questions[index].id] = selectedOptionId;

        // Highlight Selection
        if (selectedOptionId === correctOption) {
          btn.classList.remove("btn-outline-primary");
          btn.classList.add("correct");
        } else {
          btn.classList.remove("btn-outline-primary");
          btn.classList.add("wrong");
        }

        // Show correct option
        const correctBtn = Array.from(optionsContainer.children).find(
          btn => parseInt(btn.dataset.optionId) === correctOption
        );
        if (correctBtn) correctBtn.classList.add("correct");

        // Disable all buttons to prevent multiple clicks
        Array.from(optionsContainer.children).forEach(b => b.disabled = true);

        // Update progress bar
        updateProgressBar(currentIndex, questions.length)
      })

      optionsContainer.appendChild(btn)
    });
  }


  function updateProgressBar(currentQuestion, totalQuestions) {
    const progress = ((currentQuestion+1) / totalQuestions) * 100;
    document.getElementById("progress-bar").style.width = progress + "%";
  }
  
  function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== "") {
      const cookies = document.cookie.split(";");
      for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim();
        if (cookie.substring(0, name.length + 1) === name + "=") {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  }
});