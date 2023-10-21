const dashboardSlug = document.getElementById('dashboard-slug').textContent.trim();
/*
const user = document.getElementById('user').textContent.trim();
const submitBtn = document.getElementById('submit-btn');
const dataInput = document.getElementById('data-input');
*/
const dataBox = document.getElementById('data-box');

const socket = new WebSocket(`ws://${window.location.host}/ws/${dashboardSlug}/`);

// console.log(socket);

function updateInformation(value) {
    let infoElement = document.getElementById('information');
    infoElement.classList.add('fadeOutIn');

    setTimeout(() => {
        if (value === 'red') {
            infoElement.innerHTML = '<span class="badge text-bg-danger">' + value.toUpperCase() + '</span>';
        } else if (value === 'black') {
            infoElement.innerHTML = '<span class="badge text-bg-dark">' + value.toUpperCase() + '</span>';
        } else {
            infoElement.innerHTML = value;
        }
        infoElement.classList.remove('fadeOutIn');
    }, 500);  // La mitad de la duración de la animación
}

socket.onmessage = function (e) {
    const data = JSON.parse(e.data);
    if (data.information) {
        updateInformation(data.information);
    }
};


/*
submitBtn.addEventListener('click', () => {
    const dataValue = dataInput.value;
    socket.send(JSON.stringify({
        'message': dataValue,
        'sender': user,
    }));
})

const ctx = document.getElementById('myChart').getContext('2d');
let chart;

const fetchChartData = async () => {
    const response = await fetch(window.location.href + 'chart/');
    const data = await response.json();
    console.log(data);
    return data;
}

const drawChart = async () => {
    const data = await fetchChartData();
    const {chartData, chartLabels} = data;

    chart = new Chart(ctx, {
        type: 'pie',
        data: {
            labels: chartLabels,
            datasets: [{
                label: '% of contribution',
                data: chartData,
                borderWidth: 1
            }]
        },
        options: {
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    })
}

const updateChart = async () => {
    if (chart) {
        chart.destroy();
    }
    await drawChart();
}
drawChart();
*/