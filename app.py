import streamlit as st
import pandas as pd
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
import io

# Configuração da página
st.set_page_config(page_title="Geocodificador Reverso", page_icon="🌍")

st.title("Geocodificação 🌍 Reversa")
st.write("Célula Técnica - Grupo Apisul")

# 1. Upload do Arquivo
arquivo_upload = st.file_uploader("Arraste ou selecione seu arquivo .xlsx", type=['xlsx'])

if arquivo_upload is not None:
    # Ler a planilha
    df = pd.read_excel(arquivo_upload)
    
    # Validar se as colunas existem
    colunas_esperadas = ['SMP', 'Latitude', 'Longitude', 'Projeto']
    if not all(coluna in df.columns for coluna in colunas_esperadas):
        st.error(f"O arquivo deve conter exatamente as colunas: {', '.join(colunas_esperadas)}")
    else:
        st.write("📊 **Pré-visualização dos Dados Originais:**")
        st.dataframe(df.head())
        
        # Botão para iniciar o processamento
        if st.button("Iniciar Geocodificação 🚀"):
            
            # Tratamento dos dados: Converter vírgula para ponto e depois para float numérico
            df['Lat_Tratada'] = df['Latitude'].astype(str).str.replace(',', '.').astype(float)
            df['Lon_Tratada'] = df['Longitude'].astype(str).str.replace(',', '.').astype(float)

            # Configurar o Geocodificador (OpenStreetMap)
            geolocator = Nominatim(user_agent="meu_aplicativo_geocodificador")
            
            # RateLimiter é crucial para não ser bloqueado pelo OpenStreetMap por excesso de requisições rápidas
            reverse = RateLimiter(geolocator.reverse, min_delay_seconds=1.2)

            # Criar barra de progresso no Streamlit
            barra_progresso = st.progress(0)
            status_texto = st.empty()
            
            localizacoes = []
            total_linhas = len(df)
            
            status_texto.text("Processando... Isso pode levar alguns segundos por linha.")
            
            # Loop por cada linha do dataframe
            for indice, linha in df.iterrows():
                lat = linha['Lat_Tratada']
                lon = linha['Lon_Tratada']
                
                try:
                    # Busca a localização e força o retorno em português
                    local = reverse((lat, lon), language='pt')
                    if local:
                        localizacoes.append(local.address)
                    else:
                        localizacoes.append("Local não encontrado")
                except Exception as e:
                    localizacoes.append("Erro na busca")
                
                # Atualiza a barra de progresso
                barra_progresso.progress((indice + 1) / total_linhas)

            # Remover as colunas de tratamento e adicionar a coluna final
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
                file_name="planilha_com_localizacao.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )