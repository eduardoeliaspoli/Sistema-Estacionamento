import streamlit as st
import mysql.connector

st.set_page_config(
    page_title='Mostrar informações',
    page_icon="🚗"
)


conexao = mysql.connector.connect(
    host='localhost',
    user='root',
    password='root',
    database='estacionamento'
)

cursor = conexao.cursor()

st.title('Página dos dados')

with st.form('form-visualizar-dados', clear_on_submit=True):

    informacoes_veiculo = st.text_input('Informe a placa cadastrada', placeholder='Ex: AAA1A11')
    botao_dados = st.form_submit_button('Enviar')

    if botao_dados:

        cursor.execute("SELECT * FROM veiculos WHERE placa_veiculo = %s", (informacoes_veiculo,))
        veiculo = cursor.fetchone()

        if veiculo:
            st.write(f"Código do veículo: {veiculo[0]}")
            st.write(f"Placa cadastrada: {veiculo[1]}")

            
            cursor.execute("""
                SELECT veiculo_estacionado.numero_vaga_id, veiculo_estacionado.hora_entrada
                FROM veiculo_estacionado
                WHERE veiculo_estacionado.placa_veiculo_id = %s
                ORDER BY veiculo_estacionado.hora_entrada DESC LIMIT 1
            """, (veiculo[0],))
            estacionamento = cursor.fetchone()

            if estacionamento:
                st.write(f"Vaga: {estacionamento[0]}")
                st.write(f"Hora de Entrada: {estacionamento[1]}")
            else:
                st.warning('Veículo não está estacionado no momento.')
        else:
            st.warning('Placa não encontrada. Por favor, verifique os dados informados.')

cursor.close()
conexao.close()