import streamlit as st
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt





lista_anos = ['2020','2021']

lista_ligas = ['BRA1','BRA2','ARG1']

peso_ligas = {'BRA1':1, 'BRA2':0.5,'ARG1':0.9}

@st.cache
def gen_base(lista_anos, lista_ligas):
    base = pd.DataFrame()
    for liga in lista_ligas:
        for ano in lista_anos:
            for num in range(1,3):
                arquivo = liga+'-'+str(ano)+'-'+str(num)+'.csv'
                df = pd.read_csv(arquivo,sep=';',decimal=',')
                df['Ano'] = int(ano)
                df['Liga'] = liga
                base = pd.concat([base,df]).drop_duplicates().reset_index(drop=True)

    base = base.rename(columns={"Equipa dentro de um período de tempo seleccionado":"Equipe no ano",
                                "Equipa":"Equipe atual","Minutos jogados:":"Minutos"})
    
    base = base.dropna(subset=['Posição'])
    base = base.reset_index(drop=True)        

    cols_base = base.columns[-2:].tolist()
    for item in base.columns[:-2].tolist():
        cols_base.append(item)
    base = base[cols_base]
    
    return base

base = gen_base(lista_anos, lista_ligas)

vars_info = ['Ano','Liga','Jogador','Equipe atual','Equipe no ano','Posição','Idade','Valor de mercado',
             'Contrato termina','Naturalidade','País de nacionalidade','Pé','Altura','Peso','Emprestado']


vars_abs = ['Minutos','Golos','Golos esperados','Assistências','Assistências esperadas','Cortes de carrinho ajust. à posse',
            'Cartões amarelos','Cartões vermelhos','Golos sem ser por penálti','Golos de cabeça','Remate',
            'Comprimento médio de passes, m','Comprimento médio de passes longos, m','Golos sofridos','Remates sofridos',
            'Jogos sem sofrer golos','Golos sofridos esperados','Golos expectáveis defendidos','Penaltis marcados']


ano_min = min(base.Ano)
ano_max = max(base.Ano)

peso_min = 0.25
peso_max = (1-peso_min)

posicoes = ['Goleiro', 'Lat. Direito', 'Lat. Esquerdo', 'Zagueiro', 'Médio Defensivo', 
            'Médio Box to Box', 'Médio Ofensivo', 'Meia', 'Extremo Direito',
            'Extremo Esquerdo', 'Centroavante', 'Segundo Atacante']


dic_posicoes = {'Goleiro':['GK'],
                'Lat. Direito':['RB'],
                'Lat. Esquerdo':['LB'],
                'Zagueiro': ['CB', 'RCB', 'LCB'],
               'Médio Defensivo':['RDMF', 'LDMF', 'DMF'],
                'Médio Box to Box':['LCMF', 'RCMF', 'CMF'],
               'Médio Ofensivo': ['LCMF', 'RCMF', 'CMF', 'AMF', 'RAMF', 'LAMF'],
                'Meia': ['AMF', 'RAMF', 'LAMF'],
               'Extremo Direito': ['RW', 'RAMF', 'RWF'],
               'Extremo Esquerdo': ['LW', 'LAMF', 'LWF'],
               'Centroavante': ['CF'],
               'Segundo Atacante': ['CF', 'AMF']}

pos_select = st.multiselect('Quais posições entram no ranking?',options=posicoes)


lista_pos_select = []
for item in pos_select:
    lista_pos_select.append(item)

    
lista_selec = []
for coluna in base.columns.tolist():
  if coluna not in vars_info:
    if coluna != 'Minutos':
      lista_selec.append(coluna)    

vars_select = st.multiselect("Selecione variáveis para definição de ranking",options=lista_selec)

vars_comp = ['Minutos']
vars_comp.extend(vars_select)

var = vars_info.copy()
var.extend(vars_comp)


''' começo da criação da base de dados a ser usada para ranking'''
'''precisa diferenciar por liga'''

@st.cache
def gen_base2(base):
    base2 = pd.DataFrame()

    for liga in pd.unique(base.Liga):
        base_liga = base[base.Liga == liga]
        for ano in pd.unique(base_liga.Ano):
            base_ano = base_liga[base_liga.Ano == ano]

            for coluna in base_ano.columns.tolist():
                if coluna not in vars_info:
                    base_ano[coluna] = (base_ano[coluna]-np.nanmin(base_ano[coluna]))/(np.nanmax(base_ano[coluna])-np.nanmin(base_ano[coluna]))
                else:
                    base_ano[coluna] = base_ano[coluna]

            base2 = pd.concat([base2,base_ano])
            
    return base2
        
        
base2 = gen_base2(base)


@st.cache
def base2_pos(base2, lista_pos_select):
    lista_posicoes = []
    for pos in lista_pos_select:
        lista_posicoes.extend(dic_posicoes[pos])
    lista_posicoes = list(set(lista_posicoes))
    t = 0
    while t < len(base2):
        lista_teste = []
        for pos in base2['Posição'][t].split(','):
            lista_teste.append(pos.strip())
        cont = 0
        for item in lista_teste:
            if cont != 1:
                if item in lista_posicoes:
                    cont = 1
                    continue
            else:
                continue
        if cont == 0:
            base2 = base2.drop(t)
            base2 = base2.reset_index(drop = True)
        else:
            t += 1
    return base2

base2 = base2_pos(base2, lista_pos_select)

st.write(base2)



df_rank = base2[var].copy()

df_rank['Media'] = df_rank[vars_comp].mean(axis=1)
df_rank['SD'] = df_rank[vars_comp].std(axis=1)


@st.cache
def gen_df_jogs_pronto(df_rank, vars_comp):

    df_jogs = df_rank.copy().drop_duplicates(subset=['Jogador','Equipe atual']).drop(df_rank.columns[-(len(vars_select)+3):].tolist(),axis=1)

    dic_colunas = {}
    for coluna in df_rank.columns[-(len(vars_comp)+2):-2]:
        lista_medias = []

        for index, row in df_jogs.iterrows():
            if pd.isnull(df_jogs['Equipe atual'][index]):
                df_aux = df_rank[(df_rank.Jogador == df_jogs.Jogador[index])&(pd.isnull(df_rank['Equipe atual']) == True)]
            else:
                df_aux = df_rank[(df_rank.Jogador == df_jogs.Jogador[index])&(df_rank['Equipe atual'] == df_jogs['Equipe atual'][index])]
            lista_valores = []
            for liga in pd.unique(df_aux.Liga):
                for ano in pd.unique(df_aux[df_aux.Liga == liga]['Ano']):
                    aux_df = df_aux[(df_aux.Ano == ano)&(df_aux.Liga == liga)]
                    if ano == ano_min:
                        lista_valores.append(peso_ligas[liga]*peso_min*np.nanmean(aux_df[coluna]))
                    elif ano == ano_max:
                        lista_valores.append(peso_ligas[liga]*peso_max*np.nanmean(aux_df[coluna]))

            media = np.nanmean(lista_valores)
            lista_medias.append(media)

        dic_colunas[coluna] = lista_medias
        df_jogs[coluna] = dic_colunas[coluna]


    df_jogs['Media'] = df_jogs[vars_comp].mean(axis=1)
    df_jogs['SD'] = df_jogs[vars_comp].std(axis=1)                 

    df_jogs = df_jogs.dropna(subset=['Media'])
    df_jogs['Media'] = df_jogs['Media'].astype('float')
    
    return df_jogs


df_jogs = gen_df_jogs_pronto(df_rank,vars_comp)



@st.cache
def gen_df_show_pronto(df_jogs, vars_select):
    df_show = df_jogs[['Jogador','Posição','Equipe atual']]

    for coluna in df_jogs.columns[-(len(vars_select)+3):-2]:
        df_show[coluna] = ""
        for index, row in df_show.iterrows():
            aux_df = base[(base.Jogador == df_show.Jogador[index])&(base['Equipe atual']==df_show['Equipe atual'][index])]
            if coluna in vars_abs:
                soma = np.nansum(aux_df[coluna])
            else:
                soma = np.nanmean(aux_df[coluna])

            df_show[coluna][index] = soma

    df_show['Media'] = df_jogs['Media']
    df_show['SD'] = df_jogs['SD']

    df_show = df_show.assign(Nota = df_show.Media * df_show.Minutos)
    df_show = df_show.sort_values(by='Nota',ascending = False)
    df_show = df_show.assign(Ranking = range(1,len(df_show)+1))

    return df_show

df_show = gen_df_show_pronto(df_jogs,vars_select)

lista_show = ['Ranking','Nota','Jogador','Posição','Equipe atual','Minutos']
lista_show.extend(vars_select)

st.write(df_show[lista_show])


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


        
nome_busca1 = st.text_input("Nome do primeiro jogador:")

if len(df_show[df_show.Jogador==nome_busca1]) == 0:
  st.write("Favor inserir o nome do jogador igual no WyScout")

elif len(pd.unique(df_show[df_show.Jogador==nome_busca1]['Equipe atual']))>1:
  st.write("Mais de um jogador disponível com este nome, favor inserir o clube atual do jogador desejado.")
  st.write(df_show[df_show.Jogador==nome_busca1][['Ranking','Jogador','Equipe atual','Minutos']])
  clube1 = st.text_input("Clube do primeiro jogador:")
  df1 = df_show[(df_show.Jogador==nome_busca1)&(df_show["Equipe atual"] == clube1)]
  st.write("Tabela resumo do jogador desejado:")
  st.write(df1[['Ranking','Jogador','Equipe atual','Minutos']])
    
else:
  df1 = df_show[df_show.Jogador == nome_busca1]
  st.write("Tabela resumo do jogador desejado:")
  st.write(df1[['Ranking','Jogador','Equipe atual','Minutos']])




nome_busca2 = st.text_input("Nome do segundo jogador:")

if len(df_show[df_show.Jogador==nome_busca2]) == 0:
  st.write("Favor inserir o nome do jogador igual no WyScout")

elif len(pd.unique(df_show[df_show.Jogador==nome_busca2]['Equipe atual']))>1:
  st.write("Mais de um jogador disponível com este nome, favor inserir o clube atual do jogador desejado.")
  st.write(df_show[df_show.Jogador==nome_busca2][['Ranking','Jogador','Equipe atual','Minutos']])
  clube2 = st.text_input("Clube do segundo jogador:")
  df2 = df_show[(df_show.Jogador==nome_busca2)&(df_show["Equipe atual"] == clube2)]
  st.write("Tabela resumo do jogador desejado:")
  st.write(df2[['Ranking','Jogador','Equipe atual','Minutos']])
    
else:
  df2 = df_show[df_show.Jogador == nome_busca2]
  st.write("Tabela resumo do jogador desejado:")
  st.write(df2[['Ranking','Jogador','Equipe atual','Minutos']])



df = pd.concat([df1,df2])


lista_ranges = []
for coluna in df.columns[-(len(vars_select)+4):-4]:
    lista_ranges.append((np.nanmin(df_show[coluna]),np.nanmax(df_show[coluna])))
    


fig = plt.figure(figsize = (8,8))

radar = ComplexRadar(fig,vars_select,lista_ranges)
    
for jog in df.Ranking:
    aux_df = df[df.Ranking == jog]
    nome = aux_df.Jogador.tolist()[0]
    lista_valores = []
    
    for coluna in aux_df.columns[-(len(vars_select)+4):-4]:
        lista_valores.append(aux_df[coluna].tolist()[0])
        
    radar.plot(lista_valores,label=nome+" ("+str(jog)+")")

fig.legend()

st.pyplot(fig)
