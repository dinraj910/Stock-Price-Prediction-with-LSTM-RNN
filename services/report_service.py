"""
Report Service Module
=====================
Generates PDF and CSV reports for stock analysis.
"""

import logging
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path
import io
import csv

import pandas as pd

from app.config import Config

logger = logging.getLogger(__name__)


class ReportService:
    """Service for generating analysis reports."""
    
    def __init__(self):
        """Initialize the report service."""
        self.reports_dir = Config.REPORTS_DIR
        self.disclaimer = Config.DISCLAIMER
        Path(self.reports_dir).mkdir(parents=True, exist_ok=True)
    
    def generate_csv_report(
        self,
        ticker: str,
        forecast_data: Dict[str, Any],
        historical_data: pd.DataFrame,
        indicators: Dict[str, Any]
    ) -> io.StringIO:
        """
        Generate CSV report with forecast and analysis data.
        
        Args:
            ticker: Stock ticker symbol
            forecast_data: Forecast results
            historical_data: Historical price data
            indicators: Technical indicators
            
        Returns:
            StringIO buffer with CSV content
        """
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Header section
        writer.writerow(['Stock Forecast Report'])
        writer.writerow(['Generated', datetime.now().strftime('%Y-%m-%d %H:%M:%S')])
        writer.writerow(['Ticker', ticker])
        writer.writerow([])
        
        # Current price section
        writer.writerow(['=== CURRENT PRICE ==='])
        if len(historical_data) > 0:
            latest = historical_data.iloc[-1]
            writer.writerow(['Date', historical_data.index[-1].strftime('%Y-%m-%d')])
            writer.writerow(['Open', f"{latest['Open']:.2f}"])
            writer.writerow(['High', f"{latest['High']:.2f}"])
            writer.writerow(['Low', f"{latest['Low']:.2f}"])
            writer.writerow(['Close', f"{latest['Close']:.2f}"])
        writer.writerow([])
        
        # Forecast section
        writer.writerow(['=== FORECAST ==='])
        writer.writerow(['Day', 'Date', 'Open', 'High', 'Low', 'Close', 'Lower Band', 'Upper Band'])
        
        if 'forecast' in forecast_data:
            for f in forecast_data['forecast']:
                writer.writerow([
                    f['day'],
                    f['date'],
                    f['open'],
                    f['high'],
                    f['low'],
                    f['close'],
                    f['close_lower'],
                    f['close_upper']
                ])
        writer.writerow([])
        
        # Summary section
        writer.writerow(['=== FORECAST SUMMARY ==='])
        if 'summary' in forecast_data:
            summary = forecast_data['summary']
            writer.writerow(['Latest Close', summary.get('latest_close', 'N/A')])
            writer.writerow(['Final Predicted Close', summary.get('final_predicted_close', 'N/A')])
            writer.writerow(['Total Change', summary.get('total_change', 'N/A')])
            writer.writerow(['Total Change %', summary.get('total_change_percent', 'N/A')])
            writer.writerow(['Trend', summary.get('trend', 'N/A')])
        writer.writerow([])
        
        # Technical indicators section
        writer.writerow(['=== TECHNICAL INDICATORS ==='])
        if 'trend' in indicators:
            trend = indicators['trend']
            writer.writerow(['Trend Signal', trend.get('signal', 'N/A')])
            writer.writerow(['MA20', trend.get('ma20', 'N/A')])
            writer.writerow(['MA50', trend.get('ma50', 'N/A')])
        
        if 'volatility' in indicators:
            vol = indicators['volatility']
            writer.writerow(['Annual Volatility', f"{vol.get('annual_volatility', 'N/A')}%"])
            writer.writerow(['Max Drawdown', f"{vol.get('max_drawdown', 'N/A')}%"])
        writer.writerow([])
        
        # Disclaimer
        writer.writerow(['=== DISCLAIMER ==='])
        writer.writerow([self.disclaimer])
        
        output.seek(0)
        return output
    
    def generate_forecast_csv(self, forecast_data: Dict[str, Any]) -> io.StringIO:
        """
        Generate simple CSV with just forecast data.
        
        Args:
            forecast_data: Forecast results
            
        Returns:
            StringIO buffer with CSV content
        """
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Header
        writer.writerow(['Day', 'Date', 'Open', 'High', 'Low', 'Close', 'Lower_95CI', 'Upper_95CI'])
        
        # Data
        if 'forecast' in forecast_data:
            for f in forecast_data['forecast']:
                writer.writerow([
                    f['day'],
                    f['date'],
                    f['open'],
                    f['high'],
                    f['low'],
                    f['close'],
                    f['close_lower'],
                    f['close_upper']
                ])
        
        output.seek(0)
        return output
    
    def generate_pdf_report(
        self,
        ticker: str,
        forecast_data: Dict[str, Any],
        indicators: Dict[str, Any],
        chart_image: Optional[bytes] = None
    ) -> io.BytesIO:
        """
        Generate PDF report with analysis.
        
        Args:
            ticker: Stock ticker symbol
            forecast_data: Forecast results
            indicators: Technical indicators
            chart_image: Optional chart image bytes
            
        Returns:
            BytesIO buffer with PDF content
        """
        try:
            from reportlab.lib import colors
            from reportlab.lib.pagesizes import letter
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import inch
            from reportlab.platypus import (
                SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
            )
            from reportlab.lib.enums import TA_CENTER, TA_LEFT
        except ImportError:
            logger.warning("reportlab not installed, PDF generation unavailable")
            raise ImportError("reportlab is required for PDF generation")
        
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        elements = []
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.darkblue,
            alignment=TA_CENTER,
            spaceAfter=30
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=colors.darkblue,
            spaceBefore=20,
            spaceAfter=10
        )
        
        # Title
        elements.append(Paragraph(f"Stock Forecast Report: {ticker}", title_style))
        elements.append(Paragraph(
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            styles['Normal']
        ))
        elements.append(Spacer(1, 20))
        
        # Forecast Summary
        elements.append(Paragraph("Forecast Summary", heading_style))
        
        if 'summary' in forecast_data:
            summary = forecast_data['summary']
            summary_data = [
                ['Metric', 'Value'],
                ['Latest Close', f"${summary.get('latest_close', 'N/A')}"],
                ['Predicted Close', f"${summary.get('final_predicted_close', 'N/A')}"],
                ['Change', f"${summary.get('total_change', 'N/A')}"],
                ['Change %', f"{summary.get('total_change_percent', 'N/A')}%"],
                ['Trend Signal', summary.get('trend', 'N/A')]
            ]
            
            table = Table(summary_data, colWidths=[2.5*inch, 2.5*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            elements.append(table)
        
        elements.append(Spacer(1, 20))
        
        # Forecast Table
        elements.append(Paragraph("Daily Forecast", heading_style))
        
        if 'forecast' in forecast_data:
            forecast_header = ['Day', 'Date', 'Open', 'High', 'Low', 'Close', '95% CI']
            forecast_rows = [forecast_header]
            
            for f in forecast_data['forecast']:
                forecast_rows.append([
                    str(f['day']),
                    f['date'],
                    f"${f['open']}",
                    f"${f['high']}",
                    f"${f['low']}",
                    f"${f['close']}",
                    f"${f['close_lower']}-${f['close_upper']}"
                ])
            
            table = Table(forecast_rows, colWidths=[0.5*inch, 1*inch, 0.8*inch, 0.8*inch, 0.8*inch, 0.8*inch, 1.3*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)
            ]))
            elements.append(table)
        
        elements.append(Spacer(1, 20))
        
        # Technical Indicators
        if indicators:
            elements.append(Paragraph("Technical Analysis", heading_style))
            
            if 'trend' in indicators:
                trend = indicators['trend']
                trend_data = [
                    ['Indicator', 'Value'],
                    ['Trend Signal', trend.get('signal', 'N/A')],
                    ['MA20', f"${trend.get('ma20', 'N/A')}"],
                    ['MA50', f"${trend.get('ma50', 'N/A')}"],
                    ['Price vs MA20', trend.get('price_vs_ma20', 'N/A')]
                ]
                
                table = Table(trend_data, colWidths=[2.5*inch, 2.5*inch])
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.darkgreen),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)
                ]))
                elements.append(table)
        
        elements.append(Spacer(1, 30))
        
        # Disclaimer
        elements.append(Paragraph("Disclaimer", heading_style))
        disclaimer_style = ParagraphStyle(
            'Disclaimer',
            parent=styles['Normal'],
            fontSize=8,
            textColor=colors.grey,
            alignment=TA_LEFT
        )
        elements.append(Paragraph(self.disclaimer, disclaimer_style))
        
        # Build PDF
        doc.build(elements)
        buffer.seek(0)
        
        return buffer
    
    def get_report_filename(self, ticker: str, report_type: str = 'csv') -> str:
        """
        Generate a filename for the report.
        
        Args:
            ticker: Stock ticker symbol
            report_type: Type of report (csv, pdf)
            
        Returns:
            Filename string
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        return f"{ticker}_forecast_report_{timestamp}.{report_type}"
