const toggle = document.getElementById("menuToggle");
const nav = document.getElementById("mainNav");
if (toggle && nav) {
  toggle.addEventListener("click", () => nav.classList.toggle("open"));
  nav.querySelectorAll("a").forEach(link => link.addEventListener("click", () => nav.classList.remove("open")));
}
document.querySelectorAll("details").forEach(item => {
  item.addEventListener("toggle", () => {
    if (item.open) document.querySelectorAll("details").forEach(other => { if (other !== item) other.open = false; });
  });
});
