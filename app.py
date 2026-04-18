import streamlit as st
import pandas as pd
from datetime import date
from streamlit_gsheets import GSheetsConnection

# 🔥 TESTE DE VERSÃO (troque o número quando atualizar)
st.write("VERSÃO 4.0")

st.set_page_config(page_title="Diário Prof. Marco", layout="centered")

st.markdown("""
<style>
.header-title {
    color: white;
    text-align: center;
    font-size: 22px;
    font-weight: bold;
    background-color: #0d47a1;
    padding: 10px;
    border-radius: 8px;
    margin-bottom: 10px;
}
.stButton>button {
    background-color: #2e7d32 !important;
    color: white !important;
    font-weight: bold;
    width: 100%;
    height: 3em;
    border-radius: 8px;
}
.block-container {
    padding-top: 1rem;
}
</style>
""", unsafe_allow_html=True)

try:
    # 🔥 conexão
    conn = st.connection("gsheets", type=GSheetsConnection)

    # 🔥 ID fixo da planilha (resolve erro local)
    SPREADSHEET_ID = "1XfCFGVI9PUalRhiSBbQ95ZIjCz4IGhOT1m4_LeQGF1A"

    # 🔥 leitura correta
    df_alunos = conn.read(
        worksheet="Alunos",
        spreadsheet=SPREADSHEET_ID,
        ttl=0
    )

    df_alunos = df_alunos.dropna(subset=['Nome'])

    st.markdown("<div class='header-title'>📋 DIÁRIO DE CLASSE</div>", unsafe_allow_html=True)

    turmas = sorted(df_alunos['Turma'].dropna().unique())
    turma_sel = st.selectbox("Turma:", turmas)
    data_sel = st.date_input("Data:", date.today())

    df_turma = df_alunos[df_alunos['Turma'] == turma_sel][['Nome']].copy()

    st.markdown("### Chamada")

    # BOTÕES
    col1, col2, col3 = st.columns(3)

    with col1:
        marcar_todos = st.button("✔️ Todos P")

    with col2:
        salvar = st.button("💾 Salvar")

    with col3:
        resetar = st.button("🔄 Reset")

    chamada_lista = []

    # LISTA DE CHAMADA
    for i, row in df_turma.iterrows():

        if f"status_{i}" not in st.session_state:
            st.session_state[f"status_{i}"] = "P"

        c1, c2 = st.columns([3,1])

        with c1:
            st.write(row["Nome"])

        with c2:
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

    # MARCAR TODOS
    if marcar_todos:
        for i in range(len(df_turma)):
            st.session_state[f"status_{i}"] = "P"
        st.rerun()

    # RESETAR
    if resetar:
        for key in list(st.session_state.keys()):
            if "status_" in key:
                del st.session_state[key]
        st.cache_data.clear()
        st.rerun()

    chamada = pd.DataFrame(chamada_lista)

    # SALVAR
    if salvar:
        with st.spinner("Salvando..."):
            novos_dados = pd.DataFrame({
                "Data": [data_sel.strftime('%d/%m/%Y')] * len(chamada),
                "Turma": [str(turma_sel)] * len(chamada),
                "Nome": chamada['Nome'],
                "Status": chamada['Status']
            })

            try:
                historico = conn.read(
                    worksheet="Historico",
                    spreadsheet=SPREADSHEET_ID,
                    ttl=0
                )

                final = pd.concat([historico, novos_dados], ignore_index=True)

                conn.update(
                    worksheet="Historico",
                    data=final,
                    spreadsheet=SPREADSHEET_ID
                )

            except:
                conn.update(
                    worksheet="Historico",
                    data=novos_dados,
                    spreadsheet=SPREADSHEET_ID
                )

            st.success("Chamada salva com sucesso!")
            st.balloons()

except Exception as e:
    st.error(f"Erro de Conexão: {e}")

    if st.button("🔄 Reconectar"):
        st.cache_data.clear()
        st.rerun()