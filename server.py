from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
import yfinance as yf
from datetime import datetime
import os

# Get the directory where this file is located
basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__, static_folder=basedir)
CORS(app)

@app.route('/')
def index():
    return send_from_directory(basedir, 'index.html')

@app.route('/api/price/<symbol>')
def get_stock_price(symbol):
    """Get current stock price for a symbol"""
    try:
        stock = yf.Ticker(symbol)
        
        # Try multiple methods to get the price
        # Method 1: Get from history (most reliable)
        try:
            hist = stock.history(period="1d")
            if not hist.empty:
                price = hist['Close'].iloc[-1]
                return jsonify({
                    'symbol': symbol.upper(),
                    'price': float(price),
                    'timestamp': datetime.now().isoformat()
                })
        except Exception as e:
            print(f"History method failed for {symbol}: {e}")
        
        # Method 2: Get from fast_info
        try:
            price = stock.fast_info['lastPrice']
            if price:
                return jsonify({
                    'symbol': symbol.upper(),
                    'price': float(price),
                    'timestamp': datetime.now().isoformat()
                })
        except Exception as e:
            print(f"Fast info method failed for {symbol}: {e}")
        
        # Method 3: Get from info
        try:
            info = stock.info
            price = info.get('regularMarketPrice') or info.get('currentPrice') or info.get('previousClose')
            if price:
                return jsonify({
                    'symbol': symbol.upper(),
                    'price': float(price),
                    'timestamp': datetime.now().isoformat()
                })
        except Exception as e:
            print(f"Info method failed for {symbol}: {e}")
            
        return jsonify({'error': f'Could not fetch price for {symbol}'}), 404
            
    except Exception as e:
        print(f"Error fetching {symbol}: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/prices/<symbols>')
def get_multiple_prices(symbols):
    """Get prices for multiple symbols (comma-separated)"""
    try:
        symbol_list = symbols.upper().split(',')
        results = {}
        
        for symbol in symbol_list:
            if symbol.strip():
                symbol = symbol.strip()
                try:
                    stock = yf.Ticker(symbol)
                    
                    # Try history first (most reliable)
                    try:
                        hist = stock.history(period="1d")
                        if not hist.empty:
                            results[symbol] = float(hist['Close'].iloc[-1])
                            continue
                    except:
                        pass
                    
                    # Try fast_info
                    try:
                        price = stock.fast_info['lastPrice']
                        if price:
                            results[symbol] = float(price)
                            continue
                    except:
                        pass
                    
                    # Try info
                    try:
                        info = stock.info
                        price = info.get('regularMarketPrice') or info.get('currentPrice') or info.get('previousClose')
                        if price:
                            results[symbol] = float(price)
                            continue
                    except:
                        pass
                    
                    results[symbol] = None
                    print(f"Could not fetch price for {symbol}")
                    
                except Exception as e:
                    results[symbol] = None
                    print(f"Error fetching {symbol}: {str(e)}")
        
        return jsonify({
            'prices': results,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        print(f"Error in get_multiple_prices: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Render uses PORT environment variable
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port, debug=False)
