const passwords = document.querySelectorAll(".auth-input-wrapper.password i");

passwords.forEach((pass) => {
  pass.addEventListener("click", () => {
    const input = pass.previousElementSibling;

    pass.classList.toggle("fa-eye");
    pass.classList.toggle("fa-eye-slash");
    input.type = input.type === "text" ? "password" : "text";
  });
});
