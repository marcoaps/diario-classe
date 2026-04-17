import streamlit as st
import pandas as pd
from datetime import date
from streamlit_gsheets import GSheetsConnection

# Configuração da página
st.set_page_config(page_title="Diário Prof. Marco", layout="centered")

# Estilo Visual
st.markdown("""
    <style>
    .header-title { color: white; text-align: center; font-size: 22px; font-weight: bold; background-color: #0d47a1; padding: 10px; border-radius: 8px; }
    .stButton>button { background-color: #2e7d32 !important; color: white !important; font-weight: bold; width: 100%; height: 3.5em; border-radius: 10px; }
    header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

try:
    # Estabelece a conexão usando os Secrets do site
    conn = st.connection("gsheets", type=GSheetsConnection)
    
    # Lê a aba Alunos (com cache curto para não travar)
    df_alunos = conn.read(worksheet="Alunos", ttl="1m")
    df_alunos = df_alunos.dropna(subset=['Nome'])
    
    st.markdown("<div class='header-title'>📝 DIÁRIO DE CLASSE</div>", unsafe_allow_html=True)
    
    # Menu lateral
    st.sidebar.title("PROF. MARCO")
    modo = st.sidebar.radio("IR PARA:", ["Fazer Chamada", "Ver Histórico"])

    if modo == "Fazer Chamada":
        turmas = sorted(df_alunos['Turma'].dropna().unique())
        turma_sel = st.selectbox("Selecione a Turma:", turmas)
        data_sel = st.date_input("Data da Aula:", date.today())
        
        df_turma = df_alunos[df_alunos['Turma'] == turma_sel][['Nome']].copy()
        df_turma['Status'] = "P"

        st.info(f"📍 {turma_sel} | 👥 {len(df_turma)} Alunos")

        # Editor de Chamada
        chamada = st.data_editor(
            df_turma,
            column_config={
                "Nome": st.column_config.TextColumn("ALUNO", disabled=True),
                "Status": st.column_config.SelectboxColumn("P/F", options=["P", "F"], required=True)
            },
            hide_index=True, use_container_width=True
        )

        if st.button("💾 SALVAR CHAMADA NA NUVEM"):
            with st.spinner("Gravando dados..."):
                novos_dados = pd.DataFrame({
                    "Data": [data_sel.strftime('%d/%m/%Y')] * len(chamada),
                    "Turma": [str(turma_sel)] * len(chamada),
                    "Nome": chamada['Nome'].astype(str).values,
                    "Status": chamada['Status'].astype(str).values
                })
                
                try:
                    # Tenta ler o que já existe
                    hist_atual = conn.read(worksheet="Historico", ttl=0)
                    df_final = pd.concat([hist_atual, novos_dados], ignore_index=True)
                    conn.update(worksheet="Historico", data=df_final)
                except:
                    # Se der erro (aba vazia), começa o histórico do zero
                    conn.update(worksheet="Historico", data=novos_dados)
                
                st.success("✅ Chamada registrada com sucesso!")
                st.balloons()
    
    else:
        st.markdown("<div class='header-title'>HISTÓRICO DE FALTAS</div>", unsafe_allow_html=True)
        df_h = conn.read(worksheet="Historico", ttl=0)
        if not df_h.empty:
            st.dataframe(df_h, use_container_width=True, hide_index=True)
        else:
            st.write("Ainda não há registros nesta aba.")

except Exception as e:
    st.error(f"Erro de Conexão (400): O Google recusou o pedido.")
    st.info("💡 Verifique se a planilha está como 'EDITOR' no botão Compartilhar.")
    if st.button("🔄 RECONECTAR SISTEMA"):
        st.cache_data.clear()
        st.rerun()