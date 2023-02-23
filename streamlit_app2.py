import streamlit as st
import requests
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt

# CONSTANTES

NIVEIS_REGIONAIS = ['Distrito', 'Subprefeitura', 'Município']

# FUNCOES

def get_lst_indicadores():

  with requests.get('https://api.observasampa.prefeitura.sp.gov.br/v1/basic/indicadores/') as r:
    return r.json()

def pegar_nome_indicaodr(indicador:dict)->str:

    return indicador['nm_indicador']

def get_ficha_indicador(cod_indicador:int)->dict:

  url = f'https://api.observasampa.prefeitura.sp.gov.br/v1/front_end/ficha_indicador/{cod_indicador}'
  with requests.get(url) as r:
    return r.json()

def filtrar_resultados_regiao(dados:dict, nivel_regional:str)->pd.DataFrame:

  resultados_filtrados = dados['resultados'][nivel_regional]

  return pd.DataFrame(resultados_filtrados)

def filtrar_regioes(df, lst_regioes):

  return df[lst_regioes]

def grafico_linha(df:pd.DataFrame, filtro_regiao:list)->None:

    df = df[filtro_regiao]
    st.line_chart(df)

#@st.cache_resource
def mapa(_geojson:dict):
    fig, ax = plt.subplots()
    ax.axis('off')
    _geojson.plot(ax=ax) #column='resultados', cmap='Blues', legend=True)
    st.pyplot(fig, transparent=False)

# LAYOUT

st.title('Dashboard Oficina Residentes')
st.header('Realizada em fevereiro de 2023')

lst_indicadores = get_lst_indicadores()

indicador_selecionado = st.selectbox('Escolha um indicador', lst_indicadores, format_func = pegar_nome_indicaodr)

cod_indicador = indicador_selecionado['cd_indicador'] 

dados = get_ficha_indicador(cod_indicador)

with st.sidebar:
    markdown_txt = f"""
        ### {dados['nm_indicador']}
        #### Descrição: 
        *{dados['nm_completo_indicador']}*
        """
    st.markdown(markdown_txt)
    col1, col2 = st.columns(2)
    with col1:
        markdown_txt = f"""
        #### Fórmula de cálculo:
        {dados['dc_formula_indicador']}
        """
        st.markdown(markdown_txt)
    with col2:
        
        markdown_txt = f"""
        #### Fonte:
        {dados['tx_fonte_indicador']}
        """
        st.markdown(markdown_txt)
    
    st.image('https://www.prefeitura.sp.gov.br/cidade/secretarias/upload/chamadas/governo_horizontal_fundo_claro-compressed_1665689301.png')


nivel_regional = st.selectbox("Selecione o nível regional", NIVEIS_REGIONAIS)

try:
    resultados_regiao = filtrar_resultados_regiao(dados, nivel_regional)
except KeyError:
    st.warning(f'Esse indicador não possui resultados para o nivel regional {nivel_regional}')
    st.stop()

regioes = resultados_regiao.columns

regioes_selecionadas = st.multiselect('Escolha as regiões de interesse', regioes, default=regioes[0])

grafico_linha(resultados_regiao, regioes_selecionadas)

