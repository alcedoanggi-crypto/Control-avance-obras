/* Graficos del dashboard con Chart.js (paleta industrial naranja/grafito). */
(function () {
  const PALETA = {
    naranja: "#C2410C",
    naranjaClaro: "#EA580C",
    grafito: "#1F2937",
    grafitoClaro: "#334155",
    grisConcreto: "#94A3B8",
    amarillo: "#F59E0B",
    verde: "#15803D",
    rojo: "#DC2626",
  };
  const SERIE = [PALETA.naranja, PALETA.grafito, PALETA.amarillo, PALETA.verde,
                 PALETA.grisConcreto, PALETA.naranjaClaro, "#0F766E", "#7C2D12"];

  const endpoint = document.body.dataset.graficosUrl;
  if (!endpoint) return;

  Chart.defaults.font.family = "Segoe UI, Roboto, Arial, sans-serif";
  Chart.defaults.color = PALETA.grafito;

  gauge("chartGauge", parseFloat(document.body.dataset.avanceFinanciero || 0));

  fetch(endpoint)
    .then((r) => r.json())
    .then((d) => {
      if (d.avance_disciplina) barraAgrupada("chartAvanceDisciplina", d.avance_disciplina);
      if (d.peso_disciplina) dona("chartPesoDisciplina", d.peso_disciplina);
      if (d.curva_s) curvaS("chartCurvaS", d.curva_s);
      if (d.top_partidas) barraApilada("chartTopPartidas", d.top_partidas);
    })
    .catch((e) => console.error("No se pudieron cargar los graficos", e));

  function ctx(id) {
    const el = document.getElementById(id);
    return el ? el.getContext("2d") : null;
  }

  function gauge(id, valor) {
    const c = ctx(id);
    if (!c) return;
    const v = Math.max(0, Math.min(valor, 100));
    const color = v >= 80 ? PALETA.verde : v >= 40 ? PALETA.amarillo : PALETA.rojo;
    new Chart(c, {
      type: "doughnut",
      data: {
        labels: ["Ejecutado", "Restante"],
        datasets: [{ data: [v, 100 - v], backgroundColor: [color, "#E2E8F0"], borderWidth: 0 }],
      },
      options: {
        responsive: true,
        cutout: "72%",
        rotation: -90,
        circumference: 180,
        plugins: { legend: { display: false }, tooltip: { enabled: false } },
      },
    });
  }

  function barraAgrupada(id, data) {
    const c = ctx(id);
    if (!c) return;
    new Chart(c, {
      type: "bar",
      data: {
        labels: data.labels,
        datasets: [
          { label: "Presupuestado", data: data.presupuestado, backgroundColor: PALETA.grisConcreto, borderRadius: 4 },
          { label: "Ejecutado", data: data.ejecutado, backgroundColor: PALETA.naranja, borderRadius: 4 },
        ],
      },
      options: {
        indexAxis: "y",
        responsive: true,
        plugins: { legend: { position: "bottom" } },
        scales: { x: { beginAtZero: true } },
      },
    });
  }

  function dona(id, data) {
    const c = ctx(id);
    if (!c) return;
    new Chart(c, {
      type: "doughnut",
      data: { labels: data.labels, datasets: [{ data: data.data, backgroundColor: SERIE, borderColor: "#fff", borderWidth: 2 }] },
      options: {
        responsive: true,
        cutout: "55%",
        plugins: {
          legend: { position: "bottom" },
          tooltip: { callbacks: { label: (ctx) => `${ctx.label}: ${ctx.parsed}%` } },
        },
      },
    });
  }

  function curvaS(id, data) {
    const c = ctx(id);
    if (!c) return;
    new Chart(c, {
      type: "line",
      data: {
        labels: data.labels,
        datasets: [
          { label: "Planificado", data: data.planificado, borderColor: PALETA.grisConcreto,
            borderDash: [6, 4], fill: false, tension: 0.3, pointRadius: 2 },
          { label: "Real", data: data.real, borderColor: PALETA.naranja,
            backgroundColor: "rgba(194,65,12,.12)", fill: true, tension: 0.3,
            pointBackgroundColor: PALETA.naranja, pointRadius: 3 },
        ],
      },
      options: {
        responsive: true,
        plugins: { legend: { position: "bottom" } },
        scales: { y: { beginAtZero: true, ticks: { callback: (v) => "$" + v.toLocaleString() } } },
      },
    });
  }

  function barraApilada(id, data) {
    const c = ctx(id);
    if (!c) return;
    new Chart(c, {
      type: "bar",
      data: {
        labels: data.labels,
        datasets: [
          { label: "% Ejecutado", data: data.ejecutado_pct, backgroundColor: PALETA.verde, stack: "avance" },
          { label: "% Pendiente", data: data.pendiente_pct, backgroundColor: "#E2E8F0", stack: "avance" },
        ],
      },
      options: {
        indexAxis: "y",
        responsive: true,
        plugins: { legend: { position: "bottom" } },
        scales: { x: { stacked: true, max: 100 }, y: { stacked: true } },
      },
    });
  }
})();
