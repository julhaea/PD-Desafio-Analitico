import pandas as pd
import sqlite3
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.ticker import MaxNLocator
from datetime import timedelta

print("\n1-ESTATÍSTICAS DESCRITIVAS")

conn = sqlite3.connect('../ecommerce.db')
cursor = conn.cursor()

# características da tabela
cursor.execute("PRAGMA table_info(vendas)")
colunas = cursor.fetchall()

print("\n1.1-Estrutura da Tabela:")
print(f"\n{'Coluna':<25} {'Tipo':<15}")
for col in colunas:
    nome, tipo = col[1], col[2]
    print(f"{nome:<25} {tipo:<15}")


df = pd.read_sql_query("SELECT * FROM vendas", conn)
print(f"\nTotal de registros: {len(df):,} linhas")


# características do período analisado
df['data_dt'] = pd.to_datetime(df['data_compra'], format='%d-%m-%Y')
data_min = df['data_dt'].min().strftime('%d-%m-%Y')
data_max = df['data_dt'].max().strftime('%d-%m-%Y')
dias_totais = (df['data_dt'].max() - df['data_dt'].min()).days

print("\n1.2-Abrangência do Dados:")

print(f"\nData inicial: {data_min}")
print(f"Data final: {data_max}")
print(f"Total de dias analisados: {dias_totais}")

#estados abrangidos
estados_presentes = sorted(df['estado'].unique())
estados_str = ', '.join(estados_presentes)
print(f"\nEstados abrangidos: {estados_str}")
print(f"Total de estados: {len(estados_presentes)}")

#categorias vendidas
categorias = sorted(df['categoria'].unique())
categorias_str = ', '.join(categorias)
print(f"\nCategorias vendidas: {categorias_str}")
print(f"Total de categorias: {len(categorias)}")


# vendas por ano
print("\n1.3-Vendas por ano analisado:")
anos = df['data_dt'].dt.year.value_counts().sort_index()
for ano, qtd in anos.items():
    percentual = round(qtd / len(df) * 100, 1)
    print(f"   {ano}: {qtd} vendas ({percentual}%)")

#características das vendas
print("\n1.4-Métricas Vendas")

faturamento_total = df['preco_total'].sum()
print(f"\nFaturamento total: R$ {faturamento_total:,.2f}")

ticket_medio = df['preco_total'].mean()
print(f"Ticket médio por compra: R$ {ticket_medio:.2f}")

itens_vendidos = df['quantidade'].sum()
print(f"Total de itens vendidos: {itens_vendidos:,}")

preco_medio = df['preco'].mean()
print(f" Preço médio dos produtos: R$ {preco_medio:.2f}")

#características dos clientes
print("\n1.5-Métricas Clientes")

clientes_unicos = df['id_cliente_unico'].nunique()
print(f"\nTotal de clientes únicos: {clientes_unicos:,}")

ticket_por_cliente = df.groupby('id_cliente_unico')['preco_total'].sum().mean()
print(f"Gasto médio por cliente: R$ {ticket_por_cliente:.2f}")


print("\n2-CONSULTAS SQL")

#categorias/faturamento
print("\n2.1-Ranking Categorias por Faturamento")

query_rank = """
SELECT 
    categoria,
    faturamento,
    qtd_vendas,

    RANK() OVER (ORDER BY faturamento DESC) as ranking_faturamento,

    RANK() OVER (ORDER BY qtd_vendas DESC) as ranking_vendas,
    
    ROUND(faturamento * 100.0 / SUM(faturamento) OVER (), 2) as percentual_faturamento,
    ROUND(qtd_vendas * 100.0 / SUM(qtd_vendas) OVER (), 2) as percentual_vendas
FROM (
    SELECT 
        categoria,
        SUM(preco_total) as faturamento,
        COUNT(*) as qtd_vendas
    FROM vendas
    GROUP BY categoria
) 
ORDER BY faturamento DESC;
"""

df_rank = pd.read_sql(query_rank, conn)
print(f"\n{df_rank.to_string(index=False)}")

#mes/faturamento
print("\n2.2-Faturamento por mês analisado")


query_mensal = """
WITH datas_convertidas AS (
    SELECT 
        SUBSTR(data_compra, 7, 4) || '-' || 
        SUBSTR(data_compra, 4, 2) || '-' || 
        SUBSTR(data_compra, 1, 2) as data_iso,
        preco_total
    FROM vendas
),
vendas_mensais AS (
    SELECT 
        strftime('%Y-%m', data_iso) as mes,
        COUNT(*) as qtd_vendas,
        ROUND(SUM(preco_total), 2) as faturamento
    FROM datas_convertidas
    GROUP BY mes
)
SELECT 
    mes,
    qtd_vendas,
    faturamento,
    RANK() OVER (ORDER BY faturamento DESC) as ranking_faturamento,
    RANK() OVER (ORDER BY qtd_vendas DESC) as ranking_vendas,
    ROUND((faturamento - LAG(faturamento, 1) OVER (ORDER BY mes)) / 
          NULLIF(LAG(faturamento, 1) OVER (ORDER BY mes), 0) * 100, 2) as perc_variacao_mes_anterior
FROM vendas_mensais
ORDER BY mes;
"""

df_mensal = pd.read_sql(query_mensal, conn)


colunas_exibicao = ['mes', 'qtd_vendas', 'faturamento', 'ranking_faturamento', 
                   'ranking_vendas', 'perc_variacao_mes_anterior']
print(f"\n{df_mensal[colunas_exibicao].to_string(index=False)}")

#estado/faturamento
print("\n2.3-Faturamento por Estado")

query_estado = """
SELECT 
    estado,
    COUNT(*) as qtd_vendas,
    ROUND(SUM(preco_total), 2) as faturamento,
    ROUND(AVG(preco_total), 2) as ticket_medio,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) as percentual_vendas,
    ROUND(SUM(preco_total) * 100.0 / SUM(SUM(preco_total)) OVER (), 2) as percentual_faturamento
FROM vendas
GROUP BY estado
ORDER BY faturamento DESC;
"""

df_estado = pd.read_sql(query_estado, conn)
print(f"\n{df_estado.to_string(index=False)}")

#frequencia de compras clientes
print("\n2.4-Análise de frequência de compras por cliente")


query_frequencia = """
WITH frequencia_clientes AS (
    SELECT 
        id_cliente_unico,
        COUNT(*) as qtd_compras
    FROM vendas
    GROUP BY id_cliente_unico
)
SELECT 
    qtd_compras,
    COUNT(*) as quantidade_clientes,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) as percentual
FROM frequencia_clientes
GROUP BY qtd_compras
ORDER BY qtd_compras;
"""

df_frequencia = pd.read_sql(query_frequencia, conn)
print(f"\n{df_frequencia.to_string(index=False)}")

#analise formas de pagamento
print("\n2.5-Análise Formas de Pagamento")

query_pagamentos = """
SELECT 
    forma_pagamento,
    COUNT(*) as qtd_vendas,
    ROUND(SUM(preco_total), 2) as faturamento,
    ROUND(AVG(preco_total), 2) as ticket_medio,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) as percentual_vendas,
    RANK() OVER (ORDER BY SUM(preco_total) DESC) as ranking
FROM vendas
GROUP BY forma_pagamento
ORDER BY faturamento DESC;
"""

df_pagamentos_sql = pd.read_sql(query_pagamentos, conn)
print(f"\n{df_pagamentos_sql.to_string(index=False)}")

#faixa de ticket/faturamento
print("\n2.6-Análise de Ticket por faixa")

query_ticket_faixa = """
WITH faixas AS (
    SELECT 
        CASE 
            WHEN preco_total < 100 THEN 'até R$100'
            WHEN preco_total BETWEEN 100 AND 500 THEN 'R$101-500'
            WHEN preco_total BETWEEN 501 AND 2000 THEN 'R$501-2000'
            WHEN preco_total BETWEEN 2001 AND 5000 THEN 'R$2001-5000'
            ELSE '>R$5000'
        END as faixa_valor,
        COUNT(*) as qtd_vendas,
        SUM(preco_total) as faturamento,
        AVG(preco_total) as ticket_medio_faixa,
        AVG(quantidade) as media_itens,
        COUNT(DISTINCT id_cliente_unico) as clientes_unicos,
        MIN(preco_total) as valor_min_faixa
    FROM vendas
    GROUP BY 
        CASE 
            WHEN preco_total < 100 THEN 1
            WHEN preco_total BETWEEN 100 AND 500 THEN 2
            WHEN preco_total BETWEEN 501 AND 2000 THEN 3
            WHEN preco_total BETWEEN 2001 AND 5000 THEN 4
            ELSE 5
        END
)
SELECT 
    faixa_valor,
    qtd_vendas,
    ROUND(faturamento, 2) as faturamento,
    ROUND(ticket_medio_faixa, 2) as ticket_medio,
    ROUND(media_itens, 2) as media_itens,
    ROUND(faturamento * 100.0 / SUM(faturamento) OVER (), 2) as participacao_percent
FROM faixas
ORDER BY valor_min_faixa;
"""

df_faixas = pd.read_sql(query_ticket_faixa, conn)
print(f"\n{df_faixas.to_string(index=False)}")


#top 10 produtos
print("\n2.7-10 Produtos com maior faturamento")

query_top_produtos =  """
SELECT 
    nome_produto,
    categoria,
    SUM(quantidade) as unidades_vendidas,
    ROUND(SUM(preco_total), 2) as faturamento_total,
    ROUND(AVG(preco), 2) as preco,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) as percentual_vendas,
    ROUND(SUM(preco_total) * 100.0 / SUM(SUM(preco_total)) OVER (), 2) as percentual_faturamento,
    RANK() OVER (ORDER BY SUM(quantidade) DESC) as ranking_unidades_vendidas 
FROM vendas
GROUP BY nome_produto, categoria
ORDER BY faturamento_total DESC
LIMIT 10;
"""

df_top_produtos = pd.read_sql(query_top_produtos, conn)
print(f"\n{df_top_produtos.to_string(index=False)}")

print("\n3-OUTLIERS E CORRELAÇÃO DE VARIÁVEIS")

print("\n3.1-Identificação de Outliers")

#outlies quantidade
print("\n3.1.1-Quantidade")
query_quantidade = """
SELECT 
    quantidade,
    COUNT(*) as n_compras,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) as percentual
FROM vendas
GROUP BY quantidade
ORDER BY quantidade;
"""

df_qtd = pd.read_sql(query_quantidade, conn)
print("\n-Distribuição de compras por quantidade:")
print(df_qtd.to_string(index=False))

compras_1 = df_qtd[df_qtd['quantidade'] == 1]['n_compras'].values[0]
compras_2_4 = df_qtd[(df_qtd['quantidade'] >= 2) & (df_qtd['quantidade'] <= 4)]['n_compras'].sum()
compras_5_6 = df_qtd[(df_qtd['quantidade'] >= 5) & (df_qtd['quantidade'] <= 6)]['n_compras'].sum()
compras_7_mais = df_qtd[df_qtd['quantidade'] >= 7]['n_compras'].sum()

print(f"\n-Concentração")
print(f"1 item: {compras_1} ({compras_1/len(df)*100:.1f}%)")
print(f"2-4 itens: {compras_2_4} ({compras_2_4/len(df)*100:.1f}%)")
print(f"5-6 itens: {compras_5_6} ({compras_5_6/len(df)*100:.1f}%)")
print(f"7+ itens: {compras_7_mais} ({compras_7_mais/len(df)*100:.1f}%)")

df['classificacao_qtd'] = df['quantidade'].apply(
    lambda x: 'Normal (1-4)' if x <= 4 
    else 'Atenção (5-6)' if x <= 6 
    else 'Outlier (7+)'
)

outliers_quantidade = df[df['quantidade'] >= 7]

print(f"\n-Outliers de quantidade (7+ itens):")
print(f"Vendas: {len(outliers_quantidade)}")
print(f"Percentual: {len(outliers_quantidade)/len(df)*100:.2f}")
print(f"Máximo: {outliers_quantidade['quantidade'].max()}")

print("\n3.1.2-Preço produto")

#calculo outliers preço produto
Q3_preco = df['preco'].quantile(0.75)
Q1_preco = df['preco'].quantile(0.25)
IQR_preco = Q3_preco - Q1_preco
limite_superior_preco = Q3_preco + 4 * IQR_preco
outliers_preco = df[df['preco'] > limite_superior_preco]


print(f"\n-Outliers de preço produto (> R$ {limite_superior_preco:.2f})")
print(f"Vendas:{len(outliers_preco)}")
print(f"Produtos únicos: {outliers_preco['id_produto'].nunique()}")
print(f"Percentual de produtos: {len(outliers_preco)/len(df)*100:.1f}")
print(f"Preço máximo: R$ {outliers_preco['preco'].max():,.2f}")

print("\n3.1.3-Preço total da compra")

#calculo outliers preço da compra
Q3_total = df['preco_total'].quantile(0.75)
Q1_total = df['preco_total'].quantile(0.25)
IQR_total = Q3_total - Q1_total
limite_superior_total = Q3_total + 4 * IQR_total
outliers_valor_compra = df[df['preco_total'] > limite_superior_total]

print(f"\n-Outliers de preço total de compra (> de R$ {limite_superior_total:.2f})")
print(f"Vendas: {len(outliers_valor_compra)}")
print(f"Percentual das vendas: {len(outliers_valor_compra)/len(df)*100:.1f}")
print(f"Faturamento: R$ {outliers_valor_compra['preco_total'].sum():,.2f}")
print(f"Percentual do faturamento: {outliers_valor_compra['preco_total'].sum()/df['preco_total'].sum()*100:.1f}%")
print(f"Valor máximo: R$ {outliers_valor_compra['preco_total'].max():,.2f}")

#gerar graficos de outliers

fig, axes = plt.subplots(1, 3, figsize=(15, 6))

cores = ['#3498db', '#e74c3c', '#2ecc71']

#quantidade
bp3 = axes[0].boxplot(df['quantidade'], patch_artist=True,
                      boxprops=dict(facecolor=cores[2], alpha=0.7),
                      whiskerprops=dict(color='black', linewidth=1.5),
                      capprops=dict(color='black', linewidth=1.5),
                      medianprops=dict(color='black', linewidth=2),
                      flierprops=dict(marker='o', markerfacecolor='orange', markersize=4, alpha=0.5))
axes[0].set_title('Distribuição de QUANTIDADE', fontsize=12, fontweight='bold')
axes[0].set_ylabel('Quantidade')
axes[0].grid(True, alpha=0.3)
axes[0].yaxis.set_major_locator(MaxNLocator(integer=True))
axes[0].axhline(y=7, color='red', linestyle='--', alpha=0.7, linewidth=1.5)

#preço
bp1 = axes[1].boxplot(df['preco'], patch_artist=True, 
                      boxprops=dict(facecolor=cores[0], alpha=0.7),
                      whiskerprops=dict(color='black', linewidth=1.5),
                      capprops=dict(color='black', linewidth=1.5),
                      medianprops=dict(color='black', linewidth=2),
                      flierprops=dict(marker='o', markerfacecolor='red', markersize=4, alpha=0.5))
axes[1].set_title('Distribuição de PREÇO', fontsize=12, fontweight='bold')
axes[1].set_ylabel('Valor (R$)')
axes[1].grid(True, alpha=0.3)
axes[1].axhline(y=limite_superior_preco, color='red', linestyle='--', alpha=0.7, linewidth=1.5)

#preço total
bp2 = axes[2].boxplot(df['preco_total'], patch_artist=True,
                      boxprops=dict(facecolor=cores[1], alpha=0.7),
                      whiskerprops=dict(color='black', linewidth=1.5),
                      capprops=dict(color='black', linewidth=1.5),
                      medianprops=dict(color='black', linewidth=2),
                      flierprops=dict(marker='o', markerfacecolor='red', markersize=4, alpha=0.5))
axes[2].set_title('Distribuição de PREÇO TOTAL', fontsize=12, fontweight='bold')
axes[2].set_ylabel('Valor (R$)')
axes[2].grid(True, alpha=0.3)
axes[2].axhline(y=limite_superior_total, color='red', linestyle='--', alpha=0.7, linewidth=1.5)

# título
plt.suptitle('ANÁLISE DE OUTLIERS - BOXPLOT', fontsize=14, fontweight='bold', y=1.02)
plt.tight_layout()

#salvar
plt.savefig('outliers_boxplot.png', dpi=300, bbox_inches='tight')
print("\nGráfico de Outliers gerado: outliers_boxplot.png")


print("\n3.2-Análise de Correlação")

#matriz de correlação
colunas_numericas = ['preco', 'preco_total', 'quantidade']
correlacao = df[colunas_numericas].corr()

print("\nMatriz de correlação:")
print(correlacao.round(3))

#gerar matriz png
plt.figure(figsize=(8, 6))
sns.heatmap(correlacao, annot=True, cmap='coolwarm', center=0, fmt='.2f', 
            square=True, linewidths=1, cbar_kws={"shrink": 0.8})
plt.title('Matriz de Correlação', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig('matriz_correlacao.png', dpi=300, bbox_inches='tight')
print("\nMatriz de correlação gerada: matriz_correlacao.png")

#gráficos de dispersão
fig, axes = plt.subplots(1, 2, figsize=(12, 6))

# preço x quantidae
axes[0].scatter(df['preco'], df['quantidade'], alpha=0.5, c='#e74c3c', s=20)
axes[0].set_xlabel('Preço Unitário (R$)')
axes[0].set_ylabel('Quantidade')
axes[0].set_title('Preço Unitário vs Quantidade')
axes[0].grid(True, alpha=0.3)
axes[0].yaxis.set_major_locator(MaxNLocator(integer=True))

# quantidade x preco total
axes[1].scatter(df['quantidade'], df['preco_total'], alpha=0.5, c='#2ecc71', s=20)
axes[1].set_xlabel('Quantidade')
axes[1].set_ylabel('Preço Total (R$)')
axes[1].set_title('Quantidade vs Preço Total')
axes[1].grid(True, alpha=0.3)
axes[1].xaxis.set_major_locator(MaxNLocator(integer=True))

plt.suptitle('GRÁFICOS DE DISPERSÃO - RELAÇÕES ENTRE VARIÁVEIS', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig('graficos_dispersao.png', dpi=300, bbox_inches='tight')
print("\nGráficos de dispersão gerados: graficos_dispersao.png")

print("\n4-ANÁLISE DE CLIENTES RFM")

#tratamento das datas
df['data_compra'] = pd.to_datetime(df['data_compra'], dayfirst=True)
data_analise = df['data_compra'].max() + timedelta(days=1)

# gerando os segmentos de clientes
rfm = df.groupby('id_cliente_unico').agg({
    'data_compra': lambda x: (data_analise - x.max()).days,
    'id_compra': 'count',
    'preco_total': 'sum'
})

rfm.columns = ['Recencia', 'Frequencia', 'Monetario']
rfm['Monetario'] = rfm['Monetario'].round(2)

# scores
rfm['R_Score'] = pd.qcut(rfm['Recencia'], 5, labels=[5, 4, 3, 2, 1]).astype(int)

rfm['F_Score'] = rfm['Frequencia'].astype(int)

rfm['M_Score'] = pd.qcut(rfm['Monetario'], 5, labels=[1, 2, 3, 4, 5]).astype(int)
rfm['FM_Score'] = (rfm['F_Score'] + rfm['M_Score']) / 2

# segmentações
def segmentar(row):
    r = row['R_Score']
    fm = row['FM_Score']
    
    if r >= 4 and fm >= 4.5: return "Campeões"
    if r >= 3 and fm >= 4:   return "Clientes Fiéis"
    if r >= 3 and fm >= 3:   return "Lealdade Potencial"
    if r >= 4 and fm >= 1:   return "Clientes Recentes"
    if r >= 3 and fm >= 1:   return "Promissor"
    if r >= 2 and fm >= 2:   return "Precisam de Atenção"
    if r >= 2 and fm >= 1:   return "Prestes a Hibernar"
    if r <= 2 and fm >= 4:   return "Não Posso Perdê-los"
    if r <= 2 and fm >= 3:   return "Em Risco"
    if r <= 2 and fm >= 1.5: return "Hibernando"
    return "Perdido"

rfm['Segmento'] = rfm.apply(segmentar, axis=1)

rfm = rfm.reset_index()

#gerar csv
rfm.to_csv('analise_rfm.csv', sep=';', index=False, encoding='utf-8-sig')
print("\nCSV Análise RFM gerado: 'analise_rfm.csv'")

#gerar gráficos de segmentos de cliente

plt.style.use('seaborn-v0_8-darkgrid')
fig, axes = plt.subplots(1, 2, figsize=(16, 8))

segmentos_agregado = rfm.groupby('Segmento').agg({
    'id_cliente_unico': 'count',
    'Monetario': 'sum'
}).rename(columns={
    'id_cliente_unico': 'total_clientes',
    'Monetario': 'faturamento_total'
})

segmentos_agregado['percentual_clientes'] = (segmentos_agregado['total_clientes'] / segmentos_agregado['total_clientes'].sum() * 100).round(1)
segmentos_agregado['percentual_faturamento'] = (segmentos_agregado['faturamento_total'] / segmentos_agregado['faturamento_total'].sum() * 100).round(1)

segmentos_ordenados = segmentos_agregado.index.tolist()
cores_fixas = plt.cm.Set3(range(len(segmentos_ordenados)))
cores_por_segmento = {seg: cores_fixas[i] for i, seg in enumerate(segmentos_ordenados)}

segmentos_plot = segmentos_agregado.sort_values('total_clientes', ascending=True)
cores_plot1 = [cores_por_segmento[seg] for seg in segmentos_plot.index]

bars1 = axes[0].barh(segmentos_plot.index, segmentos_plot['total_clientes'], color=cores_plot1)
axes[0].set_xlabel('Quantidade de Clientes', fontsize=12)
axes[0].set_title('Distribuição de Clientes por Segmento', fontsize=14, fontweight='bold')
axes[0].grid(True, alpha=0.3)

for i, v in enumerate(segmentos_plot['total_clientes']):
    pct = segmentos_plot['percentual_clientes'].iloc[i]
    axes[0].text(v + max(segmentos_plot['total_clientes']) * 0.02, i, 
                 f'{int(v)} clientes ({pct}%)', va='center', fontsize=10)

segmentos_fat = segmentos_agregado.sort_values('percentual_faturamento', ascending=True)
cores_plot2 = [cores_por_segmento[seg] for seg in segmentos_fat.index]

bars2 = axes[1].barh(segmentos_fat.index, segmentos_fat['percentual_faturamento'], color=cores_plot2)
axes[1].set_xlabel('Percentual do Faturamento (%)', fontsize=12)
axes[1].set_title('Faturamento por Segmento', fontsize=14, fontweight='bold')
axes[1].grid(True, alpha=0.3)

for i, v in enumerate(segmentos_fat['percentual_faturamento']):
    fat = segmentos_fat['faturamento_total'].iloc[i]
    axes[1].text(v + 0.5, i, f'{v}% (R$ {fat:,.0f})', va='center', fontsize=10)

plt.suptitle('ANÁLISE RFM - SEGMENTAÇÃO DE CLIENTES', fontsize=16, fontweight='bold', y=1.02)

plt.subplots_adjust(left=0.12, right=0.95, top=0.92, bottom=0.08, wspace=0.35)

plt.savefig('rfm_segmentacao.png', dpi=300, bbox_inches='tight')
print("\nGráficos participação dos segmentos salvo: rfm_segmentacao.png")


print("\nParticipação dos segmentos no total de clientes e no total de faturamento")

print(f"\n{'Segmento':<25} {'Qtd Clientes':<15} {'% Clientes':<12} {'Faturamento (R$)':<18} {'% Faturamento':<12}")


for segmento, row in segmentos_agregado.iterrows():
    print(f"{segmento:<25} {row['total_clientes']:<15} {row['percentual_clientes']:<12}% "
          f"R$ {row['faturamento_total']:>15,.2f} {row['percentual_faturamento']:<12}%")


print("\n5-CÁLCULO DO CHURN RATE")


data_referencia = df['data_compra'].max() + timedelta(days=1)

ultima_compra = df.groupby('id_cliente_unico')['data_compra'].max().reset_index()
ultima_compra.columns = ['id_cliente_unico', 'ultima_compra']
ultima_compra['dias_desde_ultima'] = (data_referencia - ultima_compra['ultima_compra']).dt.days

churn_limite = 180
clientes_ativos = ultima_compra[ultima_compra['dias_desde_ultima'] <= churn_limite]
clientes_churn = ultima_compra[ultima_compra['dias_desde_ultima'] > churn_limite]

total_clientes = len(ultima_compra)
churn_rate = len(clientes_churn) / total_clientes * 100
retencao_rate = len(clientes_ativos) / total_clientes * 100

print(f"\nTotal de clientes: {total_clientes}")
print(f"Clientes ativos (últimos {churn_limite} dias): {len(clientes_ativos)} ({retencao_rate:.1f}%)")
print(f"Clientes em churn (+{churn_limite} dias sem compra): {len(clientes_churn)} ({churn_rate:.1f}%)")


conn.close()
