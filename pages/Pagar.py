import streamlit as st
import mysql.connector
import requests
from PIL import Image
from io import BytesIO
from datetime import datetime, timedelta

st.set_page_config(
    page_title='Estacionamento',
    page_icon="🚗"
)


# Função para gerar QR Code usando a API do goqr.me
def gerar_qr_code_pix(dados):
    url = f"https://api.qrserver.com/v1/create-qr-code/?size=350x350&data={dados}"
    resposta = requests.get(url)
    if resposta.status_code == 200:
        return Image.open(BytesIO(resposta.content))
    else:
        st.error("Erro ao gerar o QR Code")
        return None


# Função para conectar ao banco de dados
def conectar_bd():
    return mysql.connector.connect(
        host='localhost',
        user='root',
        password='root',
        database='estacionamento'
    )


# Função para calcular o tempo estacionado
def calcular_tempo_estacionado(hora_entrada, hora_saida):
    tempo_estacionado = hora_saida - hora_entrada
    horas_estacionado = tempo_estacionado.total_seconds() / 3600
    return horas_estacionado


st.title('Pagamento')

# Controlar se os dados da busca foram exibidos
mostrar_dados_busca = True

# Controlar se o botão de gerar QR Code foi clicado
gerar_qr_code = False

# Escolha da forma de busca
opcao_busca = st.radio("Selecione como deseja buscar:", ("Placa do Veículo", "Número da Vaga"))

if opcao_busca == "Placa do Veículo":
    informacoes_veiculo = st.text_input('Informe a placa cadastrada', placeholder='Ex: AAA1A11')
else:
    informacoes_veiculo = st.number_input('Informe o número da vaga ocupada', min_value=1, step=1)

# Botão para buscar dados
if st.button('Buscar'):
    mostrar_dados_busca = False  # Ocultar dados da busca após clicar em Buscar

    conexao = conectar_bd()
    cursor = conexao.cursor()

    if opcao_busca == "Placa do Veículo":
        cursor.execute("SELECT * FROM veiculos WHERE placa_veiculo = %s", (informacoes_veiculo,))
    else:
        cursor.execute("""
            SELECT veiculos.placa_veiculo
            FROM veiculos
            INNER JOIN veiculo_estacionado ON veiculos.placa_veiculo = veiculo_estacionado.placa_veiculo
            WHERE veiculo_estacionado.numero_vaga = %s
            ORDER BY veiculo_estacionado.hora_entrada DESC LIMIT 1
        """, (informacoes_veiculo,))

    veiculo = cursor.fetchone()

    if veiculo:
        if opcao_busca == "Placa do Veículo":
            st.write(f"Código do veículo: {veiculo[0]}")
            st.write(f"Placa cadastrada: {veiculo[1]}")
        else:
            st.write(f"Placa do veículo: {veiculo[0]}")

        if opcao_busca == "Placa do Veículo":
            cursor.execute("""
                SELECT veiculo_estacionado.numero_vaga, veiculo_estacionado.hora_entrada, veiculo_estacionado.hora_saida
                FROM veiculo_estacionado
                WHERE veiculo_estacionado.placa_veiculo = %s
                ORDER BY veiculo_estacionado.hora_entrada DESC LIMIT 1
            """, (informacoes_veiculo,))
        else:
            cursor.execute("""
                SELECT veiculo_estacionado.numero_vaga, veiculo_estacionado.hora_entrada, veiculo_estacionado.hora_saida
                FROM veiculo_estacionado
                WHERE veiculo_estacionado.numero_vaga = %s
                ORDER BY veiculo_estacionado.hora_entrada DESC LIMIT 1
            """, (informacoes_veiculo,))

        estacionamento = cursor.fetchone()

        if estacionamento:
            numero_vaga, hora_entrada, hora_saida = estacionamento

            st.write(f"Vaga: {numero_vaga}")
            st.write(f"Hora de Entrada: {hora_entrada.strftime('%Y-%m-%d %H:%M:%S')}")

            if hora_saida:
                st.warning('Veículo não está mais estacionado.')
                st.write(f"Hora de Saída: {hora_saida.strftime('%Y-%m-%d %H:%M:%S')}")
            else:
                st.success('Veículo está estacionado atualmente.')

            # Guardar os dados do veículo e estacionamento no session_state
            st.session_state['veiculo'] = veiculo
            st.session_state['estacionamento'] = estacionamento
        else:
            st.warning('Veículo não está estacionado no momento.')
    else:
        st.warning('Dados não encontrados. Por favor, verifique as informações informadas.')

    # Fechar cursor e conexão com o banco de dados
    cursor.close()
    conexao.close()

# Bloco separado para gerar QR Code e exibir informações para pagamento
if 'veiculo' in st.session_state and 'estacionamento' in st.session_state:
    veiculo = st.session_state['veiculo']
    estacionamento = st.session_state['estacionamento']
    numero_vaga, hora_entrada, hora_saida = estacionamento

    if not gerar_qr_code:
        gerar_qr_code = st.button('Gerar QR Code')

    if gerar_qr_code and not hora_saida:  # Veículo está atualmente estacionado
        hora_saida = datetime.now()
        conexao = conectar_bd()
        cursor = conexao.cursor()
        cursor.execute("""
            UPDATE veiculo_estacionado
            SET hora_saida = %s
            WHERE placa_veiculo = %s AND hora_saida IS NULL
        """, (hora_saida, veiculo[1] if opcao_busca == "Placa do Veículo" else veiculo[0]))
        conexao.commit()

        hora_saida_formatada = hora_saida.strftime('%Y-%m-%d %H:%M:%S')
        horas_estacionado = calcular_tempo_estacionado(hora_entrada, hora_saida)
        valor_a_pagar = round(horas_estacionado * 5, 2)

        # Exibir apenas as informações para pagamento e o QR code
        st.write("\n\n**Informações para pagamento:**")
        st.write(f"- Placa do veículo: {veiculo[1] if opcao_busca == 'Placa do Veículo' else veiculo[0]}")
        st.write(f"- Vaga: {numero_vaga}")
        st.write(f"- Hora de Entrada: {hora_entrada.strftime('%Y-%m-%d %H:%M:%S')}")
        st.write(f"- Hora de Saída: {hora_saida_formatada}")
        st.write(f"- Tempo Estacionado: {horas_estacionado:.2f} horas")
        st.write(f"- Valor a Pagar: R$ {valor_a_pagar:.2f}")

        dados_qr_code = f"""
Veículo: {veiculo[1] if opcao_busca == "Placa do Veículo" else veiculo[0]} 

Vaga: {numero_vaga} 

Hora de Entrada: {hora_entrada.strftime('%Y-%m-%d %H:%M:%S')}

Hora de Saída: {hora_saida_formatada}

Tempo Estacionado: {horas_estacionado:.2f} horas

Valor a Pagar: R$ {valor_a_pagar:.2f}
"""
        qr_code_img = gerar_qr_code_pix(dados_qr_code)
        if qr_code_img:
            st.image(qr_code_img, caption='QR Code com informações do veículo, vaga e valor a pagar')

            # Atualizar vaga para não ocupada
            cursor.execute('UPDATE vagas SET vaga_ocupada = FALSE WHERE numero_vaga = %s', (numero_vaga,))
            conexao.commit()

        # Fechar cursor e conexão com o banco de dados
        cursor.close()
        conexao.close()

        # Após gerar o QR Code, resetar o estado do botão para gerar novamente
        gerar_qr_code = False