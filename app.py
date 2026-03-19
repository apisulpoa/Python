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
            
            # Tratamento dos dados (Garante que a vírgula vira ponto e vira número)
            df['Lat_Tratada'] = df['Latitude'].astype(str).str.replace(',', '.').astype(float)
            df['Lon_Tratada'] = df['Longitude'].astype(str).str.replace(',', '.').astype(float)

            # Usando o ArcGIS que é muito mais rápido e preciso para estradas/Brasil
            geolocator = ArcGIS(user_agent="meu_app_roteirizacao")

            barra_progresso = st.progress(0)
            status_texto = st.empty()
            
            localizacoes = []
            total_linhas = len(df)
            
            status_texto.text("Processando em alta velocidade...")
            
            for indice, linha in df.iterrows():
                lat = linha['Lat_Tratada']
                lon = linha['Lon_Tratada']
                
                try:
                    # Busca a localização no ArcGIS
                    local = geolocator.reverse((lat, lon))
                    if local:
                        localizacoes.append(local.address)
                    else:
                        localizacoes.append("Local não mapeado")
                except Exception as e:
                    localizacoes.append("Erro na busca")
                
                # Uma pausa minúscula de 0.1s só para não sobrecarregar
                time.sleep(0.1)
                
                # Atualiza a barra de progresso
                barra_progresso.progress((indice + 1) / total_linhas)

            # Limpando as colunas extras e adicionando o resultado
            df = df.drop(columns=['Lat_Tratada', 'Lon_Tratada'])
            df['Localização'] = localizacoes
            
            status_texto.text("✅ Processamento concluído com sucesso!")
            
            st.write("📍 **Resultado:**")
            st.dataframe(df)

            # Preparar o arquivo para Download
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False, sheet_name='Geocodificado')
            
            st.download_button(
                label="📥 Baixar Planilha Pronta (.xlsx)",
                data=output.getvalue(),
                file_name="planilha_com_localizacao_arcgis.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
