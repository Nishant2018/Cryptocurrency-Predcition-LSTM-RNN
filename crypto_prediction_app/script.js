// script.js

async function fetchHistoricalData(ticker) {
    const response = await fetch('/historical_data_1', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: new URLSearchParams({ ticker }),
    });
    return await response.json();
}

async function renderChart(ticker) {
    const data = await fetchHistoricalData(ticker);
    const ctx = document.getElementById('priceChart').getContext('2d');
    const chart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.dates,
            datasets: [{
                label: `${ticker} Closing Price`,
                data: data.closing_prices,
                borderColor: 'rgba(75, 192, 192, 1)',
                borderWidth: 1,
                fill: false,
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: false
                }
            }
        }
    });
}

// Call this function after prediction
document.getElementById('prediction-form').onsubmit = async (e) => {
    e.preventDefault(); // Prevent the default form submission

    const ticker = document.getElementById('ticker').value; // Get the input value

    // Make a POST request to the '/predict' route
    const response = await fetch('/predict', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: new URLSearchParams({ ticker }), // Send the ticker as form data
    });

    const resultDiv = document.getElementById('result');
    if (response.ok) {
        const data = await response.json(); // Parse the JSON response
        resultDiv.innerHTML = `Predicted Price: ${data.predicted_price}`; // Display the predicted price
        
        // Render the historical chart after prediction
        renderChart(ticker);
    } else {
        const errorData = await response.json(); // Parse error response
        resultDiv.innerHTML = `Error: ${errorData.error}`; // Display the error message
    }
};
