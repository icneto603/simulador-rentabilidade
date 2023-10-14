# Importação das biliotecas

import pandas as pd
import yfinance as yf
import datetime as dt
import streamlit as st
import math

# Título da página web
st.set_page_config(
    page_title="Simulador de Rentabilidade SENAI v01", layout="wide")

# Título da aplicação

st.title(":violet[Simulador de Rentabilidade]")
st.subheader("Monitorar preços de ativos em tempo real e simular lucros.")

# Definir a data final para atual
end_date = dt.datetime.today()

# Fazer o cálculo a cada 30 dias
start_date = dt.datetime(end_date.year-1, end_date.month, end_date.day)

# Lista de ativos disponíveis para consulta
lista_ativos = ["PETR4.SA", "VALE3.SA", "VIVT3.SA", "BBAS3.SA", "BBSE3.SA", "VISC11.SA", "VGIP11.SA", "HGLG11.SA",
                "RECR11.SA", "TRXF11.SA", "EGIE3.SA", "TAEE11.SA"]

# Container de seleção dos ativos e datas.
with st.container():
    st.write(
        ":violet[Escolha o ativo, a data incial e final do período para análise.]")

    # Definir a quantidade de colunas
    col1, col2, col3 = st.columns(3)

    # Exibição de cada coluna
    with col1:
        ativo = st.selectbox("Ativo:", options=lista_ativos)
    with col2:
        data_inicial = st.date_input("Data inicial:", start_date, format="DD/MM/YYYY")
    with col3:
        data_final = st.date_input("Data final:", end_date, format="DD/MM/YYYY")

# Gerar dataframe com os dados selecionados pelo usuário
hist_ativos = yf.download(
    tickers=ativo, start=data_inicial, end=data_final, actions=True)

# Data da última atualização do preço do ativo
ult_atualizacao = hist_ativos.index.max()

# Fechamento do último pregão da bolsa (base de cálculo é o preço de abertura)
ult_cotacao = round(hist_ativos.loc[hist_ativos.index.max(), "Open"], 2)

# Menor cotacao do período selecionado
menor_cotacao = round(hist_ativos["Open"].min(), 2)

# Maior cotacao do período selecionado
maior_cotacao = round(hist_ativos["Open"].max(), 2)

# Encontrar a primeira cotação
prim_cotacao = round(hist_ativos.loc[hist_ativos.index.min(), "Open"], 2)

# Variação da cotação no período
vc_periodo = round(((ult_cotacao - prim_cotacao) / prim_cotacao) * 100, 2)

# Filtrar os pagamento maiores que zero
hist_dividendos = hist_ativos[hist_ativos["Dividends"] > 0]

# Métricas para calcular os dividendos
dividendo = hist_dividendos["Dividends"].mean()
dividendo_soma = hist_dividendos["Dividends"].sum()
qtde_pg_div = hist_dividendos["Dividends"].count()
dividen_max = hist_dividendos["Dividends"].max()
dividen_min = hist_dividendos["Dividends"].min()

# Preço/Lucro - comparar a cotação de uma empresa com o seu lucro por ação (quantos anos o retorno?)
preco_sl = ult_cotacao / dividendo_soma

# Filtrar os últimos pregões
dy_dm = hist_ativos.tail(250)

# Somar os dividendo pagos
dy_dm_soma = dy_dm["Dividends"].sum()

# Calcular o Divend Yield dos últimos 12 meses
dy = round(dy_dm_soma/ult_cotacao, 4)*100

st.divider()
# Container para exibir os principais indicadores
with st.container():

    st.subheader(f":violet[Principais Indicadores:] {ativo}")

    # Definição das colunas
    col11, col12, col13, col14, col15 = st.columns(5)

    with col11:
        st.metric(f"Última atualização - {ult_atualizacao} ",
                  " R$ {:,.2f}".format(ult_cotacao), f"{vc_periodo}%")

    with col12:
        st.metric(f"Menor cotação do período: ",
                  " R$ {:,.2f}".format(menor_cotacao))

    with col13:
        st.metric(f"Maior cotação do período: ",
                  " R$ {:,.2f}".format(maior_cotacao))

    with col14:
        st.metric(f"Preço/Lucro ", " {:,.2f}".format(preco_sl))

    with col15:
        st.metric(f"Dividend Yield", "  {:,.2f} %".format(dy))

st.divider()

# Container para exibir informações sobre dividendos
with st.container():
    st.subheader(":violet[Mapa de Dividendos]")

    # Definição das colunas
    col5, col6, col7, col8 = st.columns(4)

    with col5:
        st.metric(f"Pagamentos no período: ", " {:,.0f}".format(qtde_pg_div))
    with col6:
        st.metric(f"Pagamento mínimo:", "R$ {:,.2f}".format(dividen_min))

    with col7:
        st.metric(f"Pagamento máximo:", "R$ {:,.2f}".format(dividen_max))

    with col8:
        st.metric(f"Total:", " R$ {:,.2f}".format(dividendo_soma))

# Divisão do conteúdo
st.divider()

# Container para exbir informações sobre o histórico de atualizações do ativo
with st.container():

    # Definição das colunas
    col16, col17 = st.columns(2)

    with col16:
        st.caption(f":violet[Histórico de valorização de] {ativo}:")
        st.area_chart(hist_ativos["Open"], color=[
                      "#5900b3"], use_container_width=True)

    with col17:
        st.caption(f":violet[Histórico de dividendos de] {ativo}:")
        st.bar_chart(hist_dividendos["Dividends"], color=[
                     "#5900b3"], use_container_width=True)

st.divider()
# Container para exibir o simuador de investimento
with st.container():

    st.subheader(":violet[Simulador de Investimento]")
    col31, col32, col33, col34 = st.columns(4)
    with col31:
        # Solicitar o valor para o usuário
        valor_aporte = st.number_input("Valor do Aporte:")

    # Mpetricas para calcular a rentabilidade
    compra = valor_aporte / prim_cotacao
    lucro = compra * dividendo_soma
    saldo_val = lucro + (compra*ult_cotacao)

    # Calcular a rentabilidade do período
    dif_rent_periodo = saldo_val - valor_aporte
    rent_periodo = float("nan")
    rent_periodo = (dif_rent_periodo/valor_aporte)*100

    # Garantir que aparecerá 0 se o usário não informar o valor do aporte
    if math.isnan(rent_periodo):
        rent_periodo = 0

    # Definição das colunas
    col21, col22, col23, col24 = st.columns(4)

    with col21:
        st.metric(f"Valor pago em dividendos no período: ",
                  " R$ {:,.2f}".format(lucro))

    with col22:
        st.metric(f"Quantidade de ações: ", " {:,.0f} Ações".format(compra))

    with col23:
        st.metric(f"Saldo com a valorização do ativo:",
                  " R$ {:,.2f}".format(saldo_val))

    with col24:
        st.metric(f"Rentabilidade no período",
                  "  {:,.2f} %".format(rent_periodo))
    st.divider()
    st.title("")
    col41, col42, col43 = st.columns(3)
    with col42:
        st.caption(":violet[Copyright © 2023 por Ivo C. Neto e Otávio A. Seixas - Out/2023]")


