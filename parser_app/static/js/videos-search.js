window.addEventListener("load", (event) => {
    const showModalAction = (modal) => (event) => {
        if (modal.classList.contains("show-modal"))
            modal.classList.remove("show-modal");
        else modal.classList.add("show-modal");
    };

    const filterModal = document.querySelector(".search__filter > .modal");
    const filterbuttonsSelector = ".search__filter > div:not(:last-child)";
    for (let button of document.querySelectorAll(filterbuttonsSelector))
        button.onclick = showModalAction(filterModal);

    const addRemoveModal = document.querySelector(".remove__filter > .modal");
    const showRemove = document.querySelector(".show-add-remove");
    showRemove.onclick = showModalAction(addRemoveModal);

    document.querySelector("#remove-website").onkeydown = (event) => {
        if (event.key == "Enter") {
            document.querySelector(".add-remove").click();
            event.preventDefault();
        }
    };

    document.querySelector(".add-remove").onclick = async (event) => {
        const input = document.querySelector("#remove-website");
        if (input.value) {
            response = await fetch("/add_remove/?website=" + input.value);

            if (response.ok) {
                alert("Success");
                input.value = "";
            } else alert("Some error");
        }
    };

    for (let input of filterModal.querySelectorAll("input"))
        input.oninput = (event) => {
            if (moment(input.value, "YYYY-MM-DD", true).isValid())
                input.classList.remove("error-input");
            else input.classList.add("error-input");
        };

    document
        .querySelector(".search__icon")
        .addEventListener("click", (event) => {
            if (document.querySelectorAll(".error-input").length != 0) {
                alert("Incorrect date");
                filterModal.classList.add("show-modal");
                event.preventDefault();
            } else event.currentTarget.classList.add("not-clickable");
        });
});

// remove filter
const removeFilters = document.querySelectorAll('.remove-filter__menu')

if (removeFilters.length){initFilterRemoveFun()}

function initFilterRemoveFun(){
  removeFilters.forEach((el) => {
    const removeInput = el.querySelector('.remove-filter__input')
    const removeBtn = el.querySelector('.add-remove')

    removeInput.addEventListener('keyup', () => {
    console.log(removeInput.value)
      if (removeInput.value){
        removeBtn.classList.remove('add-remove-disabled')
      } else {
        removeBtn.classList.add('add-remove-disabled')
      }
    })
  })
}


// Отримати CSRF-токен зі сторінки
const csrfToken = document.querySelector("[name=csrfmiddlewaretoken]").value;

// Отримати всі кнопки "X"
const removeButtons = document.querySelectorAll("[id^='button-']");

removeButtons.forEach(button => {
    button.addEventListener("click", async () => {
        const removeId = button.id.split("-")[1]; // Отримати ID запису
        const response = await fetch(`/remove/${removeId}`, {
            method: "DELETE",
            headers: {
                "X-CSRFToken": csrfToken // Додати CSRF-токен у заголовок
            },
        });

        if (response.ok) {
            // Видалити запис зі списку відображення
            const listItem = document.getElementById(`remove-${removeId}`);
            listItem.remove();

            // Видалити кнопку "X" зі списку відображення
            const removeButton = document.getElementById(`button-${removeId}`);
            removeButton.remove();
        } else {
            alert("Some error");
        }
    });
});


// Отримати кнопку "Add" і контейнер списку
const addButton = document.querySelector(".add-remove");
const removeListContainer = document.getElementById("remove-list");

// Функція для додавання нового слова до списку
function addWordToRemoveList(word) {
    const listItem = document.createElement("div");
    listItem.classList.add("remove-list-div-inner");

    const removeP = document.createElement("p");
    removeP.classList.add("remove-list-p");
    removeP.id = `remove-${word}`;
    removeP.textContent = word;

    const removeButton = document.createElement("button");
    removeButton.classList.add("remove-list-button");
    removeButton.id = `remove-${word}`;
    removeButton.innerHTML = "&times;";
    removeButton.addEventListener("click", async () => {
        const removeId = removeButton.id.split("-")[1];
        const response = await fetch(`/remove/${removeId}`, {
            method: "DELETE",
            headers: {
                "X-CSRFToken": csrfToken
            },
        });

        if (response.ok) {
            listItem.remove();
            removeButton.remove();
        } else {
            alert("Some error");
        }
    });

    listItem.appendChild(removeP);
    listItem.appendChild(removeButton);
    removeListContainer.appendChild(listItem);
}

// Додати обробник події для кнопки "Add"
    addButton.addEventListener("click", async () => {
        const input = document.querySelector("#remove-website");
        const word = input.value.trim();

        const removeElements = document.querySelectorAll(".remove-list-p");

        const removes = Array.from(removeElements).map(element => element.textContent.trim());

        console.log(removes);

        if (word && !removes.includes(word)) {
            addWordToRemoveList(word);
        }
    });