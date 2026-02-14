/**
 * Forecast Page JavaScript Module
 * ================================
 * Handles forecast generation and visualization.
 */

(function() {
    'use strict';
    
    // State
    const state = {
        ticker: StockDashboard.defaultTicker,
        horizon: 5,
        historyDays: 60,
        forecastData: null,
        showConfidence: true
    };
    
    // Plotly layout
    const chartLayout = {
        paper_bgcolor: 'rgba(0,0,0,0)',
        plot_bgcolor: 'rgba(0,0,0,0)',
        font: { color: '#a0aec0' },
        margin: { l: 60, r: 30, t: 30, b: 50 },
        xaxis: {
            gridcolor: 'rgba(255,255,255,0.1)',
            showgrid: true
        },
        yaxis: {
            gridcolor: 'rgba(255,255,255,0.1)',
            showgrid: true,
            side: 'right',
            title: 'Price ($)'
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
    
    // Initialize
    function init() {
        setupEventListeners();
    }
    
    // Setup event listeners
    function setupEventListeners() {
        // Forecast form
        document.getElementById('forecastForm').addEventListener('submit', function(e) {
            e.preventDefault();
            generateForecast();
        });
        
        // Toggle confidence bands
        document.getElementById('toggleConfidence').addEventListener('click', function() {
            state.showConfidence = !state.showConfidence;
            if (state.forecastData) {
                updateForecastChart();
            }
        });
        
        // Download forecast CSV
        document.getElementById('downloadForecastCsv').addEventListener('click', function() {
            downloadForecastCSV();
        });
        
        // Stock search form override for this page
        document.getElementById('stockSearchForm').addEventListener('submit', function(e) {
            e.preventDefault();
            const ticker = document.getElementById('tickerInput').value.trim().toUpperCase();
            if (ticker) {
                document.getElementById('forecastTicker').value = ticker;
                generateForecast();
            }
        });
    }
    
    // Generate forecast
    async function generateForecast() {
        const ticker = document.getElementById('forecastTicker').value.trim().toUpperCase();
        const horizon = parseInt(document.getElementById('forecastHorizon').value);
        const historyDays = parseInt(document.getElementById('historyWindow').value);
        
        if (!ticker) {
            StockDashboard.showToast('Please enter a ticker symbol', 'error');
            return;
        }
        
        state.ticker = ticker;
        state.horizon = horizon;
        state.historyDays = historyDays;
        
        StockDashboard.showLoading('Generating forecast...');
        
        try {
            // Fetch historical data
            const histResponse = await fetch(
                `${StockDashboard.apiBase}/stock/${ticker}?days=${historyDays}`
            );
            const histData = await histResponse.json();
            
            if (!histData.success) {
                throw new Error(histData.error || 'Failed to fetch historical data');
            }
            
            // Generate forecast
            const fcResponse = await fetch(`${StockDashboard.apiBase}/forecast`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ ticker, horizon })
            });
            const fcData = await fcResponse.json();
            
            if (!fcData.success) {
                throw new Error(fcData.error || 'Failed to generate forecast');
            }
            
            // Store data
            state.forecastData = {
                historical: histData.data,
                forecast: fcData
            };
            
            // Update UI
            showResults();
            updateSummaryCards(fcData);
            updateForecastChart();
            updateForecastTable(fcData);
            updateRangeAnalysis(fcData);
            
            StockDashboard.showToast(`Forecast generated for ${ticker}`, 'success');
            
        } catch (error) {
            console.error('Forecast error:', error);
            StockDashboard.showToast(error.message, 'error');
        } finally {
            StockDashboard.hideLoading();
        }
    }
    
    // Show results section
    function showResults() {
        document.getElementById('waitingState').style.display = 'none';
        document.getElementById('forecastResults').style.display = 'block';
        document.getElementById('rangeAnalysis').style.display = 'block';
    }
    
    // Update summary cards
    function updateSummaryCards(fcData) {
        const summary = fcData.summary;
        
        // Current price
        document.getElementById('fcCurrentPrice').textContent = 
            StockDashboard.formatCurrency(summary.latest_close);
        
        // Final predicted price
        document.getElementById('fcFinalPrice').textContent = 
            StockDashboard.formatCurrency(summary.final_predicted_close);
        
        // Change
        const changeEl = document.getElementById('fcChange');
        changeEl.textContent = `${StockDashboard.formatPercent(summary.total_change_percent)}`;
        changeEl.className = summary.total_change >= 0 ? 'text-success' : 'text-danger';
        
        // Trend
        const trendEl = document.getElementById('fcTrend');
        trendEl.textContent = summary.trend;
        
        const trendCard = document.getElementById('fcTrendCard');
        trendCard.className = summary.trend === 'Bullish' 
            ? 'card summary-card trend-card bullish' 
            : 'card summary-card trend-card bearish';
    }
    
    // Update forecast chart
    function updateForecastChart() {
        const historical = state.forecastData.historical;
        const forecast = state.forecastData.forecast;
        
        const traces = [];
        
        // Historical close price
        traces.push({
            type: 'scatter',
            mode: 'lines',
            x: historical.dates,
            y: historical.ohlc.close,
            name: 'Historical Close',
            line: { color: '#4299e1', width: 2 }
        });
        
        // Historical high/low range
        traces.push({
            type: 'scatter',
            mode: 'lines',
            x: historical.dates,
            y: historical.ohlc.high,
            name: 'High',
            line: { color: 'rgba(72, 187, 120, 0.5)', width: 1 },
            showlegend: false
        });
        traces.push({
            type: 'scatter',
            mode: 'lines',
            x: historical.dates,
            y: historical.ohlc.low,
            name: 'Low',
            line: { color: 'rgba(245, 101, 101, 0.5)', width: 1 },
            fill: 'tonexty',
            fillcolor: 'rgba(160, 174, 192, 0.1)',
            showlegend: false
        });
        
        // Forecast line
        const fcDates = forecast.forecast.map(f => f.date);
        const fcClose = forecast.forecast.map(f => f.close);
        const fcHigh = forecast.forecast.map(f => f.high);
        const fcLow = forecast.forecast.map(f => f.low);
        const fcUpper = forecast.forecast.map(f => f.close_upper);
        const fcLower = forecast.forecast.map(f => f.close_lower);
        
        // Connect historical to forecast
        const lastHistDate = historical.dates[historical.dates.length - 1];
        const lastHistClose = historical.ohlc.close[historical.ohlc.close.length - 1];
        
        traces.push({
            type: 'scatter',
            mode: 'lines+markers',
            x: [lastHistDate, ...fcDates],
            y: [lastHistClose, ...fcClose],
            name: 'Forecast Close',
            line: { color: '#38b2ac', width: 3, dash: 'dash' },
            marker: { size: 8, color: '#38b2ac' }
        });
        
        // Forecast high/low
        traces.push({
            type: 'scatter',
            mode: 'markers',
            x: fcDates,
            y: fcHigh,
            name: 'Pred. High',
            marker: { size: 6, color: '#48bb78', symbol: 'triangle-up' }
        });
        traces.push({
            type: 'scatter',
            mode: 'markers',
            x: fcDates,
            y: fcLow,
            name: 'Pred. Low',
            marker: { size: 6, color: '#f56565', symbol: 'triangle-down' }
        });
        
        // Confidence bands
        if (state.showConfidence) {
            traces.push({
                type: 'scatter',
                mode: 'lines',
                x: fcDates,
                y: fcUpper,
                name: '95% CI Upper',
                line: { color: 'rgba(56, 178, 172, 0.4)', width: 1, dash: 'dot' },
                showlegend: false
            });
            traces.push({
                type: 'scatter',
                mode: 'lines',
                x: fcDates,
                y: fcLower,
                name: '95% CI Lower',
                line: { color: 'rgba(56, 178, 172, 0.4)', width: 1, dash: 'dot' },
                fill: 'tonexty',
                fillcolor: 'rgba(56, 178, 172, 0.15)',
                showlegend: false
            });
        }
        
        // Add vertical line at forecast start
        const layout = {
            ...chartLayout,
            shapes: [{
                type: 'line',
                x0: lastHistDate,
                x1: lastHistDate,
                y0: 0,
                y1: 1,
                yref: 'paper',
                line: { color: 'rgba(255,255,255,0.3)', width: 2, dash: 'dot' }
            }],
            annotations: [{
                x: lastHistDate,
                y: 1,
                yref: 'paper',
                text: 'Forecast Start',
                showarrow: false,
                font: { color: '#a0aec0', size: 10 },
                yshift: 10
            }]
        };
        
        Plotly.newPlot('forecastChart', traces, layout, chartConfig);
    }
    
    // Update forecast table
    function updateForecastTable(fcData) {
        const tbody = document.getElementById('fcTableBody');
        tbody.innerHTML = fcData.forecast.map(f => `
            <tr>
                <td><strong>${f.day}</strong></td>
                <td>${f.date}</td>
                <td>${StockDashboard.formatCurrency(f.open)}</td>
                <td class="text-success">${StockDashboard.formatCurrency(f.high)}</td>
                <td class="text-danger">${StockDashboard.formatCurrency(f.low)}</td>
                <td><strong>${StockDashboard.formatCurrency(f.close)}</strong></td>
            </tr>
        `).join('');
    }
    
    // Update range analysis
    function updateRangeAnalysis(fcData) {
        const summary = fcData.summary;
        
        document.getElementById('fcMaxHigh').textContent = 
            StockDashboard.formatCurrency(summary.max_predicted_high);
        document.getElementById('fcMinLow').textContent = 
            StockDashboard.formatCurrency(summary.min_predicted_low);
        document.getElementById('fcAvgClose').textContent = 
            StockDashboard.formatCurrency(summary.avg_predicted_close);
        document.getElementById('fcPriceRange').textContent = 
            StockDashboard.formatCurrency(summary.max_predicted_high - summary.min_predicted_low);
        
        // Range chart
        const forecast = fcData.forecast;
        
        const trace = {
            type: 'bar',
            x: forecast.map(f => `Day ${f.day}`),
            y: forecast.map(f => f.high - f.low),
            base: forecast.map(f => f.low),
            marker: {
                color: forecast.map((f, i) => {
                    const change = i === 0 
                        ? f.close - summary.latest_close 
                        : f.close - forecast[i-1].close;
                    return change >= 0 ? 'rgba(72, 187, 120, 0.7)' : 'rgba(245, 101, 101, 0.7)';
                })
            },
            hovertemplate: 'Day %{x}<br>High: $%{customdata[0]:.2f}<br>Low: $%{customdata[1]:.2f}<extra></extra>',
            customdata: forecast.map(f => [f.high, f.low])
        };
        
        const layout = {
            ...chartLayout,
            showlegend: false,
            yaxis: {
                ...chartLayout.yaxis,
                title: 'Price Range ($)'
            }
        };
        
        Plotly.newPlot('rangeChart', [trace], layout, chartConfig);
    }
    
    // Download forecast CSV
    async function downloadForecastCSV() {
        if (!state.forecastData) {
            StockDashboard.showToast('Generate a forecast first', 'warning');
            return;
        }
        
        StockDashboard.showLoading('Downloading...');
        
        try {
            const response = await fetch(`${StockDashboard.apiBase}/download/csv`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ ticker: state.ticker, horizon: state.horizon })
            });
            
            if (!response.ok) {
                throw new Error('Download failed');
            }
            
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `${state.ticker}_forecast_${state.horizon}day.csv`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            a.remove();
            
            StockDashboard.showToast('Forecast exported', 'success');
            
        } catch (error) {
            StockDashboard.showToast(error.message, 'error');
        } finally {
            StockDashboard.hideLoading();
        }
    }
    
    // Initialize on DOM ready
    document.addEventListener('DOMContentLoaded', init);
    
})();
