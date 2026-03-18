"""Centrale styling voor de Streamlit UI."""

from __future__ import annotations


def get_app_css() -> str:
    """Geef de centrale CSS voor de applicatie terug."""
    return """
    <style>
    .stApp { background-color: #f5f6f7; }
    .main .block-container { max-width: 1320px; padding-top: 2rem; padding-bottom: 2rem; }
    .app-shell { background: white; border-radius: 24px; padding: 28px 28px 24px 28px; box-shadow: 0 10px 30px rgba(0,0,0,0.06); }
    .app-title-row { display: flex; align-items: center; gap: 12px; margin-bottom: 16px; }
    .app-title-icon { width: 34px; height: 34px; border-radius: 50%; background: #4d935f; display: inline-flex; align-items: center; justify-content: center; color: white; font-size: 18px; font-weight: 700; }
    .app-title-text { font-size: 28px; font-weight: 700; color: #1f2430; }
    .stepbar { display: flex; gap: 10px; margin: 18px 0 24px 0; }
    .step { padding: 10px 18px; border-radius: 10px; font-weight: 600; font-size: 14px; background: #ececec; color: #777; }
    .step.active { background: #4d935f; color: white; }
    .page-title { font-size: 28px; font-weight: 700; color: #20242d; margin-bottom: 8px; }
    .page-subtitle { font-size: 16px; color: #555; margin-bottom: 18px; }
    .card { background: white; border: 1px solid #e6e7e8; border-radius: 18px; padding: 18px; box-shadow: 0 4px 10px rgba(0,0,0,0.03); }
    .card-title { font-size: 16px; font-weight: 800; color: #2c3038; margin-bottom: 14px; text-transform: uppercase; }
    .visual-tab-row { display: flex; gap: 8px; margin-bottom: 12px; }
    .visual-tab { padding: 10px 18px; border-radius: 10px; font-weight: 700; background: #f1f3f4; color: #5d6168; }
    .visual-tab.active { background: #4d935f; color: white; }
    .result-highlight { background: #e7f1e8; border-radius: 14px; padding: 16px; margin-bottom: 16px; }
    .result-label { font-size: 15px; color: #445; margin-bottom: 6px; }
    .result-value { font-size: 22px; font-weight: 800; color: #215d37; }
    .note-text { font-size: 13px; color: #666; }
    </style>
    """