from flask import Flask, render_template, request, jsonify
from keras.models import load_model
import yfinance as yf
import numpy as np
from sklearn.preprocessing import MinMaxScaler
import os

# Initialize Flask app
app = Flask(__name__, static_folder='static')

# Path to saved models directory
model_dir = r'saved_models'  # Use just the directory name as it is within the current folder

# Load model once during initialization
models = {}

def load_crypto_model(ticker):
    model_path = os.path.join(model_dir, f'{ticker}_model.h5')
    return load_model(model_path)

# Function to load model and make predictions
def predict_crypto(ticker, steps=60):
    if ticker not in models:
        models[ticker] = load_crypto_model(ticker)

    model = models[ticker]

    # Download latest cryptocurrency data from Yahoo Finance
    crypto_data = yf.download(ticker, period='1y', interval='1d')

    if len(crypto_data) < steps:
        return None  # Not enough data to make a prediction

    # Prepare the data (Close price)
    closing_price = crypto_data['Close'].values.reshape(-1, 1)
    scaler = MinMaxScaler(feature_range=(0, 1))
    scaled_data = scaler.fit_transform(closing_price)

    # Prepare input data for prediction
    X_test = [scaled_data[-steps:, 0]]
    X_test = np.array(X_test).reshape(1, steps, 1)

    # Make prediction
    predicted_price_scaled = model.predict(X_test)
    predicted_price = scaler.inverse_transform(predicted_price_scaled)

    # Return the predicted price
    return predicted_price[0][0]

# Route for the main page
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/predict', methods=['POST'])
def predict():
    ticker = request.form.get('ticker')
    if not ticker:
        return jsonify({'error': 'Ticker is required.'}), 400

    # Updated input validation to allow alphabets and hyphens
    if not all(c.isalnum() or c == '-' for c in ticker):
        return jsonify({'error': 'Invalid ticker symbol. Only alphabets and hyphens are allowed.'}), 400

    try:
        predicted_price = predict_crypto(ticker)
        
        if predicted_price is None:
            return jsonify({'error': 'Not enough data to make a prediction.'}), 400

        predicted_price = float(predicted_price)  # Ensure it's a regular Python float
        return jsonify({'predicted_price': predicted_price})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/historical/<ticker>', methods=['GET'])
def historical_data(ticker):
    try:
        # Download historical cryptocurrency data
        crypto_data = yf.download(ticker, period='1y', interval='1d')

        # Prepare data for the chart
        dates = crypto_data.index.strftime('%Y-%m-%d').tolist()
        prices = crypto_data['Close'].tolist()

        return jsonify({'dates': dates, 'prices': prices})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    

if __name__ == '__main__':
    app.run(debug=True)
