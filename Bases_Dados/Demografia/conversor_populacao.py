import pandas as pd

xlsx = pd.read_excel("demografia_2022.xlsx")
df = pd.DataFrame(xlsx)

# Criação manual de uma lista para inclusão das regiões
# Dicionário com mapeamento das subprefeituras para regiões
regioes_sp = {
    "Mooca": "Zona Leste",
    "Pinheiros": "Zona Oeste",
    "São Miguel": "Zona Leste",
    "Pirituba-Jaraguá": "Zona Noroeste",
    "Aricanduva-Formosa-Carrão": "Zona Leste",
    "Penha": "Zona Leste",
    "Vila Mariana": "Zona Sul",
    "Freguesia-Brasilândia": "Zona Norte",
    "Perus-Anhanguera": "Zona Noroeste",
    "Campo Limpo": "Zona Sul",
    "Vila Maria-Vila Guilherme": "Zona Norte",
    "Butantã": "Zona Oeste",
    "Ermelino Matarazzo": "Zona Leste",
    "Itaim Paulista": "Zona Leste",
    "Cidade Tiradentes": "Zona Leste",
    "Santo Amaro": "Zona Sul",
    "São Mateus": "Zona Leste",
    "Vila Prudente": "Zona Leste",
    "Ipiranga": "Zona Sudeste",
    "Sapopemba": "Zona Leste",
    "Casa Verde-Cachoeirinha": "Zona Norte",
    "Itaquera": "Zona Leste",
    "Sé": "Centro",
    "Cidade Ademar": "Zona Sul",
    "Jabaquara": "Zona Sul",
    "Capela Do Socorro": "Zona Sul",
    "Santana-Tucuruvi": "Zona Norte",
    "Guaianases": "Zona Leste",
    "M'Boi Mirim": "Zona Sul",
    "Jaçanã-Tremembé": "Zona Norte",
    "Lapa": "Zona Oeste"
}

# Padronizar os nomes da coluna 'Cidade' para facilitar o mapeamento (ex: tirar espaços, capitalizar, etc.)
df['Cidade_normalizada'] = df['Cidade'].str.strip().str.title().str.replace("’", "'").str.replace("M' Boi", "M'Boi")

# Corrigir nomes específicos para bater com o dicionário
substituicoes = {
    "Capela Do Socorro": "Capela Do Socorro",
    "M'boi Mirim": "M'Boi Mirim"
}
df['Cidade_normalizada'] = df['Cidade_normalizada'].replace(substituicoes)

# Aplicar o mapeamento
df['Região'] = df['Cidade_normalizada'].map(regioes_sp)

# Exibir resultado
df[['Cidade', 'Cidade_normalizada', 'Região', 'População']].head(10)

df.to_excel('demorgrafia_alterada.xlsx', index=False)
