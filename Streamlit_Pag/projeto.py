# Bibliotecas para exibição dos dados e análises
import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd
import plotly.express as px
from streamlit_folium import st_folium
import folium


# Configurações iniciais
st.set_page_config(page_title="Dashboard", page_icon="♻️", layout="wide")

# Menu lateral
with st.sidebar:
    seleted = option_menu(
        menu_title="MENU",
        options=["Home", "Limpa Brasil", "Ecopontos", "Pontos Revitalizados", 
                 "Pontos de Entrega Voluntaria", "Sobre"],
        icons=["house", "globe-americas", "flag", "pin", "map", "info-circle"],
        default_index=0
    )

    cores_zonas = {
        "Zona Norte": "#0096C7",
        "Zona Sul": "#0077B6",
        "Zona Leste": "#00B4D8",
        "Zona Oeste": "#90E0EF",
        "Centro": "#CAF0F8"
    }

# Função para formatar números no padrão brasileiro
def format_brasileiro(valor, casas_decimais=0):
    formato = f"{valor:,.{casas_decimais}f}"
    return formato.replace(",", "X").replace(".", ",").replace("X", ".")

# Função: Tela Limpa Brasil
def limp_br():
    st.title("Instituto Limpa Brasil")
    st.subheader("O Instituto Limpa Brasil foi fundado pela empresa Atitude Brasil em 2010. " \
    "Somos uma organização sem fins lucrativos que atua no Brasil como parceira do movimento global Let’s do It. " \
    "Colaborando localmente para o crescimento de ações de limpeza por um mundo sem lixo, mobilizando pessoas e organizações em defesa do descarte adequado de resíduos.")

    @st.cache_data
    def read_data():
        df = pd.read_excel(r"Forms_Limpa_Brasil/limpaBrasil_sp.xlsx")
        return df.dropna(subset=["Latitude", "Longitude", "Zona"])
    # df = read_data()
    #     df = pd.read_excel("Forms_Limpa_Brasil/limpaBrasil_sp.xlsx")
    #     return df.dropna(subset=["Latitude", "Longitude", "Zona"])

    df = read_data()

    df_reg_limp = df.groupby(['Zona']).size().reset_index(name='quantidade')

    total_limp = df_reg_limp['quantidade'].sum()
    df_reg_limp['Texto'] = [f"{v} ({(v/total_limp)*100:.1f}%)" for v in df_reg_limp['quantidade']]

    graf_reg = px.bar(
        df_reg_limp,
        x='Zona',
        y='quantidade',
        text='Texto',
        title='Quantidade de coletas feitas pela Limpa Brasil em cada Região de São Paulo',
        color='Zona',
        color_discrete_map=cores_zonas,
        labels={
            "quantidade": "Quantidade",
            "Zona": "Região de São Paulo"
        }
    )
    graf_reg.update_traces(
        textposition='outside',
        textfont=dict(color='black', size=12, family='Arial'),
        hovertemplate='<b>Zona:</b> %{x}<br><b>Quantidade:</b> %{y}<br><b>Percentual:</b> %{text}<extra></extra>'
    )
    graf_reg.update_layout(height=600, margin=dict(t=100))

    st.plotly_chart(graf_reg, use_container_width=True)

    def get_color(regiao):
        return cores_zonas.get(regiao, "gray")

    # Filtro lateral por zona
    st.sidebar.header("❱❱ FILTRO ❰❰")
    zonas = st.sidebar.multiselect(
        "❱❱ REGIÕES DE SÃO PAULO ❰❰",
        options=df["Zona"].unique(),
        default=df["Zona"].unique()
    )

    # Aplicar o filtro
    df_selecionado = df[df["Zona"].isin(zonas)]

    # Verifica se os dados estão prontos para o mapa
    colunas_mapa = ["Latitude", "Longitude", "Zona", "Bairro"]

    if not df_selecionado.empty and all(col in df_selecionado.columns for col in colunas_mapa):
        mapa = folium.Map(location=(-23.5503, -46.633), zoom_start=11)

        for _, row in df_selecionado.iterrows():
            folium.CircleMarker(
                location=(row["Latitude"], row["Longitude"]),
                radius=6,
                color=get_color(row["Zona"]),
                fill=True,
                fill_color=get_color(row["Zona"]),
                fill_opacity=0.7,
                popup=folium.Popup(
                    f"<b>Zona:</b> {row['Zona']}<br><b>Bairro:</b> {row['Bairro']}",
                    max_width=300
                )
            ).add_to(mapa)

        st.markdown("### Pontos de Mutirão por Zona - São Paulo")
        st_folium(mapa, width="100%", height=600)
    else:
        st.warning("Arquivo inválido ou faltando colunas essenciais.")

# Função de cor para o mapa
def get_color(regiao_agrupada):
    return cores_zonas.get(regiao_agrupada, "gray")

# Função principal combinando mapa e gráficos
def ecoponto_completo():
    st.title("Ecopontos de São Paulo")
    st.subheader(f"Os ecopontos são locais para entrega voluntária de pequenos volumes, os quais buscam eliminar o descarte irregular na cidade, recebendo também materiais inservíveis. Ao todo, a Prefeitura de São Paulo tem 128 ecopontos espalhados por toda capital.")

    @st.cache_data
    def read_data():
        caminho_arquivo = r"..\Dados_Geosampa_Prefeitura\bDADOS_TRATADOS\ECOPONTO.xlsx"
        df = pd.read_excel(caminho_arquivo)
        return df.dropna(subset=["latitude", "longitude", "região"])

    # Leitura e pré-processamento
    df = read_data()

    # Mapeamento das zonas
    mapeamento_zonas = {
        'Zona Leste': 'Zona Leste',
        'Zona Norte': 'Zona Norte',
        'Zona Sul': 'Zona Sul',
        'Zona Oeste': 'Zona Oeste',
        'Centro': 'Centro',
        'Zona Sudeste': 'Zona Sul',
        'Zona Noroeste': 'Zona Norte',
    }
    df['região_agrupada'] = df['região'].replace(mapeamento_zonas)

    st.sidebar.header("❱❱ FILTRO ❰❰")
    # Filtros compartilhados

    regioes = st.sidebar.multiselect(
        "❱❱ REGIÕES DE SÃO PAULO ❰❰",
        options=df["região_agrupada"].dropna().unique(),
        default=df["região_agrupada"].dropna().unique()
    )

    empresas = st.sidebar.multiselect(
        "❱❱ EMPRESAS ❰❰",
        options=df["ep_empresa"].dropna().unique(),
        default=df["ep_empresa"].dropna().unique()
    )

    # Aplicando filtros
    df_filtrado = df[
        (df["ep_empresa"].isin(empresas)) & 
        (df["região_agrupada"].isin(regioes))
    ]

    # --- Gráfico de Barras por Empresa ---
    if not df_filtrado.empty:
        df_agrupado = df_filtrado.groupby("ep_empresa").size().reset_index(name="quantidade")

        df_agrupado['porcentagem'] = (df_agrupado['quantidade'] / df_agrupado['quantidade'].sum() * 100).round(1)

        # Cria texto com quantidade e porcentagem
        df_agrupado['texto'] = df_agrupado['quantidade'].astype(str) + ' (' + df_agrupado['porcentagem'].astype(str) + '%)'

        # Gráfico de barras
        fig_barras = px.bar(
            df_agrupado,
            x="ep_empresa",
            y="quantidade",
            color="ep_empresa",
            title="Empresas Responsáveis",
            labels={"ep_empresa": "Empresa", "quantidade": "Quantidade"},
            text="texto" 
        )

        # Ajustes visuais
        fig_barras.update_traces(textposition='outside')
        fig_barras.update_layout(height=600)

    else:
        st.info("Sem dados para exibir no gráfico de empresas.")

    # --- Gráfico de Rosca por Região ---
    if not df_filtrado.empty:
        df_pie = df_filtrado.groupby("região_agrupada").size().reset_index(name="quantidade")

        fig_rosca = px.pie(
            df_pie,
            names="região_agrupada",
            values="quantidade",
            title="Distribuição por Região",
            color="região_agrupada",
            labels={"ep_empresa": "Empresa", "região_agrupada": "Regiões de São Paulo"},
            color_discrete_map=cores_zonas,
            hole=0.5
        )
        fig_rosca.update_traces(textinfo='percent')
        fig_rosca.update_layout(height=600)

    else:
        st.info("Sem dados para exibir no gráfico de regiões.")

    col4, col5 = st.columns(2)
    with col4:
        st.plotly_chart(fig_barras, use_container_width=True)
    with col5:
        st.plotly_chart(fig_rosca, use_container_width=True)

    # --- Mapa ---
    st.subheader("🗺️ Mapa de Distribuição dos Ecopontos")
    if not df_filtrado.empty:
        mapa = folium.Map(location=(-23.5503, -46.6330), zoom_start=11)

        for _, row in df_filtrado.iterrows():
            folium.CircleMarker(
                location=(row["latitude"], row["longitude"]),
                radius=6,
                color=get_color(row["região_agrupada"]),
                fill=True,
                fill_color=get_color(row["região_agrupada"]),
                fill_opacity=0.7,
                popup=folium.Popup(
                    f"<b>Região:</b> {row['região_agrupada']}<br><b>Endereço:</b> {row['ep_enderec']}",
                    max_width=300
                )
            ).add_to(mapa)

        st_folium(mapa, width="100%", height=600)
    else:
        st.warning("Nenhum dado encontrado com os filtros selecionados.")

# Função: Pontos Revitalizados
def rev():
    caminho_rev = r"Dados_Geosampa_Prefeitura\bDADOS_TRATADOS\PONTO REVITALIZADO.xlsx"

    try:
        df = pd.read_excel(caminho_rev)

        mapeamento_zonas = {
            'Zona Leste': 'Zona Leste',
            'Zona Norte': 'Zona Norte',
            'Zona Sul': 'Zona Sul',
            'Zona Oeste': 'Zona Oeste',
            'Centro': 'Centro',
            'Zona Sudeste': 'Zona Sul',
            'Zona Noroeste': 'Zona Norte',
        }
        df['região_agrupada'] = df['região'].replace(mapeamento_zonas)

        st.sidebar.header("❱❱ FILTRO ❰❰")

        regioes = st.sidebar.multiselect(
            "❱❱ REGIÕES DE SÃO PAULO ❰❰", 
            options=df["região_agrupada"].unique(),
            default=df["região_agrupada"].unique(),
            key="região"
        )

        empresas = st.sidebar.multiselect(
            "❱❱ EMPRESAS ❰❰", 
            options=df["pr_empresa"].unique(),
            default=df["pr_empresa"].unique(),
            key="empresa"
        )
        status = st.sidebar.multiselect(
            "❱❱ STATUS ❰❰", 
            options=df["pr_status"].unique(),
            default=df["pr_status"].unique(),
            key="status"
        )

        df_filtro = df.query("pr_empresa in @empresas and pr_status in @status and região_agrupada in @regioes")

        df_agrupar = df_filtro.groupby(['pr_empresa','pr_status']).size().reset_index(name='quantidade')

        cor_status = {'Eliminado' :'#9370DB',
                      'Revitalizado':'#A9A9A9',
                      'Revitalizado, Reativado':'#DAA520'}

        graf = px.bar(df_agrupar,
                      x='quantidade', 
                      y='pr_empresa', 
                      color='pr_status', 
                      color_discrete_map=cor_status,
                      labels={'pr_empresa':'Empresas',
                              'pr_status':'Status',
                              'quantidade':'Quantidade'},
                      barmode='stack', 
                      orientation='h',
                      title='Pontos Revitalizados ou Eliminados por Empresas')
        

        df_reg = df_filtro.groupby(['região_agrupada']).size().reset_index(name='quantidade')
        df_reg['porcentagem'] = (df_reg['quantidade'] / df_reg['quantidade'].sum() * 100).round(1)

        cores_personalizadas = {
            'Centro': '#4B4B4B',
            'Zona Leste': '#8B0000',
            'Zona Sul': '#006400',
            'Zona Norte': '#2F4F4F',
            'Zona Oeste': '#483D8B'
        }
        
        # Cria texto com quantidade e porcentagem
        df_reg['texto'] = df_reg['quantidade'].astype(str) + ' (' + df_reg['porcentagem'].astype(str) + '%)'
        
        graf_reg = px.bar(df_reg,
                          x='região_agrupada',
                          y='quantidade',
                          title='Pontos Revitalizados por Região',
                          color='região_agrupada',
                          color_discrete_map=cores_zonas,
                          text="texto",
                          labels={'quantidade':'Quantidade',
                                  'região_agrupada':'Regiões de São Paulo'})

        coresmapa = {'Revitalizado, Reativado': '#1E90FF',
                     'Eliminado': '#8B0000',
                     'Revitalizado':'green'}
        
        graf_reg.update_traces(textposition='outside')

        graf_mapa = px.scatter_mapbox(
            df_filtro,
            lat="latitude",
            lon="longitude",
            size_max=10,
            size=[5]*len(df_filtro),
            color="pr_status", 
            color_discrete_map=coresmapa,
            hover_name="pr_empresa",
            hover_data={
                "região_agrupada": True,
                "pr_enderec": True,
                "latitude": True,
                "longitude": True
            },
            labels={'pr_empresa':'Empresas',
                    'pr_status':'Status',
                    'quantidade':'Quantidade',
                    'pr_enderec':'Endereço',
                    'região_agrupada':'Região'},
            zoom=10,
            height=600
        )

        graf_mapa.update_layout(
            title="Mapa: Pontos Revitalizados e situação atual",
            mapbox_style="open-street-map",
            mapbox_center={"lat": -23.55, "lon": -46.63},
            margin={"r": 0, "t": 0, "l": 0, "b": 0}
        )

    except FileNotFoundError:
        st.error("Arquivo 'PONTO REVITALIZADO.xlsx' não encontrado. Verifique o caminho ou mova o arquivo para a pasta correta.")
        st.code(f"Caminho procurado: {caminho_rev}")
        return

    quantidade_rev = df_filtro['pr_empresa'].count()

    st.header("Pontos Revitalizados")
    st.subheader(f"Pontos revitalizados, no contexto da limpeza urbana e gestão de resíduos, "
             f"referem-se a locais onde há descarte irregular de lixo e entulho, "
             f"e que são submetidos a um processo de limpeza e recuperação.")

    st.plotly_chart(graf_reg, use_container_width=True)
    st.write(f"Podemos observar que as regiões da Zona Leste e Zona Sul apresentam uma maior proporção de pontos revitalizados em relação a outras regiões de São Paulo."
            "Ao analisarmos o contexto histórico, percebemos que essas duas regiões enfrentam desigualdade social e sofreram anos de negligência por parte da gestão pública."
            )
    
    st.plotly_chart(graf_mapa, use_container_width=True)
    st.write('Podemos identificar no mapa as empresas responsáveis pela revitalização dos pontos urbanos, destacando também a situação atual de cada local. Através das diferentes cores e informações exibidas, é possível visualizar rapidamente o progresso de cada projeto de revitalização. Além disso, é notável que a região leste se destaca com um número maior de pontos revitalizados, evidenciando um esforço concentrado nessa área da cidade.')
    
    st.plotly_chart(graf, use_container_width=True)
    st.write("As empresas que contribuem para a revitalização de pontos urbanos desempenham papéis essenciais na melhoria de espaços públicos. Elas oferecem expertise em reformas estruturais, fornecem materiais de construção de qualidade e implementam soluções inovadoras, como tecnologias sustentáveis.")

# Função: Pontos de Entrega Voluntária
def pontosEntregaVoluntaria():
    caminho_arquivo_populacao = '../Demografia/populacao_por_regiao.xlsx'
    df_populacao = pd.read_excel(caminho_arquivo_populacao)
    caminho_arquivo = 'Dados_Geosampa_Prefeitura/bDADOS_TRATADOS/PONTO DE ENTREGA VOLUNTARIA.xlsx'
    
    try:
        st.title("Pontos de Entrega Voluntária (PEVs) em São Paulo")
        st.write("PEVs (Pontos de Entrega Voluntária) são locais disponibilizados pela prefeitura onde os cidadãos podem descartar voluntariamente materiais recicláveis, como papel, plástico, vidro e metal. Esses pontos contribuem para a coleta seletiva, a redução do descarte irregular e a preservação do meio ambiente.")
        df = pd.read_excel(caminho_arquivo)

        
        st.sidebar.header("❱❱ FILTRO ❰❰")
        
        mapeamento_zonas = {
            'Zona Leste': 'Zona Leste',
            'Zona Norte': 'Zona Norte',
            'Zona Sul': 'Zona Sul',
            'Zona Oeste': 'Zona Oeste',
            'Centro': 'Centro',
            'Zona Sudeste': 'Zona Sul',
            'Zona Noroeste': 'Zona Norte',  
        }
        
        df['região_agrupada'] = df['região'].replace(mapeamento_zonas)
        
        regioes = st.sidebar.multiselect(
            "❱❱ REGIÕES DE SÃO PAULO ❰❰",
            options=df['região_agrupada'].unique(),
            default=df['região_agrupada'].unique(),
            key="regiao"
        )
        
        df_selecao = df.query("região_agrupada in @regioes")
        
        df_selecao = df.query("região_agrupada in @regioes")
        
        # Agrupa a quantidade total de PEVs
        df_agrupado = df_selecao.groupby('região_agrupada')['pev_quanti'].sum().reset_index()
        
        # Para cálculo de porcentagem e exibição no gráfico
        df_agrupado['porcentagem'] = (df_agrupado['pev_quanti'] / df_agrupado['pev_quanti'].sum() * 100).round(1)
        
        # Texto personalizado: quantidade + porcentagem
        df_agrupado['texto'] = df_agrupado['pev_quanti'].astype(str) + ' (' + df_agrupado['porcentagem'].astype(str) + '%)'
        
        fig_barras = px.bar(
            df_agrupado,
            x="região_agrupada",
            y="pev_quanti",
            color="região_agrupada",
            color_discrete_map=cores_zonas,
            title="Quantidade Total de PEV por Região de São Paulo",
            labels={
                "região_agrupada": "Região",
                "pev_quanti": "Quantidade de PEV"
            },
            text='texto'
        )
        
        fig_barras.update_traces(textposition='outside')

        fig_barras.update_layout(
            xaxis_title="Região de São Paulo",
            yaxis_title="Quantidade Total de PEV",
            showlegend=False,
            height=500
        )
        
        fig_map = px.scatter_map(
                df_selecao,
                lat="latitude",
                lon="longitude",
                size="pev_quanti",
                color="pev_subprf",
                hover_name="pev_nome",
                hover_data={
                    "pev_endere": True,
                    "pev_quanti": True,
                    "latitude": False,
                    "longitude": False
                },
                zoom=10,
                height=600,
                size_max=30,
                color_discrete_sequence=px.colors.qualitative.Set2,
                labels={
                    "pev_subprf": "Subprefeitura",
                    "pev_quanti": "Quantidade de PEV",
                    "pev_nome": "Nome do PEV",
                    "pev_endere": "Endereço"
                },
        )

        fig_map.update_layout(
            mapbox_style="open-street-map",
            mapbox_center={"lat": -23.55, "lon": -46.63},
            margin={"r":0, "t":0, "l":0, "b":0}
        )

        df_populacao.rename(columns={"Região": "região_agrupada", "População": "populacao"}, inplace=True)

        df_agrupado = df_selecao.groupby('região_agrupada')['pev_quanti'].sum().reset_index()

        df_agrupado = df_agrupado.merge(df_populacao, on='região_agrupada', how='left')

        df_agrupado['pev_por_100mil'] = (df_agrupado['pev_quanti'] / df_agrupado['populacao']) * 100000
        
        fig_ratio = px.bar(
            df_agrupado,
            x="região_agrupada",
            y="pev_por_100mil",
            color="região_agrupada",
            color_discrete_map=cores_zonas,
            title="Quantidade de PEV por 100 mil Habitantes",
            labels={
                "região_agrupada": "Região",
                "pev_por_100mil": "PEV / 100 mil hab."
            },
            text_auto=".2f"
        )

        fig_ratio.update_layout(
            xaxis_title="Região de São Paulo",
            yaxis_title="PEV por 100 mil habitantes",
            showlegend=False,
            height=500
        )

        fig_ratio.update_traces(textposition='outside')

        if df_agrupado.empty:
            st.warning("Nenhuma região selecionada ou não há dados para exibir.")
        else:
            st.plotly_chart(fig_map, use_container_width=True)
            
            col1, col2 = st.columns(2)
            with col1:
                st.plotly_chart(fig_barras, use_container_width=True)
            with col2:
                st.plotly_chart(fig_ratio, use_container_width=True)

        
    except Exception as e:
        st.error(f"Erro ao carregar os dados: {e}")

# Função: Home
def home():
    st.title("📊 Demografia do lixo: Um recorte sobre o lixo da capital paulista")

    st.sidebar.header("❱❱ FILTRO ❰❰")

    # Lista das zonas disponíveis (chaves do dicionário de cores)
    zonas = list(cores_zonas.keys())

    # Multiselect para seleção das zonas
    zonas_selecionadas = st.sidebar.multiselect(
        "❱❱ REGIÕES DE SÃO PAULO ❰❰",
        options=zonas,
        default=zonas  # todas selecionadas por padrão
    )

    # --- DEMOGRAFIA
    caminho = r"../Demografia/demografia_alterada.xlsx"
    demografia = pd.read_excel(caminho)
    demografia.columns = [str(col).strip() for col in demografia.columns]
    df_filtrado = demografia[demografia['Região'].isin(zonas_selecionadas)]

    total_cidades = df_filtrado['Cidade'].nunique()
    total_populacao = df_filtrado['População'].sum()
    media_populacao = df_filtrado['População'].mean()

    col1, col2, col3 = st.columns(3)
    col1.metric("Total de Subprefeituras", format_brasileiro(total_cidades))
    col2.metric("População Total", format_brasileiro(total_populacao))
    col3.metric("População Média", format_brasileiro(media_populacao))

    # --- População por Região
    pop_regiao = df_filtrado.groupby('Região')['População'].sum().reset_index()
    pop_regiao['Zona'] = pop_regiao['Região']
    total_pop_regiao = pop_regiao['População'].sum()
    pop_regiao['Texto'] = [f"{v:,.0f} ({(v/total_pop_regiao)*100:.1f}%)" for v in pop_regiao['População']]

    fig_regiao = px.bar(
        pop_regiao, x='Zona', 
        y='População', 
        text='Texto', 
        color='Zona',
        labels={"Zona":"Regiões de São Paulo"},
        color_discrete_map=cores_zonas, 
        title="População Total por Região"
    )
    fig_regiao.update_traces(
        textposition='outside',
        textfont=dict(color='black', size=12, family='Arial'),
        hovertemplate='<b>Zona:</b> %{x}<br><b>População:</b> %{y}<br><b>Percentual:</b> %{text}<extra></extra>'
    )
    fig_regiao.update_layout(height=600, margin=dict(t=100))

    # --- Top 5 Cidades
    top5 = df_filtrado.sort_values('População', ascending=False).head(5)
    total_top5 = df_filtrado['População'].sum()
    top5['Texto'] = [f"{v:,.0f} ({(v/total_top5)*100:.1f}%)" for v in top5['População']]

    fig_top5 = px.bar(
        top5, x='Cidade', y='População', text='Texto', color='Região',
        color_discrete_map=cores_zonas, title="Top 5 Cidades Mais Populosas"
    )
    fig_top5.update_traces(
        textposition='outside',
        textfont=dict(color='black', size=12, family='Arial'),
        hovertemplate='<b>Cidade:</b> %{x}<br><b>População:</b> %{y}<br><b>Percentual:</b> %{text}<extra></extra>'
    )
    fig_top5.update_layout(height=600, margin=dict(t=100))

    col4, col5 = st.columns(2)
    with col4:
        st.plotly_chart(fig_top5, use_container_width=True)
    with col5:
        st.plotly_chart(fig_regiao, use_container_width=True)

    # --- LIMPA BRASIL
    df_limp = pd.read_excel(r"Forms_Limpa_Brasil/limpaBrasil_sp.xlsx")
    df_limp = df_limp[df_limp['Zona'].isin(zonas_selecionadas)]

    df_reg_limp = df_limp.groupby(['Zona']).size().reset_index(name='quantidade')
    total_limp = df_reg_limp['quantidade'].sum()
    df_reg_limp['Texto'] = [f"{v} ({(v/total_limp)*100:.1f}%)" for v in df_reg_limp['quantidade']]

    graf_reg = px.bar(
        df_reg_limp, x='Zona', 
        y='quantidade', 
        labels={"quantidade": "Quantidade"},
        text='Texto',
        title='Quantidade de coletas feitas pela Limpa Brasil em cada Zona de São Paulo',
        color='Zona', color_discrete_map=cores_zonas
    )
    graf_reg.update_traces(
        textposition='outside',
        textfont=dict(color='black', size=12, family='Arial'),
        hovertemplate='<b>Zona:</b> %{x}<br><b>Quantidade:</b> %{y}<br><b>Percentual:</b> %{text}<extra></extra>'
    )
    graf_reg.update_layout(height=600, margin=dict(t=100))

    st.plotly_chart(graf_reg, use_container_width=True)

    # --- ECOPONTO
    caminho_eco = r"Dados_Geosampa_Prefeitura\bDADOS_TRATADOS\ECOPONTO.xlsx"
    df_eco = pd.read_excel(caminho_eco)
    mapeamento_zonas = {
        'Zona Leste': 'Zona Leste', 'Zona Norte': 'Zona Norte',
        'Zona Sul': 'Zona Sul', 'Zona Oeste': 'Zona Oeste',
        'Centro': 'Centro', 'Zona Sudeste': 'Zona Sul',
        'Zona Noroeste': 'Zona Norte'
    }
    df_eco['região_agrupada'] = df_eco['região'].replace(mapeamento_zonas)
    df_eco['Zona'] = df_eco['região_agrupada']
    df_eco_filtrado = df_eco[df_eco['Zona'].isin(zonas_selecionadas)]
    df_pie = df_eco_filtrado.groupby("Zona").size().reset_index(name="quantidade")
    total_pie = df_pie['quantidade'].sum()
    df_pie['Texto'] = [f"{v} ({(v/total_pie)*100:.1f}%)" for v in df_pie['quantidade']]

    fig_rosca = px.pie(
        df_pie, names="Zona", values="quantidade", title="Distribuição por Região - ECOPONTO",
        hole=0.5, color='Zona', color_discrete_map=cores_zonas
    )
    fig_rosca.update_traces(
        textinfo='percent',
        textfont=dict(color='black', size=20, family='Arial'),
        hovertemplate='<b>Zona:</b> %{label}<br><b>Quantidade:</b> %{value}<br><b>Percentual:</b> %{percent}<extra></extra>'
    )
    fig_rosca.update_layout(height=600, margin=dict(t=100))

    # --- PONTO REVITALIZADO
    caminho_rev = r"Dados_Geosampa_Prefeitura\bDADOS_TRATADOS\PONTO REVITALIZADO.xlsx"
    df_rev = pd.read_excel(caminho_rev)
    df_rev['região_agrupada'] = df_rev['região'].replace(mapeamento_zonas)
    df_rev['Zona'] = df_rev['região_agrupada']
    df_rev_filtrado = df_rev[df_rev['Zona'].isin(zonas_selecionadas)]
    df_reg_rev = df_rev_filtrado.groupby(['Zona']).size().reset_index(name='quantidade')
    total_rev = df_reg_rev['quantidade'].sum()
    df_reg_rev['Texto'] = [f"{v} ({(v/total_rev)*100:.1f}%)" for v in df_reg_rev['quantidade']]

    graf_reg_rev = px.bar(
        df_reg_rev, x='Zona', 
        y='quantidade', 
        text='Texto',
        labels={"quantidade": "Quantidade"},
        title='Pontos Revitalizados por Região', color='Zona', color_discrete_map=cores_zonas
    )
    graf_reg_rev.update_traces(
        textposition='outside',
        textfont=dict(color='black', size=12, family='Arial'),
        hovertemplate='<b>Zona:</b> %{x}<br><b>Quantidade:</b> %{y}<br><b>Percentual:</b> %{text}<extra></extra>'
    )
    graf_reg_rev.update_layout(height=600, margin=dict(t=100))

    # --- PEV
    caminho_pev = 'Dados_Geosampa_Prefeitura/bDADOS_TRATADOS/PONTO DE ENTREGA VOLUNTARIA.xlsx'
    df_pev = pd.read_excel(caminho_pev)
    df_pev['região_agrupada'] = df_pev['região'].replace(mapeamento_zonas)
    df_pev['Zona'] = df_pev['região_agrupada']
    df_pev_filtrado = df_pev[df_pev['Zona'].isin(zonas_selecionadas)]
    df_pev_agrupado = df_pev_filtrado.groupby('Zona')['pev_quanti'].sum().reset_index()
    total_pev = df_pev_agrupado['pev_quanti'].sum()
    df_pev_agrupado['Texto'] = [f"{v} ({(v/total_pev)*100:.1f}%)" for v in df_pev_agrupado['pev_quanti']]

    fig_barras_pev = px.bar(
        df_pev_agrupado, x="Zona", 
        y="pev_quanti", 
        color="Zona",
        labels={"pev_quanti": "Quantidade"},
        title="Quantidade Total de PEV por Região de São Paulo", 
        text='Texto',
        color_discrete_map=cores_zonas
    )
    fig_barras_pev.update_traces(
        textposition='outside',
        textfont=dict(color='black', size=12, family='Arial'),
        hovertemplate='<b>Zona:</b> %{x}<br><b>Quantidade:</b> %{y}<br><b>Percentual:</b> %{text}<extra></extra>'
    )
    fig_barras_pev.update_layout(height=600, margin=dict(t=100))

    col6, col7, col8 = st.columns(3)
    with col6:
        st.plotly_chart(graf_reg_rev, use_container_width=True)
    with col7:
        st.plotly_chart(fig_rosca, use_container_width=True)
    with col8:
        st.plotly_chart(fig_barras_pev, use_container_width=True)

# Execução da página conforme seleção do menu
if seleted == "Home":
    home()

elif seleted == "Limpa Brasil":
    limp_br()

elif seleted == "Ecopontos":
    ecoponto_completo()
    st.markdown("**Fonte de dados**: https://geosampa.prefeitura.sp.gov.br/PaginasPublicas/_SBC.aspx")

elif seleted == "Pontos Revitalizados":
    rev()

elif seleted == "Pontos de Entrega Voluntaria":
    pontosEntregaVoluntaria()

elif seleted == "Sobre":
    st.title("ℹ️ Sobre este Projeto")
