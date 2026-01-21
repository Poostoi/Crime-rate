let currentDistrictId = null;
let currentYearId = null;
let currentCell = null;
let modal = null;

document.addEventListener('DOMContentLoaded', function() {
    modal = new bootstrap.Modal(document.getElementById('editModal'));

    document.querySelectorAll('.population-cell').forEach(cell => {
        cell.style.cursor = 'pointer';
        cell.addEventListener('click', function() {
            currentCell = this;
            currentDistrictId = this.dataset.districtId;
            currentYearId = this.dataset.yearId;

            const districtName = this.dataset.districtName;
            const yearValue = this.dataset.yearValue;
            const currentValue = this.querySelector('.population-value').textContent.trim();

            document.getElementById('modal-district').textContent = districtName;
            document.getElementById('modal-year').textContent = yearValue;
            document.getElementById('population-input').value = currentValue === '-' ? '' : currentValue;

            const deleteBtn = document.getElementById('delete-btn');
            deleteBtn.style.display = currentValue !== '-' ? 'inline-block' : 'none';

            modal.show();
        });
    });

    document.getElementById('save-btn').addEventListener('click', savePopulation);
    document.getElementById('delete-btn').addEventListener('click', deletePopulation);
});

function savePopulation() {
    const value = document.getElementById('population-input').value;

    if (!value) {
        alert('Введите значение населения');
        return;
    }

    fetch('/api/population/save', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            district_id: currentDistrictId,
            year_id: currentYearId,
            value: parseInt(value)
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            currentCell.querySelector('.population-value').textContent = value;
            currentCell.querySelector('.population-value').classList.remove('text-muted');
            modal.hide();
        } else {
            alert('Ошибка: ' + data.message);
        }
    })
    .catch(error => {
        alert('Ошибка при сохранении: ' + error);
    });
}

function deletePopulation() {
    if (!confirm('Удалить данные о населении?')) {
        return;
    }

    fetch('/api/population/delete', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            district_id: currentDistrictId,
            year_id: currentYearId
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            currentCell.querySelector('.population-value').textContent = '-';
            currentCell.querySelector('.population-value').classList.add('text-muted');
            modal.hide();
        } else {
            alert('Ошибка: ' + data.message);
        }
    })
    .catch(error => {
        alert('Ошибка при удалении: ' + error);
    });
}
