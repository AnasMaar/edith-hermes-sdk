/* Keep the standard Material search interaction, with an additional familiar shortcut. */
document.addEventListener("keydown", (event) => {
  if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === "k") {
    const search = document.querySelector('[data-md-component="search-query"]');
    if (search) {
      event.preventDefault();
      const toggle = document.querySelector("#__search");
      if (toggle && !toggle.checked) toggle.click();
      search.focus();
    }
  }
});

// Material's search listens for keyup; an input event also covers context-menu paste.
document.addEventListener("input", (event) => {
  const search = event.target;
  if (search instanceof HTMLInputElement && search.matches('[data-md-component="search-query"]')) {
    search.dispatchEvent(new KeyboardEvent("keyup", { bubbles: true }));
  }
});
