const dialog = document.getElementById("create-user");
const openButton = document.getElementById("create-user-open");
const cancelButton = document.getElementById("create-user-cancel");
const form = document.getElementById("create-user-form");
const message = document.getElementById("create-user-message");

openButton.addEventListener("click", function() {
    message.textContent = "";
    dialog.showModal();
});

cancelButton.addEventListener("click", function() {
    dialog.close();
});

form.addEventListener("submit", async function(event) {
    event.preventDefault();
    try {
        const formData = new FormData(form);
        const response = await fetch("/create_user", {
            method: "POST",
            body: new URLSearchParams(formData),
        });
        const result = await response.text();
        message.textContent = result;
    } catch (error) {
        console.error(error);
        message.textContent = "Could not reach the server.";
    }
});

