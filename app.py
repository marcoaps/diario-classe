import streamlit as st
import pandas as pd
from datetime import date
from streamlit_gsheets import GSheetsConnection

# Configuração da página
st.set_page_config(page_title="Diário Prof. Marco", layout="centered")

# --- ESTILO VISUAL ---
st.markdown("""
    <style>
    .header-title { 
        color: white; text-align: center; font-size: 22px; font-weight: bold;
        background-color: #0d47a1; padding: 12px; border-radius: 8px; margin-bottom: 15px;
    }
    .stButton>button {
        background-color: #2e7d32 !important; color: white !important;
        height: 3.5em; width: 100%; border-radius: 10px; font-weight: bold;
    }
    header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- LOGIN ---
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
        # Conexão com o Google Sheets usando os Secrets do site
        conn = st.connection("gsheets", type=GSheetsConnection)
        
        # Lê a lista de Alunos
        df_alunos = conn.read(worksheet="Alunos", ttl=0)
        df_alunos = df_alunos.dropna(subset=['Nome'])
        
        st.sidebar.title("PROF. MARCO")
        modo = st.sidebar.radio("MENU:", ["📝 Chamada", "📊 Histórico"])

        if modo == "📝 Chamada":
            st.markdown("<div class='header-title'>CHAMADA RÁPIDA</div>", unsafe_allow_html=True)
            
            lista_turmas = sorted(df_alunos['Turma'].dropna().unique())
            turma_sel = st.selectbox("QUAL TURMA?", lista_turmas)
            data_sel = st.date_input("DATA DA AULA:", date.today())
            
            # Filtra alunos e prepara tabela
            df_turma = df_alunos[df_alunos['Turma'] == turma_sel][['Nome']].copy()
            df_turma['Status'] = "P"

            st.info(f"📍 {turma_sel} | 👥 {len(df_turma)} Alunos")

            # Editor de chamadas
            chamada_edit = st.data_editor(
                df_turma,
                column_config={
                    "Nome": st.column_config.TextColumn("ALUNO", disabled=True),
                    "Status": st.column_config.SelectboxColumn("P/F", options=["P", "F"], required=True)
                },
                hide_index=True, use_container_width=True
            )

            if st.button("💾 SALVAR CHAMADA"):
                with st.spinner("Gravando na nuvem..."):
                    # Cria o novo bloco de dados
                    novos_dados = pd.DataFrame({
                        "Data": [data_sel.strftime('%d/%m/%Y')] * len(chamada_edit),
                        "Turma": [turma_sel] * len(chamada_edit),
                        "Nome": chamada_edit['Nome'].values,
                        "Status": chamada_edit['Status'].values
                    })
                    
                    try:
                        # Lê o histórico que já existe
                        hist_existente = conn.read(worksheet="Historico", ttl=0)
                        # Junta com os novos dados
                        df_atualizado = pd.concat([hist_existente, novos_dados], ignore_index=True)
                        # Salva tudo de volta
                        conn.update(worksheet="Historico", data=df_atualizado)
                    except:
                        # Se der erro na leitura (planilha vazia), salva apenas os novos dados
                        conn.update(worksheet="Historico", data=novos_dados)
                    
                    st.success(f"✅ Chamada do {turma_sel} salva!")
                    st.balloons()
        
        else:
            st.markdown("<div class='header-title'>HISTÓRICO DE LANÇAMENTOS</div>", unsafe_allow_html=True)
            df_h = conn.read(worksheet="Historico", ttl=0)
            if not df_h.empty:
                st.dataframe(df_h, use_container_width=True, hide_index=True)
            else:
                st.write("Nenhum registro encontrado.")

    except Exception as e:
        st.error(f"Erro no sistema: {e}")
        st.info("Dica: Verifique se a aba 'Historico' existe na planilha.")