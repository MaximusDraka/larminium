document.addEventListener("DOMContentLoaded", function () {
  const buttons = document.querySelectorAll(".filter-btn");
  const cards = document.querySelectorAll(".article-card");

  buttons.forEach(button => {
    button.addEventListener("click", () => {
      const filter = button.getAttribute("data-filter");

      cards.forEach(card => {
        const category = card.getAttribute("data-category");

        if (filter === "all" || category === filter) {
          card.style.display = "block";
        } else {
          card.style.display = "none";
        }
      });

      // Optional: Highlight active button
      buttons.forEach(btn => btn.classList.remove("active"));
      button.classList.add("active");
    });
  });
});
