function getLoadElement() {
    const loadElement = document.createElement("span");
    loadElement.className = "lds-spinner";
    for (let i of Array(12).fill())
        loadElement.append(document.createElement("div"));

    return loadElement;
}

function load(obj, dataContainer) {
    return async (event) => {
        // adding load effect on fetching
        const buttonContainer = event.currentTarget;
        buttonContainer.classList.add("load");
        buttonContainer.children[0].innerText = "";
        buttonContainer.children[0].append(getLoadElement());

        console.log(dataContainer);
        const offset = dataContainer.children.length;
        let response = { status: -1 };
        try {
            response = await fetch(`/load/${obj}/limit-${15}-offset-${offset}/`);
        } catch {}

        if (response.status == 200)
            dataContainer.innerHTML += await response.text();
        else if (response.status == 404)
            buttonContainer.remove();

        if (response.status != 404) {
            // removing laod effect after fetching
            buttonContainer.classList.remove("load");
            buttonContainer.children[0].children[0].remove();
            buttonContainer.children[0].innerText = "FIND MORE";
        }
    };
}

window.addEventListener("load", (event) => {
    const showMoreButton = document.querySelector(".show__more-btn");

    if (window.location.pathname == "/channels/") {
        const dataContainer = document.querySelector(
            "table.styled-table-creator > tbody"
        );
        showMoreButton.addEventListener("click", load("channels", dataContainer));
    } else if (window.location.pathname == "/videos/") {
        const dataContainer = document.querySelector(
            "ul.search__websites.search__wrapper"
        );
        showMoreButton.addEventListener("click", load("videos", dataContainer));
    }
});
