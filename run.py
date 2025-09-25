import os
from app import create_app

app = create_app()

if __name__ == '__main__':
    # Get port from environment (useful for both local and production)
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'True').lower() in ['true', '1', 'on']
    
    print(f"Starting HealthBridge AI on port {port}")
    
    app.run(
        host='0.0.0.0' if not debug else '127.0.0.1',
        port=port,
        debug=debug
    )