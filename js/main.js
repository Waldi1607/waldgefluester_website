// ── NAVBAR: scrolled state
const navbar = document.getElementById('navbar');
window.addEventListener('scroll', () => {
  navbar.classList.toggle('scrolled', window.scrollY > 60);
});

// ── HAMBURGER MENU
const hamburger = document.querySelector('.hamburger');
const mobileMenu = document.getElementById('mobileMenu');
const mobileClose = document.querySelector('.mobile-close');

hamburger?.addEventListener('click', () => mobileMenu.classList.add('open'));
mobileClose?.addEventListener('click', () => mobileMenu.classList.remove('open'));
mobileMenu?.querySelectorAll('a').forEach(a => {
  a.addEventListener('click', () => mobileMenu.classList.remove('open'));
});

// ── CONTACT FORM
const contactForm = document.getElementById('contactForm');
contactForm?.addEventListener('submit', (e) => {
  e.preventDefault();
  const formCard = contactForm.closest('.form-card');
  formCard.innerHTML = `
    <div class="form-success" style="display:block">
      <div style="font-size:3rem; margin-bottom:1rem">✉️</div>
      <h3>Vielen Dank!</h3>
      <p>Wir haben eure Anfrage erhalten und melden uns schnellstmöglich bei euch.</p>
    </div>
  `;
});

// ── ACTIVE NAV LINK on scroll
const sections = document.querySelectorAll('section[id]');
const navAnchors = document.querySelectorAll('.nav-links a[href^="#"]');

const observer = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      const id = entry.target.id;
      navAnchors.forEach(a => {
        a.style.color = a.getAttribute('href') === `#${id}` ? 'var(--gold)' : '';
      });
    }
  });
}, { threshold: 0.4 });

sections.forEach(s => observer.observe(s));

// ── FADE-IN ANIMATION on scroll
const fadeEls = document.querySelectorAll('.fade-in');
const fadeObs = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      entry.target.classList.add('visible');
      fadeObs.unobserve(entry.target);
    }
  });
}, { threshold: 0.15 });

fadeEls.forEach(el => fadeObs.observe(el));
