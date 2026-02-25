import webview
import threading
import time
import sys
from app import app, update_cache

def start_flask():
    update_cache()
    # Run Flask without the reloader to avoid issues with webview
    app.run(port=5000, debug=False, use_reloader=False)

if __name__ == '__main__':
    # Start Flask in a background thread
    t = threading.Thread(target=start_flask)
    t.daemon = True
    t.start()

    # Give the server a moment to start
    time.sleep(2)

    # Create a native window pointing to the local Flask server
    window = webview.create_window('AI News Dashboard', 'http://127.0.0.1:5000', width=1200, height=800)
    
    # Start the webview loop
    webview.start()
    
    # Exit when window is closed
    sys.exit()
