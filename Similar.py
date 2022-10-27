import streamlit as st
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt



lista_anos = []
for ano in range(2018,2022):
  lista_anos.append(str(ano))
  
lista_ligas = ['BRA1','BRA2']

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


vars_abs = ['Golos','Golos esperados','Assistências','Assistências esperadas','Cortes de carrinho ajust. à posse',
            'Cartões amarelos','Cartões vermelhos','Golos sem ser por penálti','Golos de cabeça','Remate',
            'Comprimento médio de passes, m','Comprimento médio de passes longos, m','Golos sofridos','Remates sofridos',
            'Jogos sem sofrer golos','Golos sofridos esperados','Golos expectáveis defendidos','Penaltis marcados']




st.subheader('Resumo da Base de Dados')
st.write(base[['Jogador','Equipe atual','Equipe no ano','Minutos jogados:','Ano','Liga']])

st.subheader('Busca Rápida')
pesq_rap = st.text_input('Digite o nome desejado:')

lista_results = []
nomes = pd.unique(base.Jogador).tolist()
t = 0
while t<len(nomes):
  if pesq_rap in nomes[t]:
    lista_results.append(nomes[t])
  t += 1

st.write(base[base.Jogador.isin(lista_results)][['Jogador','Equipe atual','Equipe no ano','Minutos jogados:','Ano','Liga']])

st.subheader('Jogador 1')
nome_busca1 = st.text_input("Nome do primeiro jogador:")

if len(base[base.Jogador==nome_busca1]) == 0:
  st.write("Favor inserir o nome do jogador igual no WyScout")

elif len(pd.unique(base[base.Jogador==nome_busca1]['Equipe atual']))>1:
  st.write("Mais de um jogador disponível com este nome, favor inserir o clube atual do jogador desejado.")
  st.write(base[base.Jogador==nome_busca1][['Jogador','Equipe atual','Equipe no ano','Minutos jogados:','Ano','Liga']])
  clube1 = st.text_input("Clube do primeiro jogador:")
  if len(pd.unique(base[(base.Jogador==nome_busca1)&(base["Equipe atual"] == clube1)]['Idade']))>1:
    st.write("Mais de um jogador disponível com este nome/clube, favor inserir a idade atual do jogador desejado.")
    st.write(base[(base.Jogador==nome_busca1)&(base["Equipe atual"] == clube1)][['Jogador','Equipe atual','Equipe no ano','Minutos jogados:','Ano','Liga']])
    idade1 = int(st.text_input("Idade do primeiro jogador:"))
    st.write("Tabela resumo do jogador desejado:")
    base1 = base[(base.Jogador==nome_busca1)&(base["Equipe atual"] == clube1)&(base.Idade==idade1)]
    st.write(base1[['Jogador','Equipe atual','Equipe no ano','Minutos jogados:','Ano','Liga']])
  else:
    base1 = base[(base.Jogador==nome_busca1)&(base["Equipe atual"] == clube1)]
    st.write("Tabela resumo do jogador desejado:")
    st.write(base1[['Jogador','Equipe atual','Equipe no ano','Minutos jogados:','Ano','Liga']])
                 
else:
    base1 = base[base.Jogador == nome_busca1]
    st.write("Tabela resumo do jogador desejado:")
    st.write(base1[['Jogador','Equipe atual','Equipe no ano','Minutos jogados:','Ano','Liga']])

try:
  base1 = base1.assign(ID = 1)
except:
  st.write('...')
