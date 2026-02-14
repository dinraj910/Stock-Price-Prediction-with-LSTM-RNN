"""
Plotting utilities for chart generation.
Server-side chart configuration helpers for Plotly.js frontend.
"""

from typing import Dict, List, Optional, Any, Tuple
import pandas as pd
import numpy as np


# Dark theme color palette
COLORS = {
    'background': '#0d1117',
    'paper': '#161b22',
    'text': '#e6edf3',
    'text_secondary': '#7d8590',
    'grid': '#30363d',
    'border': '#30363d',
    'accent_green': '#3fb950',
    'accent_red': '#f85149',
    'accent_blue': '#58a6ff',
    'accent_purple': '#a371f7',
    'accent_yellow': '#d29922',
    'ma_20': '#58a6ff',
    'ma_50': '#d29922',
    'bollinger': 'rgba(163, 113, 247, 0.3)',
    'volume_up': 'rgba(63, 185, 80, 0.6)',
    'volume_down': 'rgba(248, 81, 73, 0.6)',
    'forecast': '#a371f7',
    'confidence': 'rgba(163, 113, 247, 0.2)'
}


def get_layout_config(title: str = '', height: int = 400, 
                     show_legend: bool = True, show_rangeslider: bool = False) -> Dict:
    """
    Get standard Plotly layout configuration for dark theme.
    
    Args:
        title: Chart title
        height: Chart height in pixels
        show_legend: Whether to show legend
        show_rangeslider: Whether to show range slider (for OHLC charts)
        
    Returns:
        Plotly layout dictionary
    """
    return {
        'title': {
            'text': title,
            'font': {'color': COLORS['text'], 'size': 16},
            'x': 0.5
        },
        'paper_bgcolor': COLORS['paper'],
        'plot_bgcolor': COLORS['background'],
        'font': {'color': COLORS['text'], 'family': 'Inter, system-ui, sans-serif'},
        'height': height,
        'margin': {'l': 50, 'r': 30, 't': 50, 'b': 50},
        'showlegend': show_legend,
        'legend': {
            'bgcolor': 'rgba(0,0,0,0)',
            'font': {'color': COLORS['text_secondary'], 'size': 11},
            'orientation': 'h',
            'yanchor': 'bottom',
            'y': 1.02,
            'xanchor': 'right',
            'x': 1
        },
        'xaxis': {
            'gridcolor': COLORS['grid'],
            'linecolor': COLORS['border'],
            'tickfont': {'color': COLORS['text_secondary']},
            'rangeslider': {'visible': show_rangeslider}
        },
        'yaxis': {
            'gridcolor': COLORS['grid'],
            'linecolor': COLORS['border'],
            'tickfont': {'color': COLORS['text_secondary']},
            'side': 'right'
        },
        'hovermode': 'x unified',
        'hoverlabel': {
            'bgcolor': COLORS['paper'],
            'font': {'color': COLORS['text']},
            'bordercolor': COLORS['border']
        }
    }


def get_candlestick_trace(df: pd.DataFrame, name: str = 'Price') -> Dict:
    """
    Generate candlestick trace configuration.
    
    Args:
        df: DataFrame with OHLC columns and datetime index
        name: Trace name
        
    Returns:
        Plotly candlestick trace dictionary
    """
    return {
        'type': 'candlestick',
        'name': name,
        'x': df.index.strftime('%Y-%m-%d').tolist(),
        'open': df['Open'].tolist(),
        'high': df['High'].tolist(),
        'low': df['Low'].tolist(),
        'close': df['Close'].tolist(),
        'increasing': {
            'line': {'color': COLORS['accent_green']},
            'fillcolor': COLORS['accent_green']
        },
        'decreasing': {
            'line': {'color': COLORS['accent_red']},
            'fillcolor': COLORS['accent_red']
        }
    }


def get_line_trace(x: List, y: List, name: str = '', color: str = None,
                  dash: str = 'solid', width: int = 2, fill: str = None,
                  fillcolor: str = None, showlegend: bool = True) -> Dict:
    """
    Generate line trace configuration.
    
    Args:
        x: X-axis values
        y: Y-axis values
        name: Trace name
        color: Line color
        dash: Line dash style ('solid', 'dash', 'dot', 'dashdot')
        width: Line width
        fill: Fill type ('tozeroy', 'tonexty', etc.)
        fillcolor: Fill color
        showlegend: Whether to show in legend
        
    Returns:
        Plotly scatter trace dictionary
    """
    trace = {
        'type': 'scatter',
        'mode': 'lines',
        'name': name,
        'x': x,
        'y': y,
        'line': {
            'color': color or COLORS['accent_blue'],
            'dash': dash,
            'width': width
        },
        'showlegend': showlegend,
        'hovertemplate': '%{y:.2f}<extra>' + name + '</extra>'
    }
    
    if fill:
        trace['fill'] = fill
        trace['fillcolor'] = fillcolor or 'rgba(88, 166, 255, 0.1)'
    
    return trace


def get_area_trace(x: List, y: List, name: str = '', color: str = None,
                  fillcolor: str = None) -> Dict:
    """
    Generate area trace configuration.
    
    Args:
        x: X-axis values
        y: Y-axis values
        name: Trace name
        color: Line color
        fillcolor: Fill color
        
    Returns:
        Plotly scatter trace with fill
    """
    return get_line_trace(x, y, name, color, fill='tozeroy', 
                         fillcolor=fillcolor or 'rgba(88, 166, 255, 0.2)')


def get_bar_trace(x: List, y: List, name: str = '', colors: List = None,
                 showlegend: bool = True) -> Dict:
    """
    Generate bar trace configuration.
    
    Args:
        x: X-axis values
        y: Y-axis values
        name: Trace name
        colors: List of colors per bar
        showlegend: Whether to show in legend
        
    Returns:
        Plotly bar trace dictionary
    """
    return {
        'type': 'bar',
        'name': name,
        'x': x,
        'y': y,
        'marker': {
            'color': colors or COLORS['accent_blue']
        },
        'showlegend': showlegend,
        'hovertemplate': '%{y:,.0f}<extra>' + name + '</extra>'
    }


def get_volume_trace(df: pd.DataFrame) -> Dict:
    """
    Generate volume bar trace with color based on price direction.
    
    Args:
        df: DataFrame with Volume and Close columns
        
    Returns:
        Plotly bar trace for volume
    """
    colors = [COLORS['volume_up'] if df['Close'].iloc[i] >= df['Open'].iloc[i] 
              else COLORS['volume_down'] for i in range(len(df))]
    
    return {
        'type': 'bar',
        'name': 'Volume',
        'x': df.index.strftime('%Y-%m-%d').tolist(),
        'y': df['Volume'].tolist(),
        'marker': {'color': colors},
        'yaxis': 'y2',
        'showlegend': False,
        'hovertemplate': 'Volume: %{y:,.0f}<extra></extra>'
    }


def get_moving_average_traces(df: pd.DataFrame, windows: List[int] = [20, 50]) -> List[Dict]:
    """
    Generate moving average line traces.
    
    Args:
        df: DataFrame with Close column
        windows: List of MA windows
        
    Returns:
        List of Plotly trace dictionaries
    """
    traces = []
    colors = [COLORS['ma_20'], COLORS['ma_50'], COLORS['accent_purple']]
    
    for i, window in enumerate(windows):
        ma = df['Close'].rolling(window=window).mean()
        traces.append(get_line_trace(
            x=df.index.strftime('%Y-%m-%d').tolist(),
            y=ma.tolist(),
            name=f'MA{window}',
            color=colors[i % len(colors)],
            width=1
        ))
    
    return traces


def get_bollinger_bands_traces(df: pd.DataFrame, window: int = 20, 
                               num_std: float = 2.0) -> List[Dict]:
    """
    Generate Bollinger Bands traces.
    
    Args:
        df: DataFrame with Close column
        window: Rolling window size
        num_std: Number of standard deviations
        
    Returns:
        List of Plotly trace dictionaries (upper, middle, lower)
    """
    ma = df['Close'].rolling(window=window).mean()
    std = df['Close'].rolling(window=window).std()
    upper = ma + (std * num_std)
    lower = ma - (std * num_std)
    
    x = df.index.strftime('%Y-%m-%d').tolist()
    
    return [
        get_line_trace(x, upper.tolist(), 'BB Upper', COLORS['accent_purple'], 
                      dash='dash', width=1),
        get_line_trace(x, ma.tolist(), 'BB Middle', COLORS['accent_purple'], width=1),
        get_line_trace(x, lower.tolist(), 'BB Lower', COLORS['accent_purple'], 
                      dash='dash', width=1, fill='tonexty', 
                      fillcolor=COLORS['bollinger'])
    ]


def get_forecast_traces(dates: List, forecast: List, lower_bound: List = None,
                       upper_bound: List = None) -> List[Dict]:
    """
    Generate forecast traces with optional confidence interval.
    
    Args:
        dates: List of forecast dates
        forecast: List of forecast values
        lower_bound: Lower confidence bound
        upper_bound: Upper confidence bound
        
    Returns:
        List of Plotly trace dictionaries
    """
    traces = []
    
    # Confidence interval
    if lower_bound and upper_bound:
        traces.append(get_line_trace(
            x=dates, y=upper_bound, name='Upper CI',
            color=COLORS['forecast'], dash='dot', width=1,
            showlegend=False
        ))
        traces.append(get_line_trace(
            x=dates, y=lower_bound, name='Lower CI',
            color=COLORS['forecast'], dash='dot', width=1,
            fill='tonexty', fillcolor=COLORS['confidence'],
            showlegend=False
        ))
    
    # Main forecast line
    traces.append(get_line_trace(
        x=dates, y=forecast, name='Forecast',
        color=COLORS['forecast'], width=2
    ))
    
    return traces


def get_rsi_trace(df: pd.DataFrame, window: int = 14) -> Tuple[Dict, Dict]:
    """
    Generate RSI trace with overbought/oversold zones.
    
    Args:
        df: DataFrame with Close column
        window: RSI window
        
    Returns:
        Tuple of (RSI trace, layout config for RSI subplot)
    """
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    
    trace = {
        'type': 'scatter',
        'mode': 'lines',
        'name': 'RSI',
        'x': df.index.strftime('%Y-%m-%d').tolist(),
        'y': rsi.tolist(),
        'line': {'color': COLORS['accent_blue'], 'width': 1.5},
        'yaxis': 'y3'
    }
    
    shapes = [
        {'type': 'line', 'xref': 'paper', 'x0': 0, 'x1': 1,
         'y0': 70, 'y1': 70, 'line': {'color': COLORS['accent_red'], 'dash': 'dash', 'width': 1}},
        {'type': 'line', 'xref': 'paper', 'x0': 0, 'x1': 1,
         'y0': 30, 'y1': 30, 'line': {'color': COLORS['accent_green'], 'dash': 'dash', 'width': 1}}
    ]
    
    return trace, shapes


def create_subplot_layout(rows: int = 3, row_heights: List[float] = None,
                         shared_xaxes: bool = True) -> Dict:
    """
    Create layout configuration for subplots.
    
    Args:
        rows: Number of subplot rows
        row_heights: List of row height ratios
        shared_xaxes: Whether to share x-axes
        
    Returns:
        Layout dictionary
    """
    if row_heights is None:
        row_heights = [0.6, 0.2, 0.2]
    
    layout = get_layout_config(height=600)
    
    # Configure y-axes for each row
    for i in range(rows):
        yaxis_name = 'yaxis' if i == 0 else f'yaxis{i + 1}'
        domain_start = sum(row_heights[i + 1:]) + 0.02 * (rows - i - 1)
        domain_end = domain_start + row_heights[i]
        
        layout[yaxis_name] = {
            'domain': [domain_start, domain_end],
            'gridcolor': COLORS['grid'],
            'linecolor': COLORS['border'],
            'tickfont': {'color': COLORS['text_secondary']},
            'side': 'right'
        }
    
    return layout


def format_chart_data_for_json(df: pd.DataFrame, include_indicators: bool = True) -> Dict:
    """
    Format DataFrame data for JSON response to frontend.
    
    Args:
        df: DataFrame with OHLC data
        include_indicators: Whether to include technical indicators
        
    Returns:
        Dictionary formatted for JSON response
    """
    data = {
        'dates': df.index.strftime('%Y-%m-%d').tolist(),
        'open': df['Open'].tolist(),
        'high': df['High'].tolist(),
        'low': df['Low'].tolist(),
        'close': df['Close'].tolist(),
        'volume': df['Volume'].tolist() if 'Volume' in df.columns else []
    }
    
    if include_indicators:
        data['ma20'] = df['Close'].rolling(window=20).mean().tolist()
        data['ma50'] = df['Close'].rolling(window=50).mean().tolist()
        
        # RSI
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        data['rsi'] = (100 - (100 / (1 + rs))).tolist()
        
        # Bollinger Bands
        ma = df['Close'].rolling(window=20).mean()
        std = df['Close'].rolling(window=20).std()
        data['bb_upper'] = (ma + 2 * std).tolist()
        data['bb_lower'] = (ma - 2 * std).tolist()
    
    return data


def get_chart_config() -> Dict:
    """
    Get standard Plotly config for all charts.
    
    Returns:
        Plotly config dictionary
    """
    return {
        'responsive': True,
        'displayModeBar': True,
        'modeBarButtonsToRemove': ['lasso2d', 'select2d'],
        'displaylogo': False,
        'toImageButtonOptions': {
            'format': 'png',
            'filename': 'stock_chart',
            'height': 600,
            'width': 1200,
            'scale': 2
        }
    }
