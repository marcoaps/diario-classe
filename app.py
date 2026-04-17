import streamlit as st
import pandas as pd
from datetime import date
from streamlit_gsheets import GSheetsConnection

st.set_page_config(page_title="Diário Prof. Marco", layout="centered")

st.markdown("""
    <style>
    .header-title { color: white; text-align: center; font-size: 22px; font-weight: bold; background-color: #0d47a1; padding: 10px; border-radius: 8px; }
    .stButton>button { background-color: #2e7d32 !important; color: white !important; font-weight: bold; width: 100%; height: 3em; }
    header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    
    # Tentativa de leitura robusta
    df_alunos = conn.read(worksheet="Alunos", ttl="1m") # Cache de 1 minuto para evitar Erro 400
    
    st.markdown("<div class='header-title'>📝 LANÇAR CHAMADA</div>", unsafe_allow_html=True)
    
    turmas = sorted(df_alunos['Turma'].dropna().unique())
    turma_sel = st.selectbox("Selecione a Turma:", turmas)
    
    df_turma = df_alunos[df_alunos['Turma'] == turma_sel][['Nome']].copy()
    df_turma['Status'] = "P"

    chamada = st.data_editor(df_turma, hide_index=True, use_container_width=True)

    if st.button("💾 CONFIRMAR E SALVAR"):
        with st.spinner("Conectando ao Google..."):
            novos = pd.DataFrame({
                "Data": [date.today().strftime('%d/%m/%Y')] * len(chamada),
                "Turma": [str(turma_sel)] * len(chamada),
                "Nome": chamada['Nome'].astype(str).values,
                "Status": chamada['Status'].astype(str).values
            })
            
            try:
                # O comando 'ttl=0' aqui força o salvamento imediato
                hist = conn.read(worksheet="Historico", ttl=0)
                df_final = pd.concat([hist, novos], ignore_index=True)
                conn.update(worksheet="Historico", data=df_final)
                st.success("✅ Salvo com sucesso!")
                st.balloons()
            except Exception as e_save:
                # Tenta salvar como novo se o histórico falhar
                conn.update(worksheet="Historico", data=novos)
                st.success("✅ Histórico iniciado e salvo!")

except Exception as e:
    st.error(f"Erro de Conexão (400): O Google recusou o pedido.")
    st.info("💡 Verifique se a planilha está como 'EDITOR' no botão Compartilhar.")
    if st.button("🔄 RECONECTAR SISTEMA"):
        st.cache_data.clear()
        st.rerun()