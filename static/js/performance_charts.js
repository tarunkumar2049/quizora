const progressCanvas = document.getElementById("progressChart");
const correctPieCanvas = document.getElementById("correctPieChart");
const topicBarCanvas = document.getElementById("topicBarChart");

if (progressCanvas) {
    new Chart(progressCanvas, {
        type: "line",
        data: {
            labels: progressLabels,
            datasets: [{
                label: "Accuracy %",
                data: progressValues,
                borderColor: "#0d6efd",
                backgroundColor: "rgba(13, 110, 253, 0.12)",
                tension: 0.3,
                fill: true
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100
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
                data: correctVsIncorrect,
                backgroundColor: ["#198754", "#dc3545"]
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false
        }
    });
}

if (topicBarCanvas) {
    new Chart(topicBarCanvas, {
        type: "bar",
        data: {
            labels: topicLabels,
            datasets: [{
                label: "Topic Accuracy %",
                data: topicValues,
                backgroundColor: "#0dcaf0"
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100
                }
            }
        }
    });
}
