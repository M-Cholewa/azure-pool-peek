document.addEventListener('DOMContentLoaded', function() {
    const apiEndpoint = '/api/PoolApiFunction';
    const dateInput = document.getElementById('datePicker');
    const applyBtn = document.getElementById('applyDate');
    const todayBtn = document.getElementById('todayBtn');
    const pageTitle = document.getElementById('pageTitle');
    const ctx = document.getElementById('poolChart').getContext('2d');

    // ustaw domyślną datę na dziś
    const today = new Date();
    const yyyy = today.getFullYear();
    const mm = String(today.getMonth() + 1).padStart(2, '0');
    const dd = String(today.getDate()).padStart(2, '0');
    dateInput.value = `${yyyy}-${mm}-${dd}`;

    let originalData = [];
    let chart = null;

    function pickLabel(item) {
        return item.time || item.label || item.Timestamp || item.TimestampString || item.TimestampFormatted || '';
    }
    function pickCount(item) {
        return (item.count ?? item.Count ?? item.PeopleCount ?? item.value ?? 0);
    }

    function updateTitle(dateStr) {
        if (!dateStr) {
            pageTitle.textContent = 'Liczba Osób na Basenie (Dziś)';
            return;
        }
        pageTitle.textContent = `Liczba Osób na Basenie (${dateStr})`;
    }

    function createOrUpdateChart(labels, counts) {
        if (chart) {
            chart.data.labels = labels;
            chart.data.datasets[0].data = counts;
            chart.update();
            return;
        }

        chart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Liczba Osób',
                    data: counts,
                    borderColor: 'rgb(75, 192, 192)',
                    tension: 0.1,
                    fill: false,
                    pointRadius: 3
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: { beginAtZero: true, title: { display: true, text: 'Liczba Osób' } },
                    x: {
                        title: { display: true, text: 'Godzina' },
                        ticks: {
                            maxRotation: 45,
                            minRotation: 0,
                            align: 'center'
                        }
                    }
                },
                plugins: {
                    title: { display: true, text: 'Statystyki Obłożenia Basenu' },
                    tooltip: {
                        callbacks: {
                            // pokaż pełną datę/czas (jeśli jest) i wartość w tooltipie
                            title: (ctx) => {
                                if (!ctx || !ctx.length) return '';
                                const idx = ctx[0].dataIndex;
                                const item = originalData[idx] || {};
                                return (item.datetime || item.date || item.timestamp || pickLabel(item) || '');
                            },
                            label: (ctx) => {
                                const idx = ctx.dataIndex;
                                const item = originalData[idx] || {};
                                const count = pickCount(item);
                                return `Liczba osób: ${count}`;
                            }
                        }
                    }
                },
                interaction: {
                    mode: 'index',
                    intersect: false,
                    axis: 'x'
                },
                hover: {
                    mode: 'index',
                    intersect: false,
                    axis: 'x'
                }
            }
        });
    }

    async function fetchDataForDate(dateStr) {
        // dateStr expected in YYYY-MM-DD or empty
        const url = dateStr ? `${apiEndpoint}?date=${encodeURIComponent(dateStr)}` : apiEndpoint;
        try {
            const response = await fetch(url);
            if (!response.ok) {
                let bodyText;
                try { bodyText = await response.text(); } catch (_) { bodyText = '<brak body>'; }
                throw new Error(`HTTP ${response.status} ${response.statusText} - ${bodyText}`);
            }
            const data = await response.json();
            if (!Array.isArray(data)) throw new Error('Oczekiwano tablicy danych z API');

            originalData = data;
            const labels = data.map(pickLabel);
            const counts = data.map(pickCount);

            createOrUpdateChart(labels, counts);
            updateTitle(dateStr);
        } catch (err) {
            console.error('Błąd pobierania danych:', err);
            pageTitle.textContent = 'Nie udało się załadować wykresu: ' + (err.message || err);
        }
    }

    applyBtn.addEventListener('click', () => {
        const selected = dateInput.value;
        fetchDataForDate(selected);
    });

    todayBtn.addEventListener('click', () => {
        dateInput.value = `${yyyy}-${mm}-${dd}`;
        fetchDataForDate(dateInput.value);
    });

    // załaduj domyślnie (dziś)
    fetchDataForDate(dateInput.value);
});