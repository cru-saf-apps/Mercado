import streamlit as st
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt


@st.cache
def load_basews(lista_anos,lista_ligas):
  base = pd.DataFrame()
  for ano in lista_anos:
    for liga in lista_ligas:
      for item in range(1,3):
        arquivo = str(liga)+'-'+ano+'-'+str(item)+'.csv'
        df = pd.read_csv(arquivo,sep=';',decimal=',')
        df['Ano'] = int(ano)
        df['Liga'] = liga
        base = base.append(df).drop_duplicates().reset_index(drop=True)

  base = base.rename(columns={"Equipa dentro de um período de tempo seleccionado":"Equipe no ano","Equipa":"Equipe atual"})
  base = base.reset_index(drop=True)
  
  return base

lista_anos = []
for ano in range(2018,2022):
  lista_anos.append(str(ano))
  
lista_ligas = ['BRA1','BRA2']

base = load_basews(lista_anos,lista_ligas)
