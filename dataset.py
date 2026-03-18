import pandas as pd
import sqlite3

print("=" * 70)
print("📊 ESTATÍSTICAS DESCRITIVAS - ANÁLISE COMPLETA")
print("=" * 70)

# 1. CONECTAR AO BANCO
conn = sqlite3.connect('ecommerce.db')
cursor = conn.cursor()

print("\n📂 CONEXÃO ESTABELECIDA COM O BANCO")
print("-" * 50)

# 2. ESTRUTURA DO BANCO DE DADOS
print("\n🏗️  ESTRUTURA DO BANCO DE DADOS")
print("-" * 50)

# Listar tabelas
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tabelas = cursor.fetchall()
print(f"📌 Tabelas encontradas: {[tabela[0] for tabela in tabelas]}")

# Estrutura da tabela vendas
cursor.execute("PRAGMA table_info(vendas)")
colunas = cursor.fetchall()
print("\n📋 ESTRUTURA DA TABELA 'vendas':")
print(f"{'Coluna':<25} {'Tipo':<15} {'Nulo':<10} {'PK'}")
print("-" * 60)
for col in colunas:
    nome, tipo, nulo, pk = col[1], col[2], 'SIM' if col[3] else 'NÃO', 'SIM' if col[5] else ''
    print(f"{nome:<25} {tipo:<15} {nulo:<10} {pk}")

# 3. CARREGAR OS DADOS
print("\n📂 CARREGANDO DADOS...")
df = pd.read_sql_query("SELECT * FROM vendas", conn)
print(f"✅ Total de registros carregados: {len(df):,} linhas")
print(f"✅ Total de colunas: {len(df.columns)}")

print("\n" + "=" * 70)
print("📌 1. INFORMAÇÕES GERAIS DO DATASET")
print("=" * 70)

# Período dos dados
data_min = df['data_compra'].min()
data_max = df['data_compra'].max()
print(f"📅 PERÍODO ANALISADO: {data_min} a {data_max}")
print(f"   Total de dias: {(pd.to_datetime(data_max, format='%d-%m-%Y') - pd.to_datetime(data_min, format='%d-%m-%Y')).days} dias")

# Tipos de dados
print("\n📋 TIPOS DE DADOS POR COLUNA:")
print(df.dtypes.to_string())

# Valores nulos
print("\n🔍 VALORES NULOS POR COLUNA:")
nulos = df.isnull().sum()
print(nulos[nulos > 0] if any(nulos > 0) else "Nenhum valor nulo encontrado!")

print("\n" + "=" * 70)
print("📌 2. MÉTRICAS GERAIS DE NEGÓCIO")
print("=" * 70)

# Faturamento total
faturamento_total = df['preco_total'].sum()
print(f"💰 Faturamento total: R$ {faturamento_total:,.2f}")

# Ticket médio
ticket_medio = df['preco_total'].mean()
print(f"🎫 Ticket médio por venda: R$ {ticket_medio:.2f}")

# Total de itens vendidos
itens_vendidos = df['quantidade'].sum()
print(f"📦 Total de itens vendidos: {itens_vendidos:,}")

# Média de itens por compra
media_itens = df['quantidade'].mean()
print(f"📊 Média de itens por compra: {media_itens:.2f}")

# Preço médio dos produtos
preco_medio = df['preco'].mean()
print(f"🏷️  Preço médio dos produtos: R$ {preco_medio:.2f}")

print("\n" + "=" * 70)
print("👥 3. MÉTRICAS DE CLIENTES")
print("=" * 70)

# Clientes únicos
clientes_unicos = df['id_cliente_unico'].nunique()
print(f"👤 Total de clientes únicos: {clientes_unicos:,}")

# Compras por cliente (média)
compras_por_cliente = len(df) / clientes_unicos
print(f"🔄 Média de compras por cliente: {compras_por_cliente:.2f}")

# Ticket médio por cliente
ticket_por_cliente = df.groupby('id_cliente_unico')['preco_total'].sum().mean()
print(f"💰 Gasto médio por cliente: R$ {ticket_por_cliente:.2f}")

# Cliente que mais comprou
top_cliente = df.groupby('id_cliente_unico').agg({
    'preco_total': 'sum',
    'id_compra': 'count'
}).sort_values('preco_total', ascending=False).iloc[0]
print(f"🏆 Cliente top (maior gasto): R$ {top_cliente['preco_total']:,.2f} em {top_cliente['id_compra']} compras")

print("\n" + "=" * 70)
print("🏷️ 4. MÉTRICAS POR CATEGORIA (TOP 5)")
print("=" * 70)

# Faturamento por categoria
cat_faturamento = df.groupby('categoria').agg({
    'preco_total': 'sum',
    'id_compra': 'count',
    'quantidade': 'sum',
    'preco': 'mean'
}).round(2)
cat_faturamento.columns = ['faturamento', 'qtd_vendas', 'itens_vendidos', 'preco_medio']
cat_faturamento = cat_faturamento.sort_values('faturamento', ascending=False).head(5)
cat_faturamento['%_faturamento'] = (cat_faturamento['faturamento'] / faturamento_total * 100).round(1)
print(cat_faturamento.to_string())

print("\n" + "=" * 70)
print("📍 5. MÉTRICAS POR ESTADO (TOP 5)")
print("=" * 70)

# Faturamento por estado
estado_faturamento = df.groupby('estado').agg({
    'preco_total': 'sum',
    'id_compra': 'count',
    'id_cliente_unico': 'nunique'
}).round(2)
estado_faturamento.columns = ['faturamento', 'qtd_vendas', 'clientes']
estado_faturamento = estado_faturamento.sort_values('faturamento', ascending=False).head(5)
estado_faturamento['%_faturamento'] = (estado_faturamento['faturamento'] / faturamento_total * 100).round(1)
print(estado_faturamento.to_string())

print("\n" + "=" * 70)
print("💳 6. FORMAS DE PAGAMENTO")
print("=" * 70)

# Distribuição de pagamentos
pagamentos = df['forma_pagamento'].value_counts()
pagamentos_percent = (pagamentos / len(df) * 100).round(1)
pagamentos_df = pd.DataFrame({
    'quantidade': pagamentos,
    'percentual': pagamentos_percent
})
print(pagamentos_df.to_string())

print("\n" + "=" * 70)
print("🏆 7. TOP 10 PRODUTOS MAIS VENDIDOS")
print("=" * 70)

# Produtos mais vendidos
top_produtos = df.groupby(['nome_produto', 'categoria']).agg({
    'quantidade': 'sum',
    'preco_total': 'sum',
    'id_compra': 'count'
}).round(2)
top_produtos.columns = ['unidades_vendidas', 'faturamento', 'qtd_vendas']
top_produtos = top_produtos.sort_values('unidades_vendidas', ascending=False).head(10)
print(top_produtos.to_string())

print("\n" + "=" * 70)
print("📊 8. DISTRIBUIÇÃO DOS VALORES DE VENDA")
print("=" * 70)

# Estatísticas descritivas básicas do preco_total
print("📈 Estatísticas da variável 'preco_total':")
print(f"Média: R$ {df['preco_total'].mean():.2f}")
print(f"Mediana: R$ {df['preco_total'].median():.2f}")
print(f"Desvio padrão: R$ {df['preco_total'].std():.2f}")
print(f"Valor mínimo: R$ {df['preco_total'].min():.2f}")
print(f"Valor máximo: R$ {df['preco_total'].max():.2f}")
print(f"1º Quartil (25%): R$ {df['preco_total'].quantile(0.25):.2f}")
print(f"3º Quartil (75%): R$ {df['preco_total'].quantile(0.75):.2f}")

# Faixas de valor
print("\n📊 Distribuição por faixas de valor:")
faixas = [0, 50, 100, 200, 500, 1000, 5000, 10000]
labels = ['Até R$50', 'R$51-100', 'R$101-200', 'R$201-500', 'R$501-1000', 'R$1001-5000', 'Acima R$5000']
df['faixa_valor'] = pd.cut(df['preco_total'], bins=faixas, labels=labels)
distribuicao = df['faixa_valor'].value_counts().sort_index()
distribuicao_percent = (distribuicao / len(df) * 100).round(1)
faixas_df = pd.DataFrame({
    'quantidade': distribuicao,
    'percentual': distribuicao_percent
})
print(faixas_df.to_string())

print("\n" + "=" * 70)
print("📋 RESUMO EXECUTIVO")
print("=" * 70)

print(f"""
📅 PERÍODO ANALISADO: {data_min} a {data_max}

💰 FATURAMENTO TOTAL: R$ {faturamento_total:,.2f}
   • Ticket médio: R$ {ticket_medio:.2f}
   • {itens_vendidos} itens vendidos
   • Média de {media_itens:.1f} itens por compra

👥 CLIENTES: {clientes_unicos} clientes únicos
   • Cada cliente compra em média {compras_por_cliente:.1f} vezes
   • Gasto médio por cliente: R$ {ticket_por_cliente:.2f}
   • Cliente top gastou: R$ {top_cliente['preco_total']:,.2f}

🏷️ CATEGORIA DESTAQUE: {cat_faturamento.index[0]}
   • Faturamento: R$ {cat_faturamento.iloc[0]['faturamento']:,.2f}
   • {cat_faturamento['%_faturamento'].iloc[0]}% do total

📍 ESTADO DESTAQUE: {estado_faturamento.index[0]}
   • Faturamento: R$ {estado_faturamento.iloc[0]['faturamento']:,.2f}
   • {estado_faturamento['%_faturamento'].iloc[0]}% do total

💳 PAGAMENTO PREFERIDO: {pagamentos.index[0]}
   • Usado em {pagamentos_percent.iloc[0]}% das compras

📦 PRODUTO MAIS VENDIDO: {top_produtos.index[0][0]}
   • {top_produtos.iloc[0]['unidades_vendidas']} unidades vendidas
""")

# Salvar resumo em CSV
resumo = pd.DataFrame({
    'métrica': ['periodo_inicio', 'periodo_fim', 'faturamento_total', 'ticket_medio', 
                'itens_vendidos', 'clientes_unicos', 'compras_por_cliente', 
                'gasto_medio_cliente', 'categoria_top', 'estado_top', 'pagamento_top'],
    'valor': [data_min, data_max, faturamento_total, ticket_medio, 
              itens_vendidos, clientes_unicos, compras_por_cliente,
              ticket_por_cliente, cat_faturamento.index[0], estado_faturamento.index[0], 
              pagamentos.index[0]]
})
resumo.to_csv('resumo_executivo.csv', index=False)
print("\n💾 Resumo salvo em: resumo_executivo.csv")

# Fechar conexão
conn.close()
print("\n🔌 Conexão fechada.")
print("✅ Análise estatística concluída!")