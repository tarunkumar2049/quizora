const chartDefaults = {
    responsive: true,
    maintainAspectRatio: false
};

const attemptTrendCanvas = document.getElementById("attemptTrendChart");
const correctPieCanvas = document.getElementById("adminCorrectPieChart");
const quizAccuracyCanvas = document.getElementById("quizAccuracyChart");
const subjectAccuracyCanvas = document.getElementById("subjectAccuracyChart");
const difficultyAccuracyCanvas = document.getElementById("difficultyAccuracyChart");

if (attemptTrendCanvas) {
    new Chart(attemptTrendCanvas, {
        type: "line",
        data: {
            labels: analyticsChartData.attempt_labels,
            datasets: [
                {
                    label: "Attempts",
                    data: analyticsChartData.attempt_counts,
                    borderColor: "#0d6efd",
                    backgroundColor: "rgba(13, 110, 253, 0.12)",
                    tension: 0.3,
                    yAxisID: "y"
                },
                {
                    label: "Average Accuracy %",
                    data: analyticsChartData.attempt_accuracy,
                    borderColor: "#198754",
                    backgroundColor: "rgba(25, 135, 84, 0.12)",
                    tension: 0.3,
                    yAxisID: "y1"
                }
            ]
        },
        options: {
            ...chartDefaults,
            scales: {
                y: {
                    beginAtZero: true,
                    position: "left"
                },
                y1: {
                    beginAtZero: true,
                    max: 100,
                    position: "right",
                    grid: {
                        drawOnChartArea: false
                    }
                }
            }
        }
    });
}

if (correctPieCanvas) {
    new Chart(correctPieCanvas, {
        type: "pie",
        data: {
            labels: ["Correct", "Incorrect"],
            datasets: [{
                data: analyticsChartData.correct_vs_incorrect,
                backgroundColor: ["#198754", "#dc3545"]
            }]
        },
        options: chartDefaults
    });
}

if (quizAccuracyCanvas) {
    new Chart(quizAccuracyCanvas, {
        type: "bar",
        data: {
            labels: analyticsChartData.quiz_labels,
            datasets: [{
                label: "Accuracy %",
                data: analyticsChartData.quiz_accuracy,
                backgroundColor: "#0d6efd"
            }]
        },
        options: {
            ...chartDefaults,
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100
                }
            }
        }
    });
}

if (subjectAccuracyCanvas) {
    new Chart(subjectAccuracyCanvas, {
        type: "bar",
        data: {
            labels: analyticsChartData.subject_labels,
            datasets: [{
                label: "Accuracy %",
                data: analyticsChartData.subject_accuracy,
                backgroundColor: "#0dcaf0"
            }]
        },
        options: {
            ...chartDefaults,
            indexAxis: "y",
            scales: {
                x: {
                    beginAtZero: true,
                    max: 100
                }
            }
        }
    });
}

if (difficultyAccuracyCanvas) {
    new Chart(difficultyAccuracyCanvas, {
        type: "doughnut",
        data: {
            labels: analyticsChartData.difficulty_labels,
            datasets: [{
                data: analyticsChartData.difficulty_accuracy,
                backgroundColor: ["#198754", "#ffc107", "#dc3545"]
            }]
        },
        options: chartDefaults
    });
}
