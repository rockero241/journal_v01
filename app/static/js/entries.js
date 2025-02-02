document.addEventListener("DOMContentLoaded", function () {
    console.log("Entries.js loaded and ready for enhancement!");
    console.log("Current entry cards:", document.querySelectorAll(".entry-card").length);
    
    document.querySelectorAll(".toggle-feedback").forEach(button => {
        console.log("Found button:", button);
        
        button.addEventListener("click", function () {
            console.log("Button clicked!");
            const feedbackText = this.nextElementSibling;
            feedbackText.style.display = (feedbackText.style.display === "none" || !feedbackText.style.display) ? "block" : "none";
            this.textContent = feedbackText.style.display === "none" ? "Show AI Feedback" : "Hide AI Feedback";
        });
    });
});
