from __future__ import annotations


def get_app_css() -> str:
    """Retourneer de globale CSS voor de Streamlit-app."""
    return """
    <style>
    .stApp {
        background-color: #f5f6f7;
    }

    .main .block-container {
        max-width: 1320px;
        padding-top: 2rem;
        padding-bottom: 2rem;
    }

    .app-shell {
        background: white;
        border-radius: 24px;
        padding: 28px 28px 24px 28px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.06);
    }

    .app-title-row {
        display: flex;
        align-items: center;
        gap: 14px;
        margin-bottom: 16px;
        flex-wrap: wrap;
    }

    .app-title-icon {
        width: 38px;
        height: 38px;
        border-radius: 50%;
        background: #ff8a11;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-size: 20px;
        font-weight: 700;
        flex: 0 0 auto;
    }

    .app-brand-logo img {
        height: 42px;
        width: auto;
        display: block;
    }

    .app-title-text {
        font-size: 28px;
        font-weight: 700;
        color: #1f2430;
    }

    .stepbar {
        display: flex;
        gap: 10px;
        margin: 18px 0 24px 0;
    }

    .step {
        padding: 10px 18px;
        border-radius: 10px;
        font-weight: 600;
        font-size: 14px;
        background: #ececec;
        color: #777;
    }

    .step.active {
        background: #ff8a11;
        color: white;
    }

    .page-title {
        font-size: 28px;
        font-weight: 700;
        color: #20242d;
        margin-bottom: 8px;
    }

    .page-subtitle {
        font-size: 16px;
        color: #555;
        margin-bottom: 18px;
    }

    .card {
        background: white;
        border: 1px solid #e6e7e8;
        border-radius: 18px;
        padding: 18px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.03);
    }

    .card-title {
        font-size: 16px;
        font-weight: 800;
        color: #2c3038;
        margin-bottom: 14px;
        text-transform: uppercase;
    }

    .result-highlight {
        background: #fff3e7;
        border-radius: 14px;
        padding: 16px;
        margin-bottom: 16px;
    }

    .result-label {
        font-size: 15px;
        color: #445;
        margin-bottom: 6px;
    }

    .result-value {
        font-size: 22px;
        font-weight: 800;
        color: #c45f00;
    }

    .note-text {
        font-size: 13px;
        color: #666;
    }

    .stButton > button {
        background-color: #ff8a11 !important;
        color: white !important;
        border: 1px solid #ff8a11 !important;
        border-radius: 10px !important;
        font-weight: 700 !important;
    }

    .stButton > button:hover {
        background-color: #e97908 !important;
        border-color: #e97908 !important;
        color: white !important;
    }

    div[data-baseweb="select"] > div {
        border-radius: 10px !important;
    }
    </style>
    """