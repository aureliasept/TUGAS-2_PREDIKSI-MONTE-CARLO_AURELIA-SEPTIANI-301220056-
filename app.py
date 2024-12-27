from flask import Flask, render_template, request
import pandas as pd
import numpy as np

app = Flask(__name__)

# Fungsi untuk membaca data CSV
def load_data():
    try:
        csv_path = 'jumlah_capaian_penanganan_sampah.csv'
        df = pd.read_csv(csv_path)
        return df
    except FileNotFoundError:
        print(f"File {csv_path} tidak ditemukan.")
        return pd.DataFrame()
    except Exception as e:
        print(f"Error membaca file CSV: {e}")
        return pd.DataFrame()

# Fungsi untuk simulasi Monte Carlo
def monte_carlo_prediction(df, year, num_simulations=1000):
    try:
        data = df['jumlah_sampah'].values
        mean = np.mean(data)
        std_dev = np.std(data)
        simulated_data = np.random.normal(mean, std_dev, num_simulations)
        
        prediction = simulated_data.mean()
        probabilities = {
            "naik": np.mean(simulated_data > mean) * 100,
            "turun": np.mean(simulated_data < mean) * 100,
            "stabil": np.mean((simulated_data >= mean - std_dev) & (simulated_data <= mean + std_dev)) * 100
        }
        percentiles = {
            "10%": np.percentile(simulated_data, 10),
            "25%": np.percentile(simulated_data, 25),
            "50%": np.percentile(simulated_data, 50),
            "75%": np.percentile(simulated_data, 75),
            "90%": np.percentile(simulated_data, 90)
        }
        return prediction, probabilities, percentiles
    except Exception as e:
        print(f"Error di monte_carlo_prediction: {e}")
        return 0, {}, {}

@app.route('/')
def index_page():
    try:
        df = load_data()
        if df.empty:
            return "<h1>Data CSV kosong atau tidak ditemukan.</h1>"
        table_html = df.to_html(classes='table table-striped', index=False)
        return render_template('index.html', table_html=table_html)
    except Exception as e:
        return f"Error di route /: {e}"

@app.route('/predict', methods=['POST'])
def predict():
    try:
        year = int(request.form['year'])
        df = load_data()
        if df.empty:
            return "<h1>Data CSV kosong atau tidak ditemukan.</h1>"

        prediction, probabilities, percentiles = monte_carlo_prediction(df, year)
        return render_template(
            'prediction.html', 
            year=year, 
            prediction=round(prediction, 2),
            probabilities=probabilities,
            percentiles=percentiles
        )
    except Exception as e:
        return f"Error di route /predict: {e}"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
