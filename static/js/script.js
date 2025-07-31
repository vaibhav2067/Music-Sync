const bg2 = document.querySelector('.bg2');
const bg3 = document.querySelector('.bg3');

window.addEventListener('scroll', () => {
  const scrollTop = window.scrollY;

  // bg2 rotates normally
  const rotation1 = scrollTop * 0.1;

  // bg3 starts at 99deg and rotates with scroll
  const rotation2 = 99 + (scrollTop * -0.1);

  bg2.style.transform = `rotate(${rotation1}deg)`;
  bg3.style.transform = `rotate(${rotation2}deg)`;
});

