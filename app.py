from flask import Flask, render_template, request, redirect, url_for
import pandas as pd
import matplotlib.pyplot as plt
import os
from datetime import datetime

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        return redirect(request.url)
    if file:
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)
        return redirect(url_for('dashboard', filename=file.filename))

@app.route('/dashboard/<filename>')
def dashboard(filename):
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    df = pd.read_csv(filepath, parse_dates=['Date'])

    df['Revenue'] = df['Quantity'] * df['Price']
    df['Month'] = df['Date'].dt.to_period('M')

    total_sales = df['Revenue'].sum()
    top_product = df.groupby('Product')['Revenue'].sum().idxmax()
    monthly_sales = df.groupby('Month')['Revenue'].sum()

    plt.figure(figsize=(8,4))
    monthly_sales.plot(kind='bar', color='#00D8FF')
    plt.title('Monthly Revenue')
    plt.ylabel('Revenue')
    plt.tight_layout()
    chart_path = os.path.join('static', 'monthly_sales.png')
    plt.savefig(chart_path)
    plt.close()

    return render_template('dashboard.html',
                           total_sales=round(total_sales, 2),
                           top_product=top_product,
                           chart_path=chart_path)

if __name__ == '__main__':
    app.run(debug=True)
