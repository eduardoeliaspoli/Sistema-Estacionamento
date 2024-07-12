import streamlit as st
import pandas as pd
import mysql.connector

conexao = mysql.connector.connect(
    host='localhost',
    username='root',
    password='root',
    database='estacionamento'
)

cursor = conexao.cursor()

cursor.execute('select * from historico_vendas')
historico = cursor.fetchall
print(historico)

dados = pd.DataFrame({
    "col1": list(range(1,31)),
    "col2": 3
})

st.bar_chart(dados,x="col1",y="col2")