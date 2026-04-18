import streamlit as st
import pandas as pd
from datetime import date
from streamlit_gsheets import GSheetsConnection

st.set_page_config(page_title="Diário Prof. Marco", layout="centered")

st.markdown("## 📋 DIÁRIO DE CLASSE")

try:
    conn = st.connection("gsheets", type=GSheetsConnection)

    df_alunos = conn.read(worksheet="Alunos", ttl=0)
    df_alunos = df_alunos.dropna(subset=['Nome'])

    turmas = sorted(df_alunos['Turma'].dropna().unique())
    turma_sel = st.selectbox("Turma:", turmas)
    data_sel = st.date_input("Data:", date.today())

    df_turma = df_alunos[df_alunos['Turma'] == turma_sel][['Nome']]

    col1, col2 = st.columns(2)

    with col1:
        marcar_todos = st.button("✔️ Todos P")

    with col2:
        salvar = st.button("💾 Salvar")

    chamada_lista = []

    for i, row in df_turma.iterrows():

        if f"status_{i}" not in st.session_state:
            st.session_state[f"status_{i}"] = "P"

        c1, c2 = st.columns([3,1])

        with c1:
            st.write(row["Nome"])

        with c2:
            status = st.radio("", ["P","F"], horizontal=True, key=f"status_{i}")

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

        st.success("Chamada salva!")
        st.balloons()

except Exception as e:
    st.error(f"Erro: {e}")