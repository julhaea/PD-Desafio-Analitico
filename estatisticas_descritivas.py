import pandas as pd
import sqlite3

print("\nESTATÍSTICAS DESCRITIVAS")

conn = sqlite3.connect('ecommerce.db')
cursor = conn.cursor()

# características da tabela
cursor.execute("PRAGMA table_info(vendas)")
colunas = cursor.fetchall()

print("\n-Estrutura da Tabela:")
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

print("\n-Período Analisado:")

print(f"\nData inicial: {data_min}")
print(f"Data final: {data_max}")
print(f"Total de dias analisados: {dias_totais}")


# vendas por ano
print("\n-Vendas por ano analisado:")
anos = df['data_dt'].dt.year.value_counts().sort_index()
for ano, qtd in anos.items():
    percentual = round(qtd / len(df) * 100, 1)
    print(f"   {ano}: {qtd} vendas ({percentual}%)")


#características das vendas
print("\n-Métricas Vendas")

faturamento_total = df['preco_total'].sum()
print(f"\nFaturamento total: R$ {faturamento_total:,.2f}")

ticket_medio = df['preco_total'].mean()
print(f"Ticket médio por compra: R$ {ticket_medio:.2f}")

itens_vendidos = df['quantidade'].sum()
print(f"Total de itens vendidos: {itens_vendidos:,}")

preco_medio = df['preco'].mean()
print(f" Preço médio dos produtos: R$ {preco_medio:.2f}")

#características dos clientes
print("\n-Métricas Clientes")

clientes_unicos = df['id_cliente_unico'].nunique()
print(f"\nTotal de clientes únicos: {clientes_unicos:,}")

ticket_por_cliente = df.groupby('id_cliente_unico')['preco_total'].sum().mean()
print(f"Gasto médio por cliente: R$ {ticket_por_cliente:.2f}")

#características das categorias
print("\n-Métricas Categorias")

cat_faturamento = df.groupby('categoria').agg({
    'preco_total': 'sum',
    'id_compra': 'count',
    'quantidade': 'sum',
    'preco': 'mean'
}).round(2)
cat_faturamento.columns = ['faturamento', 'qtd_vendas', 'itens_vendidos', 'preco_medio']
cat_faturamento = cat_faturamento.sort_values('faturamento', ascending=False)
cat_faturamento['percentual_faturamento'] = (cat_faturamento['faturamento'] / faturamento_total * 100).round(1)
print(f"\n {cat_faturamento.to_string()}")

#características dos estados
print("\n-Métricas Estados\n")

estado_faturamento = df.groupby('estado').agg({
    'preco_total': 'sum',
    'id_compra': 'count',
    'id_cliente_unico': 'nunique'
}).round(2)
estado_faturamento.columns = ['faturamento', 'qtd_vendas', 'clientes']
estado_faturamento = estado_faturamento.sort_values('faturamento', ascending=False)
estado_faturamento['percentual_faturamento'] = (estado_faturamento['faturamento'] / faturamento_total * 100).round(1)
print(estado_faturamento.to_string())
