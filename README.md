# 📈 Trading News Analyzer - ICT Setup

Aplicação Python para análise automatizada de notícias econômicas e recomendações de trading baseadas na confluência de eventos do mesmo dia.

## 🚀 Características

- **Interface PyQt5** moderna e intuitiva
- **Análise de confluência** de múltiplas notícias do dia
- **Recomendações automáticas** de pares forex, commodities e futuros
- **Estratégia ICT** integrada com identificação de kill zones
- **15+ tipos de notícias** econômicas pré-configuradas

## 📦 Instalação

```bash
# Instalar dependências
pip install PyQt5

# Executar aplicação
python trading_analyzer.py
```

## 💡 Como Usar

1. **Selecione a data** de trading
2. **Adicione as notícias** do dia na tabela:
   - Nome da notícia (ex: "Japan BoJ Interest Rate Decision")
   - Previous (valor anterior)
   - Consensus (consenso esperado)
   - Horário (opcional)
3. **Clique em ANALISAR**
4. **Receba recomendações**:
   - Pares forex recomendados/evitar
   - Sessões ideais (London, NY AM, NY PM, Overlap)
   - Nível de risco calculado
   - Dicas ICT específicas

## 🎯 Instrumentos Suportados

### Forex
- **Majors**: EURUSD, GBPUSD, USDJPY, USDCHF, USDCAD, AUDUSD, NZDUSD
- **Secundários**: EURJPY, GBPJPY, EURGBP, AUDJPY, EURAUD, GBPAUD, CADJPY

### Commodities
- **XAUUSD** (Ouro)

### Futuros
- **US30** (Dow Jones)
- **SPX500** (S&P 500)
- **NAS100** (Nasdaq)

## 📊 Tipos de Notícias Analisadas

- **Decisões de Juros** (Fed, BoJ, ECB, BoE)
- **Indicadores de Emprego** (NFP, Unemployment Rate)
- **Inflação** (CPI, PPI)
- **PIB e Crescimento**
- **PMI e Indicadores de Manufatura**
- **Vendas no Varejo**
- **Dados de Commodities**

## ⚡ Exemplo de Uso

```
Data: 2025-06-16
Notícias:
1. Japan BoJ Interest Rate Decision | Previous: 0.25% | Consensus: 0.25%
2. US Empire State Manufacturing Index | Previous: 15.6 | Consensus: 16.2

Resultado:
✅ Pares Recomendados: USDJPY, EURJPY
⏰ Sessões: London, NY AM
⚠️ Risco: HIGH (múltiplas notícias de impacto)
```

## 🔥 Funcionalidades Avançadas

- **Confluência Automática**: Identifica quando múltiplas notícias afetam o mesmo par
- **Prevenção de Whipsaw**: Evita pares com conflito de notícias (ex: EUR e USD ambos com high impact)
- **Sessões Otimizadas**: Recomenda horários específicos baseados no tipo de notícia
- **ICT Integration**: Dicas sobre estrutura de mercado e zonas de liquidez

## 🛠️ Requisitos

- Python 3.6+
- PyQt5
- Sistema operacional: Windows, macOS, Linux

## 📝 Notas

- Aplicação funciona **offline** após instalação
- Base de dados de impacto **pré-configurada** e expansível
- Interface **responsiva** com scroll automático
- **Múltiplas análises** por sessão suportadas

---

**Desenvolvido para traders que utilizam metodologia ICT e buscam confluência de notícias econômicas para maximizar probabilidade de sucesso nos trades.**
