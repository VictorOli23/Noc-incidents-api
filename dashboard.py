import streamlit as st
import requests
import pandas as pd

# Substitua pela URL real do seu Render (sem o /docs)
API_URL = "https://seu-projeto.onrender.com"

st.set_page_config(page_title="NOC Dashboard", layout="wide")

st.title("📊 Painel de Incidentes NOC")
st.write("Visualização em tempo real dos ativos e falhas de rede.")

# Botão para atualizar os dados
if st.button('🔄 Atualizar Dados'):
    st.rerun()

# --- BUSCANDO DADOS ---
try:
    response = requests.get(f"{API_URL}/incidentes/")
    if response.status_code == 200:
        dados = response.json()
        
        if dados:
            df = pd.DataFrame(dados)
            
            # --- MÉTRICAS RÁPIDAS ---
            col1, col2, col3 = st.columns(3)
            col1.metric("Total de Incidentes", len(df))
            col2.metric("Críticos", len(df[df['severidade'] == 'Critica']))
            col3.metric("Clientes Afetados", df['cliente_b2b'].nunique())

            # --- TABELA DE INCIDENTES ---
            st.subheader("📋 Lista de Incidentes")
            st.dataframe(df, use_container_width=True)
            
        else:
            st.warning("Nenhum incidente cadastrado no momento.")
    else:
        st.error("Erro ao conectar com a API.")
except Exception as e:
    st.error(f"Erro de conexão: {e}")
