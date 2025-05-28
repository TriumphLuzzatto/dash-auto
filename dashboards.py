import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout='wide')

# Carregar dados
df = pd.read_csv('dados1.csv', encoding='utf-8')

# 🧹 Limpeza dos nomes das colunas (remove quebras, espaços extras, duplicadas)
df.columns = df.columns.str.replace('\n', ' ', regex=False).str.replace('\r', '', regex=False).str.replace('"', '', regex=False)
df.columns = df.columns.str.strip().str.replace(' +', ' ', regex=True)
df = df.loc[:, ~df.columns.duplicated()]  # Remove colunas duplicadas

# Converter coluna DATA para datetime
df['DATA'] = pd.to_datetime(df['DATA'], errors='coerce', dayfirst=True)

# Ordenar por data
df = df.sort_values('DATA')

# Criar coluna MÊS no formato ano-mês
df['MÊS'] = df['DATA'].apply(lambda x: f"{x.year}-{x.month:02}" if pd.notnull(x) else None)

# Filtro de mês na sidebar
month = st.sidebar.selectbox('Selecione o MÊS', df['MÊS'].dropna().unique())

# Filtrar dataframe pelo mês selecionado
df_filtrado = df[df['MÊS'] == month]

# Forçar colunas numéricas a serem realmente numéricas
colunas_numericas = [
    'LEADS NOVOS WHATSAPP', 'LEADS ÚTEIS INSTAGRAM', 'AGENDAMENTOS FEITOS NO DIA WHATSAPP', 'AGENDAMENTOS INSTAGRAM'
]

for coluna in colunas_numericas:
    if coluna in df_filtrado.columns:
        df_filtrado[coluna] = pd.to_numeric(df_filtrado[coluna], errors='coerce').fillna(0)

# Mostrar o dataframe filtrado
st.write(df_filtrado)

# 📊 MÉTRICAS E GRÁFICOS

col1, col2 = st.columns(2)
col3, col4, col5 = st.columns(3)

with col1:
    st.metric("Total Leads WhatsApp", int(df_filtrado['LEADS NOVOS WHATSAPP'].sum()))
    st.bar_chart(df_filtrado.groupby('DATA')['LEADS NOVOS WHATSAPP'].sum(), use_container_width=True)

with col2:
    st.metric("Total Leads Instagram", int(df_filtrado['TOTAL DE LEADS ÚTEIS INSTAGRAM'].sum()))
    st.bar_chart(df_filtrado.groupby('DATA')['TOTAL DE LEADS ÚTEIS INSTAGRAM'].sum(), use_container_width=True)

with col3:
    st.metric("Agendamentos WhatsApp", int(df_filtrado['AGENDAMENTOS FEITOS NO DIA WHATSAPP'].sum()))
    st.line_chart(df_filtrado.groupby('DATA')['AGENDAMENTOS FEITOS NO DIA WHATSAPP'].sum(), use_container_width=True)

with col4:
    st.metric("Agendamentos Instagram", int(df_filtrado['AGENDAMENTOS INSTAGRAM'].sum()))
    st.line_chart(df_filtrado.groupby('DATA')['AGENDAMENTOS INSTAGRAM'].sum(), use_container_width=True)

with col5:
    total_wpp = df_filtrado['LEADS NOVOS WHATSAPP'].sum()
    total_insta = df_filtrado['TOTAL DE LEADS ÚTEIS INSTAGRAM'].sum()
    total_geral = total_wpp + total_insta
    if total_geral > 0:
        perc_wpp = round((total_wpp / total_geral) * 100, 2)
        perc_insta = round((total_insta / total_geral) * 100, 2)
    else:
        perc_wpp = perc_insta = 0

    st.metric("WhatsApp %", f"{perc_wpp}%")
    st.metric("Instagram %", f"{perc_insta}%")

# Gráfico de Pizza - Proporção de Leads WhatsApp e Instagram
labels = ['WhatsApp', 'Instagram']
values = [total_wpp, total_insta]

fig_pizza = px.pie(
    names=labels,
    values=values,
    title='Proporção de Leads - WhatsApp vs. Instagram',
    color_discrete_sequence=px.colors.sequential.RdBu
)

st.plotly_chart(fig_pizza, use_container_width=True)