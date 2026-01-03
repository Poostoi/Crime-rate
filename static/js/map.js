// Константы
const CONFIG = {
    DEFAULT_YEAR: 2015,
    MAP_PADDING: [20, 20],
    LABEL_SIZE: 12
};

const COLORS = {
    HIGH: '#FF0000',      // >= 4
    ELEVATED: '#FFA500',  // >= 3
    MEDIUM: '#FFFF00',    // >= 2.5
    LOW: '#008000'        // < 2.5
};

const DISTRICT_NAMES = {
    1: 'Слободзейский',
    2: 'Тираспольский',
    3: 'Бендерский',
    4: 'Григориопольский',
    5: 'Дубоссарский',
    6: 'Рыбницкий',
    7: 'Каменский'
};

// Состояние
let crimeData = {};
let geoJsonLayer;
let markers = [];

// Инициализация карты
const map = L.map('map', { attributionControl: false });
L.control.attribution({ prefix: 'Карта преступности ПМР' }).addTo(map);
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© OpenStreetMap'
}).addTo(map);

// Утилиты
function getCrimeValue(year, regionId) {
    return crimeData[year]?.[regionId] || 0;
}

function getColor(value) {
    if (value >= 4) return COLORS.HIGH;
    if (value >= 3) return COLORS.ELEVATED;
    if (value >= 2.5) return COLORS.MEDIUM;
    return COLORS.LOW;
}

function getColorClass(value) {
    if (value >= 4) return 'color-high';
    if (value >= 3) return 'color-elevated';
    if (value >= 2.5) return 'color-medium';
    return 'color-low';
}

function createRegionStyle(year, feature) {
    const regionId = feature?.properties?.id;
    return {
        fillColor: regionId ? getColor(getCrimeValue(year, regionId)) : '#CCCCCC',
        weight: 2,
        opacity: 0.8,
        color: '#333',
        fillOpacity: 0.35
    };
}

function createRegionLabel(layer, feature) {
    const name = feature?.properties?.name || '';
    const marker = L.marker(layer.getBounds().getCenter(), {
        icon: L.divIcon({
            className: 'region-label',
            html: `<div class="label-text">${name}</div>`,
            iconSize: null
        })
    });
    markers.push(marker);
    return marker;
}

// Загрузка данных
function loadGeoJSON() {
    return fetch('/static/map.geojson').then(r => r.json());
}

function loadCrimeData() {
    return fetch('/api/crime-data').then(r => r.json());
}

// Инициализация слоя районов
function initGeoJSONLayer(data, year) {
    geoJsonLayer = L.geoJSON(data, {
        style: feature => createRegionStyle(year, feature),
        onEachFeature: (feature, layer) => {
            if (!feature?.properties?.name) return;

            const value = getCrimeValue(year, feature.properties.id);
            layer.bindPopup(`<b>${feature.properties.name}</b><br>Показатель: ${value}`);
            createRegionLabel(layer, feature).addTo(map);
        }
    }).addTo(map);

    map.fitBounds(geoJsonLayer.getBounds(), { padding: CONFIG.MAP_PADDING });
}

// Обновление карты
function updateMap(year) {
    if (!geoJsonLayer) return;

    geoJsonLayer.eachLayer(layer => {
        const feature = layer.feature;
        if (!feature?.properties?.id) return;

        const regionId = feature.properties.id;
        const value = getCrimeValue(year, regionId);
        const name = feature.properties.name || 'Неизвестно';

        layer.setStyle({ fillColor: getColor(value) });
        layer.setPopupContent(`<b>${name}</b><br>Показатель: ${value}`);
    });

    updateDistrictsList(year);
}

// Обновление списка районов
function updateDistrictsList(year) {
    const container = document.getElementById('districtsList');
    if (!container) return;

    const yearData = crimeData[year];
    if (!yearData) {
        container.innerHTML = '<div class="text-muted">Нет данных</div>';
        return;
    }

    const districts = Object.entries(yearData)
        .map(([id, value]) => ({
            name: DISTRICT_NAMES[id] || 'Неизвестно',
            value: value
        }))
        .sort((a, b) => b.value - a.value);

    container.innerHTML = districts.map(d => `
        <div class="district-item p-2 mb-2 bg-light rounded">
            <div class="district-name">${d.name}</div>
            <div class="district-value ${getColorClass(d.value)}">
                ${d.value.toFixed(2)}
            </div>
        </div>
    `).join('');
}

// Пересчет уровня преступности
function calculateCrimeLevel() {
    const btn = document.getElementById('calculateBtn');
    const btnText = document.getElementById('calculateBtnText');
    const spinner = document.getElementById('calculateSpinner');

    btn.disabled = true;
    btnText.textContent = 'Расчет...';
    spinner.classList.remove('hidden');

    fetch('/api/calculate-crime-level', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
    })
    .then(r => r.json())
    .then(data => {
        if (data.success) {
            return loadCrimeData().then(newData => {
                crimeData = newData;
                const year = parseInt(document.getElementById('yearValue').textContent);
                updateMap(year);
                alert(data.message);
            });
        }
        throw new Error(data.message);
    })
    .catch(error => alert('Ошибка: ' + error))
    .finally(() => {
        btn.disabled = false;
        btnText.textContent = 'Пересчитать уровень преступности';
        spinner.classList.add('hidden');
    });
}

// Слушатель слайдера года
document.getElementById('yearSlider').addEventListener('input', e => {
    const year = parseInt(e.target.value);
    document.getElementById('yearValue').textContent = year;
    updateMap(year);
});

// Запуск приложения
loadCrimeData()
    .then(data => {
        crimeData = data;
        return loadGeoJSON();
    })
    .then(geoData => {
        initGeoJSONLayer(geoData, CONFIG.DEFAULT_YEAR);
        updateDistrictsList(CONFIG.DEFAULT_YEAR);
    });
