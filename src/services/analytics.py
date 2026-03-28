import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

@st.cache_data
def dados_testes():
    np.random.seed(42)
    
    datas = [datetime.today() - timedelta(days=i) for i in range(30)]
    locais = ["Hospital das Clínicas", "Hospital de Base", "Hospital Anchieta", "Clínica Particular"]
    tipos = ["Primeira Consulta", "Retorno", "Procedimento", "Plantão 12h"]

    dados = []

    for _ in range(150):
        dados.append({
            "data": np.random.choice(datas),
            "local": np.random.choice(locais),
            "tipo": np.random.choice(tipos),
            "valor": np.random.uniform(150.0, 1500.0)
        })
    df = pd.DataFrame(dados)

    df.loc[df['tipo'] == 'Retorno' 'valor'] = 0.0
    df.loc[df['tipo'] == 'Plantão 12h' 'valor'] = 1200.0
    
    return df