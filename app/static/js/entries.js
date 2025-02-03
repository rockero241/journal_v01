document.addEventListener("DOMContentLoaded", function () {
    document.querySelector(".delete-entry-btn")?.addEventListener("click", function () {
        const entryId = this.getAttribute("data-entry-id");

        if (confirm("Are you sure you want to delete this entry? This action cannot be undone.")) {
            fetch(`/journal/delete/${entryId}`, { method: "POST" })
            .then(response => {
                if (response.ok) {
                    window.location.href = "/entries";  // Redirect to entries list
                } else {
                    alert("Error deleting entry. Please try again.");
                }
            });
        }
    });
});
