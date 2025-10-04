document.addEventListener('DOMContentLoaded', function() {
    const apiEndpoint = '/api/PoolApiFunction';

    fetch(apiEndpoint)
        .then(async response => {
            if (!response.ok) {
                // próbujemy odczytać treść odpowiedzi (tekst/json)
                let bodyText;
                try {
                    bodyText = await response.text();
                } catch (e) {
                    bodyText = '<nie można odczytać body>';
                }
                const msg = `HTTP ${response.status} ${response.statusText} - ${bodyText}`;
                console.error('API response not ok:', msg, response);
                throw new Error(msg);
            }
            // bezpieczne parsowanie JSON — jeśli serwer zwraca pusty string, obsłużymy to
            try {
                return await response.json();
            } catch (e) {
                console.error('Błąd parsowania JSON z API:', e);
                throw new Error('Nieprawidłowy JSON z API');
            }
        })
        .then(data => {
            const labels = data.map(item => item.time);
            const counts = data.map(item => item.count);

            const ctx = document.getElementById('poolChart').getContext('2d');

            new Chart(ctx, {
                type: 'line',
                data: {
                    labels: labels,
                    datasets: [{
                        label: 'Liczba Osób',
                        data: counts,
                        borderColor: 'rgb(75, 192, 192)',
                        tension: 0.1,
                        fill: false
                    }]
                },
                options: {
                    responsive: true,
                    scales: {
                        y: { beginAtZero: true, title: { display: true, text: 'Liczba Osób' } },
                        x: { title: { display: true, text: 'Godzina' } }
                    },
                    plugins: { title: { display: true, text: 'Statystyki Obłożenia Basenu' } }
                }
            });
        })
        .catch(error => {
            console.error('Błąd pobierania danych:', error);
            document.querySelector('h1').textContent = 'Nie udało się załadować wykresu: ' + (error.message || error);
        });
});