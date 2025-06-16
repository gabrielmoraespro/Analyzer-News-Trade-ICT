import sys
import json
from datetime import datetime, timedelta
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QTableWidget, QTableWidgetItem, 
                             QPushButton, QTextEdit, QLabel, QFrame, 
                             QScrollArea, QGroupBox, QGridLayout, QComboBox,
                             QDateEdit, QHeaderView, QMessageBox)
from PyQt5.QtCore import Qt, QDate, QThread, pyqtSignal
from PyQt5.QtGui import QFont, QColor, QPalette

# Configurações de análise de notícias
NEWS_IMPACT_DATABASE = {
    # Decisões de Juros
    "Interest Rate Decision": {
        "impact": "HIGH",
        "currencies": ["USD", "EUR", "GBP", "JPY", "AUD", "CAD", "CHF", "NZD"],
        "description": "Decisões de taxa de juros impactam diretamente a moeda",
        "trading_strategy": "Aguardar breakout após confirmação da decisão"
    },
    "BoJ Interest Rate": {
        "impact": "HIGH",
        "currencies": ["JPY"],
        "pairs_affected": ["USDJPY", "EURJPY", "GBPJPY", "AUDJPY", "CADJPY"],
        "description": "Banco do Japão - impacto direto no JPY"
    },
    "FOMC Rate Decision": {
        "impact": "VERY_HIGH",
        "currencies": ["USD"],
        "pairs_affected": ["EURUSD", "GBPUSD", "USDJPY", "USDCHF", "USDCAD", "AUDUSD", "NZDUSD"],
        "description": "Federal Reserve - maior impacto no USD"
    },
    
    # Indicadores Econômicos
    "Empire State Manufacturing Index": {
        "impact": "MEDIUM",
        "currencies": ["USD"],
        "pairs_affected": ["EURUSD", "GBPUSD", "USDJPY"],
        "description": "Indicador de manufatura de NY - impacto moderado no USD"
    },
    "Non-Farm Payrolls": {
        "impact": "VERY_HIGH",
        "currencies": ["USD"],
        "pairs_affected": ["EURUSD", "GBPUSD", "USDJPY", "USDCHF", "USDCAD"],
        "description": "Dados de emprego dos EUA - impacto muito alto no USD"
    },
    "CPI": {
        "impact": "HIGH",
        "currencies": ["USD", "EUR", "GBP"],
        "description": "Índice de preços ao consumidor - impacto na inflação"
    },
    "GDP": {
        "impact": "HIGH",
        "currencies": ["USD", "EUR", "GBP", "JPY", "AUD", "CAD"],
        "description": "Produto Interno Bruto - indicador de crescimento econômico"
    },
    "PMI": {
        "impact": "MEDIUM",
        "currencies": ["USD", "EUR", "GBP"],
        "description": "Índice de Gerentes de Compras - indicador de atividade econômica"
    },
    
    # Commodities
    "Oil Inventories": {
        "impact": "MEDIUM",
        "instruments": ["XAUUSD", "USDCAD"],
        "description": "Estoques de petróleo - impacto em CAD e ouro"
    },
    "Gold": {
        "impact": "HIGH",
        "instruments": ["XAUUSD"],
        "description": "Notícias relacionadas ao ouro"
    },
    
    # Índices
    "Retail Sales": {
        "impact": "HIGH",
        "currencies": ["USD"],
        "indices": ["US30", "SPX500", "NAS100"],
        "description": "Vendas no varejo - impacto em índices americanos"
    }
}

# Sessões de trading
TRADING_SESSIONS = {
    "London": {"start": "03:00", "end": "12:00", "timezone": "EST"},
    "NY_AM": {"start": "08:00", "end": "12:00", "timezone": "EST"},
    "NY_PM": {"start": "13:00", "end": "17:00", "timezone": "EST"},
    "Overlap": {"start": "08:00", "end": "12:00", "timezone": "EST"}
}

# Pares de moedas
FOREX_PAIRS = {
    "majors": ["EURUSD", "GBPUSD", "USDJPY", "USDCHF", "USDCAD", "AUDUSD", "NZDUSD"],
    "secondary": ["EURJPY", "GBPJPY", "EURGBP", "AUDJPY", "EURAUD", "GBPAUD", "CADJPY"]
}

COMMODITIES = ["XAUUSD", "XAGUSD", "USOIL", "UKOIL"]
INDICES = ["US30", "SPX500", "NAS100", "GER30", "UK100"]

class NewsAnalyzer:
    def __init__(self):
        self.news_data = []
        
    def add_news(self, news_item):
        self.news_data.append(news_item)
        
    def analyze_confluence(self, date):
        """Analisa confluência de notícias para uma data específica"""
        daily_news = [news for news in self.news_data if news['date'] == date]
        
        if not daily_news:
            return {"error": "Nenhuma notícia encontrada para esta data"}
            
        # Análise de impacto
        high_impact_news = []
        medium_impact_news = []
        currencies_affected = set()
        pairs_affected = set()
        instruments_affected = set()
        
        for news in daily_news:
            impact_info = self.get_news_impact(news['name'])
            if impact_info:
                news['impact_info'] = impact_info
                
                if impact_info['impact'] in ['VERY_HIGH', 'HIGH']:
                    high_impact_news.append(news)
                elif impact_info['impact'] == 'MEDIUM':
                    medium_impact_news.append(news)
                    
                # Coletar moedas e pares afetados
                if 'currencies' in impact_info:
                    currencies_affected.update(impact_info['currencies'])
                if 'pairs_affected' in impact_info:
                    pairs_affected.update(impact_info['pairs_affected'])
                if 'instruments' in impact_info:
                    instruments_affected.update(impact_info['instruments'])
        
        # Determinar melhor estratégia
        strategy = self.determine_trading_strategy(high_impact_news, medium_impact_news, 
                                                 currencies_affected, pairs_affected)
        
        return {
            "date": date,
            "high_impact_news": high_impact_news,
            "medium_impact_news": medium_impact_news,
            "currencies_affected": list(currencies_affected),
            "pairs_affected": list(pairs_affected),
            "instruments_affected": list(instruments_affected),
            "strategy": strategy
        }
    
    def get_news_impact(self, news_name):
        """Identifica o impacto de uma notícia específica"""
        for key, value in NEWS_IMPACT_DATABASE.items():
            if key.lower() in news_name.lower():
                return value
        return None
    
    def determine_trading_strategy(self, high_impact, medium_impact, currencies, pairs):
        """Determina a melhor estratégia de trading baseada na confluência"""
        strategy = {
            "recommended_pairs": [],
            "avoid_pairs": [],
            "recommended_instruments": [],
            "session_focus": [],
            "risk_level": "MEDIUM",
            "notes": []
        }
        
        if len(high_impact) >= 2:
            strategy["risk_level"] = "HIGH"
            strategy["notes"].append("Múltiplas notícias de alto impacto - volatilidade esperada")
            
        # Recomendar pares baseado nas moedas afetadas
        if "USD" in currencies:
            if len([n for n in high_impact if "USD" in str(n.get('impact_info', {}).get('currencies', []))]) >= 2:
                strategy["recommended_pairs"].extend(["EURUSD", "GBPUSD", "USDJPY"])
                strategy["session_focus"].append("NY_AM")
                
        if "JPY" in currencies:
            strategy["recommended_pairs"].extend(["USDJPY", "EURJPY", "GBPJPY"])
            strategy["session_focus"].append("London")
            
        # Evitar pares com conflito de notícias
        conflicting_pairs = []
        for pair in FOREX_PAIRS["majors"] + FOREX_PAIRS["secondary"]:
            base_currency = pair[:3]
            quote_currency = pair[3:]
            if base_currency in currencies and quote_currency in currencies:
                conflicting_pairs.append(pair)
                
        strategy["avoid_pairs"] = conflicting_pairs
        
        # Remover duplicatas
        strategy["recommended_pairs"] = list(set(strategy["recommended_pairs"]))
        
        return strategy

class TradingAnalyzerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.news_analyzer = NewsAnalyzer()
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("Analisador de Notícias para Trading - ICT Setup")
        self.setGeometry(100, 100, 1400, 900)
        
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)
        
        # Título
        title = QLabel("🔍 ANALISADOR DE NOTÍCIAS PARA TRADING")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setStyleSheet("color: #2E86AB; margin: 10px; padding: 10px;")
        main_layout.addWidget(title)
        
        # Layout horizontal para input e análise
        content_layout = QHBoxLayout()
        
        # Seção de input de notícias
        input_section = self.create_input_section()
        content_layout.addWidget(input_section, 1)
        
        # Seção de análise e resultados
        analysis_section = self.create_analysis_section()
        content_layout.addWidget(analysis_section, 2)
        
        main_layout.addLayout(content_layout)
        
        # Aplicar estilo
        self.apply_styles()
        
    def create_input_section(self):
        """Cria seção de input de notícias"""
        group = QGroupBox("📰 Input de Notícias")
        layout = QVBoxLayout()
        
        # Data seleção
        date_layout = QHBoxLayout()
        date_layout.addWidget(QLabel("Data:"))
        self.date_edit = QDateEdit()
        self.date_edit.setDate(QDate.currentDate())
        self.date_edit.setCalendarPopup(True)
        date_layout.addWidget(self.date_edit)
        layout.addLayout(date_layout)
        
        # Tabela de notícias
        self.news_table = QTableWidget()
        self.news_table.setColumnCount(4)
        self.news_table.setHorizontalHeaderLabels(["Notícia", "Previous", "Consensus", "Horário"])
        self.news_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.news_table.setRowCount(10)  # Começar com 10 linhas
        layout.addWidget(self.news_table)
        
        # Botões
        button_layout = QHBoxLayout()
        
        add_row_btn = QPushButton("➕ Adicionar Linha")
        add_row_btn.clicked.connect(self.add_news_row)
        button_layout.addWidget(add_row_btn)
        
        clear_btn = QPushButton("🗑️ Limpar")
        clear_btn.clicked.connect(self.clear_news_table)
        button_layout.addWidget(clear_btn)
        
        analyze_btn = QPushButton("🔍 ANALISAR")
        analyze_btn.clicked.connect(self.analyze_news)
        analyze_btn.setStyleSheet("background-color: #28a745; color: white; font-weight: bold; padding: 10px;")
        button_layout.addWidget(analyze_btn)
        
        layout.addLayout(button_layout)
        
        group.setLayout(layout)
        return group
        
    def create_analysis_section(self):
        """Cria seção de análise e resultados"""
        group = QGroupBox("📊 Análise e Recomendações")
        layout = QVBoxLayout()
        
        # Área de resultados com scroll
        scroll_area = QScrollArea()
        scroll_widget = QWidget()
        self.results_layout = QVBoxLayout()
        scroll_widget.setLayout(self.results_layout)
        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)
        
        layout.addWidget(scroll_area)
        group.setLayout(layout)
        
        # Inicializar com mensagem
        self.show_initial_message()
        
        return group
        
    def show_initial_message(self):
        """Mostra mensagem inicial"""
        msg = QLabel("📝 Adicione as notícias do dia e clique em 'ANALISAR' para obter recomendações de trading.")
        msg.setAlignment(Qt.AlignCenter)
        msg.setStyleSheet("color: #666; font-size: 14px; padding: 20px;")
        self.results_layout.addWidget(msg)
        
    def add_news_row(self):
        """Adiciona uma nova linha à tabela de notícias"""
        current_rows = self.news_table.rowCount()
        self.news_table.insertRow(current_rows)
        
    def clear_news_table(self):
        """Limpa a tabela de notícias"""
        self.news_table.setRowCount(0)
        self.news_table.setRowCount(10)
        
    def analyze_news(self):
        """Analisa as notícias inseridas"""
        # Limpar resultados anteriores
        self.clear_results()
        
        # Coletar dados da tabela
        news_data = []
        selected_date = self.date_edit.date().toString("yyyy-MM-dd")
        
        for row in range(self.news_table.rowCount()):
            news_item = self.news_table.item(row, 0)
            previous_item = self.news_table.item(row, 1)
            consensus_item = self.news_table.item(row, 2)
            time_item = self.news_table.item(row, 3)
            
            if news_item and news_item.text().strip():
                news_data.append({
                    "name": news_item.text().strip(),
                    "previous": previous_item.text().strip() if previous_item else "",
                    "consensus": consensus_item.text().strip() if consensus_item else "",
                    "time": time_item.text().strip() if time_item else "",
                    "date": selected_date
                })
        
        if not news_data:
            QMessageBox.warning(self, "Aviso", "Por favor, adicione pelo menos uma notícia para análise.")
            return
            
        # Limpar dados anteriores e adicionar novos
        self.news_analyzer.news_data = news_data
        
        # Executar análise
        analysis = self.news_analyzer.analyze_confluence(selected_date)
        
        # Mostrar resultados
        self.display_analysis_results(analysis)
        
    def clear_results(self):
        """Limpa os resultados anteriores"""
        for i in reversed(range(self.results_layout.count())):
            child = self.results_layout.itemAt(i).widget()
            if child:
                child.setParent(None)
                
    def display_analysis_results(self, analysis):
        """Exibe os resultados da análise"""
        if "error" in analysis:
            error_label = QLabel(f"❌ {analysis['error']}")
            error_label.setStyleSheet("color: red; font-size: 14px;")
            self.results_layout.addWidget(error_label)
            return
            
        # Cabeçalho
        header = QLabel(f"📅 ANÁLISE PARA {analysis['date']}")
        header.setFont(QFont("Arial", 14, QFont.Bold))
        header.setStyleSheet("color: #2E86AB; padding: 10px; border-bottom: 2px solid #2E86AB;")
        self.results_layout.addWidget(header)
        
        # Notícias de alto impacto
        if analysis['high_impact_news']:
            high_impact_frame = self.create_news_frame("🔴 NOTÍCIAS DE ALTO IMPACTO", 
                                                     analysis['high_impact_news'], "#dc3545")
            self.results_layout.addWidget(high_impact_frame)
            
        # Notícias de médio impacto
        if analysis['medium_impact_news']:
            medium_impact_frame = self.create_news_frame("🟡 NOTÍCIAS DE MÉDIO IMPACTO", 
                                                       analysis['medium_impact_news'], "#ffc107")
            self.results_layout.addWidget(medium_impact_frame)
            
        # Estratégia recomendada
        strategy_frame = self.create_strategy_frame(analysis['strategy'])
        self.results_layout.addWidget(strategy_frame)
        
        # Adicionar espaçador
        self.results_layout.addStretch()
        
    def create_news_frame(self, title, news_list, color):
        """Cria frame para exibir notícias"""
        frame = QFrame()
        frame.setFrameStyle(QFrame.Box)
        frame.setStyleSheet(f"border: 2px solid {color}; border-radius: 5px; margin: 5px;")
        
        layout = QVBoxLayout()
        
        # Título
        title_label = QLabel(title)
        title_label.setFont(QFont("Arial", 12, QFont.Bold))
        title_label.setStyleSheet(f"color: {color}; padding: 5px;")
        layout.addWidget(title_label)
        
        # Lista de notícias
        for news in news_list:
            news_widget = QWidget()
            news_layout = QVBoxLayout()
            
            # Nome da notícia
            name_label = QLabel(f"📰 {news['name']}")
            name_label.setFont(QFont("Arial", 10, QFont.Bold))
            news_layout.addWidget(name_label)
            
            # Informações adicionais
            if 'impact_info' in news:
                impact_info = news['impact_info']
                info_text = f"💡 {impact_info.get('description', '')}"
                info_label = QLabel(info_text)
                info_label.setWordWrap(True)
                info_label.setStyleSheet("color: #666; font-size: 9px;")
                news_layout.addWidget(info_label)
                
            # Dados Previous/Consensus
            if news['previous'] or news['consensus']:
                data_text = f"📊 Previous: {news['previous']} | Consensus: {news['consensus']}"
                data_label = QLabel(data_text)
                data_label.setStyleSheet("color: #333; font-size: 9px;")
                news_layout.addWidget(data_label)
                
            news_widget.setLayout(news_layout)
            layout.addWidget(news_widget)
            
        frame.setLayout(layout)
        return frame
        
    def create_strategy_frame(self, strategy):
        """Cria frame com estratégia recomendada"""
        frame = QFrame()
        frame.setFrameStyle(QFrame.Box)
        frame.setStyleSheet("border: 2px solid #28a745; border-radius: 5px; margin: 5px; background-color: #f8f9fa;")
        
        layout = QVBoxLayout()
        
        # Título
        title_label = QLabel("🎯 ESTRATÉGIA RECOMENDADA - SETUP ICT")
        title_label.setFont(QFont("Arial", 14, QFont.Bold))
        title_label.setStyleSheet("color: #28a745; padding: 10px; text-align: center;")
        layout.addWidget(title_label)
        
        # Grid para organizar informações
        grid_layout = QGridLayout()
        
        # Pares recomendados
        if strategy['recommended_pairs']:
            rec_pairs_label = QLabel("✅ PARES RECOMENDADOS:")
            rec_pairs_label.setFont(QFont("Arial", 10, QFont.Bold))
            grid_layout.addWidget(rec_pairs_label, 0, 0)
            
            pairs_text = ", ".join(strategy['recommended_pairs'])
            pairs_value = QLabel(pairs_text)
            pairs_value.setStyleSheet("color: #28a745; font-weight: bold;")
            grid_layout.addWidget(pairs_value, 0, 1)
            
        # Pares a evitar
        if strategy['avoid_pairs']:
            avoid_pairs_label = QLabel("❌ PARES A EVITAR:")
            avoid_pairs_label.setFont(QFont("Arial", 10, QFont.Bold))
            grid_layout.addWidget(avoid_pairs_label, 1, 0)
            
            avoid_text = ", ".join(strategy['avoid_pairs'])
            avoid_value = QLabel(avoid_text)
            avoid_value.setStyleSheet("color: #dc3545; font-weight: bold;")
            grid_layout.addWidget(avoid_value, 1, 1)
            
        # Sessões de foco
        if strategy['session_focus']:
            session_label = QLabel("⏰ SESSÕES DE FOCO:")
            session_label.setFont(QFont("Arial", 10, QFont.Bold))
            grid_layout.addWidget(session_label, 2, 0)
            
            session_text = ", ".join(strategy['session_focus'])
            session_value = QLabel(session_text)
            session_value.setStyleSheet("color: #007bff; font-weight: bold;")
            grid_layout.addWidget(session_value, 2, 1)
            
        # Nível de risco
        risk_label = QLabel("⚠️ NÍVEL DE RISCO:")
        risk_label.setFont(QFont("Arial", 10, QFont.Bold))
        grid_layout.addWidget(risk_label, 3, 0)
        
        risk_colors = {"LOW": "#28a745", "MEDIUM": "#ffc107", "HIGH": "#dc3545"}
        risk_value = QLabel(strategy['risk_level'])
        risk_value.setStyleSheet(f"color: {risk_colors.get(strategy['risk_level'], '#333')}; font-weight: bold;")
        grid_layout.addWidget(risk_value, 3, 1)
        
        layout.addLayout(grid_layout)
        
        # Notas adicionais
        if strategy['notes']:
            notes_label = QLabel("📝 NOTAS IMPORTANTES:")
            notes_label.setFont(QFont("Arial", 10, QFont.Bold))
            layout.addWidget(notes_label)
            
            for note in strategy['notes']:
                note_label = QLabel(f"• {note}")
                note_label.setWordWrap(True)
                note_label.setStyleSheet("color: #666; margin-left: 20px;")
                layout.addWidget(note_label)
                
        # Dica ICT
        ict_tip = QLabel("💡 DICA ICT: Aguarde formação de estrutura de mercado e confluência com zonas de liquidez antes de entrar no trade. Respeite os horários de kill zone para maior probabilidade de sucesso.")
        ict_tip.setWordWrap(True)
        ict_tip.setStyleSheet("background-color: #e7f3ff; border: 1px solid #007bff; border-radius: 3px; padding: 10px; margin: 10px; color: #004085;")
        layout.addWidget(ict_tip)
        
        frame.setLayout(layout)
        return frame
        
    def apply_styles(self):
        """Aplica estilos à aplicação"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f8f9fa;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #dee2e6;
                border-radius: 5px;
                margin: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
            QTableWidget {
                gridline-color: #dee2e6;
                background-color: white;
                border: 1px solid #dee2e6;
                border-radius: 3px;
            }
            QTableWidget::item {
                padding: 5px;
            }
            QPushButton {
                background-color: #007bff;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
            QPushButton:pressed {
                background-color: #004085;
            }
            QDateEdit {
                padding: 5px;
                border: 1px solid #dee2e6;
                border-radius: 3px;
            }
        """)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TradingAnalyzerApp()
    window.show()
    sys.exit(app.exec_())
