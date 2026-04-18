import streamlit as st
import pandas as pd
from datetime import date
from streamlit_gsheets import GSheetsConnection

st.set_page_config(page_title="Diário Prof. Marco", layout="centered")

# 🎨 ESTILO MELHORADO
st.markdown("""
<style>
.header {
    background: linear-gradient(90deg, #0d47a1, #1565c0);
    padding: 12px;
    border-radius: 10px;
    text-align: center;
    color: white;
    font-size: 20px;
    font-weight: bold;
    margin-bottom: 15px;
}

.linha {
    padding: 6px 0;
    border-bottom: 1px solid #333;
    margin-bottom: 4px;
}

.stRadio > div {
    flex-direction: row;
    gap: 10px;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="header">📋 DIÁRIO DE CLASSE</div>', unsafe_allow_html=True)

try:
    conn = st.connection("gsheets", type=GSheetsConnection)

    df_alunos = conn.read(worksheet="Alunos", ttl=0)
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

    for i, row in df_turma.iterrows():

        if f"status_{i}" not in st.session_state:
            st.session_state[f"status_{i}"] = "P"

        st.markdown(f"<div class='linha'>{row['Nome']}</div>", unsafe_allow_html=True)

        status = st.radio(
            "",
            ["P", "F"],
            horizontal=True,
            key=f"status_{i}"
        )

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
        novos_dados = pd.DataFrame({
            "Data": [data_sel.strftime('%d/%m/%Y')] * len(chamada),
            "Turma": [str(turma_sel)] * len(chamada),
            "Nome": chamada['Nome'],
            "Status": chamada['Status']
        })

        try:
            hist = conn.read(worksheet="Historico", ttl=0)
            final = pd.concat([hist, novos_dados], ignore_index=True)
            conn.update(worksheet="Historico", data=final)
        except:
            conn.update(worksheet="Historico", data=novos_dados)

        st.success("Chamada salva com sucesso!")
        st.balloons()

except Exception as e:
    st.error(f"Erro de conexão: {e}")