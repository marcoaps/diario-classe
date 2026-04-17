import streamlit as st
import pandas as pd
from datetime import date
from streamlit_gsheets import GSheetsConnection

# 1. Configuração da Página para Celular
st.set_page_config(page_title="Diário Prof. Marco", layout="centered")

# --- CONEXÃO COM SUA PLANILHA ---
URL_PLANILHA = "https://docs.google.com/spreadsheets/d/1XfCFGVI9PUalRhiSBbQ95ZIjCz4IGhOT1m4_LeQGF1A/edit?usp=sharing"

# 2. Estilo Visual para uso na Quadra
st.markdown("""
    <style>
    .header-title { 
        color: #ffffff; text-align: center; font-size: 22px; font-weight: bold;
        background-color: #0d47a1; padding: 12px; border-radius: 8px;
        margin-bottom: 15px;
    }
    .stButton>button {
        background-color: #2e7d32 !important; color: white !important;
        height: 3.5em; width: 100%; border-radius: 10px; font-weight: bold;
        font-size: 18px !important;
    }
    header {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# 3. Sistema de Acesso
if "logado" not in st.session_state:
    st.markdown("<div class='header-title'>📓 DIÁRIO DE CLASSE</div>", unsafe_allow_html=True)
    senha = st.text_input("Senha de Acesso:", type="password")
    if st.button("ENTRAR"):
        if senha == "1234":
            st.session_state.logado = True
            st.rerun()
        else:
            st.error("Senha incorreta!")
else:
    try:
        # Conecta ao Google Sheets
        conn = st.connection("gsheets", type=GSheetsConnection)
        
        # Lê a aba Alunos (Sempre atualizado)
        df_alunos = conn.read(spreadsheet=URL_PLANILHA, worksheet="Alunos", ttl=0)
        df_alunos = df_alunos.dropna(subset=['Nome'])
        
        st.sidebar.title("PROF. MARCO")
        modo = st.sidebar.radio("MENU:", ["📝 Chamada", "📊 Histórico"])

        if modo == "📝 Chamada":
            st.markdown("<div class='header-title'>CHAMADA RÁPIDA</div>", unsafe_allow_html=True)
            
            # Lista as turmas em ordem alfabética
            lista_turmas = sorted(df_alunos['Turma'].dropna().unique())
            turma_sel = st.selectbox("QUAL TURMA?", lista_turmas)
            data_sel = st.date_input("DATA DA AULA:", date.today())
            
            # Filtra os alunos da turma
            df_turma = df_alunos[df_alunos['Turma'] == turma_sel].copy()
            df_turma['Status'] = "P" # Padrão é Presença

            st.info(f"📍 {turma_sel} | 👥 {len(df_turma)} Alunos")

            # Tabela de Chamada Ajustada para Celular
            chamada_edit = st.data_editor(
                df_turma[['Nome', 'Status']],
                column_config={
                    "Nome": st.column_config.TextColumn("ALUNO", width="medium", disabled=True),
                    "Status": st.column_config.SelectboxColumn("P/F", options=["P", "F"], width="small", required=True)
                },
                hide_index=True, 
                use_container_width=True
            )

            # BOTÃO DE SALVAR (O coração do sistema)
            if st.button("💾 SALVAR CHAMADA NA NUVEM"):
                with st.spinner("Gravando no Google Sheets..."):
                    # Prepara os dados exatamente como estão na sua aba Historico
                    novo_registro = pd.DataFrame({
                        "Data": [data_sel.strftime('%d/%m/%Y')] * len(chamada_edit),
                        "Turma": [turma_sel] * len(chamada_edit),
                        "Nome": chamada_edit['Nome'].values,
                        "Status": chamada_edit['Status'].values
                    })
                    
                    try:
                        # Tenta ler o histórico para anexar o novo
                        hist_atual = conn.read(spreadsheet=URL_PLANILHA, worksheet="Historico", ttl=0)
                        df_final = pd.concat([hist_atual, novo_registro], ignore_index=True)
                        conn.update(spreadsheet=URL_PLANILHA, worksheet="Historico", data=df_final)
                        st.success(f"✅ Chamada do {turma_sel} enviada!")
                        st.balloons()
                    except:
                        # Se der erro (aba vazia), cria o primeiro registro
                        conn.update(spreadsheet=URL_PLANILHA, worksheet="Historico", data=novo_registro)
                        st.success("✅ Histórico iniciado com sucesso!")
        
        else:
            # ABA DE HISTÓRICO
            st.markdown("<div class='header-title'>HISTÓRICO DE LANÇAMENTOS</div>", unsafe_allow_html=True)
            df_h = conn.read(spreadsheet=URL_PLANILHA, worksheet="Historico", ttl=0)
            if not df_h.empty:
                st.dataframe(df_h, use_container_width=True, hide_index=True)
            else:
                st.write("Ainda não existem chamadas salvas.")

    except Exception as e:
        st.error(f"Erro de Conexão: {e}")
        st.info("Verifique se a planilha está como 'Editor' para qualquer pessoa com o link.")