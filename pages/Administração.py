import streamlit as st
import mysql.connector
from datetime import datetime
from time import sleep

conexao = mysql.connector.connect(
    host='localhost',
    username='root',
    password='root',
    database='estacionamento'
)

st.set_page_config(
    page_title='Administração',
    page_icon="🚗"
)


cursor = conexao.cursor()

# Armazenar variáveis para usar em callbacks
if 'qtd_vagas' not in st.session_state:
    st.session_state['qtd_vagas'] = 0


def login_usuario(nome, senha):
    dados = (nome, senha)
    cursor = conexao.cursor(dictionary=True)
    cursor.execute('SELECT nome, senha FROM administrador WHERE nome = %s AND senha = %s', dados)
    usuario = cursor.fetchone()
    conexao.commit()
    return usuario



def clicou_confirmar():
    cursor.execute('SELECT v.numero_vaga FROM vagas v')
    vagas = cursor.fetchall()
    ult_numero_vaga = vagas[-1][0] if vagas else 0

    qtd_vagas = int(st.session_state['qtd_vagas'])

    s = ''
    for num_vaga_nova in range(ult_numero_vaga + 1, ult_numero_vaga + qtd_vagas + 1):
        s += f'({num_vaga_nova}, FALSE),'

    cursor.execute(f'INSERT INTO vagas (numero_vaga, ocupado) VALUES {s[:-1]};')
    conexao.commit()


def clicou_remover_vaga(vaga_numero):
    cursor.execute('DELETE FROM vagas WHERE numero_vaga = %s', (vaga_numero,))
    conexao.commit()



def clicou_liberar_vaga(vaga_numero,id_placa):
    cursor.execute('UPDATE veiculo_estacionado SET hora_saida = %s WHERE numero_vaga_id = %s AND hora_saida IS NULL',
                   (datetime.now(), vaga_numero))
    cursor.execute('UPDATE vagas SET ocupado = FALSE WHERE numero_vaga = %s', (vaga_numero,))
    cursor.execute('INSERT INTO historico_vendas(data_saida) VALUES (current_timestamp())')
    cursor.execute('DELETE FROM veiculos where id = %s', (id_placa,))
    cursor.execute('Delete from veiculo_estacionado where id = %s',(id_placa,))
    conexao.commit()

def apos_login():
    st.header('Vagas Ocupadas')
    cursor.execute('''
        SELECT v.numero_vaga, ve.placa_veiculo_id, ve.hora_entrada
        FROM vagas v
        JOIN veiculo_estacionado ve ON v.numero_vaga = ve.numero_vaga_id
        WHERE ve.hora_saida IS NULL
    ''')
    vagas_ocupadas = cursor.fetchall()
    


    if vagas_ocupadas:
        for index, vaga in enumerate(vagas_ocupadas):
            st.write(f"Vaga: {vaga[0]}")
            st.write(f"ID do veiculo: {vaga[1]}")
            st.write(f"Hora de Entrada: {vaga[2]}")
            if st.button(f'Liberar Vaga {vaga[0]}', key=f'liberar_{index}'):
                clicou_liberar_vaga(vaga[0],vaga[1])
                st.success(f'Vaga {vaga[0]} liberada com sucesso!')
                sleep(2)
                st.rerun()
    else:
        st.write("Nenhuma vaga ocupada no momento.")

    st.header('Adicione uma vaga')
    qtd_vagas = st.number_input('Quantas vagas deseja?', min_value=1)
    st.session_state['qtd_vagas'] = qtd_vagas
    st.button('Confirmar', on_click=clicou_confirmar)

    st.header('Remover Vaga')
    vaga_numero = st.number_input('Número da vaga para remover:', min_value=1)
    if st.button('Remover Vaga'):
        clicou_remover_vaga(vaga_numero)
        st.experimental_rerun()

    st.header('Adicionar Novo Administrador')
    admin_nome = st.text_input('Nome do novo administrador:')
    admin_senha = st.text_input('Senha do novo administrador:', type='password')
    if st.button('Adicionar Administrador'):
        cursor.execute('INSERT INTO administrador (nome, senha) VALUES (%s, %s)', (admin_nome, admin_senha))
        conexao.commit()
        st.success('Novo administrador adicionado!')

    st.header('Histórico de Veículos')
    if st.button('Exibir Histórico de Veículos'):
        cursor.execute('SELECT * FROM historico_vendas')
        historico = cursor.fetchall()
        for hist in historico:
            st.write(f"ID da venda: {hist[0]}")
            st.write(f"Hora de Saída: {hist[1]}")
            st.write(f'Valor pago: {hist[2]}')
            st.write("---")
        if st.button('Esconder Histórico de Veículos'):
            st.experimental_rerun()


st.title('Administração')

if 'authenticated' in st.session_state:
    if st.session_state['authenticated']:
        apos_login()
else:
    st.subheader('Login do Administrador')
    login_nome = st.text_input('Nome: ')
    login_senha = st.text_input('Senha: ', type='password')
    botao_login = st.button('Login')

    if botao_login:
        login = login_usuario(login_nome, login_senha)

        if login:
            st.session_state['authenticated'] = True
            st.session_state['login_nome'] = login['nome']
        else:
            st.error('Nome ou senha incorreto(a).')
            