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

    for (let input of filterModal.querySelectorAll("input"))
        input.oninput = (event) => {
            if (input.value != "" && (isNaN(input.value) || input.value < 0))
                input.classList.add("error-input");
            else input.classList.remove("error-input");
        };

    document
        .querySelector(".search__icon")
        .addEventListener("click", (event) => {
            if (document.querySelectorAll(".error-input").length != 0) {
                alert("Incorrect input");
                filterModal.classList.add("show-modal");
                event.preventDefault();
            } else {
                const lessThan = document.querySelector("#id_less_than");
                const moreThan = document.querySelector("#id_more_than");

                if (
                    lessThan.value.length != 0 &&
                    moreThan.value.length != 0 &&
                    lessThan.value < moreThan.value
                ) {
                    alert("'Less than' must be greater than 'more than'");
                    filterModal.classList.add("show-modal");
                    event.preventDefault();
                }
            }
        });
});
