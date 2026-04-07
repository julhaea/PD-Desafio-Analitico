import pandas as pd
import sqlite3
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from datetime import datetime, timedelta

print("PREVISÃO DE VENDAS")

conn = sqlite3.connect('../dados/ecommerce.db')
df = pd.read_sql_query("SELECT * FROM vendas", conn)

df['data_compra'] = pd.to_datetime(df['data_compra'], format='%d-%m-%Y')

df_mensal = df.groupby(df['data_compra'].dt.to_period('M')).agg({
    'preco_total': 'sum',
    'id_compra': 'count'
}).reset_index()
df_mensal.columns = ['mes', 'faturamento', 'qtd_vendas']

df_mensal['mes_num'] = range(1, len(df_mensal) + 1)


X = df_mensal[['mes_num']].values
y = df_mensal['faturamento'].values

modelo = LinearRegression()
modelo.fit(X, y)

print(f"\nCoeficiente (inclinação): R$ {modelo.coef_[0]:,.2f} por mês")
print(f"Intercepto (ponto de partida): R$ {modelo.intercept_:,.2f}")

ultimo_mes = df_mensal['mes_num'].max()
ultima_data = df_mensal['mes'].iloc[-1].start_time

meses_futuros = np.array(range(ultimo_mes + 1, ultimo_mes + 3 + 1)).reshape(-1, 1)
previsoes = modelo.predict(meses_futuros)

datas_futuras = []
for i in range(3):
    nova_data = ultima_data + timedelta(days=32 * (i + 1))
    datas_futuras.append(nova_data.strftime('%b/%Y'))

print(f"\nPrevisão para os próximos 3 meses:")
for i, (data, prev) in enumerate(zip(datas_futuras, previsoes)):
    print(f"   {data}: R$ {prev:,.2f}")

# 5. AVALIAR O MODELO
print("\nAnálise do modelo preditivo:")
y_pred = modelo.predict(X)
mae = mean_absolute_error(y, y_pred)
r2 = r2_score(y, y_pred)

print(f"   R² (coeficiente de determinação): {r2:.3f}")
print(f"   MAE (média de erro): R$ {mae:,.2f}")

fig, ax = plt.subplots(figsize=(14, 7))

# Converter períodos para string para o gráfico
meses_str = [m.strftime('%b/%Y') for m in df_mensal['mes'].dt.to_timestamp()]
meses_previsao_str = datas_futuras

# Plotar histórico
ax.plot(meses_str, y, 'o-', label='Histórico (Real)', color='#3498db', linewidth=2, markersize=4)

# Plotar previsões
ax.plot(meses_previsao_str, previsoes, 'o-', label='Previsão', color='#e74c3c', linewidth=2, markersize=6)

# Linha de tendência (regressão)
linha_tendencia = modelo.predict(X)
ax.plot(meses_str, linha_tendencia, '--', label='Linha de Tendência', color='#2ecc71', linewidth=1.5, alpha=0.7)

# Destacar os últimos 6 meses
ultimos_6 = meses_str[-6:]
ultimos_6_valores = y[-6:]
ax.scatter(ultimos_6, ultimos_6_valores, color='orange', s=80, zorder=5, label='Últimos 6 meses')

# Configurar gráfico
ax.set_xlabel('Período', fontsize=12)
ax.set_ylabel('Faturamento (R$)', fontsize=12)
ax.set_title('Previsão de Vendas - Regressão Linear\nDados de 2022 a 2025', fontsize=14, fontweight='bold')
ax.legend(loc='upper left')
ax.grid(True, alpha=0.3)
plt.xticks(rotation=45, ha='right')

# Adicionar anotação com métricas
texto_metricas = f'R² = {r2:.3f}\nMAE = R$ {mae:,.0f}\nTendência: +R$ {modelo.coef_[0]:,.0f}/mês'
ax.text(0.01, 0.80, texto_metricas, transform=ax.transAxes, fontsize=10,
        verticalalignment='top', 
        bbox=dict(boxstyle='round', facecolor='white', alpha=0.9, edgecolor='gray'))

plt.tight_layout()
plt.savefig('../imagens/grafico_reglinear.png', dpi=300, bbox_inches='tight')
print("\nGráfico gerado: ../imagens/grafico_reglinear.png")
