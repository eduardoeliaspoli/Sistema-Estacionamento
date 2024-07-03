import streamlit as st
with st.form('form-pagar', clear_on_submit=True):
        # Cria o input para o usuario informar seu códico do veiculo para poder fazer o pagamento do estacionamento
    st.header('Tela de pagamento')
    codigo_saida = st.number_input('Informe seu códico do veiculo', 1, 10000)
    botao_pagar = st.form_submit_button('Enviar')
    if botao_pagar and len(codigo_saida) == 7:
        st.image('qrcode_openai.png')
# row1 = st.columns(4)
# row2 = st.columns(4)
# row3 = st.columns(4)
#
# tile = []*12
#
# i = 0
# for col in row1 + row2 + row3:
#     tile[i] = col.container(height=150)
#     with tile[i]:
#         bt = st.button('BUTÃO')
#     tile +=1