# PD - Desafio Analítico

# Visão Geral do Projeto

Este projeto consiste em uma análise completa de dados de um e-commerce. O objetivo é transformar dados em estratégias para o negócio, identificando padrões de consumo, segmentando clientes e prevendo tendências de vendas.

# Estrutura do Repositório

PD - Desafio Analítico/
│  
├── dados/  
│ ├── ecommerce.db # Banco de dados SQLite  
│ ├── vendas_powerbi_final.csv # Dataset tratado para o PowerBI  
│ └── analise_rfm.csv # Análise RFM de cada cliente  
│  
├── imagens/  
│ ├── grafico_reglinear.png # Gráfico da regressão linear  
│ ├── graficos_dispersao.png # Gráficos de dispersão quantidade/preco e quantidade/preco_total  
│ ├── matriz_correlacao.png # Matriz de correlação quantidade/preco/preco_total  
│ ├── outliers_boxplot.png # Boxplot dos outliers quantidade/preco/preco_total  
│ └── rfm_segmentacao.png # Gráficos de segmentação RFM  
│  
├── relatorios/  
│ ├── Análise Exploratória.pdf # Resultados do script da análise exploratória  
│ ├── Relatório Previsão de Vendas.pdf # Resultados do modelo preditivo  
│ └── STORYTELLING E PRINCIPAIS INSIGHTS DO NEGÓCIO.pdf  
│  
├── scripts/  
│ ├── analise_exploratoria.py # script da análise exploratória (estatísticas descritivas, consultas SQL, outliers e correlação, segmentação de clientes e cálculo de KPIs)  
│ └── reg_linear.py # Script regressão linear para previsão de vendas  
│  
├── visualizacao/  
│ └── Desafio Final - PD.pbix # Dashboard Power BI  
│  
├── .gitattributes  
├── README.md  
└── requirements.txt  


# Ferramentas Utilizadas

Python - Análise de dados, ETL, modelagem  
Pandas/NumPy - Manipulação de dados  
Matplotlib/Seaborn - Visualizações estáticas  
Scikit-learn - Regressão linear  
SQLite - Banco de dados relacional  
Power BI - Dashboard interativo  
GitHub - Versionamento  

# Como Executar o Projeto

1 - Clone o repositório  
git clone https://github.com/julhaea/PD-Desafio-Analitico.git  
cd PD-Desafio-Analitico  

2 - Crie e ative o ambiente virtual
python -m venv venv  
venv\Scripts\activate  

3 - Instale as dependências  
pip install -r requirements.txt  

4 - Execute as análises  
python scripts/analise_exploratoria.py  
python scripts/reg_linear.py  

5 - Abra o dashboard  
Abra o Power BI Desktop e carregue o arquivo: visualizacao/Desafio Final - PD.pbix  