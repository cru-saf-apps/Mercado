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


ano1min = int(np.nanmin(base1.Ano))
ano1max = int(np.nanmax(base1.Ano))

if ano1min < ano1max:
  anos1 = st.slider('Anos analisados para '+nome_busca1,ano1min, ano1max, (ano1min, ano1max))
else:
  st.write(nome_busca1 + " somente disponível em "+str(ano1min))
  anos1 = [ano1min,ano1max]

df = base1[(base1.Ano>=anos1[0])&(base1.Ano<=anos1[1])]

st.write(df)


st.subheader("Variáveis para comparação")
vars = st.multiselect(label = 'Selecione as variáveis desejadas',options=df.columns[9:])
lista_vars = ['ID','Jogador','Pé','Altura','Equipe atual','Equipe no ano','Liga','Posição','Idade']
for var in vars:
  lista_vars.append(str(var))

df_comp = df[lista_vars].copy()

st.write(df_comp)


lista_ranges = []

for coluna in df_comp.columns[9:]:
  if coluna in vars_abs:
    top = df_comp[coluna].sum()
  else:
    top = df_comp[coluna].mean()

  lista_ranges.append((0.85*np.nanmin(df_comp[coluna]),top*1.15))

def _invert(x, limits):
    """inverts a value x on a scale from
    limits[0] to limits[1]"""
    return limits[1] - (x - limits[0])

def _scale_data(data, ranges):
    """scales data[1:] to ranges[0],
    inverts if the scale is reversed"""
    for d, (y1, y2) in zip(data[1:], ranges[1:]):
        assert (y1 <= d <= y2) or (y2 <= d <= y1)
    x1, x2 = ranges[0]
    d = data[0]
    if x1 > x2:
        d = _invert(d, (x1, x2))
        x1, x2 = x2, x1
    sdata = [d]
    for d, (y1, y2) in zip(data[1:], ranges[1:]):
        if y1 > y2:
            d = _invert(d, (y1, y2))
            y1, y2 = y2, y1
        sdata.append((d-y1) / (y2-y1) 
                     * (x2 - x1) + x1)
    return sdata

class ComplexRadar():
    def __init__(self, fig, variables, ranges,
                 n_ordinate_levels=6):
        angles = np.arange(0, 360, 360./len(variables))

        axes = [fig.add_axes([0.1,0.1,0.9,0.9],polar=True,
                label = "axes{}".format(i)) 
                for i in range(len(variables))]
        l, text = axes[0].set_thetagrids(angles, 
                                         labels=variables)
        [txt.set_rotation(angle-90) for txt, angle 
             in zip(text, angles)]
        for ax in axes[1:]:
            ax.patch.set_visible(False)
            ax.grid("off")
            ax.xaxis.set_visible(False)
        for i, ax in enumerate(axes):
            grid = np.linspace(*ranges[i], 
                               num=n_ordinate_levels)
            gridlabel = ["{}".format(round(x,2)) 
                         for x in grid]
            if ranges[i][0] > ranges[i][1]:
                grid = grid[::-1] # hack to invert grid
                          # gridlabels aren't reversed
            gridlabel[0] = "" # clean up origin
            ax.set_rgrids(grid, labels=gridlabel,
                         angle=angles[i])
            #ax.spines["polar"].set_visible(False)
            ax.set_ylim(*ranges[i])
        # variables for plotting
        self.angle = np.deg2rad(np.r_[angles, angles[0]])
        self.ranges = ranges
        self.ax = axes[0]
    def plot(self, data, *args, **kw):
        sdata = _scale_data(data, self.ranges)
        self.ax.plot(self.angle, np.r_[sdata, sdata[0]], *args, **kw)
    def fill(self, data, *args, **kw):
        sdata = _scale_data(data, self.ranges)
        self.ax.fill(self.angle, np.r_[sdata, sdata[0]], *args, **kw)

categorias = lista_vars[9:]

fig = plt.figure(figsize = (8,8))

radar = ComplexRadar(fig,categorias,lista_ranges)

nome = df_comp['Jogador'].tolist()[0]
if df_comp['Pé'].tolist()[0] == 'direito':
  pe = 'Destro'
elif df_comp['Pé'].tolist()[0] == 'esquerdo':
  pe = 'Canhoto'
elif df_comp['Pé'].tolist()[0] == 'ambos':
  pe = 'Ambidestro'
else:
  pe = 'Desconhecido'

altura = df_comp['Altura'].tolist()[0]

aux_df = df_comp.loc[:, df_comp.columns != 'Jogador']
aux_df = aux_df.loc[:, aux_df.columns != 'Equipe atual']
aux_df = aux_df.loc[:, aux_df.columns != 'Equipe no ano']
aux_df = aux_df.loc[:, aux_df.columns != 'Posição']
aux_df = aux_df.loc[:, aux_df.columns != 'Idade']
aux_df = aux_df.loc[:, aux_df.columns != 'ID']
aux_df = aux_df.loc[:, aux_df.columns != 'Liga']
aux_df = aux_df.loc[:, aux_df.columns != 'Pé']
aux_df = aux_df.loc[:, aux_df.columns != 'Altura']

aux_df = aux_df.reset_index(drop=True)

lista_valores = []

for coluna in aux_df.columns:
  if coluna in vars_abs:
    lista_valores.append(aux_df[coluna].sum())
  else:
    lista_valores.append(aux_df[coluna].mean())

legenda = nome + " (" + str(altura) +"cm; Pé: "+pe+")"
radar.plot(lista_valores,label=legenda)


fig.legend()

st.subheader("Radar de Desempenho\n"+nome_busca1 + " ("+str(anos1[0])+" a "+str(anos1[1]) + ")")
st.pyplot(fig)


cols_interesse = df_comp.columns.tolist()[1:]
base_comp = base[cols_interesse].copy()

st.write(base_comp)

df_jogs = base_comp.drop_duplicates(subset=['Jogador','Equipe atual']).reset_index(drop=True)

st.write(df_jogs)

df_stats = base_comp[base_comp.columns.tolist()[8:]].copy().subtract(lista_valores)
v = 0
for coluna in categorias:
  df_stats[coluna] = df_stats[coluna]/lista_valores[v]
  v += 1

df_stats['Jogador'] = base_comp['Jogador']
df_stats['Equipe atual'] = base_comp['Equipe atual']

st.write(df_stats)

df_final = df_jogs[['Jogador','Equipe atual']].copy()
df_final['Media'] = ""

t = 0
while t < len(df_jogs):
  aux_df = df_stats[(df_stats.Jogador == df_jogs.Jogador[t])&(df_stats['Equipe atual']==df_jogs['Equipe atual'][t])]

  lista_medias = []
  for coluna in aux_df.columns.tolist()[8:]:
    media = aux_df[coluna].mean()
    lista_medias.append(media)

  df_final['Media'][t] = sum(lista_medias)/len(lista_medias)
  t += 1


st.write(df_final)


