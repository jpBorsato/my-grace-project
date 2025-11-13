document.addEventListener("DOMContentLoaded", function () {
  const input = document.getElementById("search-input");
  const resultsBox = document.getElementById("search-results");
  let timeout = null;

  input.addEventListener("keyup", function () {
    clearTimeout(timeout);
    const query = this.value.trim();
    if (query.length === 0) {
      resultsBox.style.display = "none";
      return;
    }

    timeout = setTimeout(() => {
      fetch(`/search/?q=${encodeURIComponent(query)}`, {
        headers: { "X-Requested-With": "XMLHttpRequest" }
      })
        .then(response => response.json())
        .then(data => {
          const { results } = data;
          let html = "";

          for (const [category, items] of Object.entries(results)) {
            if (items.list.length > 0) {
              html += `<h6 class="dropdown-header text-uppercase">${category}</h6>`;
              items.list.forEach(item => {
                html += `<a class="dropdown-item" href="/${items.url}${item.slug}">${item.text}</a>`;
              });
            }
          }

          resultsBox.innerHTML = html || '<span class="dropdown-item disabled">No results found</span>';
          resultsBox.style.display = "block";
        });
    }, 300); // debounce delay
  });

  document.addEventListener("click", (e) => {
    if (!resultsBox.contains(e.target) && e.target !== input) {
      resultsBox.style.display = "none";
    }
  });
});
