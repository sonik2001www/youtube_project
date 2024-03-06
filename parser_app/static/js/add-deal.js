// requirea/unrequired fields
const viewsImpressionsCheckbox = document.getElementById('viewsImpressionsCheckbox');
const affiliateCheckbox = document.getElementById('affiliateCheckbox');
const viewsAmountField = document.getElementById('viewsAmountField');
const affiliateLinkField = document.getElementById('affiliateLinkField');
const commissionsField = document.getElementById('commissionsField');

viewsImpressionsCheckbox.addEventListener('change', function() {
//  viewsAmountField.style.display = this.checked ? 'block' : 'none';
  viewsAmountField.required = this.checked;
});

affiliateCheckbox.addEventListener('change', function() {
//  affiliateLinkField.style.display = this.checked ? 'block' : 'none';
//  commissionsField.style.display = this.checked ? 'block' : 'none';
  affiliateLinkField.required = this.checked;
  commissionsField.required = this.checked;
});

//calendar
const calendars = document.querySelectorAll('.add-deal__input-calendar');

const mth_element = document.querySelector('.add-deal__input-calendar .calendar-box-container .calendar-box .calendar-box__month .calendar-box-dropdown .dropdown__button');
const next_mth_element = document.querySelector('.add-deal__input-calendar .calendar-box-container .calendar-box .calendar-box__month .calendar-box__arrow-next');
const prev_mth_element = document.querySelector('.add-deal__input-calendar .calendar-box-container .calendar-box .calendar-box__month .calendar-box__arrow-prev');
const days_element = document.querySelector('.add-deal__input-calendar .calendar-box-container .calendar-box .calendar-box__dates');
const dropdownList = document.querySelector('.calendar-box-dropdown__list');

const addDealFormDateField = document.querySelector('.add-deal__input.add-deal__input-calendar-btn');

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

// set today date if form is empty else set date from form
const originalDateValue = addDealFormDateField.value;
if (originalDateValue) {
  const originalDate = new Date(originalDateValue);
  addDealFormDateField.value = formatDate(originalDate);
} else {
  addDealFormDateField.value = formatDate(date);
}

// open calendar
if (calendars.length) {
  initCalendar();
}

function initCalendar() {
  calendars.forEach((calendarWrapper) => {
    const calendarBtn = calendarWrapper.querySelector('.add-deal__input-calendar-btn');
    const calendar = calendarWrapper.querySelector('.calendar-box-container');

    calendarBtn.addEventListener("click", (e) => {
      calendarBtn.classList.toggle('add-deal__input-calendar-btn-open');
      calendar.classList.toggle('calendar-box-container-open');
    });
    hideOnClickOut(calendarBtn, calendar);
  });

  function hideOnClickOut(calendarBtn, calendar) {
    document.addEventListener("click", (e) => {
      if (!e.composedPath().includes(calendarBtn) && !e.composedPath().includes(calendar)) {
        calendarBtn.classList.remove('add-deal__input-calendar-btn-open');
        calendar.classList.remove('calendar-box-container-open');
      }
    });
  }
}

//arrows  next/prev
next_mth_element.addEventListener('click', goToNextMonth);
prev_mth_element.addEventListener('click', goToPrevMonth);

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

dropdownList.innerHTML = '';

months.forEach((dropdown_month, index) => {
  const listItem = document.createElement('li');
  listItem.classList.add('dropdown__list-item');
  listItem.setAttribute('data-value', dropdown_month);
  listItem.textContent = dropdown_month;
  dropdownList.appendChild(listItem);

  if (index === month) {
    listItem.classList.add('dropdown__list-item_active');
  }

  listItem.addEventListener('click', function () {
    month = index;
    selectedDate.setMonth(month);
    selectedYear = selectedDate.getFullYear();
    mth_element.textContent = dropdown_month + ' ' + selectedYear;
    populateDates();

    const activeListItem = dropdownList.querySelector('.dropdown__list-item_active');
    if (activeListItem) {
      activeListItem.classList.remove('dropdown__list-item_active');
    }

    listItem.classList.add('dropdown__list-item_active');
  });
});

//populate days
function populateDates(e) {
  days_element.innerHTML = '';
  let firstDayofMonth = new Date(year, month, 1).getDay();
  let lastDateofMonth = new Date(year, month + 1, 0).getDate();
  let lastDayofMonth = new Date(year, month, lastDateofMonth).getDay();
  let lastDateofLastMonth = new Date(year, month, 0).getDate();

  for (let i = firstDayofMonth; i > 0; i--) {
    const day_element = document.createElement('button');
    day_element.classList.add('day');
    day_element.classList.add('inactive');
    day_element.textContent = lastDateofLastMonth - i + 1;

    days_element.appendChild(day_element);
  }

  for (let i = 1; i <= lastDateofMonth; i++) {
    const day_element = document.createElement('button');
    day_element.classList.add('day');
    day_element.textContent = i;

    if (selectedDay === i && selectedYear === year && selectedMonth === month) {
      day_element.classList.add('calendar-box__today');
    }

    day_element.addEventListener('click', function () {
      selectedDate = new Date(year + '-' + (month + 1) + '-' + i);
      console.log(selectedDate);
      selectedDay = i;
      selectedMonth = month;
      selectedYear = year;

      populateDates();
      addDealFormDateField.value = formatDate(selectedDate);
    });

    days_element.appendChild(day_element);
  }

  for (let i = lastDayofMonth; i < 6; i++) {
    const day_element = document.createElement('button');
    day_element.classList.add('day');
    day_element.classList.add('inactive');
    day_element.textContent = i - lastDayofMonth + 1;

    days_element.appendChild(day_element);
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


$(document).ready(function() {
    $(".file_upload input").change(function() {
        var file_input = $(this);
        var file_name = file_input.val().replace(/C:\\fakepath\\/i, '');

        var file_upload = file_input.closest(".file_upload");
        var file_display = file_upload.find("div");

        var file_button = file_upload.find("button");
        file_button.text("Change"); // Зміна тексту кнопки на "Change"

        if (file_name) {
            file_display.text(file_name);
        } else {
            file_display.text("Файл не выбран");
        }
    });
});


