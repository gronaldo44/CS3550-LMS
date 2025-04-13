function say_hi(elt) {
    console.log("Welcome to", elt.innerText);
}

say_hi(document.querySelector("h1"));

function make_table_sortable(table) {
    if(!table.classList.contains("sortable")) {
        return;
    }

    const headers = table.querySelectorAll("thead th.sort-column")
    const tbody = table.querySelector("tbody");
    const rows = Array.from(tbody.querySelectorAll("tr"));

    headers.forEach((header, columnIndex) => {
        header.addEventListener("click", () => {
            // Find sort direction
            let currClass = header.className;
            let newState;
            if (currClass.includes("sort-asc")) {
                header.className = currClass.replace("sort-asc", "sort-desc");
                newState = "desc";
            } else if (currClass.includes("sort-desc")){
                header.className = currClass.replace("sort-desc", "").replace("  ", " ");
                newState = "default";
            } else {
                header.className += " sort-asc";
                newState = "asc";
            }

            // clear other headers
            headers.forEach(h => {
                if (h !== header){
                    h.className = h.className.replace("sort-asc", "").replace("sort-desc", "").trim();
                }
            });

            const currRows = Array.from(tbody.querySelectorAll("tr"));
            function cellValue(row) {
                const cell = row.children[header.cellIndex]
                
                const dataVal = cell.getAttribute("data-value");
                if (dataVal != null){
                    return parseFloat(dataVal)
                }

                const text = cell.textContent.trim().toLowerCase();
                if (text === "missing"){
                    return -3;
                } else if (text === "not due") {
                    return -2;
                } else if (text === "ungraded") {
                    return -1;
                } else {
                    const val = parseFloat(text);
                    return isNaN(val) ? 0 : val;
                }   
            }
            if (newState === "asc" || newState === "desc") {
                currRows.sort((a, b) => {
                    const aVal = cellValue(a);
                    const bVal = cellValue(b);
                    return newState === "asc" ? aVal - bVal : bVal - aVal;
                });
            } else {
                currRows.sort((a, b) => {
                    return parseInt(a.getAttribute("data-index")) - parseInt(b.getAttribute("data-index"));
                });
            }

            currRows.forEach(row => tbody.appendChild(row));
        });
    });
}
const sortableTable = document.querySelector("table.sortable");
if (sortableTable){
    make_table_sortable(sortableTable)
}

async function make_form_async(form) {
    const formData = new FormData(form);
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    const output = form.querySelector("output");

    try {
        const response = await fetch(form.action, {
            method: form.method,
            headers: {
                "X-CSRFToken": csrfToken
            },
            body: formData,
        });

        const data = await response.json();
        if (!response.ok) {
            throw new Error(data.error || "Something went wrong.");
        }

        // Display success message or data if submission is successful
        output.textContent = data.message;
    } catch (e) {
        // Show error message in case of failure
        output.textContent = `Error: ${e.message}`;
    }
}
const form = document.querySelector("#submit-assignment-form");
if (form){
    form.addEventListener("submit", (event) => {
        event.preventDefault();
        make_form_async(form);
    });
}
