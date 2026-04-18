import streamlit as st
import pandas as pd
from datetime import date
import gspread
from google.oauth2.service_account import Credentials

st.set_page_config(page_title="Diário Prof. Marco", layout="centered")

st.markdown("""
<style>
.header {
    background: linear-gradient(90deg, #0d47a1, #1565c0);
    padding: 12px;
    border-radius: 10px;
    text-align: center;
    color: white;
    font-size: 22px;
    font-weight: bold;
    margin-bottom: 15px;
}

.aluno {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 6px 0;
    border-bottom: 1px solid #222;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="header">📋 DIÁRIO DE CLASSE</div>', unsafe_allow_html=True)

# 🔐 Conexão
def conectar():
    scope = ["https://www.googleapis.com/auth/spreadsheets"]

    creds = Credentials.from_service_account_info(
        st.secrets["connections"]["gsheets"],
        scopes=scope
    )

    client = gspread.authorize(creds)
    return client.open_by_key("1XfCFGVI9PUalRhiSBbQ95ZIjCz4IGhOT1m4_LeQGF1A")

try:
    planilha = conectar()

    # 📥 Ler dados
    aba_alunos = planilha.worksheet("Alunos")
    dados = aba_alunos.get_all_records()
    df_alunos = pd.DataFrame(dados)

    df_alunos = df_alunos.dropna(subset=["Nome"])

    turmas = sorted(df_alunos["Turma"].dropna().unique())
    turma_sel = st.selectbox("Turma:", turmas)
    data_sel = st.date_input("Data:", date.today())

    df_turma = df_alunos[df_alunos["Turma"] == turma_sel][["Nome"]]

    col1, col2 = st.columns(2)

    with col1:
        marcar_todos = st.button("✔️ Todos P")

    with col2:
        salvar = st.button("💾 Salvar")

    chamada_lista = []

    # 📋 Lista
    for i, row in df_turma.iterrows():

        if f"status_{i}" not in st.session_state:
            st.session_state[f"status_{i}"] = "P"

        col_nome, col_radio = st.columns([4,1])

        with col_nome:
            st.write(row["Nome"])

        with col_radio:
            status = st.radio("", ["P", "F"], horizontal=True, key=f"status_{i}")

        chamada_lista.append({
            "Nome": row["Nome"],
            "Status": status
        })

    if marcar_todos:
        for i in range(len(df_turma)):
            st.session_state[f"status_{i}"] = "P"
        st.rerun()

    chamada = pd.DataFrame(chamada_lista)

    if salvar:
        aba_hist = planilha.worksheet("Historico")

        for _, row in chamada.iterrows():
            aba_hist.append_row([
                data_sel.strftime('%d/%m/%Y'),
                turma_sel,
                row["Nome"],
                row["Status"]
            ])

        st.success("Chamada salva com sucesso!")
        st.balloons()

except Exception as e:
    st.error(f"Erro geral: {e}")