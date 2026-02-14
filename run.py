"""
Application Entry Point
=======================
Run this file to start the Flask development server.
For production, use Gunicorn: gunicorn -w 4 "app:create_app()"
"""

import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app

# Create application instance
app = create_app()

if __name__ == '__main__':
    # Development server configuration
    host = os.environ.get('HOST', '127.0.0.1')
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'True').lower() in ('true', '1', 'yes')
    
    print(f"""
    ╔══════════════════════════════════════════════════════════════╗
    ║           Stock Forecast Dashboard v1.0.0                    ║
    ║══════════════════════════════════════════════════════════════║
    ║  • Server running at: http://{host}:{port}                    
    ║  • Debug mode: {debug}                                        
    ║  • Press CTRL+C to stop                                      ║
    ╚══════════════════════════════════════════════════════════════╝
    """)
    
    app.run(
        host=host,
        port=port,
        debug=debug,
        threaded=True
    )
