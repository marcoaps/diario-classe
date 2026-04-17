import streamlit as st
import pandas as pd
from datetime import date
from streamlit_gsheets import GSheetsConnection

# Configuração para Celular (Foco em leitura rápida)
st.set_page_config(page_title="Diário Prof. Marco", layout="centered")

# --- CONEXÃO COM GOOGLE SHEETS ---
URL_PLANILHA = "https://docs.google.com/spreadsheets/d/1XfCFGVI9PUalRhiSBbQ95ZIjCz4IGhOT1m4_LeQGF1A/edit?usp=sharing"

# --- ESTILO VISUAL (MAIOR PARA A QUADRA) ---
st.markdown("""
    <style>
    .header-title { 
        color: #ffffff; text-align: center; font-size: 24px; font-weight: bold;
        background-color: #0d47a1; padding: 15px; border-radius: 10px;
        margin-bottom: 20px;
    }
    .stButton>button {
        background-color: #2e7d32 !important; color: white !important;
        height: 3.5em; width: 100%; border-radius: 10px; font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# --- ACESSO ---
if "logado" not in st.session_state:
    st.markdown("<div class='header-title'>📓 DIÁRIO DE CLASSE</div>", unsafe_allow_html=True)
    senha = st.text_input("Senha:", type="password")
    if st.button("ENTRAR"):
        if senha == "1234":
            st.session_state.logado = True
            st.rerun()
else:
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        # Lê a aba Alunos
        df_alunos = conn.read(spreadsheet=URL_PLANILHA, worksheet="Alunos", ttl=0)
        df_alunos = df_alunos.dropna(subset=['Nome'])
        
        st.sidebar.title("PROF. MARCO")
        modo = st.sidebar.radio("Navegação:", ["📝 Chamada", "📊 Histórico"])

        if modo == "📝 Chamada":
            st.markdown("<div class='header-title'>CHAMADA RÁPIDA</div>", unsafe_allow_html=True)
            
            lista_turmas = sorted(df_alunos['Turma'].dropna().unique())
            turma_sel = st.selectbox("QUAL TURMA?", lista_turmas)
            data_sel = st.date_input("DATA:", date.today())
            
            df_turma = df_alunos[df_alunos['Turma'] == turma_sel].copy()
            df_turma['STATUS'] = "P"

            st.info(f"📍 {turma_sel} | 👥 {len(df_turma)} Alunos")

            # Editor de Chamada
            chamada_edit = st.data_editor(
                df_turma[['Nome', 'STATUS']],
                column_config={
                    "Nome": st.column_config.TextColumn("ALUNO", disabled=True),
                    "STATUS": st.column_config.SelectboxColumn("P/F", options=["P", "F"], required=True)
                },
                hide_index=True, use_container_width=True
            )

            if st.button("💾 SALVAR CHAMADA NA NUVEM"):
                with st.spinner("Gravando no Google Sheets..."):
                    # Prepara os dados do histórico
                    chamada_edit['Data'] = data_sel.strftime('%d/%m/%Y')
                    chamada_edit['Turma'] = turma_sel
                    
                    # Lê histórico atual e anexa a nova chamada
                    try:
                        hist_atual = conn.read(spreadsheet=URL_PLANILHA, worksheet="Historico", ttl=0)
                        df_final = pd.concat([hist_atual, chamada_edit], ignore_index=True)
                        conn.update(spreadsheet=URL_PLANILHA, worksheet="Historico", data=df_final)
                        st.success(f"✅ Chamada do {turma_sel} gravada!")
                        st.balloons()
                    except:
                        # Se a aba estiver vazia
                        conn.update(spreadsheet=URL_PLANILHA, worksheet="Historico", data=chamada_edit)
                        st.success("✅ Histórico iniciado com sucesso!")
        
        else:
            st.markdown("<div class='header-title'>HISTÓRICO DE AULAS</div>", unsafe_allow_html=True)
            df_h = conn.read(spreadsheet=URL_PLANILHA, worksheet="Historico", ttl=0)
            st.dataframe(df_h, use_container_width=True, hide_index=True)

    except Exception as e:
        st.error(f"Erro: {e}")