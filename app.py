import streamlit as st
import pandas as pd
from geopy.geocoders import ArcGIS
import time
import io
import re

# Configuração da página
st.set_page_config(page_title="Geocodificador Reverso", page_icon="🌍")

st.title("🌍 Automação de Geocodificação Reversa")
st.write("Envie qualquer planilha contendo as colunas **Latitude** e **Longitude**. O aplicativo manterá todas as suas outras colunas intactas e adicionará os dados de localização no final.")

# 1. Upload do Arquivo
arquivo_upload = st.file_uploader("Arraste ou selecione seu arquivo .xlsx", type=['xlsx'])

if arquivo_upload is not None:
    df = pd.read_excel(arquivo_upload)
    
    # Validação dinâmica: verifica apenas se Lat e Lon existem na planilha
    if 'Latitude' not in df.columns or 'Longitude' not in df.columns:
        st.error("O arquivo deve conter as colunas 'Latitude' e 'Longitude' (exatamente com esses nomes, com a primeira letra maiúscula).")
    else:
        st.write("📊 **Pré-visualização dos Dados Originais:**")
        st.dataframe(df.head())
        
        if st.button("Iniciar Geocodificação Turbo 🚀"):
            
            df['Lat_Tratada'] = df['Latitude'].astype(str).str.replace(',', '.').astype(float)
            df['Lon_Tratada'] = df['Longitude'].astype(str).str.replace(',', '.').astype(float)

            geolocator = ArcGIS(user_agent="meu_app_roteirizacao")

            barra_progresso = st.progress(0)
            status_texto = st.empty()
            
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
                        endereco_completo = local.address
                        localizacoes.append(endereco_completo)
                        
                        # Lógica para fatiar o texto separando por vírgula
                        partes = endereco_completo.split(',')
                        partes = [p.strip() for p in partes] # Limpa espaços em branco
                        
                        if len(partes) >= 3:
                            # O Estado + CEP costuma ser o penúltimo item
                            estado_com_cep = partes[-2]
                            # Remove todos os números (0-9) e traços (-) para deixar só o nome do Estado
                            estado_limpo = re.sub(r'[0-9-]', '', estado_com_cep).strip()
                            
                            # A Cidade costuma ser o antepenúltimo item
                            cidade = partes[-3]
                            
                            cidades.append(cidade)
                            estados.append(estado_limpo)
                        else:
                            # Caso o endereço venha muito curto e fora do padrão
                            cidades.append("Não identificada")
                            estados.append("Não identificado")
                            
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
            
            # Adiciona as colunas novas no final da planilha original
            df['Cidade'] = cidades
            df['Estado'] = estados
            df['Localização Completa'] = localizacoes
            
            status_texto.text("✅ Processamento concluído com sucesso!")
            
            st.write("📍 **Resultado:**")
            st.dataframe(df)

            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False, sheet_name='Geocodificado')
            
            # Cuidado ao copiar esta parte para não quebrar a linha do mime= novamente!
            st.download_button(
                label="📥 Baixar Planilha Pronta (.xlsx)",
                data=output.getvalue(),
                file_name="planilha_com_localizacao_detalhada.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
