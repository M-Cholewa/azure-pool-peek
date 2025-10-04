document.addEventListener('DOMContentLoaded', function() {
    // SWA automatycznie mapuje funkcję do ścieżki /api/{functionName}
    const apiEndpoint = '/api/PoolApiFunction'; 

    fetch(apiEndpoint)
        .then(response => {
            if (!response.ok) {
                throw new Error(`Błąd sieci: ${response.statusText}`);
            }
            return response.json();
        })
        .then(data => {
            // Przetwarzanie danych dla Chart.js
            const labels = data.map(item => item.time); // Czas (X)
            const counts = data.map(item => item.count); // Liczba osób (Y)

            const ctx = document.getElementById('poolChart').getContext('2d');
            
            new Chart(ctx, {
                type: 'line', // Wykres liniowy
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
                        y: {
                            beginAtZero: true,
                            title: {
                                display: true,
                                text: 'Liczba Osób'
                            }
                        },
                        x: {
                            title: {
                                display: true,
                                text: 'Godzina'
                            }
                        }
                    },
                    plugins: {
                        title: {
                            display: true,
                            text: 'Statystyki Obłożenia Basenu'
                        }
                    }
                }
            });
        })
        .catch(error => {
            console.error('Błąd pobierania danych:', error);
            document.querySelector('h1').textContent = 'Nie udało się załadować wykresu: ' + error.message;
        });
});