const API_URL = "https://predictvalue-production.up.railway.app";

// Dicionário ÚNICO para traduzir os termos visuais das barras para o Português
const traducoes = {
    // Combustível (Fuel)
    "Petrol": "Gasolina",
    "Diesel": "Diesel",
    "CNG": "Gás GNV",
    "LPG": "Gás GLP",
    "Electric": "Elétrico",
    
    // Tipo de Vendedor (Seller Type)
    "Dealer": "Concessionária",
    "Individual": "Particular",
    "Trustmark Dealer": "Revendedor Certificado",
    
    // Transmissão (Transmission)
    "Automatic": "Automático",
    "Manual": "Manual",
    
    // Proprietário (Owner)
    "First Owner": "Único Dono",
    "Second Owner": "2º Dono",
    "Third Owner": "3º Dono",
    "Fourth & Above Owner": "4º Dono ou mais",
    "Test Drive Car": "Carro de Teste"
};

// Formata o preço final para a moeda padrão brasileira (R$)
function formatPrice(value) {
    // CONVERSÃO: Multiplica o valor em Rupias por 0.065 para converter para o Real brasileiro
    const valorEmReais = value * 0.065;

    return new Intl.NumberFormat("pt-BR", {
        style: "currency",
        currency: "BRL",
        maximumFractionDigits: 0, // Mantém sem centavos para o visual ficar mais limpo
    }).format(valorEmReais);
}

// Preenche as barras de seleção mantendo o valor original (inglês) por trás e o texto em português visível
function fillSelect(id, options) {
    const select = document.getElementById(id);
    if (!select) return; 
    
    select.innerHTML = "";
    options.forEach((option) => {
        const el = document.createElement("option");
        el.value = option; // Envia o termo original exigido pelo modelo do backend Python
        
        // Exibe o termo traduzido em PT-BR para o usuário brasileiro
        el.textContent = traducoes[option] || option; 
        
        select.appendChild(el);
    });
}

// Carrega os dados nas caixas de seleção assim que a página abre
async function loadMetadata() {
    try {
        const response = await fetch(`${API_URL}/metadata`);
        if (!response.ok) {
            throw new Error("Erro ao buscar metadados do servidor");
        }
        const data = await response.json();

        fillSelect("brand", data.brands || []);
        fillSelect("fuel", data.fuels || []);
        fillSelect("seller_type", data.seller_types || []);
        fillSelect("transmission", data.transmissions || []);
        fillSelect("owner", data.owners || []);
    } catch (err) {
        console.error("Erro ao carregar metadados:", err);
        const errorEl = document.getElementById("error");
        if (errorEl) {
            errorEl.textContent = "Não foi possível preencher as opções do formulário. Verifique o servidor.";
            errorEl.classList.remove("hidden");
        }
    }
}

// Coleta os dados do formulário e envia para a rota de predição do modelo
async function predictPrice(event) {
    event.preventDefault();

    const resultEl = document.getElementById("result");
    const errorEl = document.getElementById("error");
    
    if (resultEl) resultEl.classList.add("hidden");
    if (errorEl) errorEl.classList.add("hidden");

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
            throw new Error("Erro ao realizar predição no modelo");
        }

        const data = await response.json();
        if (resultEl) {
            resultEl.innerHTML = `
                <strong>Preço estimado:</strong> ${formatPrice(data.predicted_price)}
                <br><small>ID da predição: #${data.id}</small>
            `;
            resultEl.classList.remove("hidden");
        }
        loadHistory();
    } catch (err) {
        if (errorEl) {
            errorEl.textContent = err.message;
            errorEl.classList.remove("hidden");
        }
    }
}

// Carrega a tabela de histórico formatando os números para o padrão brasileiro (.toLocaleString)
async function loadHistory() {
    const historyEl = document.getElementById("history");
    if (!historyEl) return;

    try {
        const response = await fetch(`${API_URL}/predictions?limit=10`);
        if (!response.ok) {
            throw new Error();
        }
        const rows = await response.json();

        if (!rows || rows.length === 0) {
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
                            <td>${row.km_driven.toLocaleString("pt-BR")} km</td>
                            <td>${traducoes[row.brand] || row.brand}</td>
                            <td>${formatPrice(row.predicted_price)}</td>
                        </tr>
                    `
                        )
                        .join("")}
                </tbody>
            </table>
        `;
    } catch {
        historyEl.innerHTML = "<p>Não foi possível carregar o histórico de predições.</p>";
    }
}

// Inicialização segura dos eventos do DOM
const predictForm = document.getElementById("predictForm");
if (predictForm) {
    predictForm.addEventListener("submit", predictPrice);
}

const refreshHistory = document.getElementById("refreshHistory");
if (refreshHistory) {
    refreshHistory.addEventListener("click", loadHistory);
}

// Execução inicial
loadMetadata();
loadHistory();
// correção vercel