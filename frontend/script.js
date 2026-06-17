const API_URL = "http://127.0.0.1:8000";

function formatPrice(value) {
    return new Intl.NumberFormat("pt-BR", {
        style: "currency",
        currency: "INR",
        maximumFractionDigits: 0,
    }).format(value);
}

function fillSelect(id, options) {
    const select = document.getElementById(id);
    select.innerHTML = "";
    options.forEach((option) => {
        const el = document.createElement("option");
        el.value = option;
        el.textContent = option;
        select.appendChild(el);
    });
}

async function loadMetadata() {
    const response = await fetch(`${API_URL}/metadata`);
    const data = await response.json();

    fillSelect("brand", data.brands);
    fillSelect("fuel", data.fuels);
    fillSelect("seller_type", data.seller_types);
    fillSelect("transmission", data.transmissions);
    fillSelect("owner", data.owners);
}

async function predictPrice(event) {
    event.preventDefault();

    const resultEl = document.getElementById("result");
    const errorEl = document.getElementById("error");
    resultEl.classList.add("hidden");
    errorEl.classList.add("hidden");

    const payload = {
        year: Number(document.getElementById("year").value),
        km_driven: Number(document.getElementById("km").value),
        brand: document.getElementById("brand").value,
        fuel: document.getElementById("fuel").value,
        seller_type: document.getElementById("seller_type").value,
        transmission: document.getElementById("transmission").value,
        owner: document.getElementById("owner").value,
    };

    try {
        const response = await fetch(`${API_URL}/predict`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload),
        });

        if (!response.ok) {
            throw new Error("Erro ao realizar predição");
        }

        const data = await response.json();
        resultEl.innerHTML = `
            <strong>Preço estimado:</strong> ${formatPrice(data.predicted_price)}
            <br><small>ID da predição: #${data.id}</small>
        `;
        resultEl.classList.remove("hidden");
        loadHistory();
    } catch (err) {
        errorEl.textContent = err.message;
        errorEl.classList.remove("hidden");
    }
}

async function loadHistory() {
    const historyEl = document.getElementById("history");

    try {
        const response = await fetch(`${API_URL}/predictions?limit=10`);
        const rows = await response.json();

        if (rows.length === 0) {
            historyEl.innerHTML = "<p>Nenhuma predição registrada ainda.</p>";
            return;
        }

        historyEl.innerHTML = `
            <table>
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Ano</th>
                        <th>KM</th>
                        <th>Marca</th>
                        <th>Preço Previsto</th>
                    </tr>
                </thead>
                <tbody>
                    ${rows
                        .map(
                            (row) => `
                        <tr>
                            <td>#${row.id}</td>
                            <td>${row.year}</td>
                            <td>${row.km_driven.toLocaleString("pt-BR")}</td>
                            <td>${row.brand}</td>
                            <td>${formatPrice(row.predicted_price)}</td>
                        </tr>
                    `
                        )
                        .join("")}
                </tbody>
            </table>
        `;
    } catch {
        historyEl.innerHTML = "<p>Não foi possível carregar o histórico.</p>";
    }
}

document.getElementById("predictForm").addEventListener("submit", predictPrice);
document.getElementById("refreshHistory").addEventListener("click", loadHistory);

loadMetadata();
loadHistory();
