// Small interface helpers. The server still validates and saves all data.
(function () {
  // Mobile menu
  var toggle = document.getElementById("nav-toggle");
  var nav = document.getElementById("site-nav");
  if (toggle && nav) {
    toggle.addEventListener("click", function () {
      var open = nav.classList.toggle("open");
      toggle.setAttribute("aria-expanded", open ? "true" : "false");
    });
  }

  // Confirmation dialog before delete: any form with data-confirm="message"
  document.querySelectorAll("form[data-confirm]").forEach(function (form) {
    form.addEventListener("submit", function (event) {
      if (!window.confirm(form.getAttribute("data-confirm"))) {
        event.preventDefault();
      }
    });
  });

  // Default the planner's due date to today for convenience
  var due = document.querySelector('form[action$="/planner/add"] input[type="date"]');
  if (due && !due.value) {
    var d = new Date();
    due.value = d.getFullYear() + "-" + String(d.getMonth() + 1).padStart(2, "0") + "-" + String(d.getDate()).padStart(2, "0");
  }
})();
