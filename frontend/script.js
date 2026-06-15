async function predictPrice() {
    const year = document.getElementById("year").value;
    const km = document.getElementById("km").value;
    const fuel = document.getElementById("fuel").value;

    const response = await fetch("http://127.0.0.1:8000/predict", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            year: Number(year),
            km_driven: Number(km),
            fuel: fuel
        })
    });

    const data = await response.json();

    document.getElementById("result").innerText =
        "Preço estimado: R$ " + data.predicted_price.toFixed(2);
}