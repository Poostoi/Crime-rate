document.addEventListener('DOMContentLoaded', function() {
    const yearTabs = document.querySelectorAll('#yearsTabs button[data-year]');

    yearTabs.forEach(tab => {
        tab.addEventListener('shown.bs.tab', function(event) {
            const year = event.target.getAttribute('data-year');
            const tabPane = document.getElementById('year-' + year);

            if (tabPane.getAttribute('data-loaded') === 'false') {
                loadYearData(year, tabPane);
            }
        });
    });
});

function loadYearData(year, tabPane) {
    fetch('/api/year-data/' + year)
        .then(response => {
            if (!response.ok) {
                throw new Error('Ошибка загрузки данных');
            }
            return response.json();
        })
        .then(data => {
            renderYearData(data, tabPane);
            tabPane.setAttribute('data-loaded', 'true');
        })
        .catch(error => {
            tabPane.innerHTML = `
                <div class="alert alert-danger" role="alert">
                    <strong>Ошибка:</strong> Не удалось загрузить данные за ${year} год.
                    <br>${error.message}
                </div>
            `;
        });
}

function renderYearData(data, tabPane) {
    let html = `
        <h4 class="mb-3">Год: ${data.year}</h4>
        <div class="table-responsive">
            <table class="table table-striped table-hover table-bordered table-sm">
                <thead class="table-primary">
                    <tr>
                        <th class="text-center align-middle" style="min-width: 200px;">Признак</th>
    `;

    data.district_names.forEach(district => {
        html += `<th class="text-center align-middle">${district}</th>`;
    });

    html += `
                    </tr>
                </thead>
                <tbody>
    `;

    data.features.forEach(feature => {
        html += `<tr><td class="fw-bold">${feature.name}</td>`;
        feature.district_values.forEach(value => {
            if (value !== null) {
                html += `<td class="text-end">${value.toFixed(2)}</td>`;
            } else {
                html += `<td class="text-end"><span class="text-muted">—</span></td>`;
            }
        });
        html += `</tr>`;
    });

    html += `
                </tbody>
            </table>
        </div>
        <div class="mt-3 text-muted">
            <small>
                Признаков: <strong>${data.features.length}</strong> |
                Районов: <strong>${data.district_names.length}</strong>
            </small>
        </div>
    `;

    tabPane.innerHTML = html;
}
