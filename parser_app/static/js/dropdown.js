window.addEventListener("DOMContentLoaded", () => {
    const dropdowns = document.querySelectorAll(".AsideDropdown");

    for (let dropdown of dropdowns) {
        const button = document.querySelector(
            dropdown.getAttribute("button-selector")
        );
        console.log(dropdowns);

        button.addEventListener("click", (event) => {
            if (dropdown.classList.contains("show-AsideDropdown")){
                button.classList.remove('active-AsideDropdown')
                dropdown.classList.remove("show-AsideDropdown")
                dropdown.style.maxHeight = '0'
            }else {
                button.classList.add('active-AsideDropdown')
                dropdown.classList.add("show-AsideDropdown")
                dropdown.style.maxHeight = dropdown.scrollHeight + 'px'
            }
        });
    }
});

document.addEventListener("DOMContentLoaded", function() {
    var buttonDealsTracker = document.getElementById("button-deals-tracker");
    var divDealsTracker = document.getElementById("div-deals-tracker");
    var currentURL = window.location.href;

    buttonDealsTracker.addEventListener("click", function() {
        if (divDealsTracker.style.display !== "none" && !currentURL.includes('add_deal') && !currentURL.includes('deals') && !currentURL.includes('calendar')) {
            divDealsTracker.style.display = "none";
        } else {
            divDealsTracker.style.display = "block";
        }
    });

    console.log(typeof currentURL)
    if (currentURL.includes('add_deal')) {
        divDealsTracker.style.display = "block";
        console.log("add_deal")
    } else if (currentURL.includes('deals')) {
        divDealsTracker.style.display = "block";
        console.log("deals")
    } else if (currentURL.includes('calendar')) {
        divDealsTracker.style.display = "block";
        console.log("calendar")
    } else {
        divDealsTracker.style.display = "none";
        console.log("none")
    }
});
