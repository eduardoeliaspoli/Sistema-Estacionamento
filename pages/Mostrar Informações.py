import streamlit as st

col1, col2, col3 = st.columns(3)
tiles = list(range(12))
botoes = list(range(12))
i = 0
with col1:
    for i in range(3):
        tiles[i] = st.container(height=150)
        with tiles[i]:
            botoes[i] = st.write(f'Vaga {i + 1}', key=f'bt-c1-{i}')
        i += 1
with col2:
    for i in range(3):
        tiles[i] = st.container(height=150)
        with tiles[i]:
            botoes[i] = st.write(f'Vaga {i + 4}', key=f'bt-c2-{i}')
        i += 1
with col3:
    for i in range(3):
        tiles[i] = st.container(height=150)
        with tiles[i]:
            botoes[i] = st.write(f'Vaga {i + 7}', key=f'bt-c3-{i}')
        i += 1