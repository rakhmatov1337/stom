window.addEventListener("scroll", () => {
  const hero_top = hero.getBoundingClientRect().top;

  if (homeTags.getBoundingClientRect().top <= 0) {
    homeTags.classList.add("scrolled");
    if (hero_top >= 0) {
      homeTags.classList.remove("scrolled");
    }
  }
});

categoryItems.forEach((item) => {
  item.addEventListener("click", () => {
    categoryItems.forEach((catItem) => {
      catItem.classList.remove("active");
    });

    item.classList.add("active");
  });
});
