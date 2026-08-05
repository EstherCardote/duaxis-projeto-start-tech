document.addEventListener("DOMContentLoaded", () => {
  const sidebar = document.getElementById("sidebar");
  const toggleBtn = document.getElementById("sidebar-toggle");
  const chatInput = document.getElementById("chat-input");
  const chips = document.querySelectorAll(".chip[data-suggestion]");
  const disabledLinks = document.querySelectorAll(".sidebar__item--disabled");

  if (toggleBtn && sidebar) {
    toggleBtn.addEventListener("click", () => {
      const isCollapsed = sidebar.classList.toggle("sidebar--collapsed");
      toggleBtn.setAttribute(
        "aria-label",
        isCollapsed ? "Expandir menu" : "Recolher menu",
      );
    });
  }

  disabledLinks.forEach((link) => {
    link.addEventListener("click", (event) => {
      event.preventDefault();
    });
  });

  chips.forEach((chip) => {
    chip.addEventListener("click", () => {
      if (chatInput) {
        chatInput.value = chip.dataset.suggestion || "";
        chatInput.focus();
      }
    });
  });
});
