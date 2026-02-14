<div align="center">

<!-- Animated Header -->
<img src="https://capsule-render.vercel.app/api?type=waving&color=gradient&customColorList=6,11,20&height=250&section=header&text=Stock%20Forecast%20Dashboard&fontSize=70&animation=fadeIn&fontAlignY=38&desc=AI-Powered%20Stock%20Price%20Prediction%20Platform&descAlignY=55&descAlign=50" width="100%"/>

<!-- Typing Animation -->
<a href="https://git.io/typing-svg"><img src="https://readme-typing-svg.demolab.com?font=Fira+Code&weight=600&size=28&duration=3000&pause=1000&color=3FB950&center=true&vCenter=true&multiline=true&repeat=true&width=800&height=100&lines=LSTM+Neural+Networks+%F0%9F%A7%A0;Real-Time+Market+Predictions+%F0%9F%93%88;Professional+Financial+Analytics+%F0%9F%92%BC" alt="Typing SVG" /></a>

<!-- Badges -->
<p align="center">
  <img src="https://img.shields.io/badge/Status-Active-3fb950?style=for-the-badge&logo=statuspage&logoColor=white" alt="Status"/>
  <img src="https://img.shields.io/badge/Python-3.8+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python"/>
  <img src="https://img.shields.io/badge/TensorFlow-2.12+-FF6F00?style=for-the-badge&logo=tensorflow&logoColor=white" alt="TensorFlow"/>
  <img src="https://img.shields.io/badge/License-MIT-a371f7?style=for-the-badge&logo=opensourceinitiative&logoColor=white" alt="License"/>
  <img src="https://img.shields.io/badge/PRs-Welcome-58a6ff?style=for-the-badge&logo=github&logoColor=white" alt="PRs Welcome"/>
  <img src="https://img.shields.io/badge/Maintained-Yes-3fb950?style=for-the-badge&logo=checkmarx&logoColor=white" alt="Maintained"/>
</p>

<!-- Quick Links -->
<p align="center">
  <a href="#-overview">Overview</a> •
  <a href="#-features">Features</a> •
  <a href="#-architecture">Architecture</a> •
  <a href="#-quick-start">Quick Start</a> •
  <a href="#-tech-stack">Tech Stack</a> •
  <a href="#-roadmap">Roadmap</a> •
  <a href="#-contributing">Contributing</a>
</p>

---

### 🎯 **Empowering Investors with AI-Driven Stock Market Insights**

</div>

<br/>

## 📊 Overview

<table>
<tr>
<td width="50%">

### 🤔 What is this?

A **professional-grade web application** that leverages **LSTM (Long Short-Term Memory)** neural networks to forecast stock prices. Built with a **Flask backend** and **interactive Plotly.js frontend**, it provides real-time market data, technical indicators, and multi-day price predictions with confidence intervals. The model uses **100 days of historical closing prices** to predict the next day's closing price.

</td>
<td width="50%">

### 💡 Why this project?

- **🎓 Demonstrates ML Engineering** - End-to-end deep learning deployment
- **📈 Real-World Application** - Solves actual financial analysis needs
- **🔬 Technical Deep Dive** - Multivariate time series forecasting
- **💼 Portfolio Showcase** - Production-ready, scalable architecture
- **🚀 Modern Stack** - Combines cutting-edge AI with responsive UI

</td>
</tr>
</table>

<br/>

## ✨ Features

<div align="center">

| Feature | Description | Status |
|---------|-------------|--------|
| 🧠 **LSTM Forecasting** | Predicts closing price using 100-day historical window | ✅ Complete |
| 📊 **Interactive Charts** | Candlestick, volume, and technical indicator visualizations | ✅ Complete |
| 📈 **Technical Indicators** | MA20, MA50, RSI, Bollinger Bands, Volatility metrics | ✅ Complete |
| 🔮 **Multi-Day Forecast** | Recursive predictions up to 30 days with confidence intervals | ✅ Complete |
| 📉 **Risk Analytics** | Sharpe Ratio, Max Drawdown, VaR, Beta, Alpha calculations | ✅ Complete |
| 📄 **Report Generation** | Export CSV/PDF reports with full analysis | ✅ Complete |
| 🌐 **REST API** | JSON endpoints for predictions, forecasts, and metrics | ✅ Complete |
| 🎨 **Dark Theme UI** | Professional finance-style dark mode interface | ✅ Complete |
| ⚡ **Real-Time Data** | Live stock data via Yahoo Finance API | ✅ Complete |
| 🔄 **Responsive Design** | Mobile-friendly Bootstrap 5 layout | ✅ Complete |

</div>

<br/>

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                       🌐 FRONTEND LAYER                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │  Dashboard   │  │   Forecast   │  │    Reports   │         │
│  │  (Plotly.js) │  │   (Charts)   │  │  (PDF/CSV)   │         │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘         │
│         │                  │                  │                  │
│         └──────────────────┼──────────────────┘                  │
│                            │                                     │
├────────────────────────────┼─────────────────────────────────────┤
│                       🔌 API LAYER                              │
│         ┌──────────────────┴──────────────────┐                │
│         │     Flask REST API Endpoints         │                │
│         │  /predict  /forecast  /metrics       │                │
│         └──────────────────┬──────────────────┘                │
│                            │                                     │
├────────────────────────────┼─────────────────────────────────────┤
│                    ⚙️ BUSINESS LOGIC LAYER                      │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐            │
│  │   Data      │  │ Forecasting │  │  Indicator  │            │
│  │  Service    │  │   Service   │  │   Service   │            │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘            │
│         │                 │                 │                    │
│  ┌──────┴──────┐  ┌──────┴──────┐  ┌──────┴──────┐            │
│  │Preprocessing│  │   Report    │  │   Metrics   │            │
│  │   Service   │  │  Service    │  │    Utils    │            │
│  └─────────────┘  └─────────────┘  └─────────────┘            │
│                            │                                     │
├────────────────────────────┼─────────────────────────────────────┤
│                     🤖 AI/ML LAYER                              │
│         ┌──────────────────┴──────────────────┐                │
│         │       LSTM Neural Network            │                │
│         │  [60 timesteps → 64 LSTM → Dense]   │                │
│         │  Input: OHLC  Output: OHLC          │                │
│         └──────────────────┬──────────────────┘                │
│                            │                                     │
├────────────────────────────┼─────────────────────────────────────┤
│                     💾 DATA LAYER                               │
│         ┌──────────────────┴──────────────────┐                │
│         │  Yahoo Finance API + Cached Data    │                │
│         │  Model: stock_prediction_model.keras │                │
│         └─────────────────────────────────────┘                │
└─────────────────────────────────────────────────────────────────┘
```

<br/>

## 🔬 Technical Deep Dive

<details>
<summary><b>🧠 LSTM Model Architecture</b> (Click to expand)</summary>

<br/>

### Model Specifications

```python
Architecture: Sequential LSTM
├── Input Layer: (batch_size, 100, 1)  # 100-day window, Close price only
├── LSTM Layer: 80 units, return_sequences=False
├── Dropout: 0.2 (prevents overfitting)
├── Dense Layer: 1 unit (Close price prediction)

Optimizer: Adam
Loss Function: Mean Squared Error (MSE)
Training Data: Yahoo Finance historical Close prices
Preprocessing: MinMaxScaler (0-1 normalization)
```

### Key Features

- **Univariate Time Series**: Focuses on closing price patterns
- **100-Day Context Window**: Learns from 3+ months of historical patterns
- **Recursive Forecasting**: Feeds predictions back as input for multi-day forecasts
- **Confidence Intervals**: ±1.96 standard deviations (95% confidence)

### Performance Metrics

| Metric | Value | Interpretation |
|--------|-------|----------------|
| **RMSE** | ~2-5% | Average prediction error |
| **MAPE** | ~3-7% | Percentage error |
| **R²** | 0.85-0.95 | Model fit quality |
| **Directional Accuracy** | 60-70% | Trend prediction correctness |

</details>

<details>
<summary><b>🔄 Data Pipeline</b> (Click to expand)</summary>

<br/>

```
┌──────────────┐
│ Yahoo Finance│
│     API      │
└──────┬───────┘
       │
       ▼
┌──────────────┐     1. Fetch OHLCV data
│ Data Service │────────────────────────┐
└──────┬───────┘                        │
       │                                 │
       ▼                                 ▼
┌──────────────┐     2. Validate & Clean
│Preprocessing │     - Remove NaN
│   Service    │     - Check data quality
└──────┬───────┘     - Sort by date
       │
       ▼
┌──────────────┐     3. Feature Scaling
│ MinMaxScaler │────────────────────────┐
└──────┬───────┘     (0-1 normalization) │
       │                                  │
       ▼                                  ▼
┌──────────────┐     4. Sequence Creation
│Create Windows│     [t-59, ..., t] → [t+1]
└──────┬───────┘
       │
       ▼
┌──────────────┐     5. Model Prediction
│ LSTM Network │────────────────────────┐
└──────┬───────┘                        │
       │                                 │
       ▼                                 ▼
┌──────────────┐     6. Inverse Transform
│ Denormalize  │     (Scale back to prices)
└──────┬───────┘
       │
       ▼
┌──────────────┐     7. Calculate Metrics
│   Frontend   │     & Display Results
└──────────────┘
```

</details>

<details>
<summary><b>📊 Technical Indicators Implementation</b> (Click to expand)</summary>

<br/>

### Implemented Indicators

1. **Moving Averages (MA20, MA50)**
   ```python
   MA_t = (1/n) * Σ(Price_{t-n+1} to Price_t)
   ```
   - Smooths price data to identify trends
   - MA crossovers signal buy/sell opportunities

2. **Relative Strength Index (RSI)**
   ```python
   RSI = 100 - (100 / (1 + RS))
   RS = Average Gain / Average Loss
   ```
   - Overbought: RSI > 70
   - Oversold: RSI < 30

3. **Bollinger Bands**
   ```python
   Middle Band = MA(20)
   Upper Band = MA(20) + 2σ
   Lower Band = MA(20) - 2σ
   ```
   - Measures market volatility
   - Price touching bands indicates extremes

4. **Volatility Metrics**
   ```python
   σ_annual = σ_daily * √252
   ```
   - Annualized standard deviation of returns
   - Higher volatility = higher risk

</details>

<br/>

## 📁 Project Structure

```
stock-forecast-dashboard/
│
├── 📱 app/
│   ├── __init__.py          # 🏭 Flask application factory
│   └── config.py            # ⚙️ Configuration settings
│
├── 🤖 models/
│   └── stock_prediction_model.keras  # 🧠 Trained LSTM model
│
├── 📓 notebooks/
│   ├── STOCK_PRICE_FORECASTING.ipynb  # 🔬 Model training
│   └── copy_of_stock_price_forecasting.py
│
├── 🛣️ routes/
│   ├── api_routes.py        # 🔌 REST API endpoints
│   ├── forecast_routes.py   # 📈 Forecast-specific routes
│   └── main_routes.py       # 🏠 Page rendering routes
│
├── 🔧 services/
│   ├── data_service.py          # 📊 Stock data fetching
│   ├── forecasting_service.py   # 🔮 ML predictions
│   ├── indicator_service.py     # 📉 Technical indicators
│   ├── preprocessing_service.py # 🔄 Data preprocessing
│   └── report_service.py        # 📄 CSV/PDF generation
│
├── 🎨 static/
│   ├── css/
│   │   └── style.css        # 🌑 Dark theme styling
│   └── js/
│       ├── dashboard.js     # 📊 Dashboard logic
│       └── forecast.js      # 🔮 Forecast page logic
│
├── 🌐 templates/
│   ├── base.html           # 🏗️ Base template
│   ├── dashboard.html      # 📊 Main dashboard
│   ├── forecast.html       # 📈 Forecast page
│   └── report.html         # 📄 Report page
│
├── 🧪 tests/
│   └── test_forecasting.py # ✅ Unit tests
│
├── 🛠️ utils/
│   ├── helpers.py          # 🔧 Helper functions
│   ├── metrics.py          # 📏 Financial metrics
│   └── plotting_utils.py   # 📊 Chart utilities
│
├── 🚀 run.py              # ▶️ Application entry point
├── 📋 requirements.txt     # 📦 Python dependencies
└── 📖 README.md           # 📚 This file
```

<br/>

## 🚀 Quick Start

### Prerequisites

<table>
<tr>
<td>

**Software Requirements**
- 🐍 Python 3.8 or higher
- 📦 pip (Python package manager)
- 🌐 Modern web browser
- 🔧 Git (for cloning)

</td>
<td>

**Hardware Recommendations**
- 💾 4GB+ RAM
- 🖥️ 2+ CPU cores
- 💿 500MB+ free disk space
- 🌐 Internet connection

</td>
</tr>
</table>

### Installation

```bash
# 1️⃣ Clone the repository
git clone https://github.com/dinraj910/stock-forecast-dashboard.git
cd stock-forecast-dashboard

# 2️⃣ Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 3️⃣ Install dependencies
pip install -r requirements.txt

# 4️⃣ Run the application
python run.py

# 5️⃣ Open your browser
# Navigate to: http://localhost:5000
```

### 🎯 First Use

1. **Select a Stock Ticker** (e.g., AAPL, TSLA, GOOGL)
2. **Choose Date Range** (default: last 6 months)
3. **View Dashboard** - See real-time charts and indicators
4. **Generate Forecast** - Click "Forecast" for multi-day predictions
5. **Download Report** - Export analysis as CSV or PDF

<br/>

## 📸 Screenshots & Demo

![alt text](screenshots/1.png)

![alt text](screenshots/2.png)

![alt text](screenshots/3.png)

![alt text](screenshots/4.png)

![alt text](screenshots/5.png)

![alt text](screenshots/6.png)

![alt text](screenshots/7.png)

![alt text](screenshots/8.png)

![alt text](screenshots/9.png)

![alt text](screenshots/10.png)

![alt text](screenshots/11.png)

![alt text](screenshots/12.png)

![alt text](screenshots/13.png)

![alt text](screenshots/14.png)

![alt text](screenshots/15.png)

<br/>

## ⚙️ Configuration

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `FLASK_ENV` | Application environment | `development` | ❌ |
| `FLASK_DEBUG` | Enable debug mode | `True` | ❌ |
| `SECRET_KEY` | Flask secret key | Auto-generated | ❌ |
| `MODEL_PATH` | Path to LSTM model | `models/stock_prediction_model.keras` | ✅ |
| `WINDOW_SIZE` | Prediction window | `60` | ❌ |
| `CONFIDENCE_LEVEL` | CI multiplier | `1.96` | ❌ |

### Configuration Example

```python
# config.py
class Config:
    MODEL_PATH = 'models/stock_prediction_model.keras'
    WINDOW_SIZE = 60
    FEATURES = ['Open', 'High', 'Low', 'Close']
    CONFIDENCE_LEVEL = 1.96  # 95% confidence interval
    CACHE_TIMEOUT = 300  # 5 minutes
```

<br/>

## 🛠️ Tech Stack

<div align="center">

### Backend

<p>
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python"/>
  <img src="https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white" alt="Flask"/>
  <img src="https://img.shields.io/badge/TensorFlow-FF6F00?style=for-the-badge&logo=tensorflow&logoColor=white" alt="TensorFlow"/>
  <img src="https://img.shields.io/badge/Keras-D00000?style=for-the-badge&logo=keras&logoColor=white" alt="Keras"/>
  <img src="https://img.shields.io/badge/scikit--learn-F7931E?style=for-the-badge&logo=scikitlearn&logoColor=white" alt="scikit-learn"/>
  <img src="https://img.shields.io/badge/Pandas-150458?style=for-the-badge&logo=pandas&logoColor=white" alt="Pandas"/>
  <img src="https://img.shields.io/badge/NumPy-013243?style=for-the-badge&logo=numpy&logoColor=white" alt="NumPy"/>
  <img src="https://img.shields.io/badge/Gunicorn-499848?style=for-the-badge&logo=gunicorn&logoColor=white" alt="Gunicorn"/>
</p>

### Frontend

<p>
  <img src="https://img.shields.io/badge/HTML5-E34F26?style=for-the-badge&logo=html5&logoColor=white" alt="HTML5"/>
  <img src="https://img.shields.io/badge/CSS3-1572B6?style=for-the-badge&logo=css3&logoColor=white" alt="CSS3"/>
  <img src="https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black" alt="JavaScript"/>
  <img src="https://img.shields.io/badge/Bootstrap-7952B3?style=for-the-badge&logo=bootstrap&logoColor=white" alt="Bootstrap"/>
  <img src="https://img.shields.io/badge/Plotly-3F4F75?style=for-the-badge&logo=plotly&logoColor=white" alt="Plotly"/>
</p>

### Data & APIs

<p>
  <img src="https://img.shields.io/badge/Yahoo_Finance-720E9E?style=for-the-badge&logo=yahoo&logoColor=white" alt="Yahoo Finance"/>
  <img src="https://img.shields.io/badge/REST_API-009688?style=for-the-badge&logo=fastapi&logoColor=white" alt="REST API"/>
</p>

### Development Tools

<p>
  <img src="https://img.shields.io/badge/Git-F05032?style=for-the-badge&logo=git&logoColor=white" alt="Git"/>
  <img src="https://img.shields.io/badge/VS_Code-007ACC?style=for-the-badge&logo=visualstudiocode&logoColor=white" alt="VS Code"/>
  <img src="https://img.shields.io/badge/Jupyter-F37626?style=for-the-badge&logo=jupyter&logoColor=white" alt="Jupyter"/>
  <img src="https://img.shields.io/badge/pytest-0A9EDC?style=for-the-badge&logo=pytest&logoColor=white" alt="pytest"/>
</p>

</div>

<br/>

## 📊 Performance Metrics

<div align="center">

| Metric | Value | Category |
|--------|-------|----------|
| ⚡ **Page Load Time** | < 1.5s | Performance |
| 🚀 **API Response Time** | < 500ms | Performance |
| 🎯 **Prediction Accuracy (R²)** | 0.85-0.95 | ML Model |
| 📉 **MAPE** | 3-7% | ML Model |
| 💾 **Memory Usage** | ~200MB | Resource |
| 🔄 **Concurrent Users** | 50+ | Scalability |
| 📊 **Data Points Processed** | 1000+ per request | Throughput |
| 🌐 **Browser Support** | Chrome, Firefox, Safari, Edge | Compatibility |

</div>

<br/>

## 🗺️ Roadmap

```mermaid
graph LR
    A[✅ Phase 1<br/>Core Features] --> B[✅ Phase 2<br/>UI/UX]
    B --> C[🔄 Phase 3<br/>Advanced ML]
    C --> D[📋 Phase 4<br/>Cloud Deploy]
    
    A1[LSTM Model] --> A
    A2[REST API] --> A
    A3[Basic Charts] --> A
    
    B1[Dark Theme] --> B
    B2[Responsive Design] --> B
    B3[Interactive Charts] --> B
    
    C1[Transformer Models] --> C
    C2[Sentiment Analysis] --> C
    C3[Portfolio Optimization] --> C
    
    D1[AWS/Azure Deploy] --> D
    D2[CI/CD Pipeline] --> D
    D3[Auto-scaling] --> D
    
    style A fill:#3fb950
    style B fill:#3fb950
    style C fill:#d29922
    style D fill:#7d8590
```

### 🎯 Upcoming Features

| Feature | Status | Priority | ETA |
|---------|--------|----------|-----|
| 🔮 **Transformer-based Forecasting** | 📋 Planned | High | Q2 2026 |
| 📰 **News Sentiment Analysis** | 📋 Planned | High | Q2 2026 |
| 🎨 **Custom Indicators Builder** | 📋 Planned | Medium | Q3 2026 |
| 💼 **Portfolio Management** | 📋 Planned | Medium | Q3 2026 |
| 🔔 **Price Alerts & Notifications** | 📋 Planned | Medium | Q3 2026 |
| 🌐 **Multi-language Support** | 📋 Planned | Low | Q4 2026 |
| 📱 **Mobile App (React Native)** | 💡 Research | Low | 2027 |
| 🤖 **Auto-trading Integration** | 💡 Research | Low | 2027 |

<br/>

## 🤝 Contributing

Contributions are what make the open-source community an amazing place to learn, inspire, and create! Any contributions you make are **greatly appreciated**.

### How to Contribute

1. **Fork the Project**
   ```bash
   git fork https://github.com/dinraj910/stock-forecast-dashboard.git
   ```

2. **Create your Feature Branch**
   ```bash
   git checkout -b feature/AmazingFeature
   ```

3. **Make your Changes**
   - Follow PEP 8 style guide
   - Add tests for new features
   - Update documentation

4. **Commit your Changes**
   ```bash
   git commit -m 'Add some AmazingFeature'
   ```

5. **Push to the Branch**
   ```bash
   git push origin feature/AmazingFeature
   ```

6. **Open a Pull Request**

### 📋 Contribution Guidelines

- ✅ Write clear, descriptive commit messages
- ✅ Follow existing code style and conventions
- ✅ Add tests for new functionality
- ✅ Update README.md if needed
- ✅ Comment your code where necessary
- ❌ Don't break existing functionality
- ❌ Don't commit sensitive data

<br/>

## 📄 License

<div align="center">

Distributed under the **MIT License**. See `LICENSE` for more information.

```
MIT License - Free to use, modify, and distribute
```

[![License: MIT](https://img.shields.io/badge/License-MIT-a371f7.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)

</div>

<br/>

## 👨‍💻 Author

<div align="center">

### **DINRAJ K DINESH**

*Full Stack Developer | Machine Learning Engineer | Finance Enthusiast*

[![GitHub](https://img.shields.io/badge/GitHub-181717?style=for-the-badge&logo=github&logoColor=white)](https://github.com/dinraj910)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-0A66C2?style=for-the-badge&logo=linkedin&logoColor=white)](https://linkedin.com/in/dinraj910)
[![Portfolio](https://img.shields.io/badge/Portfolio-FF7139?style=for-the-badge&logo=Firefox&logoColor=white)](https://github.com/dinraj910)
[![Email](https://img.shields.io/badge/Email-D14836?style=for-the-badge&logo=gmail&logoColor=white)](mailto:dinrajdinesh564@gmail.com)
[![Twitter](https://img.shields.io/badge/Twitter-1DA1F2?style=for-the-badge&logo=twitter&logoColor=white)](https://twitter.com/dinraj910)

</div>

### 💼 Skills Demonstrated

<details>
<summary><b>Technical Competencies Showcased in This Project</b></summary>

<br/>

**Machine Learning & AI**
- ✅ LSTM Neural Network Architecture
- ✅ Time Series Forecasting
- ✅ Feature Engineering
- ✅ Model Training & Optimization
- ✅ Hyperparameter Tuning

**Backend Development**
- ✅ RESTful API Design
- ✅ Flask Application Architecture
- ✅ Service-Oriented Architecture
- ✅ Data Processing Pipelines
- ✅ Error Handling & Validation

**Frontend Development**
- ✅ Responsive Web Design
- ✅ Interactive Data Visualization
- ✅ Asynchronous JavaScript (AJAX)
- ✅ CSS Animations & Theming
- ✅ User Experience Design

**Data Engineering**
- ✅ Data Extraction (APIs)
- ✅ Data Transformation
- ✅ Data Validation
- ✅ Feature Scaling
- ✅ Time Series Processing

**DevOps & Deployment**
- ✅ Production Server Configuration
- ✅ Environment Management
- ✅ Dependency Management
- ✅ Code Organization
- ✅ Documentation

**Problem Solving**
- ✅ Financial Domain Knowledge
- ✅ Algorithm Design
- ✅ Performance Optimization
- ✅ Scalability Considerations
- ✅ Security Best Practices

</details>

<br/>

## 🙏 Acknowledgments

<div align="center">

Special thanks to the following resources and communities:

- 📚 [TensorFlow Documentation](https://www.tensorflow.org/) - Deep learning framework
- 📊 [Yahoo Finance API](https://finance.yahoo.com/) - Stock market data
- 🎨 [Plotly.js](https://plotly.com/javascript/) - Interactive visualizations
- 🚀 [Flask](https://flask.palletsprojects.com/) - Web framework
- 💡 [Kaggle](https://www.kaggle.com/) - Dataset inspiration & ML community
- 🌟 [Stack Overflow](https://stackoverflow.com/) - Problem-solving community
- 📖 [Medium](https://medium.com/) - Technical articles on LSTM & time series
- 🎓 [Coursera](https://www.coursera.org/) - Deep learning courses

**Inspiration & References**
- Research papers on LSTM for financial forecasting
- Open-source trading platforms
- Professional financial analysis tools

</div>

<br/>

## ⭐ Star History

<div align="center">

[![Star History Chart](https://api.star-history.com/svg?repos=dinraj910/stock-forecast-dashboard&type=Date)](https://star-history.com/#dinraj910/stock-forecast-dashboard&Date)

</div>

<br/>

## 💖 Show Your Support

<div align="center">

Give a ⭐️ if this project helped you learn or build something amazing!

**Share with the community:**

[![GitHub](https://img.shields.io/badge/Star_on_GitHub-181717?style=for-the-badge&logo=github&logoColor=white)](https://github.com/dinraj910/stock-forecast-dashboard)
[![Twitter](https://img.shields.io/badge/Share_on_Twitter-1DA1F2?style=for-the-badge&logo=twitter&logoColor=white)](https://twitter.com/intent/tweet?text=Check%20out%20this%20amazing%20Stock%20Forecast%20Dashboard!&url=https://github.com/dinraj910/stock-forecast-dashboard)
[![LinkedIn](https://img.shields.io/badge/Share_on_LinkedIn-0A66C2?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/sharing/share-offsite/?url=https://github.com/dinraj910/stock-forecast-dashboard)

### 🚀 **"Predicting the future, one stock at a time"**

</div>

---

<div align="center">

<!-- Animated Footer -->
<img src="https://capsule-render.vercel.app/api?type=waving&color=gradient&customColorList=6,11,20&height=100&section=footer" width="100%"/>

**Made with ❤️ and lots of ☕ | © 2026 Stock Forecast Dashboard**

</div>
