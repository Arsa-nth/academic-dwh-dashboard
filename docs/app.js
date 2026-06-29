/* ════════════════════════════════════════════════════════════════════
   app.js — DWH Dashboard JavaScript
   Nathanael Komang Bagus Prakarsa | 2026
   ════════════════════════════════════════════════════════════════════ */

// ── Color Palette (matches clean white theme) ────────────────────
const C = {
  text:    '#1a2133',
  muted:   '#6b7a99',
  dim:     '#a0aabe',
  border:  '#e4e8ef',
  // Primary palette
  blue:    '#2563eb',
  indigo:  '#4f46e5',
  green:   '#059669',
  amber:   '#d97706',
  red:     '#dc2626',
  teal:    '#0891b2',
  purple:  '#7c3aed',
  // Lighter tints for fills
  blueA:   'rgba(37,99,235,0.18)',
  indigoA: 'rgba(79,70,229,0.18)',
  greenA:  'rgba(5,150,105,0.18)',
  amberA:  'rgba(217,119,6,0.18)',
  redA:    'rgba(220,38,38,0.18)',
  tealA:   'rgba(8,145,178,0.18)',
  purpleA: 'rgba(124,58,237,0.18)',
  // Grid line
  grid:    'rgba(0,0,0,0.06)',
};

// ── Chart.js global defaults ─────────────────────────────────────
Chart.defaults.color          = C.muted;
Chart.defaults.borderColor    = C.grid;
Chart.defaults.font.family    = "'Plus Jakarta Sans', 'Inter', system-ui, sans-serif";
Chart.defaults.font.size      = 12;
Chart.defaults.plugins.legend.labels.boxRadius = 4;
Chart.defaults.plugins.legend.labels.padding   = 14;
Chart.defaults.plugins.legend.labels.color     = C.muted;

const gridOpts = {
  color: C.grid,
  drawBorder: false,
};

const tooltipDefaults = {
  backgroundColor: '#fff',
  titleColor: C.text,
  bodyColor: C.muted,
  borderColor: C.border,
  borderWidth: 1,
  padding: 10,
  cornerRadius: 8,
  boxPadding: 4,
};

// ── Data fetch ───────────────────────────────────────────────────
async function loadData() {
  try {
    const res = await fetch('data/dashboard_data.json');
    if (!res.ok) throw new Error('fetch failed');
    return await res.json();
  } catch (e) {
    console.warn('Fetch failed, using embedded fallback data.', e);
    return FALLBACK_DATA;
  }
}

// ── KPI Cards ────────────────────────────────────────────────────
const KPI_CONFIG = [
  { key: 'total_mhs',     label: 'Total Mahasiswa', icon: '👥', accent: C.blue,   accentLight: 'rgba(37,99,235,0.1)',   fmt: v => v },
  { key: 'total_records', label: 'Total Records',   icon: '📋', accent: C.indigo, accentLight: 'rgba(79,70,229,0.1)',   fmt: v => v },
  { key: 'total_lengkap', label: 'Nilai Lengkap',   icon: '✅', accent: C.green,  accentLight: 'rgba(5,150,105,0.1)',   fmt: v => v },
  { key: 'avg_prak',      label: 'Avg. Praktikum',  icon: '📈', accent: C.amber,  accentLight: 'rgba(217,119,6,0.1)',   fmt: v => parseFloat(v).toFixed(2) },
  { key: 'avg_teori',     label: 'Avg. Teori',      icon: '📉', accent: C.teal,   accentLight: 'rgba(8,145,178,0.1)',   fmt: v => parseFloat(v).toFixed(2) },
  { key: 'avg_overall',   label: 'Avg. Overall',    icon: '⭐', accent: C.purple, accentLight: 'rgba(124,58,237,0.1)',  fmt: v => parseFloat(v).toFixed(2) },
];

function renderKPI(kpi) {
  const grid = document.getElementById('kpi-grid');
  grid.innerHTML = '';
  KPI_CONFIG.forEach((cfg, i) => {
    const val = kpi[cfg.key] ?? '—';
    const card = document.createElement('div');
    card.className = 'kpi-card animate-in';
    card.id = `kpi-card-${i}`;
    card.style.setProperty('--accent', cfg.accent);
    card.style.animationDelay = `${i * 70}ms`;
    card.innerHTML = `
      <div class="kpi-icon-wrap" style="background:${cfg.accentLight};">${cfg.icon}</div>
      <div class="kpi-value">${cfg.fmt(val)}</div>
      <div class="kpi-label">${cfg.label}</div>
    `;
    grid.appendChild(card);
  });
}

// ── Chart 1: Progress Kelengkapan (Stacked Horizontal Bar) ───────
function buildChart1(data) {
  const raw = data.progress;
  const tipes = [...new Set(raw.map(r => r.tipe_kelas))];
  const statuses = ['lengkap', 'belum_dikoreksi', 'belum_dilaksanakan'];
  const labels_clean = { lengkap: 'Lengkap', belum_dikoreksi: 'Belum Dikoreksi', belum_dilaksanakan: 'Belum Dilaksanakan' };
  const colors = [C.green, C.amber, C.red];

  const pivot = {};
  tipes.forEach(t => { pivot[t] = {}; statuses.forEach(s => pivot[t][s] = 0); });
  raw.forEach(r => { pivot[r.tipe_kelas][r.status_nilai] = r.jumlah; });

  const datasets = statuses.map((s, si) => ({
    label: labels_clean[s],
    data: tipes.map(t => {
      const total = statuses.reduce((acc, ss) => acc + pivot[t][ss], 0);
      return total ? Math.round(pivot[t][s] / total * 1000) / 10 : 0;
    }),
    backgroundColor: colors[si],
    borderRadius: 4,
    borderSkipped: false,
  }));

  new Chart(document.getElementById('chart1'), {
    type: 'bar',
    data: {
      labels: tipes.map(t => t.charAt(0).toUpperCase() + t.slice(1)),
      datasets,
    },
    options: {
      indexAxis: 'y',
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        tooltip: {
          ...tooltipDefaults,
          callbacks: { label: ctx => ` ${ctx.dataset.label}: ${ctx.raw}%` },
        },
      },
      scales: {
        x: {
          stacked: true,
          min: 0, max: 100,
          ticks: { callback: v => v + '%', color: C.muted },
          grid: gridOpts,
        },
        y: {
          stacked: true,
          grid: { display: false },
          ticks: { color: C.text, font: { weight: '600' } },
        },
      },
    },
  });
}

// ── Chart 2: Distribusi Teori vs Praktikum (Grouped Bar Stats) ───
function buildChart2(data) {
  const dist = data.distribusi_tipe;
  const labels = dist.map(r => r.tipe_kelas.charAt(0).toUpperCase() + r.tipe_kelas.slice(1));
  const palette = [C.blue, C.indigo];
  const paletteA = [C.blueA, C.indigoA];

  new Chart(document.getElementById('chart2'), {
    type: 'bar',
    data: {
      labels,
      datasets: [
        {
          label: 'Rata-rata',
          data: dist.map(r => r.avg),
          backgroundColor: palette,
          borderRadius: 6,
          borderSkipped: false,
        },
        {
          label: 'Nilai Max',
          data: dist.map(r => r.mx),
          backgroundColor: paletteA,
          borderRadius: 6,
          borderSkipped: false,
        },
        {
          label: 'Nilai Min',
          data: dist.map(r => r.mn),
          backgroundColor: ['rgba(37,99,235,0.07)', 'rgba(79,70,229,0.07)'],
          borderRadius: 6,
          borderSkipped: false,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        tooltip: {
          ...tooltipDefaults,
          callbacks: { label: ctx => ` ${ctx.dataset.label}: ${ctx.raw}` },
        },
      },
      scales: {
        y: {
          min: 0,
          max: 115,
          grid: gridOpts,
          ticks: { color: C.muted },
        },
        x: { grid: { display: false }, ticks: { color: C.text, font: { weight: '600' } } },
      },
    },
  });
}

// ── Chart 3: Rata-rata per Mata Kuliah (Grouped Bar) ─────────────
function buildChart3(data) {
  const raw = data.rata_per_matkul;
  const matkuls = [...new Set(raw.map(r => r.nama_matkul))];
  const tipes   = ['praktikum', 'teori'];
  const tipeColors = { praktikum: C.blue, teori: C.indigo };

  const shortName = s => s.replace('Metode ', 'M. ');

  const pivot = {};
  matkuls.forEach(m => { pivot[m] = {}; });
  raw.forEach(r => { pivot[r.nama_matkul][r.tipe_kelas] = r.rata_rata; });

  const datasets = tipes.map(t => ({
    label: t.charAt(0).toUpperCase() + t.slice(1),
    data: matkuls.map(m => pivot[m][t] ?? 0),
    backgroundColor: tipeColors[t],
    borderRadius: 6,
    borderSkipped: false,
  }));

  new Chart(document.getElementById('chart3'), {
    type: 'bar',
    data: {
      labels: matkuls.map(shortName),
      datasets,
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        tooltip: {
          ...tooltipDefaults,
          callbacks: { label: ctx => ` ${ctx.dataset.label}: ${ctx.raw}` },
        },
      },
      scales: {
        y: {
          min: 0,
          max: 115,
          grid: gridOpts,
          ticks: { color: C.muted },
        },
        x: {
          grid: { display: false },
          ticks: {
            color: C.text,
            font: { weight: '600', size: 11 },
            maxRotation: 10,
          },
        },
      },
    },
  });
}

// ── Chart 4: Komponen Praktikum (Grouped Bar avg per komponen) ───
function buildChart4(data) {
  const raw = data.komponen_praktikum;
  const komps  = ['Tugas 1','Tugas 2','Presensi','Sikap','UTP','UAP'];
  const matkuls = [...new Set(raw.map(r => r.nama_matkul))];
  const matkul_colors = [C.blue, C.indigo, C.teal];

  const pivot = {};
  komps.forEach(k => { pivot[k] = {}; });
  raw.forEach(r => {
    if (komps.includes(r.nama_komponen)) {
      pivot[r.nama_komponen][r.nama_matkul] = r.rata_rata;
    }
  });

  const datasets = matkuls.map((m, i) => ({
    label: m,
    data: komps.map(k => pivot[k][m] ?? 0),
    backgroundColor: matkul_colors[i] || C.amber,
    borderRadius: 5,
    borderSkipped: false,
  }));

  new Chart(document.getElementById('chart4'), {
    type: 'bar',
    data: { labels: komps, datasets },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        tooltip: {
          ...tooltipDefaults,
          callbacks: { label: ctx => ` ${ctx.dataset.label}: ${ctx.raw}` },
        },
      },
      scales: {
        y: { min: 60, max: 105, grid: gridOpts, ticks: { color: C.muted } },
        x: { grid: { display: false }, ticks: { color: C.text, font: { weight: '600' } } },
      },
    },
  });
}

// ── Chart 5: Top 10 (Horizontal Bar) ─────────────────────────────
function buildChart5(data) {
  const top10 = [...data.top10].reverse();
  const labels = top10.map(r => {
    const initials = r.nama_matkul.split(' ').map(w => w[0]).join('');
    return `${r.nama} (${initials})`;
  });
  const values = top10.map(r => r.nilai_akhir);

  // Blue gradient from light to deep
  const gradColors = values.map((v, i) => {
    const t = i / Math.max(values.length - 1, 1);
    const opacity = 0.55 + t * 0.45;
    return `rgba(37,99,235,${opacity.toFixed(2)})`;
  });

  new Chart(document.getElementById('chart5'), {
    type: 'bar',
    data: {
      labels,
      datasets: [{
        label: 'Nilai Akhir Estimasi',
        data: values,
        backgroundColor: gradColors,
        borderRadius: 5,
        borderSkipped: false,
      }],
    },
    options: {
      indexAxis: 'y',
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: {
          ...tooltipDefaults,
          callbacks: { label: ctx => ` Nilai: ${ctx.raw}` },
        },
      },
      scales: {
        x: {
          min: 85, max: 102,
          grid: gridOpts,
          ticks: { color: C.muted },
        },
        y: {
          grid: { display: false },
          ticks: { color: C.text, font: { size: 11 } },
        },
      },
    },
  });
}

// ── Intersection Observer for animate-in ─────────────────────────
function initScrollAnimations() {
  const observer = new IntersectionObserver(
    entries => {
      entries.forEach(e => {
        if (e.isIntersecting) {
          e.target.classList.add('visible');
          observer.unobserve(e.target);
        }
      });
    },
    { threshold: 0.1 }
  );
  document.querySelectorAll('.chart-card, .kpi-card, .tech-card, .stat-card, .arch-card').forEach(el => {
    el.classList.add('animate-in');
    observer.observe(el);
  });
}

// ── Main ─────────────────────────────────────────────────────────
(async function main() {
  const data = await loadData();

  renderKPI(data.kpi);
  buildChart1(data);
  buildChart2(data);
  buildChart3(data);
  buildChart4(data);
  buildChart5(data);
  initScrollAnimations();
})();

// ── Fallback embedded data (jika file JSON tidak tersedia) ────────
const FALLBACK_DATA = {
  kpi: {
    total_mhs: 57,
    total_records: 740,
    total_lengkap: 482,
    avg_overall: 79.46,
    avg_prak: 92.66,
    avg_teori: 57.25,
    total_matkul: 3
  },
  progress: [
    {tipe_kelas:'praktikum', status_nilai:'lengkap',            jumlah: 350},
    {tipe_kelas:'praktikum', status_nilai:'belum_dikoreksi',    jumlah:  80},
    {tipe_kelas:'teori',     status_nilai:'lengkap',            jumlah: 132},
    {tipe_kelas:'teori',     status_nilai:'belum_dikoreksi',    jumlah:  57},
    {tipe_kelas:'teori',     status_nilai:'belum_dilaksanakan', jumlah:  57},
  ],
  distribusi_tipe: [
    {tipe_kelas:'praktikum', avg:92.66, mn:50.0, mx:100.0, n:350},
    {tipe_kelas:'teori',     avg:57.25, mn:10.0, mx:100.0, n:132},
  ],
  rata_per_matkul: [
    {nama_matkul:'Metode Statistika I',  tipe_kelas:'praktikum', rata_rata:94.1},
    {nama_matkul:'Metode Statistika II', tipe_kelas:'praktikum', rata_rata:91.8},
    {nama_matkul:'Metode Statistika II', tipe_kelas:'teori',     rata_rata:57.25},
    {nama_matkul:'Metode Sains Data I',  tipe_kelas:'praktikum', rata_rata:92.0},
  ],
  komponen_praktikum: [
    {nama_matkul:'Metode Statistika I',  nama_komponen:'Tugas 1',  bobot_persen:15, rata_rata:92.5, n:34},
    {nama_matkul:'Metode Statistika I',  nama_komponen:'Tugas 2',  bobot_persen:15, rata_rata:91.0, n:34},
    {nama_matkul:'Metode Statistika I',  nama_komponen:'Presensi', bobot_persen:15, rata_rata:96.2, n:34},
    {nama_matkul:'Metode Statistika I',  nama_komponen:'Sikap',    bobot_persen:5,  rata_rata:99.0, n:34},
    {nama_matkul:'Metode Statistika I',  nama_komponen:'UTP',      bobot_persen:20, rata_rata:89.3, n:34},
    {nama_matkul:'Metode Statistika I',  nama_komponen:'UAP',      bobot_persen:30, rata_rata:95.1, n:34},
    {nama_matkul:'Metode Statistika II', nama_komponen:'Tugas 1',  bobot_persen:15, rata_rata:91.0, n:34},
    {nama_matkul:'Metode Statistika II', nama_komponen:'Presensi', bobot_persen:15, rata_rata:95.0, n:34},
    {nama_matkul:'Metode Statistika II', nama_komponen:'Sikap',    bobot_persen:5,  rata_rata:98.5, n:34},
    {nama_matkul:'Metode Statistika II', nama_komponen:'UTP',      bobot_persen:20, rata_rata:88.0, n:34},
    {nama_matkul:'Metode Sains Data I',  nama_komponen:'UAP',      bobot_persen:30, rata_rata:92.0, n:34},
    {nama_matkul:'Metode Sains Data I',  nama_komponen:'Presensi', bobot_persen:15, rata_rata:97.0, n:34},
  ],
  top10: [
    {nama:'Mahasiswa 30', nama_matkul:'Metode Statistika I',  nilai_akhir:98.65},
    {nama:'Mahasiswa 13', nama_matkul:'Metode Statistika I',  nilai_akhir:97.40},
    {nama:'Mahasiswa 06', nama_matkul:'Metode Statistika I',  nilai_akhir:97.20},
    {nama:'Mahasiswa 17', nama_matkul:'Metode Statistika I',  nilai_akhir:96.90},
    {nama:'Mahasiswa 22', nama_matkul:'Metode Statistika II', nilai_akhir:96.50},
    {nama:'Mahasiswa 05', nama_matkul:'Metode Statistika I',  nilai_akhir:96.20},
    {nama:'Mahasiswa 41', nama_matkul:'Metode Sains Data I',  nilai_akhir:95.80},
    {nama:'Mahasiswa 33', nama_matkul:'Metode Statistika II', nilai_akhir:95.50},
    {nama:'Mahasiswa 09', nama_matkul:'Metode Sains Data I',  nilai_akhir:95.10},
    {nama:'Mahasiswa 15', nama_matkul:'Metode Statistika I',  nilai_akhir:94.70},
  ],
  semua_nilai: []
};
