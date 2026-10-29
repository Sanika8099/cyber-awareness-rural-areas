document.addEventListener("DOMContentLoaded", () => {
  const flash = document.querySelector(".flash");
  if (flash) setTimeout(() => flash.remove(), 3500);

  document.querySelectorAll("[data-menu]").forEach(btn => {
    btn.addEventListener("click", () => document.body.classList.toggle("menu-open"));
  });

  document.querySelectorAll("textarea[data-counter]").forEach(t => {
    const counter = document.getElementById(t.dataset.counter);
    const max = t.maxLength || 500;
    const update = () => { if(counter) counter.textContent = `${t.value.length}/${max}`; };
    t.addEventListener("input", update); update();
  });

  document.querySelectorAll(".rating-stars").forEach(box => {
    const hidden = box.querySelector("input");
    box.querySelectorAll("button").forEach((b,i) => b.addEventListener("click",()=>{
      hidden.value = i + 1;
      box.querySelectorAll("button").forEach((x,j)=>x.style.opacity = j <= i ? "1" : ".35");
    }));
  });
});
