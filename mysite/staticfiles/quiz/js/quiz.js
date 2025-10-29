document.addEventListener("DOMContentLoaded", () => {
  const questions = JSON.parse(
    document.getElementById("questions-data").textContent
  );

  let currentIndex = 0;
  let answered = false;

  const answers = {}; // <-- store question_id : selected_option_id

  const questionText = document.getElementById("question-text");
  const form = document.getElementById("quiz-form");
  const nextBtn = document.getElementById("next-btn");

  // Enable Next when option selected
  form.addEventListener("change", () => {
    nextBtn.disabled = false;
  });

  nextBtn.addEventListener("click", () => {
    const selected = form.querySelector("input[name='answer']:checked");
    if (!selected) return;

    // Save questionId and selectedOptionId in the form
    const questionId = questions[currentIndex].id;
    const selectedOptionId = parseInt(selected.value);
    answers[questionId] = selectedOptionId;

    if (!answered) {
      // First click -> check correctness
      const correctOption = questions[currentIndex].options.find(opt => opt.is_correct).id;
      console.log(correctOption)

      if (parseInt(selected.value) === correctOption) {
        selected.parentElement.classList.add("text-success", "fw-bold");
      } else {
        selected.parentElement.classList.add("text-danger", "fw-bold");
      }
      answered = true;
      nextBtn.textContent = "Next Question";
    } else {
      // Second click -> load next question
      currentIndex++;
      if (currentIndex < questions.length) {
        loadQuestion(currentIndex);
      } else {
        // Attach answers dict before submit
        const answersInput = document.createElement("input");
        answersInput.type = "hidden";
        answersInput.name = "answers";
        answersInput.value = JSON.stringify(answers);
        form.appendChild(answersInput);

        form.submit();
      }
    }
  });


  const optionsContainer = document.getElementById("options-container");

  function loadQuestion(index) {
    answered = false;
    nextBtn.textContent = "Next";
    nextBtn.disabled = true;

    // Load question text
    questionText.textContent = questions[index].text;

    // Rebuild form options
    optionsContainer.innerHTML = "";
    questions[index].options.forEach(option => {
      const div = document.createElement("div");
      div.className = "form-check mb-3";
      div.innerHTML = `
        <input class="form-check-input" type="radio" name="answer" id="option${option.id}" value="${option.id}">
        <label class="form-check-label" for="option${option.id}">
          ${option.text}
        </label>
      `;
      optionsContainer.appendChild(div);
    });
  }
  // Load first question
  loadQuestion(currentIndex);
});