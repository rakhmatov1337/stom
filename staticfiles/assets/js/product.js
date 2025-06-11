window.addEventListener("load", () => {
  const cartItems = Number(localStorage.getItem("cartItems"));
  headerCart.textContent = !cartItems ? 0 : cartItems;
});

homeLikes.forEach((like) => {
  like.addEventListener("click", () => {
    like.classList.toggle("fa-solid");
    like.classList.toggle("fa-regular");
  });
});

homeAddBtn.forEach((btn) => {
  btn.addEventListener("click", () => {
    const additionals = btn.nextElementSibling;
    const cartItems = Number(localStorage.getItem("cartItems"));
    const span = additionals.querySelector("span");

    btn.classList.add("disabled");
    additionals.classList.add("active");
    localStorage.setItem("cartItems", cartItems + 1);
    span.textContent = "1 шт.";

    headerCart.textContent = localStorage.getItem("cartItems");
  });
});

cartControlBtns.forEach((btn) => {
  btn.addEventListener("click", () => {
    const parent = btn.parentElement;
    const parentPrevSibling = btn.parentElement.previousElementSibling;
    const cartItems = Number(localStorage.getItem("cartItems"));

    const increment = btn.className.search("increment") >= 0;
    const decrement = btn.className.search("decrement") >= 0;

    const span = parent.querySelector("span");
    let count = Number(span.textContent.split(" ")[0]);

    if (increment) {
      count++;
      localStorage.setItem("cartItems", cartItems + 1);
      headerCart.textContent = localStorage.getItem("cartItems");
    } else if (decrement && count > 0) {
      count--;
      localStorage.setItem("cartItems", cartItems - 1);
      headerCart.textContent = localStorage.getItem("cartItems");
    }

    span.textContent = `${count} шт.`;

    if (count === 0) {
      parentPrevSibling.classList.remove("disabled");
      parent.classList.remove("active");
    }
  });
});
