import json
import sys
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path

SAVE_PATH = Path("data/01_raw/docx/12_2022_ND_CP.txt")
SAVE_PATH.parent.mkdir(parents=True, exist_ok=True)

class SaveHandler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length)
        data = json.loads(post_data.decode('utf-8'))
        text = data.get('text', '') or data.get('content', '')
        
        SAVE_PATH.write_text(text, encoding='utf-8')
        print(f"SUCCESSFULLY SAVED {len(text)} characters to {SAVE_PATH}", flush=True)
        
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({"status": "ok", "chars": len(text)}).encode('utf-8'))
        
        import threading
        threading.Thread(target=self.server.shutdown).start()

def run():
    server = HTTPServer(('127.0.0.1', 8899), SaveHandler)
    print("Receiver server listening on http://127.0.0.1:8899 ...", flush=True)
    server.serve_forever()

if __name__ == '__main__':
    run()
