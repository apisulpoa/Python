import streamlit as st
import pandas as pd
from geopy.geocoders import ArcGIS
import time
import io

# Configuração da página
st.set_page_config(page_title="Geocodificador Reverso", page_icon="🌍")

st.title("🌍 Automação de Geocodificação Reversa")
st.write("Envie sua planilha com as colunas **SMP, Latitude, Longitude e Projeto** e descubra o endereço de cada ponto.")

# 1. Upload do Arquivo
arquivo_upload = st.file_uploader("Arraste ou selecione seu arquivo .xlsx", type=['xlsx'])

if arquivo_upload is not None:
    df = pd.read_excel(arquivo_upload)
    
    colunas_esperadas = ['SMP', 'Latitude', 'Longitude', 'Projeto']
    if not all(coluna in df.columns for coluna in colunas_esperadas):
        st.error(f"O arquivo deve conter exatamente as colunas: {', '.join(colunas_esperadas)}")
    else:
        st.write("📊 **Pré-visualização dos Dados Originais:**")
        st.dataframe(df.head())
        
        if st.button("Iniciar Geocodificação Turbo 🚀"):
            
            df['Lat_Tratada'] = df['Latitude'].astype(str).str.replace(',', '.').astype(float)
            df['Lon_Tratada'] = df['Longitude'].astype(str).str.replace(',', '.').astype(float)

            geolocator = ArcGIS(user_agent="meu_app_roteirizacao")

            barra_progresso = st.progress(0)
            status_texto = st.empty()
            
            # Novas listas para guardar as informações separadas
            cidades = []
            estados = []
            localizacoes = []
            
            total_linhas = len(df)
            status_texto.text("Processando em alta velocidade...")
            
            for indice, linha in df.iterrows():
                lat = linha['Lat_Tratada']
                lon = linha['Lon_Tratada']
                
                try:
                    local = geolocator.reverse((lat, lon))
                    if local:
                        # Guarda o endereço completo
                        localizacoes.append(local.address)
                        
                        # Acessa os dados "crus" (raw) que o ArcGIS devolve em formato de dicionário
                        dados_brutos = local.raw.get('address', {})
                        
                        # Pega a Cidade. Se for área rural e 'City' estiver vazio, tenta pegar 'Subregion' (Município)
                        cidade = dados_brutos.get('City') or dados_brutos.get('Subregion') or "Não identificada"
                        # Pega o Estado ('Region' no padrão ArcGIS)
                        estado = dados_brutos.get('Region') or "Não identificado"
                        
                        cidades.append(cidade)
                        estados.append(estado)
                    else:
                        localizacoes.append("Local não mapeado")
                        cidades.append("N/A")
                        estados.append("N/A")
                        
                except Exception as e:
                    localizacoes.append("Erro na busca")
                    cidades.append("Erro")
                    estados.append("Erro")
                
                time.sleep(0.1)
                barra_progresso.progress((indice + 1) / total_linhas)

            df = df.drop(columns=['Lat_Tratada', 'Lon_Tratada'])
            
            # Adicionando as três novas colunas ao DataFrame final
            df['Cidade'] = cidades
            df['Estado'] = estados
            df['Localização Completa'] = localizacoes
            
            status_texto.text("✅ Processamento concluído com sucesso!")
            
            st.write("📍 **Resultado:**")
            st.dataframe(df)

            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False, sheet_name='Geocodificado')
            
            st.download_button(
                label="📥 Baixar Planilha Pronta (.xlsx)",
                data=output.getvalue(),
                file_name="planilha_com_localizacao_detalhada.xlsx",
                mime="application
