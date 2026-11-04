// Filters the full publication list by type and by free text (publications.html, el/publications.html).
(function () {
  var list = document.getElementById("plist");
  if (!list) return;
  var items = Array.prototype.slice.call(list.querySelectorAll("li[data-type]"));
  var groups = Array.prototype.slice.call(list.querySelectorAll("[data-year-group]"));
  var buttons = Array.prototype.slice.call(document.querySelectorAll(".filters button[data-filter]"));
  var search = document.getElementById("psearch");
  var count = document.getElementById("pcount");
  var template = count.getAttribute("data-template");
  var type = "all";

  function norm(s) {
    return s.toLowerCase().normalize("NFD").replace(/[̀-ͯ]/g, "");
  }
  items.forEach(function (li) { li._text = norm(li.textContent); });

  function apply() {
    var q = norm(search.value.trim());
    var shown = 0;
    items.forEach(function (li) {
      var ok = (type === "all" || li.getAttribute("data-type") === type) && (!q || li._text.indexOf(q) !== -1);
      li.hidden = !ok;
      if (ok) shown += 1;
    });
    groups.forEach(function (g) {
      g.hidden = !g.querySelector("li[data-type]:not([hidden])");
    });
    count.textContent = template.replace("{n}", shown).replace("{total}", items.length);
  }

  buttons.forEach(function (b) {
    b.addEventListener("click", function () {
      type = b.getAttribute("data-filter");
      buttons.forEach(function (x) { x.setAttribute("aria-pressed", String(x === b)); });
      apply();
    });
  });
  search.addEventListener("input", apply);
  apply();
})();
