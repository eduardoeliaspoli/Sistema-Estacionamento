import streamlit as st
import mysql.connector
from time import sleep


st.set_page_config(
    page_title='Estacionamento ',
    page_icon="🚗"
)

with open(".\style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


st.title('Página de login')

# Faz a conexão com o banco de dados
conexao = mysql.connector.connect(
    host='localhost',
    username='root',
    password='root',
    database='estacionamento'
)
cursor = conexao.cursor()


st.header('Informar placa')
informar_placa = st.text_input('Informe a placa do veiculo', placeholder='Ex: AAA1A11')
col1, col2, col3 = st.columns(3)
i = 0

# CONSULTA AS VAGAS
cursor.execute('SELECT v.numero_vaga, v.ocupado FROM vagas v where ocupado = false')

# CARREGA A VARIÁVEL 'vagas' COM AS VAGAS CONSULTADAS. 'vagas' VEM COMO LISTA DE TUPLAS
vagas = cursor.fetchall()
print(vagas)

if 'indice_botao' not in st.session_state:
    st.session_state['indice_botao'] = 0

def clique_botao(indice: int):
    st.session_state['indice_botao'] = indice

lista_botoes = []
col1, col2, col3 = st.columns(3)
colunas = [col1, col2, col3]
var_controle = 0
for vaga in vagas:
    with colunas[var_controle]:
        lista_botoes.append(
            st.button(
                f'Vaga {vaga[0]}',
                key=f'{vaga[0]}', 
                on_click=clique_botao, 
                args=[int(vaga[0])]
            ))
        print(vaga[0])
    var_controle = (var_controle + 1) % 3

for botao_bool in lista_botoes:
    if botao_bool:
        st.write(f'{st.session_state["indice_botao"]}, tipo: {type(st.session_state["indice_botao"])}')
        
botao_enviar = st.button('Enviar')
if botao_enviar and informar_placa != '':
    cursor.execute('INSERT INTO veiculos(placa_veiculo) VALUES (%s)', (informar_placa,))
    cursor.commit()
    cursor.execute(f'UPDATE vagas set ocupado = TRUE where numero_vaga = {st.session_state["indice_botao"]}')
    cursor.commit()
    cursor.execute(
        'INSERT INTO veiculo_estacionado(placa_veiculo,numero_vaga,hora_entrada) VALUES (%s,%s,current_timestamp())',
        (informar_placa, st.session_state["indice_botao"],))
    cursor.commit()
    conexao.commit()
    st.success(f'Veiculo com a placa {informar_placa} cadastrado na vaga {st.session_state["indice_botao"]} com sucesso!')
    sleep(2)
    st.rerun()