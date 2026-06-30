const timerElement = document.getElementById("quizTimer");
const quizForm = document.getElementById("quizAttemptForm");

if (timerElement && quizForm) {
    let remainingSeconds = Number(timerElement.dataset.duration) * 60;
    let submitted = false;

    const updateTimer = () => {
        const minutes = Math.floor(remainingSeconds / 60);
        const seconds = remainingSeconds % 60;

        timerElement.textContent = `${minutes}:${String(seconds).padStart(2, "0")}`;

        if (remainingSeconds <= 60) {
            timerElement.classList.add("text-danger");
        }

        if (remainingSeconds <= 0 && !submitted) {
            submitted = true;
            quizForm.submit();
            return;
        }

        remainingSeconds -= 1;
    };

    quizForm.addEventListener("submit", () => {
        submitted = true;
    });

    updateTimer();
    setInterval(updateTimer, 1000);
}
