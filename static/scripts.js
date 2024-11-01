document.addEventListener("DOMContentLoaded", () => {
    // Form validation for login and signup pages
    const loginForm = document.querySelector("form[action='/login']");
    const signUpForm = document.querySelector("form[action='/signup']");
    
    if (loginForm) {
        loginForm.addEventListener("submit", (event) => {
            const username = document.getElementById("username").value.trim();
            const password = document.getElementById("password").value.trim();
            if (!username || !password) {
                event.preventDefault();
                alert("Please enter both username and password.");
            }
        });
    }

    if (signUpForm) {
        signUpForm.addEventListener("submit", (event) => {
            const username = document.getElementById("username").value.trim();
            const password = document.getElementById("password").value.trim();
            const role = document.getElementById("role").value;
            if (!username || !password || !role) {
                event.preventDefault();
                alert("Please fill in all fields.");
            }
        });
    }

    // Delete confirmation for tasks
    const deleteForms = document.querySelectorAll("form[action*='delete_task']");
    deleteForms.forEach(form => {
        form.addEventListener("submit", function(event) {
            event.preventDefault();
            const taskName = form.parentNode.querySelector("strong").innerText;
            const confirmDelete = confirm(`Are you sure you want to delete the task: "${taskName}"?`);
            if (confirmDelete) {
                form.submit();
            }
        });
    });

    // Update task status dynamically without refreshing the page
    const statusSelects = document.querySelectorAll("select[name='status']");
    statusSelects.forEach(select => {
        select.addEventListener("change", function() {
            this.form.submit();
        });
    });
});

  