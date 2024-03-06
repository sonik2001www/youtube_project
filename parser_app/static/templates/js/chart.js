// chart
const ctx = document.getElementById('myChart');


new Chart(ctx, {
  type: 'line',
  data: {
    labels: ['Red', 'Blue', 'Yellow', 'Green', 'Purple', 'Orange'],
    datasets: [{
      label: '# of Votes',
      data: [12, 19, 3, 5, 2, 3],
      borderWidth: 1
    }]
  },
  options: {
    responsive: true,
    plugins: {
      legend: {
        position: 'top',
      },
    }
  },
});

// chart toogle

const toogle_chart_btns = document.querySelectorAll('[data-toogle-chart]')

const activeToogleChartBtn = () => {
  toogle_chart_btns.forEach((btn) => {
    
    btn.addEventListener('click', () => {
      if (!btn.classList.contains('overview__chart-btn-isActive')){

        toogle_chart_btns.forEach(e => e.classList.remove('overview__chart-btn-isActive'))

        btn.classList.add('overview__chart-btn-isActive')
      }
    })
  })
}

if (toogle_chart_btns) {activeToogleChartBtn()}

// chart choose
const choose_chart_btns = document.querySelectorAll('[data-choose-chart]')

const activeChooseChartBtn = () => {
  choose_chart_btns.forEach((btn) => {
    
    btn.addEventListener('click', () => {
      if (!btn.classList.contains('overview-chart-info-btn-isActive')){
        
        choose_chart_btns.forEach(e => e.classList.remove('overview-chart-info-btn-isActive'))

        btn.classList.add('overview-chart-info-btn-isActive')
      }
    })
  })
}

if (choose_chart_btns) {activeChooseChartBtn()}