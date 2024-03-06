//// discount field
//const discount_percent = document.querySelector('.add-deal__box discount .discount-percent');
//const discount_value = document.querySelector('.add-deal__box discount .discount-value');
//const discount_input = document.querySelector('#id_discount_changer');
//const discount_button = document.querySelector('.change-discount');
//
//discount_button.addEventListener('click', function() {
//  if (discount_percent.hidden) {
//    discount_percent.hidden = false;
//    discount_value.hidden = true;
//    discount_input.checked = !discount_input.checked;
//  } else {
//    discount_percent.hidden = true;
//    discount_value.hidden = false;
//    discount_input.checked = !discount_input.checked;
//  }
//});
//
//
//// tax field
//const tax_icon = document.querySelector('.tax-div i');
//const tax_input = document.querySelector('#id_tax_changer');
//const tax_button = document.querySelector('.change-tax');
//
//tax_button.addEventListener('click', function() {
//
//  if (tax_icon.textContent === '%') {
//    tax_input.checked = !tax_input.checked;
//    tax_icon.textContent = '$';
//  } else {
//    tax_input.checked = !tax_input.checked;
//    tax_icon.textContent = '%';
//  }
//});


//// formset script
//let itemForm = document.querySelectorAll(".header-table-invoice__list")
//let container = document.querySelector("#form-container")
//let addButton = document.querySelector("#add-form")
//let totalForms = document.querySelector("#id_form-TOTAL_FORMS")
//
//let formNum = itemForm.length-1
//addButton.addEventListener('click', addForm)
//
//function addForm(e){
//    e.preventDefault()
//
//    let newForm = itemForm[0].cloneNode(true)
//    let formRegex = RegExp(`form-(\\d){1}-`,'g')
//
//    formNum++
//    newForm.innerHTML = newForm.innerHTML.replace(formRegex, `form-${formNum}-`)
//    container.insertBefore(newForm, addButton)
//
//    totalForms.setAttribute('value', `${formNum+1}`)
//}


// hidden form
const hForm_btns = document.querySelectorAll('.body-table-hForm__btn')

if (hForm_btns.length){hForm_btns.forEach(e => initHFormBtn(e))}

function initHFormBtn (hFormBtn) {
    data_form = hFormBtn.getAttribute('data-hForm')
    const hForm = document.querySelector(data_form)

    if (hForm){
        hForm.classList.add('hForm')

        const hFormClose = document.createElement('span')
        hFormClose.classList.add('hForm-close')
        hForm.append(hFormClose)

        hFormClose.addEventListener("click", toggleForm);
        hFormBtn.addEventListener("click", toggleForm);

        function toggleForm () {
            hForm.classList.toggle('_hidden')
            hFormBtn.classList.toggle('_hidden')
            hForm.querySelector('.add-deal__input').value = 0

            // set total
            document.querySelector('.body-table-invoice-total-val').innerHTML = setSumTotal()
            // set balance due paid
            document.querySelector('.body-table-invoice-balance-due-val').innerHTML = setBalanceDue()
        }
    }
}

// currencyList
const currencyList = document.querySelectorAll('[data-CurrencyList] .dropdown__list-item')

if (currencyList.length){currencyList.forEach(e => initCurrency(e))}

function initCurrency(currency) {
    let activeCurrencyText, currencyItems, activeCurrency, currencyForSubmit

    function setActiveCurrency () {
        currencyItems = document.querySelectorAll('[data-Currency]')
        activeCurrency = document.querySelector('[data-CurrencyList] .dropdown__list-item_active')
        activeCurrencyText = activeCurrency.textContent

        // set current currency to input 
        currencyForSubmit = document.querySelector('.tools-invoic-dropdown .dropdown__input_hidden')
        currencyForSubmit.setAttribute('value', activeCurrencyText)

        currencyItems.forEach(e => e.innerHTML = activeCurrencyText)
    }
    setActiveCurrency()

    currency.addEventListener('click', setActiveCurrency)
}

// add list
const addListBtn = document.querySelector('.header-table-invoice__addList')

if (addListBtn){initTableList()}

function initTableList() {
    let currentValue = 0

    const tableListContainer = document.querySelector('.header-table-invoice__body')
    const tableList = document.querySelector('.header-table-invoice__list')

    // first set id and name
    addPersonalIdAndName(tableList)

    addListBtn.addEventListener('click', () => {
        const cloneTableList = tableList.cloneNode(true)
        cloneTableList.querySelectorAll('.add-deal__input').forEach(e => e.value = '')
        toZero(cloneTableList.querySelector('.header-table-invoice-amount-num'), 'data-amountVal')
        cloneTableList.querySelector('.header-table-invoice__input-quantity').value = 1
        cloneTableList.querySelector('.header-table-invoice__input-rate').value = 0
        tableListContainer.append(cloneTableList)

        // add personal name && id
        addPersonalIdAndName(cloneTableList)

        // add sum for amount
        setAllSumOnDocnument(cloneTableList)

        cloneTableList.querySelector('.add-deal__input').focus()

        document.querySelectorAll('.header-table-invoice__list').forEach(e => initCloseListBtn(e))
    })

    function initCloseListBtn(list){
        let closeListbtn = list.querySelector('.header-table-invoice__removeList')
        if (!closeListbtn){
            closeListbtn = document.createElement('button')
            closeListbtn.classList.add('header-table-invoice__removeList')
            list.append(closeListbtn)
        }
        if (closeListbtn){
            closeListbtn.addEventListener('click', () => {
                list.remove()

                // set new id and name
                updatePersonalIdAndName()

                // set subtotal
                document.querySelector('.body-table-invoice-subtotal-val').innerHTML = setSumSubtotal()
                // set total
                document.querySelector('.body-table-invoice-total-val').innerHTML = setSumTotal()
                // set balance due paid
                document.querySelector('.body-table-invoice-balance-due-val').innerHTML = setBalanceDue()


                if (document.querySelectorAll('.header-table-invoice__list').length <= 1){
                    document.querySelectorAll('.header-table-invoice__removeList').forEach(e => e.remove())
                }

            })
        }
    }

    // init elements Form
    function addPersonalIdAndName (list) {
      const descr = list.querySelector(`.header-table-invoice__input-descr`)
      const quantity = list.querySelector(`.header-table-invoice__input-quantity`)
      const rate = list.querySelector(`.header-table-invoice__input-rate`)
      
      let allForms = [
        {name: 'item_description', element: descr},
        {name: 'quantity', element: quantity},
        {name: 'rate', element: rate}
      ]

      allForms.forEach((form) => {
        form.element.setAttribute('id',`id_form-${currentValue}-${form.name}`);
        form.element.setAttribute('name',`form-${currentValue}-${form.name}`);
      })
      currentValue += 1
    }

    // set new current value
    function updatePersonalIdAndName() {
      currentValue = 0

      const allTableList = document.querySelectorAll('.header-table-invoice__list')
      allTableList.forEach(list => addPersonalIdAndName(list))
    }
}

// toggle prc
const prsBtns = document.querySelectorAll('.body-table-invoice__inpbtn')

if (prsBtns.length){prsBtns.forEach(e => initPrsBtn(e))}


// START CHANGED =========================================================>
function initPrsBtn(prsBtn) {
    const prsBtnBox = prsBtn.parentNode
    prsBtn.addEventListener('click', () => {
        prsBtnBox.classList.toggle('prs_active')
        // set prs or currency to hidden input
        setCurrencyOrProsent(prsBtnBox.querySelector('.prs-input'))
        // set total
        document.querySelector('.body-table-invoice-total-val').innerHTML = setSumTotal()
        // set balance due paid
        document.querySelector('.body-table-invoice-balance-due-val').innerHTML = setBalanceDue()
    })

    function setCurrencyOrProsent(el) {
      if (prsBtnBox.classList.contains('prs_active')){
        el.setAttribute('value', true)
      } else {
        el.setAttribute('value', false)
      }
    }
    setCurrencyOrProsent(prsBtnBox.querySelector('.prs-input'))
}
// END CHANGED =========================================================>


//////////calendar//////////
const calendars = document.querySelectorAll('.add-deal__input-calendar');

if (calendars.length){calendars.forEach(calendar => setCalendar(calendar))}
function setCalendar (calendar) {
  const mth_element = calendar.querySelector('.calendar-box-container .calendar-box .calendar-box__month .calendar-box-dropdown .dropdown__button');
  const next_mth_element = calendar.querySelector('.calendar-box-container .calendar-box .calendar-box__month .calendar-box__arrow-next');
  const prev_mth_element = calendar.querySelector('.calendar-box-container .calendar-box .calendar-box__month .calendar-box__arrow-prev');
  const days_element = calendar.querySelector('.calendar-box-container .calendar-box .calendar-box__dates');
  const dropdownList = calendar.querySelector('.calendar-box-dropdown__list');

  const addDealFormDateField = calendar.querySelector('.add-deal__input.add-deal__input-calendar-btn');

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
}

// open / close calendar
if (calendars.length) {
  initStateCalendar();
}

function initStateCalendar() {
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
//////////end calendar//////////

// sum amount 
document.querySelectorAll('.header-table-invoice__list').forEach(e => setAllSumOnDocnument(e))

function setAllSumOnDocnument (tablelist) {
    const total = document.querySelector('.body-table-invoice-total-val')
    const subtotal = document.querySelector('.body-table-invoice-subtotal-val')
    const quantity = tablelist.querySelector('.header-table-invoice__input-quantity')
    const rate = tablelist.querySelector('.header-table-invoice__input-rate')
    const amount = tablelist.querySelector('.header-table-invoice-amount-num')
    let amountVal = 0

    const discount = document.querySelector('.add-deal__box.discount').querySelector('.add-deal__input')
    const tax = document.querySelector('.add-deal__box.tax').querySelector('.add-deal__input')
    const shipping = document.querySelector('.add-deal__box.shipping').querySelector('.add-deal__input')
  
    const amount_paid = document.querySelector('#id_amount_paid')
    const balance_due = document.querySelector('.body-table-invoice-balance-due-val')

      
    discount.addEventListener('keyup', onKyeUpHform)
    tax.addEventListener('keyup', onKyeUpHform)
    shipping.addEventListener('keyup', onKyeUpHform)
    
    quantity.addEventListener('keyup', onKeyUpInput)
    rate.addEventListener('keyup', onKeyUpInput)

    amount_paid.addEventListener('keyup', onKeyUpAmountPaid)


    function onKeyUpInput () {
      let quantityVal = quantity.value
      let rateVal = rate.value

      if (!quantityVal || !rateVal || rateVal == 0) {
        toZero(amount, 'data-amountVal')
        subtotal.innerHTML = setSumSubtotal()
        total.innerHTML = setSumTotal()
        balance_due.innerHTML = setBalanceDue()
      } else {
        amountVal = parseFloat(quantityVal * rateVal).toFixed(2)
        amount.setAttribute('data-amountVal', amountVal)
        amount.innerHTML = amountVal
        subtotal.innerHTML = setSumSubtotal()
        total.innerHTML = setSumTotal()
        balance_due.innerHTML = setBalanceDue()
      }
    }

    function onKyeUpHform() {
      total.innerHTML = setSumTotal()
      balance_due.innerHTML = setBalanceDue()
    }

    function onKeyUpAmountPaid() {
      balance_due.innerHTML = setBalanceDue()
    }
}
function toZero(el, data) {
  el.innerHTML = '0,00'
  el.setAttribute(data, '0,00')
}
function checkValue(value) {
  if (!value || value == 0){
    return 0
  } else {
    return parseInt(value)
  }
}
function getProsent(prosent, prosentFrom) {
  res = prosentFrom / 100 * prosent
  return res
}

// START CHANGED =========================================================>

function setSumSubtotal () {
  let sumAllAmount = 0

  document.querySelectorAll('.header-table-invoice-amount-num').forEach((e) => {
    const currentAmount = e.getAttribute('data-amountVal')
    sumAllAmount += parseInt(currentAmount)
  })

  if (!sumAllAmount) {
    return sumAllAmount = '0,00'
  }
  return sumAllAmount.toFixed(2)
}

function setSumTotal(discountVal, taxVal, shipingVal) {
  const total = document.querySelector('.body-table-invoice-total-val')
  const discount = document.querySelector('.add-deal__box.discount')
  const tax = document.querySelector('.add-deal__box.tax')
  const shipping = document.querySelector('.add-deal__box.shipping')
  let totalVal

  let subtotalVal = setSumSubtotal()
  discountVal = checkValue(discount.querySelector('.add-deal__input').value)
  taxVal = checkValue(tax.querySelector('.add-deal__input').value)
  shipingVal = checkValue(shipping.querySelector('.add-deal__input').value)
  subtotalVal = checkValue(subtotalVal)

  // if procent
  if (discount.querySelector('.header-table-invoice__input.prs_active')){
    discountVal= getProsent(discountVal, subtotalVal)
  }
  if (tax.querySelector('.header-table-invoice__input.prs_active')){
    taxVal = getProsent(taxVal, subtotalVal)
  }

  if (!discountVal && !taxVal && !shipingVal && !subtotalVal){
    total.innerHTML = '0,00'
    return 0
  } else {
    totalVal = ((taxVal + shipingVal + subtotalVal) - discountVal ).toFixed(2) 
    if (totalVal <= 0){
      return totalVal = '0,00'
    }
    return totalVal
  }
}

// END CHANGED =========================================================>

function setBalanceDue() {
  const amount_paid = document.querySelector('#id_amount_paid')
  let amount_paidVal = amount_paid.value

  if (!amount_paidVal) {
    amount_paidVal = 0
  }
  if (!setSumTotal()) return '0,00'

  let balance_dueVal = setSumTotal() - parseInt(amount_paidVal) 

  if (balance_dueVal <= 0 || !balance_dueVal){
    return balance_dueVal = '0,00'
  }
  return balance_dueVal.toFixed(2)
}