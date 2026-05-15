# FinTech Regression Automation Suite

An automated end-to-end regression testing framework designed to validate core trading systems, transaction lifecycles, and risk evaluation engines. Built completely with Python, this framework provides automated test coverage via a web-based dashboard and standalone test suites.

**Created by srinivasta**

🔗 **Live Demo:** [Access the Web Dashboard](https://fintech-regression-automation-xmg7yrkex5apmvc29knpxl.streamlit.app/)

## 🚀 Key Features

* **Trading Engine Validation:** End-to-end testing of real-time trading executions, orders, and algorithmic transactions (`trading_engine.py`).
* **Automated Regression Suite:** Scalable, isolated test cases powered by Python's test runner framework (`test_trading_suite.py`).
* **Web Dashboard:** An interactive Streamlit interface (`app.py`) to launch tests, track test runs, and view live pass/fail analytics.
* **CI/CD Integrated:** Production-ready automation pipelines built with GitHub Actions to trigger tests on every pull request or push event.

## 📂 Repository Structure

* `app.py`: Streamlit web application acting as the control center and dashboard for the regression tests.
* `trading_engine.py`: Core trading logic simulator managing order validation, pricing, or ledger calculations.
* `test_trading_suite.py`: Automated testing scripts targeting individual modules inside the trading engine.
* `requirements.txt`: Set of external third-party dependencies required to execute and run the suite.
* `.github/workflows/`: Pipeline integration configurations for ongoing continuous integration.

## 🛠️ Installation & Setup

Ensure you have **Python 3.8+** installed on your system.

1. **Clone the repository:**
   ```bash
   git clone https://github.com
   cd fintech-regression-automation
   ```

2. **Set up a virtual environment (Recommended):**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## 💻 How to Run

### Running the Web Control Dashboard Locally
Launch the visualization app to run tests from an interactive browser-based portal:
```bash
streamlit run app.py
```

### Running Tests from the Command Line
To run the standard python regression suite locally using the command-line interface:
```bash
pytest test_trading_suite.py
```
*(Or use `python -m unittest test_trading_suite.py` based on your testing framework implementation).*

## ⚙️ CI/CD Integration
Continuous automation is handled inside `.github/workflows/`. Every pull request or direct branch update evaluates code health against the regression suite automatically before merging into the `main` branch.

## 📄 License
This repository is licensed under the [MIT License](LICENSE).
