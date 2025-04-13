function say_hi(elt) {
    console.log("Welcome to", elt.innerText);
}

say_hi(document.querySelector("h1"));

function make_table_sortable(table) {
    if(!table.classList.contains("sortable")) return;

    const numberColumnHeader = table.querySelector("thead tr").lastElementChild;
    numberColumnHeader.addEventListener("click", () => {
        // Find sort direction
        let currClass = numberColumnHeader.className;
        let asc;
        if (currClass.includes("sort-asc")) {
            numberColumnHeader.className = currClass.replace("sort-asc", "sort-desc");
            asc = false;
        } else if (currClass.includes("sort-desc")){
            numberColumnHeader.className = currClass.replace("sort-desc", "sort-asc");
            asc = true;
        } else {
            numberColumnHeader.className += " sort-asc";
            asc = true;
        }

        const tbody = table.querySelector("tbody");
        const rows = Array.from(tbody.querySelectorAll("tr"));
        function cellValue(row) {
            const text = row.lastElementChild.textContent.trim().toLowerCase();
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

        rows.sort((a, b) => {
            const aVal = cellValue(a);
            const bVal = cellValue(b);
            return asc ? aVal - bVal : bVal - aVal;
        });

        for (const row of rows){
            tbody.appendChild(row);
        }
    })
}

make_table_sortable(document.querySelector("table.sortable"));