import streamlit as st
import pandas as pd
from datetime import date
from streamlit_gsheets import GSheetsConnection

# Configuração da página
st.set_page_config(page_title="Diário Prof. Marco", layout="centered")

st.markdown("""
    <style>
    .header-title { color: white; text-align: center; font-size: 22px; font-weight: bold; background-color: #0d47a1; padding: 10px; border-radius: 8px; }
    .stButton>button { background-color: #2e7d32 !important; color: white !important; font-weight: bold; width: 100%; height: 3.5em; border-radius: 10px; }
    header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    
    df_alunos = conn.read(worksheet="Alunos", ttl=0)
    df_alunos = df_alunos.dropna(subset=['Nome'])
    
    st.markdown("<div class='header-title'>📝 DIÁRIO DE CLASSE</div>", unsafe_allow_html=True)
    
    turmas = sorted(df_alunos['Turma'].dropna().unique())
    turma_sel = st.selectbox("Selecione a Turma:", turmas)
    data_sel = st.date_input("Data da Aula:", date.today())
    
    df_turma = df_alunos[df_alunos['Turma'] == turma_sel][['Nome']].copy()

    st.markdown("### Chamada")

    # BOTÕES LADO A LADO
    col_btn1, col_btn2 = st.columns(2)

    with col_btn1:
        marcar_todos = st.button("✔️ Marcar todos como P")

    with col_btn2:
        salvar = st.button("💾 Salvar na Nuvem")

    # LISTA DE CHAMADA
    chamada_lista = []

    for i, row in df_turma.iterrows():
        col1, col2 = st.columns([4, 1])
        
        with col1:
            st.write(row["Nome"])
        
        with col2:
            # valor padrão = P
            if f"status_{i}" not in st.session_state:
                st.session_state[f"status_{i}"] = "P"

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

    # AÇÃO: MARCAR TODOS
    if marcar_todos:
        for i in range(len(df_turma)):
            st.session_state[f"status_{i}"] = "P"
        st.rerun()

    chamada = pd.DataFrame(chamada_lista)

    # AÇÃO: SALVAR
    if salvar:
        with st.spinner("Gravando dados..."):
            novos_dados = pd.DataFrame({
                "Data": [data_sel.strftime('%d/%m/%Y')] * len(chamada),
                "Turma": [str(turma_sel)] * len(chamada),
                "Nome": chamada['Nome'].astype(str).values,
                "Status": chamada['Status'].astype(str).values
            })
            
            try:
                hist_atual = conn.read(worksheet="Historico", ttl=0)
                df_final = pd.concat([hist_atual, novos_dados], ignore_index=True)
                conn.update(worksheet="Historico", data=df_final)
            except:
                conn.update(worksheet="Historico", data=novos_dados)
            
            st.success("✅ Chamada registrada com sucesso!")
            st.balloons()

except Exception as e:
    st.error(f"Erro de Conexão: {e}")
    if st.button("🔄 RECONECTAR"):
        st.cache_data.clear()
        st.rerun()