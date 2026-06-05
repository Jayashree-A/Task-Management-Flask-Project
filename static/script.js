document.getElementById("searchInput").addEventListener("keyup", function () {
    let value = this.value.toLowerCase();
    let tasks = document.querySelectorAll(".task-card");

    tasks.forEach(task => {
        let text = task.innerText.toLowerCase();
        task.style.display = text.includes(value) ? "block" : "none";
    });
});