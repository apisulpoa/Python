import streamlit as st
import pandas as pd
from geopy.geocoders import ArcGIS
import time
import io
import re

# Configuração da página
st.set_page_config(page_title="Geocodificador Reverso", page_icon="🌍")

st.title("Geocodificação 🌍 Reversa")
st.write("Célula Técnica - Grupo Apisul")

# 1. Upload do Arquivo
arquivo_upload = st.file_uploader("Arraste ou selecione seu arquivo .xlsx que possui Latitude e Longitude.", type=['xlsx'])

if arquivo_upload is not None:
    df = pd.read_excel(arquivo_upload)
    
    # Validação dinâmica
    if 'Latitude' not in df.columns or 'Longitude' not in df.columns:
        st.error("O arquivo deve conter as colunas 'Latitude' e 'Longitude' (exatamente com esses nomes, com a primeira letra maiúscula).")
    else:
        st.write("📊 **Pré-visualização dos Dados Originais:**")
        st.dataframe(df.head())
        
        if st.button("Iniciar Geocodificação 🚀"):
            
            # Tratamento de Segurança: Remove espaços, aceita ponto ou vírgula e força a ser número
            lat_limpa = df['Latitude'].astype(str).str.strip().str.replace(',', '.')
            lon_limpa = df['Longitude'].astype(str).str.strip().str.replace(',', '.')
            
            # Se houver texto/letras no lugar de números, converte para vazio (NaN) em vez de quebrar o app
            df['Lat_Tratada'] = pd.to_numeric(lat_limpa, errors='coerce')
            df['Lon_Tratada'] = pd.to_numeric(lon_limpa, errors='coerce')

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
                
                # Regra de segurança: Se a coordenada for inválida ou texto, ele pula a busca
                if pd.isna(lat) or pd.isna(lon):
                    localizacoes.append("Coordenada inválida na planilha")
                    cidades.append("N/A")
                    estados.append("N/A")
                else:
                    try:
                        local = geolocator.reverse((lat, lon))
                        if local:
                            endereco_completo = local.address
                            localizacoes.append(endereco_completo)
                            
                            partes = endereco_completo.split(',')
                            partes = [p.strip() for p in partes]
                            
                            if len(partes) >= 3:
                                estado_com_cep = partes[-2]
                                estado_limpo = re.sub(r'[0-9-]', '', estado_com_cep).strip()
                                cidade = partes[-3]
                                
                                cidades.append(cidade)
                                estados.append(estado_limpo)
                            else:
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
                label="📥 Baixar planilha pronta (.xlsx)",
                data=output.getvalue(),
                file_name="PlanilhaLocalizacao.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

# --- RODAPÉ PROFISSIONAL ---
st.markdown("---") # Cria uma linha divisória bem sutil
st.markdown(
    """
    <div style="text-align: center; color: #888888; padding-top: 10px;">
        <p style="margin-bottom: 2px;">Desenvolvido por <b>Luciano Henriques</b> | Analista de Dados</p>
        <p style="font-size: 12px; margin-top: 0px;">Célula Técnica - Grupo Apisul</p>
    </div>
    """, 
    unsafe_allow_html=True
)