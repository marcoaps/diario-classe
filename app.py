import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import date

# Configuração para Celular
st.set_page_config(page_title="Diário Online Marco", layout="centered")

# --- CONEXÃO COM GOOGLE SHEETS ---
# (Isso permitirá que o app salve os dados na nuvem)
conn = st.connection("gsheets", type=GSheetsConnection)

st.markdown("""
    <style>
    .stApp { background-color: #ffffff; }
    .header-title { 
        color: #0d47a1; text-align: center; font-size: 26px; font-weight: bold;
        border-bottom: 3px solid #0d47a1; margin-bottom: 20px;
    }
    label, p { color: #000000 !important; font-weight: bold !important; }
    .stButton>button {
        background-color: #1a73e8 !important; color: white !important;
        height: 3.5em; width: 100%; border-radius: 10px; font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

if "logado" not in st.session_state:
    st.markdown("<div class='header-title'>DIÁRIO ONLINE</div>", unsafe_allow_html=True)
    senha = st.text_input("Senha do Professor", type="password")
    if st.button("ENTRAR"):
        if senha == "1234":
            st.session_state.logado = True
            st.rerun()
else:
    modo = st.sidebar.radio("MENU", ["📝 Chamada", "⚙️ Configurar Turmas"])

    # Carregar dados dos alunos da planilha (Aba 'Alunos')
    try:
        df_alunos = conn.read(worksheet="Alunos")
    except:
        st.error("Configure a aba 'Alunos' na sua Planilha Google primeiro!")
        st.stop()

    if modo == "📝 Chamada":
        st.markdown("<div class='header-title'>LANÇAMENTO RÁPIDO</div>", unsafe_allow_html=True)
        
        turma_sel = st.selectbox("TURMA:", sorted(df_alunos['Turma'].unique()))
        data_sel = st.date_input("DATA:", date.today())
        
        df_turma = df_alunos[df_alunos['Turma'] == turma_sel].copy()
        df_turma['STATUS'] = "P"

        chamada_edit = st.data_editor(
            df_turma[['Nome', 'STATUS']],
            column_config={
                "Nome": st.column_config.TextColumn("ALUNO", disabled=True),
                "STATUS": st.column_config.SelectboxColumn("P/F", options=["P", "F"])
            },
            hide_index=True, use_container_width=True
        )

        if st.button("💾 ENVIAR PARA A NUVEM"):
            # Lógica para anexar os dados na aba 'Historico' da planilha
            chamada_edit['Data'] = data_sel.strftime('%d/%m/%Y')
            chamada_edit['Turma'] = turma_sel
            
            # Lê o histórico atual e adiciona a nova chamada
            hist_atual = conn.read(worksheet="Historico")
            novo_hist = pd.concat([hist_atual, chamada_edit], ignore_index=True)
            
            conn.update(worksheet="Historico", data=novo_hist)
            st.success("✅ Sincronizado com o Google Sheets!")
            st.balloons()