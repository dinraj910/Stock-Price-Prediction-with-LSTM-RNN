/**
 * Dashboard JavaScript Module
 * ==========================
 * Handles all dashboard functionality including charts, KPIs, and data loading.
 */

(function() {
    'use strict';
    
    // State management
    const state = {
        ticker: StockDashboard.defaultTicker,
        chartDays: 90,
        chartData: null,
        forecastData: null,
        showMA20: true,
        showMA50: true,
        showBB: false
    };
    
    // Plotly chart layout defaults (dark theme)
    const chartLayout = {
        paper_bgcolor: 'rgba(0,0,0,0)',
        plot_bgcolor: 'rgba(0,0,0,0)',
        font: { color: '#a0aec0' },
        margin: { l: 50, r: 30, t: 30, b: 50 },
        xaxis: {
            gridcolor: 'rgba(255,255,255,0.1)',
            showgrid: true,
            rangeslider: { visible: false }
        },
        yaxis: {
            gridcolor: 'rgba(255,255,255,0.1)',
            showgrid: true,
            side: 'right'
        },
        legend: {
            orientation: 'h',
            y: 1.1,
            x: 0.5,
            xanchor: 'center'
        },
        hovermode: 'x unified'
    };
    
    const chartConfig = {
        responsive: true,
        displayModeBar: true,
        modeBarButtonsToRemove: ['lasso2d', 'select2d'],
        displaylogo: false
    };
    
    // Initialize dashboard
    function init() {
        setupEventListeners();
        loadDashboardData(state.ticker);
    }
    
    // Setup event listeners
    function setupEventListeners() {
        // Stock search form
        document.getElementById('stockSearchForm').addEventListener('submit', function(e) {
            e.preventDefault();
            const ticker = document.getElementById('tickerInput').value.trim().toUpperCase();
            if (ticker) {
                state.ticker = ticker;
                StockDashboard.currentTicker = ticker;
                loadDashboardData(ticker);
            }
        });
        
        // Refresh button
        document.getElementById('refreshBtn').addEventListener('click', function() {
            loadDashboardData(state.ticker);
        });
        
        // Download CSV button
        document.getElementById('downloadCsvBtn').addEventListener('click', function() {
            downloadCSV();
        });
        
        // Chart range buttons
        document.querySelectorAll('.chart-range').forEach(btn => {
            btn.addEventListener('click', function() {
                document.querySelectorAll('.chart-range').forEach(b => b.classList.remove('active'));
                this.classList.add('active');
                state.chartDays = parseInt(this.dataset.days);
                if (state.chartData) {
                    updatePriceChart();
                }
            });
        });
        
        // Indicator toggles
        document.getElementById('showMA20').addEventListener('change', function() {
            state.showMA20 = this.checked;
            if (state.chartData) updatePriceChart();
        });
        
        document.getElementById('showMA50').addEventListener('change', function() {
            state.showMA50 = this.checked;
            if (state.chartData) updatePriceChart();
        });
        
        document.getElementById('showBB').addEventListener('change', function() {
            state.showBB = this.checked;
            if (state.chartData) updatePriceChart();
        });
    }
    
    // Load all dashboard data
    async function loadDashboardData(ticker) {
        StockDashboard.showLoading('Loading dashboard data...');
        
        try {
            // Fetch dashboard data from combined endpoint
            const response = await fetch(
                `${StockDashboard.forecastBase}/dashboard/${ticker}?days=${state.chartDays}&horizon=5`
            );
            
            const data = await response.json();
            
            if (!data.success) {
                throw new Error(data.error || 'Failed to load data');
            }
            
            // Store data
            state.chartData = data.chart_data;
            state.forecastData = data.forecast;
            
            // Update UI components
            updateHeader(ticker, data.latest);
            updateKPIs(data.latest, data.prediction, data.indicators);
            updatePriceChart();
            updateForecastPanel(data.forecast);
            updateVolatilityChart(data.chart_data);
            updateReturnsHistogram(data.chart_data);
            updateMetrics(data.indicators);
            
            // Load model metrics separately (can be slow)
            loadModelMetrics(ticker);
            
            StockDashboard.showToast(`${ticker} data loaded successfully`, 'success');
            
        } catch (error) {
            console.error('Dashboard error:', error);
            StockDashboard.showToast(error.message, 'error');
        } finally {
            StockDashboard.hideLoading();
        }
    }
    
    // Update header
    function updateHeader(ticker, latest) {
        document.getElementById('stockTitle').textContent = 
            `${ticker} - ${latest.name || ticker}`;
        document.getElementById('lastUpdated').textContent = 
            `Last updated: ${new Date().toLocaleString()}`;
    }
    
    // Update KPI cards
    function updateKPIs(latest, prediction, indicators) {
        // Current price
        document.getElementById('currentPrice').textContent = 
            StockDashboard.formatCurrency(latest.current_price);
        
        const changeEl = document.getElementById('priceChange');
        changeEl.textContent = `${StockDashboard.formatPercent(latest.change_percent)} today`;
        changeEl.className = StockDashboard.getChangeClass(latest.change_percent);
        
        // Predicted close
        if (prediction) {
            document.getElementById('predictedClose').textContent = 
                StockDashboard.formatCurrency(prediction.predicted.close);
            
            const predChangeEl = document.getElementById('predictedChange');
            predChangeEl.textContent = `${StockDashboard.formatPercent(prediction.change_percent)}`;
            predChangeEl.className = StockDashboard.getChangeClass(prediction.change_percent);
        }
        
        // Trend signal
        const trend = indicators.trend;
        document.getElementById('trendSignal').textContent = trend.signal;
        
        const trendIconBg = document.getElementById('trendIconBg');
        const trendIcon = document.getElementById('trendIcon');
        
        if (trend.signal === 'Bullish') {
            trendIconBg.className = 'kpi-icon bg-success';
            trendIcon.className = 'bi bi-arrow-up-right';
        } else if (trend.signal === 'Bearish') {
            trendIconBg.className = 'kpi-icon bg-danger';
            trendIcon.className = 'bi bi-arrow-down-right';
        } else {
            trendIconBg.className = 'kpi-icon bg-secondary';
            trendIcon.className = 'bi bi-arrow-right';
        }
        
        document.getElementById('trendDetail').textContent = 
            `MA20: ${trend.price_vs_ma20}`;
        
        // Volatility
        const vol = indicators.volatility;
        document.getElementById('volatility').textContent = 
            `${vol.annual_volatility}%`;
        document.getElementById('volatilityDesc').textContent = 
            vol.interpretation.split(' - ')[0];
    }
    
    // Update price chart
    function updatePriceChart() {
        const data = state.chartData;
        if (!data) return;
        
        // Slice data based on selected range
        const sliceIndex = Math.max(0, data.dates.length - state.chartDays);
        const dates = data.dates.slice(sliceIndex);
        const ohlc = {
            open: data.ohlc.open.slice(sliceIndex),
            high: data.ohlc.high.slice(sliceIndex),
            low: data.ohlc.low.slice(sliceIndex),
            close: data.ohlc.close.slice(sliceIndex)
        };
        const indicators = {
            ma20: data.indicators.ma20.slice(sliceIndex),
            ma50: data.indicators.ma50.slice(sliceIndex),
            bb_upper: data.indicators.bb_upper.slice(sliceIndex),
            bb_middle: data.indicators.bb_middle.slice(sliceIndex),
            bb_lower: data.indicators.bb_lower.slice(sliceIndex)
        };
        
        const traces = [];
        
        // Candlestick chart
        traces.push({
            type: 'candlestick',
            x: dates,
            open: ohlc.open,
            high: ohlc.high,
            low: ohlc.low,
            close: ohlc.close,
            name: 'OHLC',
            increasing: { line: { color: '#48bb78' } },
            decreasing: { line: { color: '#f56565' } }
        });
        
        // MA20
        if (state.showMA20) {
            traces.push({
                type: 'scatter',
                mode: 'lines',
                x: dates,
                y: indicators.ma20,
                name: 'MA20',
                line: { color: '#4299e1', width: 1.5 }
            });
        }
        
        // MA50
        if (state.showMA50) {
            traces.push({
                type: 'scatter',
                mode: 'lines',
                x: dates,
                y: indicators.ma50,
                name: 'MA50',
                line: { color: '#ed8936', width: 1.5 }
            });
        }
        
        // Bollinger Bands
        if (state.showBB) {
            traces.push({
                type: 'scatter',
                mode: 'lines',
                x: dates,
                y: indicators.bb_upper,
                name: 'BB Upper',
                line: { color: '#9f7aea', width: 1, dash: 'dot' }
            });
            traces.push({
                type: 'scatter',
                mode: 'lines',
                x: dates,
                y: indicators.bb_lower,
                name: 'BB Lower',
                line: { color: '#9f7aea', width: 1, dash: 'dot' },
                fill: 'tonexty',
                fillcolor: 'rgba(159, 122, 234, 0.1)'
            });
        }
        
        // Add forecast if available
        if (state.forecastData && state.forecastData.forecast) {
            const fcDates = state.forecastData.forecast.map(f => f.date);
            const fcClose = state.forecastData.forecast.map(f => f.close);
            const fcUpper = state.forecastData.forecast.map(f => f.close_upper);
            const fcLower = state.forecastData.forecast.map(f => f.close_lower);
            
            // Forecast line
            traces.push({
                type: 'scatter',
                mode: 'lines+markers',
                x: [dates[dates.length - 1], ...fcDates],
                y: [ohlc.close[ohlc.close.length - 1], ...fcClose],
                name: 'Forecast',
                line: { color: '#38b2ac', width: 2, dash: 'dash' },
                marker: { size: 6 }
            });
            
            // Confidence band
            traces.push({
                type: 'scatter',
                mode: 'lines',
                x: fcDates,
                y: fcUpper,
                name: 'Upper CI',
                line: { color: 'rgba(56, 178, 172, 0.3)', width: 0 },
                showlegend: false
            });
            traces.push({
                type: 'scatter',
                mode: 'lines',
                x: fcDates,
                y: fcLower,
                name: 'Lower CI',
                line: { color: 'rgba(56, 178, 172, 0.3)', width: 0 },
                fill: 'tonexty',
                fillcolor: 'rgba(56, 178, 172, 0.2)',
                showlegend: false
            });
        }
        
        const layout = {
            ...chartLayout,
            showlegend: true
        };
        
        Plotly.newPlot('priceChart', traces, layout, chartConfig);
    }
    
    // Update forecast panel
    function updateForecastPanel(forecast) {
        if (!forecast) {
            document.getElementById('forecastSummary').innerHTML = 
                '<p class="text-muted text-center">Forecast unavailable</p>';
            return;
        }
        
        const summary = forecast.summary;
        const trend = summary.trend;
        const trendClass = trend === 'Bullish' ? 'text-success' : 'text-danger';
        const trendIcon = trend === 'Bullish' ? 'bi-arrow-up-right' : 'bi-arrow-down-right';
        
        document.getElementById('forecastSummary').innerHTML = `
            <div class="forecast-summary-content">
                <div class="d-flex justify-content-between mb-2">
                    <span>5-Day Trend</span>
                    <span class="badge ${trend === 'Bullish' ? 'bg-success' : 'bg-danger'}">
                        <i class="bi ${trendIcon}"></i> ${trend}
                    </span>
                </div>
                <div class="d-flex justify-content-between mb-2">
                    <span>Predicted Change</span>
                    <strong class="${trendClass}">${StockDashboard.formatPercent(summary.total_change_percent)}</strong>
                </div>
                <div class="d-flex justify-content-between mb-2">
                    <span>Target Price</span>
                    <strong>${StockDashboard.formatCurrency(summary.final_predicted_close)}</strong>
                </div>
                <div class="d-flex justify-content-between">
                    <span>Predicted Range</span>
                    <strong>${StockDashboard.formatCurrency(summary.min_predicted_low)} - ${StockDashboard.formatCurrency(summary.max_predicted_high)}</strong>
                </div>
            </div>
        `;
        
        // Update forecast table
        const tbody = document.getElementById('forecastTableBody');
        tbody.innerHTML = forecast.forecast.map(f => `
            <tr>
                <td>${f.date}</td>
                <td>${StockDashboard.formatCurrency(f.close)}</td>
                <td><small class="text-muted">${StockDashboard.formatCurrency(f.close_lower)} - ${StockDashboard.formatCurrency(f.close_upper)}</small></td>
            </tr>
        `).join('');
    }
    
    // Update volatility chart
    function updateVolatilityChart(data) {
        const sliceIndex = Math.max(0, data.dates.length - state.chartDays);
        const dates = data.dates.slice(sliceIndex);
        const volatility = data.volatility.slice(sliceIndex);
        
        const trace = {
            type: 'scatter',
            mode: 'lines',
            x: dates,
            y: volatility,
            fill: 'tozeroy',
            fillcolor: 'rgba(237, 137, 54, 0.2)',
            line: { color: '#ed8936', width: 2 }
        };
        
        const layout = {
            ...chartLayout,
            showlegend: false,
            yaxis: {
                ...chartLayout.yaxis,
                title: 'Volatility %'
            }
        };
        
        Plotly.newPlot('volatilityChart', [trace], layout, chartConfig);
    }
    
    // Update returns histogram
    function updateReturnsHistogram(data) {
        const sliceIndex = Math.max(0, data.returns.length - state.chartDays);
        const returns = data.returns.slice(sliceIndex).filter(r => r !== 0);
        
        const trace = {
            type: 'histogram',
            x: returns,
            nbinsx: 30,
            marker: {
                color: 'rgba(66, 153, 225, 0.7)',
                line: { color: '#4299e1', width: 1 }
            }
        };
        
        const layout = {
            ...chartLayout,
            showlegend: false,
            xaxis: {
                ...chartLayout.xaxis,
                title: 'Daily Return %'
            },
            yaxis: {
                ...chartLayout.yaxis,
                title: 'Frequency'
            }
        };
        
        Plotly.newPlot('returnsHistogram', [trace], layout, chartConfig);
    }
    
    // Update metrics panels
    function updateMetrics(indicators) {
        // Risk metrics
        const vol = indicators.volatility;
        const returns = indicators.returns || {};
        
        document.getElementById('maxDrawdown').textContent = `${vol.max_drawdown}%`;
        document.getElementById('var95').textContent = `${vol.var_95}%`;
        document.getElementById('bestDay').textContent = `+${returns.best_day || 0}%`;
        document.getElementById('worstDay').textContent = `${returns.worst_day || 0}%`;
        
        // Technical signals
        const rsi = indicators.rsi;
        const sr = indicators.support_resistance;
        
        document.getElementById('rsiValue').textContent = rsi.rsi || '--';
        
        const rsiSignalEl = document.getElementById('rsiSignal');
        rsiSignalEl.textContent = rsi.signal || '--';
        rsiSignalEl.className = 'badge ' + getRSIBadgeClass(rsi.signal);
        
        document.getElementById('support1').textContent = 
            StockDashboard.formatCurrency(sr.support_1);
        document.getElementById('resistance1').textContent = 
            StockDashboard.formatCurrency(sr.resistance_1);
    }
    
    // Load model metrics
    async function loadModelMetrics(ticker) {
        try {
            const response = await fetch(`${StockDashboard.apiBase}/metrics/${ticker}`);
            const data = await response.json();
            
            if (data.success && data.metrics) {
                const m = data.metrics;
                document.getElementById('modelRmse').textContent = `$${m.rmse}`;
                document.getElementById('naiveRmse').textContent = `$${m.naive_rmse}`;
                document.getElementById('skillScore').textContent = `${m.skill_score}%`;
                document.getElementById('directionAcc').textContent = `${m.directional_accuracy}%`;
            }
        } catch (error) {
            console.log('Model metrics unavailable');
        }
    }
    
    // Download CSV report
    async function downloadCSV() {
        StockDashboard.showLoading('Generating report...');
        
        try {
            const response = await fetch(`${StockDashboard.apiBase}/download/report`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ ticker: state.ticker, horizon: 5 })
            });
            
            if (!response.ok) {
                throw new Error('Failed to generate report');
            }
            
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `${state.ticker}_report.csv`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            a.remove();
            
            StockDashboard.showToast('Report downloaded', 'success');
            
        } catch (error) {
            StockDashboard.showToast(error.message, 'error');
        } finally {
            StockDashboard.hideLoading();
        }
    }
    
    // Helper function for RSI badge class
    function getRSIBadgeClass(signal) {
        switch (signal) {
            case 'Overbought': return 'bg-danger';
            case 'Oversold': return 'bg-success';
            case 'Bullish': return 'bg-info';
            case 'Bearish': return 'bg-warning';
            default: return 'bg-secondary';
        }
    }
    
    // Initialize on DOM ready
    document.addEventListener('DOMContentLoaded', init);
    
})();
