import streamlit as st
import pandas as pd
from datetime import date
from streamlit_gsheets import GSheetsConnection

st.set_page_config(page_title="Diário Prof. Marco")

# --- ESTILO ---
st.markdown("<style>header {visibility: hidden;} .stButton>button {background-color: #2e7d32; color: white; width: 100%; height: 3em;}</style>", unsafe_allow_html=True)

try:
    # Tenta conectar usando os Secrets do site
    conn = st.connection("gsheets", type=GSheetsConnection)
    
    # Busca os alunos
    df_alunos = conn.read(worksheet="Alunos", ttl=0)
    
    st.title("📝 Chamada")
    
    lista_turmas = sorted(df_alunos['Turma'].dropna().unique())
    turma_sel = st.selectbox("Selecione a Turma:", lista_turmas)
    
    df_turma = df_alunos[df_alunos['Turma'] == turma_sel][['Nome']].copy()
    df_turma['Status'] = "P"

    # Editor simplificado
    chamada_edit = st.data_editor(df_turma, hide_index=True, use_container_width=True)

    if st.button("💾 SALVAR AGORA"):
        with st.spinner("Gravando..."):
            novos_dados = pd.DataFrame({
                "Data": [date.today().strftime('%d/%m/%Y')] * len(chamada_edit),
                "Turma": [str(turma_sel)] * len(chamada_edit),
                "Nome": chamada_edit['Nome'].astype(str).values,
                "Status": chamada_edit['Status'].astype(str).values
            })
            
            # Tenta salvar direto na aba Historico
            try:
                hist = conn.read(worksheet="Historico", ttl=0)
                df_final = pd.concat([hist, novos_dados], ignore_index=True)
                conn.update(worksheet="Historico", data=df_final)
            except:
                conn.update(worksheet="Historico", data=novos_dados)
            
            st.success("Salvo com sucesso!")
            st.balloons()

except Exception as e:
    st.error(f"Erro Crítico: {e}")
    st.warning("Verifique se a Planilha está como 'Editor' e se a aba 'Historico' existe.")