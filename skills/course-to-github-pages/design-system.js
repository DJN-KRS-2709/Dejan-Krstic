const sections = Array.from(document.querySelectorAll('section'));
const navDotsContainer = document.getElementById('navDots');
let currentIdx = 0;
let sorterVisible = false;

const STORAGE_KEY = 'skip-sections-' + document.title.replace(/[^a-zA-Z0-9]/g, '-').substring(0, 60);
const skippedSections = new Set(JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]'));

function saveSkips() { localStorage.setItem(STORAGE_KEY, JSON.stringify([...skippedSections])); }

function applySkips() {
  sections.forEach((sec, i) => sec.classList.toggle('skipped', skippedSections.has(i)));
  rebuildDots();
}

function rebuildDots() {
  navDotsContainer.innerHTML = '';
  sections.forEach((sec, i) => {
    if (skippedSections.has(i)) return;
    const dot = document.createElement('button');
    dot.className = 'nav-dot';
    const title = sec.dataset.title || 'Section';
    dot.innerHTML = `<span class="tooltip">${title}</span>`;
    dot.dataset.idx = i;
    dot.onclick = () => sections[i].scrollIntoView({ behavior: 'smooth' });
    navDotsContainer.appendChild(dot);
  });
}

function getActiveSections() { return sections.map((s, i) => i).filter(i => !skippedSections.has(i)); }

function updateProgress(idx) {
  currentIdx = idx;
  const active = getActiveSections();
  const posInActive = active.indexOf(idx);
  const progress = posInActive >= 0 ? (posInActive + 1) / active.length * 100 : 0;
  document.getElementById('progressBar').style.width = progress + '%';
  const dots = navDotsContainer.querySelectorAll('.nav-dot');
  dots.forEach(d => d.classList.toggle('active', parseInt(d.dataset.idx) === idx));
  document.getElementById('skip-badge').classList.toggle('visible', skippedSections.has(idx));
}

function toggleSkip(idx) {
  if (skippedSections.has(idx)) skippedSections.delete(idx);
  else skippedSections.add(idx);
  saveSkips();
  applySkips();
  updateProgress(currentIdx);
  if (sorterVisible) renderSorter();
}

function nextActive(from, dir) {
  let i = from + dir;
  while (i >= 0 && i < sections.length) {
    if (!skippedSections.has(i)) return i;
    i += dir;
  }
  return -1;
}

const observer = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      entry.target.classList.add('visible');
      const idx = sections.indexOf(entry.target);
      updateProgress(idx);
    }
  });
}, { threshold: 0.35 });
sections.forEach(sec => observer.observe(sec));

function renderSorter() {
  const grid = document.getElementById('sorter-grid');
  grid.innerHTML = '';
  sections.forEach((sec, i) => {
    const isSkipped = skippedSections.has(i);
    const isCurrent = i === currentIdx;
    const div = document.createElement('div');
    div.className = 'sorter-item' + (isSkipped ? ' sorter-skipped' : '') + (isCurrent ? ' sorter-active' : '');
    const title = sec.dataset.title || 'Section';
    div.innerHTML = `
      <div class="sorter-num">Section ${i + 1}</div>
      <div class="sorter-label">${title}</div>
      <button class="sorter-skip-btn ${isSkipped ? 'skip-on' : 'skip-off'}"
              onclick="event.stopPropagation(); toggleSkip(${i})">
        ${isSkipped ? '↩ Unskip' : '⊘ Skip'}
      </button>`;
    div.addEventListener('click', () => { sections[i].scrollIntoView({ behavior: 'smooth' }); closeSorter(); });
    grid.appendChild(div);
  });
}
function openSorter() { sorterVisible = true; renderSorter(); document.getElementById('slide-sorter').classList.add('visible'); }
function closeSorter() { sorterVisible = false; document.getElementById('slide-sorter').classList.remove('visible'); }

document.getElementById('skip-badge').addEventListener('click', () => toggleSkip(currentIdx));

document.addEventListener('keydown', (e) => {
  if (sorterVisible) {
    if (e.key === 'Escape' || e.key === 'm' || e.key === 'M') { e.preventDefault(); closeSorter(); }
    return;
  }
  if (e.key === 'ArrowDown' || e.key === 'ArrowRight' || e.key === ' ') {
    e.preventDefault();
    const n = nextActive(currentIdx, 1);
    if (n >= 0) sections[n].scrollIntoView({ behavior: 'smooth' });
  }
  else if (e.key === 'ArrowUp' || e.key === 'ArrowLeft') {
    e.preventDefault();
    const n = nextActive(currentIdx, -1);
    if (n >= 0) sections[n].scrollIntoView({ behavior: 'smooth' });
  }
  else if (e.key === 'k' || e.key === 'K') { toggleSkip(currentIdx); }
  else if (e.key === 'm' || e.key === 'M') { openSorter(); }
});

applySkips();
sections[0].classList.add('visible');
document.querySelectorAll('.tf-item').forEach(item => {
  item.addEventListener('click', () => item.classList.toggle('revealed'));
});
