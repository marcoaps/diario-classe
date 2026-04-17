import streamlit as st
import pandas as pd
from datetime import date
import requests
from io import StringIO

# Configuração da página
st.set_page_config(page_title="Diário Marco - Ed. Física", layout="centered")

# --- CONFIGURAÇÃO DOS LINKS ---
SHEET_ID = "1XfCFGVI9PUalRhiSBbQ95ZIjCz4IGhOT1m4_LeQGF1A"
# Link para ler os dados (Aba Alunos)
URL_DADOS = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=0"

# --- ESTILO MELHORADO ---
st.markdown("""
    <style>
    .stApp { background-color: #f8f9fa; }
    .header-title { 
        color: #1565c0; text-align: center; font-size: 28px; font-weight: bold;
        padding: 10px; border-radius: 10px; background: white;
        box-shadow: 0px 2px 5px rgba(0,0,0,0.1); margin-bottom: 20px;
    }
    .stButton>button {
        background-color: #2e7d32 !important; color: white !important;
        height: 3em; width: 100%; border-radius: 8px; font-size: 18px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- ACESSO ---
if "logado" not in st.session_state:
    st.markdown("<div class='header-title'>📓 DIÁRIO DIGITAL</div>", unsafe_allow_html=True)
    senha = st.text_input("Senha do Professor", type="password")
    if st.button("ACESSAR"):
        if senha == "1234":
            st.session_state.logado = True
            st.rerun()
else:
    # --- LEITURA DOS DADOS COM CORREÇÃO DE ACENTOS (UTF-8) ---
    try:
        response = requests.get(URL_DADOS)
        response.encoding = 'utf-8' # Força a correção dos acentos (Arcília, Vitória)
        df = pd.read_csv(StringIO(response.text))
        df.columns = df.columns.str.strip()
        
        st.sidebar.title(f"Olá, Marco")
        modo = st.sidebar.radio("Navegação:", ["📝 Chamada", "📊 Histórico"])

        if modo == "📝 Chamada":
            st.markdown("<div class='header-title'>LANÇAMENTO RÁPIDO</div>", unsafe_allow_html=True)
            
            lista_turmas = sorted(df['Turma'].dropna().unique())
            turma_sel = st.selectbox("QUAL A TURMA?", lista_turmas)
            data_sel = st.date_input("DATA DA AULA:", date.today())
            
            df_turma = df[df['Turma'] == turma_sel].copy()
            df_turma['STATUS'] = "P"

            st.success(f"**Turma:** {turma_sel} | **Alunos:** {len(df_turma)}")

            # Editor de Chamada
            chamada_edit = st.data_editor(
                df_turma[['Nome', 'STATUS']],
                column_config={
                    "Nome": st.column_config.TextColumn("ALUNO", width="large", disabled=True),
                    "STATUS": st.column_config.SelectboxColumn("P/F", options=["P", "F"], required=True)
                },
                hide_index=True, use_container_width=True
            )

            if st.button("💾 FINALIZAR E SALVAR CHAMADA"):
                # No localhost, vamos simular o salvamento para você ver o resultado
                st.info("Sincronizando com o Google Sheets...")
                # Aqui no código final para Web, usaremos a biblioteca gsheets para dar o 'update'
                st.success(f"Chamada do {turma_sel} processada com sucesso!")
                st.balloons()
        
        else:
            st.markdown("<div class='header-title'>HISTÓRICO DE AULAS</div>", unsafe_allow_html=True)
            st.write("Aqui aparecerão os relatórios de faltas consolidados.")

    except Exception as e:
        st.error(f"Erro ao carregar dados: {e}")