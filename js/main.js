// ── NAVBAR: scrolled state + scroll-to-top
const navbar = document.getElementById('navbar');
const scrollTopBtn = document.getElementById('scrollTop');

window.addEventListener('scroll', () => {
  const y = window.scrollY;
  navbar.classList.toggle('scrolled', y > 60);
  scrollTopBtn?.classList.toggle('visible', y > 400);
});

scrollTopBtn?.addEventListener('click', () => window.scrollTo({ top: 0, behavior: 'smooth' }));

// ── HAMBURGER / MOBILE MENU
const hamburger = document.querySelector('.hamburger');
const mobileMenu = document.getElementById('mobileMenu');
hamburger?.addEventListener('click', () => mobileMenu.classList.add('open'));
document.querySelector('.mobile-close')?.addEventListener('click', () => mobileMenu.classList.remove('open'));
mobileMenu?.querySelectorAll('a').forEach(a => a.addEventListener('click', () => mobileMenu.classList.remove('open')));

// ── HERO SLIDER
function initSlider(slides, dots, prevBtn, nextBtn) {
  if (!slides.length) return;
  let current = 0;
  const total = slides.length;

  function goTo(i) {
    slides[current].classList.remove('active');
    dots?.[current]?.classList.remove('active');
    current = (i + total) % total;
    slides[current].classList.add('active');
    dots?.[current]?.classList.add('active');
  }

  prevBtn?.addEventListener('click', () => goTo(current - 1));
  nextBtn?.addEventListener('click', () => goTo(current + 1));
  dots?.forEach((dot, i) => dot.addEventListener('click', () => goTo(i)));

  setInterval(() => goTo(current + 1), 5000);
}

initSlider(
  [...document.querySelectorAll('.hero-slide')],
  [...document.querySelectorAll('.hero-dot')],
  document.querySelector('.hero-arrow-prev'),
  document.querySelector('.hero-arrow-next')
);

// ── IMAGE CAROUSELS (Hochzeit, Winter)
document.querySelectorAll('.carousel').forEach(carousel => {
  const track = carousel.querySelector('.carousel-track');
  const slides = carousel.querySelectorAll('.carousel-slide');
  const prev = carousel.querySelector('.carousel-btn.prev');
  const next = carousel.querySelector('.carousel-btn.next');
  if (!slides.length) return;

  let current = 0;

  function moveTo(i) {
    current = (i + slides.length) % slides.length;
    track.style.transform = `translateX(-${current * 100}%)`;
  }

  prev?.addEventListener('click', () => moveTo(current - 1));
  next?.addEventListener('click', () => moveTo(current + 1));
});

// ── ACCORDION / FAQ
document.querySelectorAll('.accordion-trigger').forEach(trigger => {
  trigger.addEventListener('click', () => {
    const panel = trigger.nextElementSibling;
    const isOpen = panel.classList.contains('open');

    // Close all
    document.querySelectorAll('.accordion-panel').forEach(p => p.classList.remove('open'));
    document.querySelectorAll('.accordion-trigger').forEach(t => t.classList.remove('open'));

    if (!isOpen) {
      panel.classList.add('open');
      trigger.classList.add('open');
    }
  });
});

// ── CONTACT FORM
document.getElementById('contactForm')?.addEventListener('submit', e => {
  e.preventDefault();
  const form = e.target;
  form.innerHTML = `
    <div style="text-align:center;padding:3rem 1rem">
      <div style="font-size:3rem;margin-bottom:1rem">✉️</div>
      <h3 style="font-family:'Playfair Display',serif;color:#1e3a1e;margin-bottom:.75rem">Vielen Dank!</h3>
      <p style="color:#5a5a5a">Wir haben eure Anfrage erhalten und melden uns schnellstmöglich.</p>
    </div>
  `;
});

// ── FADE-IN ON SCROLL
const fadeEls = document.querySelectorAll('.fade-in');
const fadeObserver = new IntersectionObserver(entries => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      entry.target.classList.add('visible');
      fadeObserver.unobserve(entry.target);
    }
  });
}, { threshold: 0.12 });

fadeEls.forEach(el => fadeObserver.observe(el));

// ── COOKIE BANNER
const cookieBanner = document.getElementById('cookieBanner');
if (cookieBanner && !localStorage.getItem('cookieConsent')) {
  setTimeout(() => cookieBanner.classList.add('visible'), 1500);
}
document.getElementById('cookieAccept')?.addEventListener('click', () => {
  localStorage.setItem('cookieConsent', 'all');
  cookieBanner.classList.remove('visible');
});
document.getElementById('cookieDecline')?.addEventListener('click', () => {
  localStorage.setItem('cookieConsent', 'necessary');
  cookieBanner.classList.remove('visible');
});
