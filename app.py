import streamlit as st
import pandas as pd
from datetime import date
import gspread
from google.oauth2.service_account import Credentials

st.set_page_config(page_title="Diário Prof. Marco", layout="centered")

st.markdown("## 📋 DIÁRIO DE CLASSE")

# 🔐 Conexão com Google Sheets
def conectar():
    scope = ["https://www.googleapis.com/auth/spreadsheets"]

    creds = Credentials.from_service_account_info(
        st.secrets["connections"]["gsheets"],
        scopes=scope
    )

    client = gspread.authorize(creds)
    planilha = client.open_by_key("1XfCFGVI9PUalRhiSBbQ95ZIjCz4IGhOT1m4_LeQGF1A")

    return planilha

try:
    planilha = conectar()

    # 🔍 MOSTRAR NOMES DAS ABAS (TEMPORÁRIO PRA DEBUG)
    abas = planilha.worksheets()
    st.write("Abas encontradas:", [aba.title for aba in abas])

    st.stop()

except Exception as e:
    st.error(f"Erro geral: {e}")