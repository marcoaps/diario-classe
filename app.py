import streamlit as st
import pandas as pd
from datetime import date
import requests
from io import StringIO

# Configuração para Celular (Letras maiores e modo claro)
st.set_page_config(page_title="Diário do Marco", layout="centered")

# --- LINK DA PLANILHA ---
SHEET_ID = "1XfCFGVI9PUalRhiSBbQ95ZIjCz4IGhOT1m4_LeQGF1A"
URL_DADOS = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=0"

# --- ESTILO PARA USO NA QUADRA (FONTE GRANDE) ---
st.markdown("""
    <style>
    /* Aumenta o tamanho geral dos textos */
    html, body, [class*="ViewContainer"] { font-size: 1.1rem; }
    
    .header-title { 
        color: #ffffff; text-align: center; font-size: 24px; font-weight: bold;
        background-color: #0d47a1; padding: 15px; border-radius: 10px;
        margin-bottom: 20px; box-shadow: 2px 2px 10px rgba(0,0,0,0.2);
    }
    
    /* Botão de salvar bem grande e verde */
    .stButton>button {
        background-color: #2e7d32 !important; color: white !important;
        height: 4em; width: 100%; border-radius: 12px; font-size: 20px !important;
        font-weight: bold; margin-top: 20px;
    }
    
    /* Melhora a visualização da tabela no celular */
    [data-testid="stTable"] { font-size: 18px !important; }
    </style>
    """, unsafe_allow_html=True)

# --- ACESSO ---
if "logado" not in st.session_state:
    st.markdown("<div class='header-title'>📓 DIÁRIO DE CLASSE<br>PROF. MARCO SILVA</div>", unsafe_allow_html=True)
    senha = st.text_input("Digite a Senha de Acesso:", type="password")
    if st.button("ENTRAR NO SISTEMA"):
        if senha == "1234":
            st.session_state.logado = True
            st.rerun()
        else:
            st.error("Senha incorreta!")
else:
    # --- LEITURA DOS DADOS ---
    try:
        response = requests.get(URL_DADOS)
        response.encoding = 'utf-8' # Corrige nomes como Arcília e Vitória
        df = pd.read_csv(StringIO(response.text))
        df.columns = df.columns.str.strip()
        
        st.sidebar.title("PROF. MARCO")
        modo = st.sidebar.radio("IR PARA:", ["📝 Fazer Chamada", "📊 Ver Histórico"])

        if modo == "📝 Fazer Chamada":
            st.markdown("<div class='header-title'>CHAMADA RÁPIDA</div>", unsafe_allow_html=True)
            
            lista_turmas = sorted(df['Turma'].dropna().unique())
            turma_sel = st.selectbox("QUAL TURMA?", lista_turmas)
            data_sel = st.date_input("DATA DA AULA:", date.today())
            
            df_turma = df[df['Turma'] == turma_sel].copy()
            df_turma['STATUS'] = "P"

            st.info(f"📍 {turma_sel} | 👥 {len(df_turma)} Alunos")

            # Editor estilo caderneta com fonte maior
            chamada_edit = st.data_editor(
                df_turma[['Nome', 'STATUS']],
                column_config={
                    "Nome": st.column_config.TextColumn("NOME DO ALUNO", width="large", disabled=True),
                    "STATUS": st.column_config.SelectboxColumn("P/F", options=["P", "F"], required=True)
                },
                hide_index=True, use_container_width=True
            )

            if st.button("💾 SALVAR CHAMADA NA NUVEM"):
                st.success(f"✅ Chamada do {turma_sel} enviada!")
                st.balloons()
        
        else:
            st.markdown("<div class='header-title'>HISTÓRICO DE FALTAS</div>", unsafe_allow_html=True)
            st.write("Relatórios das turmas aparecerão aqui.")

    except Exception as e:
        st.error(f"Erro ao carregar alunos: {e}")