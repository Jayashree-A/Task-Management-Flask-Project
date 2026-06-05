document.addEventListener("DOMContentLoaded", function () {

    const searchInput = document.getElementById("searchInput");

    if (!searchInput) return;

    searchInput.addEventListener("keyup", function () {

        let value = this.value.toLowerCase().trim();
        let tasks = document.querySelectorAll(".task-card");

        tasks.forEach(task => {
            let text = task.innerText.toLowerCase();

            if (text.includes(value)) {
                task.style.display = "";
            } else {
                task.style.display = "none";
            }
        });
    });

});