const swiper = new Swiper(".swiper", {
  direction: "horizontal",
  loop: true,
  autoHeight: true,

  pagination: {
    el: ".swiper-pagination",
  },

  speed: 2000,

  autoplay: {
    delay: 2000,
  },
  spaceBetween: 20,

  navigation: {
    nextEl: ".swiper-button-next",
    prevEl: ".swiper-button-prev",
  },
});
