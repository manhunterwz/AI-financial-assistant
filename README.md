# AI Financial Assistant 🤖💰

An intelligent financial assistant powered by AI, designed to help users manage their personal finances, analyze spending patterns, detect anomalies, and chat with their financial data using generative AI.

## Features ✨

*   **Expense Tracking & Categorization:** Automatically categorize transactions using Machine Learning (Random Forest).
*   **Anomaly Detection:** Identify unusual spending patterns or potential fraud using Isolation Forests.
*   **Interactive Dashboard:** A rich, intuitive UI built with Streamlit for data visualization and management.
*   **Chat with Data:** Natural language querying of financial data powered by Google's Gemini LLM.
*   **RESTful API:** Robust backend powered by FastAPI for seamless data flow.

## Tech Stack 🛠️

| Component | Technology |
| :--- | :--- |
| **Backend** | FastAPI, Python 3.11+ |
| **Frontend** | Streamlit |
| **Database** | SQLite, SQLAlchemy |
| **Machine Learning** | Scikit-learn, Pandas, NumPy |
| **LLM Integration**| Google Generative AI (Gemini) |
| **Data Viz** | Plotly |

## Prerequisites 📝

Before you begin, ensure you have the following installed on your system:
*   [Python 3.11+](https://www.python.org/downloads/)
*   [Git](https://git-scm.com/)

## Quick Start 🚀 (Windows)

The easiest way to get started is by using the provided batch scripts.

1.  **Clone the repository:**
    ```bash
    git clone <repository_url>
    cd ai-financial-assistant
    ```

2.  **Run the Setup Script:**
    Double-click on `setup.bat` or run it from the command line:
    ```bash
    setup.bat
    ```
    This script will automatically check for Python, create a virtual environment (`.venv`), install all dependencies from `requirements.txt`, create necessary directories, and populate the database with initial seed data.

3.  **Start the Services:**
    Double-click on `run.bat` or run it from the command line:
    ```bash
    run.bat
    ```
    This script will launch both the FastAPI backend and the Streamlit frontend in separate terminal windows.

## Manual Setup ⚙️

If you prefer to set up the project manually or are on a non-Windows OS:

1.  Create a virtual environment:
    ```bash
    python -m venv .venv
    ```
2.  Activate the virtual environment:
    *   Windows: `.venv\Scripts\activate`
    *   macOS/Linux: `source .venv/bin/activate`
3.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
4.  Run the backend:
    ```bash
    uvicorn backend.main:app --reload
    ```
5.  Run the frontend (in a new terminal, with venv activated):
    ```bash
    streamlit run frontend/app.py
    ```

## Project Structure 📁

```text
.
├── backend/            # FastAPI application
├── frontend/           # Streamlit application
├── data/               # SQLite database & static files
├── models/             # Saved ML models (.pkl)
├── docs/               # Project documentation & reports
├── requirements.txt    # Project dependencies
├── setup.bat           # Windows setup script
├── run.bat             # Windows run script
└── README.md           # This file
```

## Screenshots 📸

*(Coming soon in Phase 7)*

## ML Models 🧠

*   **Categorizer Model:** A Random Forest classifier trained to categorize transactions based on description and amount.
*   **Anomaly Detector:** An Isolation Forest model used to flag unusually high or out-of-character spending.

## API Documentation 📚

Once the backend is running, interactive API documentation (Swagger UI) is available at:
`http://localhost:8000/docs`

## Authors ✍️

*   [Your Name/Team] - Final Year Project

## License 📄

This project is licensed under the MIT License.
