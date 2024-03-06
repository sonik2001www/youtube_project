const dates_element = document.querySelector('.calendar-block .calendar-block__title');
const mth_element = document.querySelector('.calendar-block .calendar-block__title .h1');
const next_mth_element = document.querySelector('.calendar-block .calendar-block__title .pagination-calendar .pagination-calendar__arrows .pagination-calendar__arrow-next');
const prev_mth_element = document.querySelector('.calendar-block .calendar-block__title .pagination-calendar .pagination-calendar__arrows .pagination-calendar__arrow-prev');
const days_element = document.querySelector('.calendar-block .calendar-table-container .calendar .calendar-body');
const active_deals = document.querySelector('.calendar-container .active-deals .main-block .active-deals-tasks .active-deals-task .calendar-tasks')
const day_element = document.createElement('td');
const deals = JSON.parse(document.getElementById('deals').textContent);

const months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'];

let date = new Date();
let day = date.getDate();
let month = date.getMonth();
let year = date.getFullYear();

let selectedDate = date;
let selectedDay = day;
let selectedMonth = month;
let selectedYear = year;

mth_element.textContent = months[month] + ' ' + year;


populateDates();

const todayDeals = deals.filter((deal) => {
  const dealDate = new Date(deal.date);
  return (
    dealDate.getDate() === selectedDay &&
    dealDate.getMonth() === selectedMonth &&
    dealDate.getFullYear() === selectedYear
  );
});

if (todayDeals.length > 0) {
  todayDeals.forEach((deal) => {
    const taskItem = document.createElement('li');
    taskItem.classList.add('calendar-task');

    let dealName = deal.name;
    if (dealName.length > 40) {
      dealName = dealName.substring(0, 40) + '...';
    }

    taskItem.textContent = dealName;
    active_deals.appendChild(taskItem);
  });
}

//arrows  next/prev
next_mth_element.addEventListener('click', goToNextMonth);
prev_mth_element.addEventListener('click', goToPrevMonth);

day_element.addEventListener('click', function () {
  if (!day_element.classList.contains('calendar-body__item-task')) {
    const taskList = document.querySelector('.calendar-tasks');
    taskList.innerHTML = '';
  }

  selectedDate = new Date(year + '-' + (month + 1) + '-' + i);
  selectedDay = i;
  selectedMonth = month;
  selectedYear = year;

  populateDates();
});

//functions for arrows
function goToNextMonth(e) {
  month++;
  if (month > 11) {
    month = 0;
    year++;
  }
  mth_element.textContent = months[month] + ' ' + year;
  populateDates();
}

function goToPrevMonth(e) {
  month--;
  if (month < 0) {
    month = 11;
    year--;
  }
  mth_element.textContent = months[month] + ' ' + year;
  populateDates();
}


// populate dates
function populateDates(e) {
  days_element.innerHTML = '';
  let firstDayofMonth = new Date(year, month, 1).getDay();
  let lastDateofMonth = new Date(year, month + 1, 0).getDate();
  let lastDayofMonth = new Date(year, month, lastDateofMonth).getDay();
  let lastDateofLastMonth = new Date(year, month, 0).getDate();

  let row_element = document.createElement('tr');
  let dayCounter = 0;

  for (let i = firstDayofMonth; i > 0; i--) {
    const day_element = document.createElement('td');
    day_element.classList.add('calendar-body__item');
    day_element.classList.add('calendar-body__item-disabled');
    day_element.textContent = lastDateofLastMonth - i + 1;

    if (dayCounter % 7 === 0) {
      row_element = document.createElement('tr');
      days_element.appendChild(row_element);
    }

    row_element.appendChild(day_element);
    dayCounter++;
  }

  for (let i = 1; i <= lastDateofMonth; i++) {
    const day_element = document.createElement('td');
    day_element.classList.add('calendar-body__item');
    day_element.textContent = i;

    if (selectedDay === i && selectedYear === year && selectedMonth === month) {
      day_element.classList.add('calendar-body__item-active');
    }


    // shows deals in the day calendar
    const currentDate = new Date(year, month, i);
    const matchingDeals = deals.filter((deal) => {
      const dealDate = new Date(deal.date);
      return (
        dealDate.getDate() === currentDate.getDate() &&
        dealDate.getMonth() === currentDate.getMonth() &&
        dealDate.getFullYear() === currentDate.getFullYear()
      );
    });

    if (matchingDeals.length > 0) {
      day_element.classList.add('calendar-body__item-task');

      const taskList = document.createElement('ul');
      taskList.classList.add('calendar-body-tasks');

      matchingDeals.forEach((deal) => {
      const taskItem = document.createElement('li');
      taskItem.classList.add('calendar-body-task', 'calendar-task');

      let dealName = deal.name;
      if (dealName.length > 12) {
        dealName = dealName.substring(0, 12) + '...';
      }

      taskItem.textContent = dealName;
      taskList.appendChild(taskItem);
    });

      day_element.appendChild(taskList);

      day_element.addEventListener('click', function () {
        active_deals.innerHTML = '';

        matchingDeals.forEach((deal) => {
          const taskItem = document.createElement('li');
          taskItem.classList.add('calendar-task');

          let dealName = deal.name;
          if (dealName.length > 40) {
            dealName = dealName.substring(0, 40) + '...';
          }

          taskItem.textContent = dealName;
          active_deals.appendChild(taskItem);
        });
      });
    } else {
      day_element.addEventListener('click', function () {
        if (!day_element.classList.contains('calendar-body__item-task')) {
          const taskList = document.querySelector('.calendar-tasks');
          taskList.innerHTML = '';
        }

        selectedDate = new Date(year + '-' + (month + 1) + '-' + i);
        selectedDay = i;
        selectedMonth = month;
        selectedYear = year;

        populateDates();
      });
    }

    if (dayCounter % 7 === 0) {
      row_element = document.createElement('tr');
      days_element.appendChild(row_element);
    }

    row_element.appendChild(day_element);
    dayCounter++;

    day_element.addEventListener('click', function () {
      selectedDate = new Date(year + '-' + (month + 1) + '-' + i);
      selectedDay = i;
      selectedMonth = month;
      selectedYear = year;

      populateDates();
//      addDealFormDateField.value = formatDate(selectedDate);
    });
  }

  for (let i = lastDayofMonth; i < 6; i++) {
    const day_element = document.createElement('td');
    day_element.classList.add('calendar-body__item');
    day_element.classList.add('calendar-body__item-disabled');
    day_element.textContent = i - lastDayofMonth + 1;


    if (dayCounter % 7 === 0) {
      row_element = document.createElement('tr');
      days_element.appendChild(row_element);
    }

    row_element.appendChild(day_element);
    dayCounter++;
  }
}

//helper function
function formatDate(d) {
  let day = d.getDate();
  if (day < 10) {
    day = '0' + day;
  }

  let month = d.getMonth() + 1;
  if (month < 10) {
    month = '0' + month;
  }

  let year = d.getFullYear().toString().substr(-2);

  return day + '/' + month + '/' + year;
}