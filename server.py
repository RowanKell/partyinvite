from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import os
import time

# File to store RSVP data
RSVP_FILE = "rsvp_data.json"

# Initialize empty RSVP data if file doesn't exist
if not os.path.exists(RSVP_FILE):
    with open(RSVP_FILE, "w") as f:
        json.dump([], f)

class PartyServer(BaseHTTPRequestHandler):
    def _set_response_headers(self, content_type='text/html'):
        self.send_response(200)
        self.send_header('Content-type', content_type)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def do_OPTIONS(self):
        self._set_response_headers()
    
    def do_GET(self):
        if self.path == '/':
            # Serve the main HTML page
            with open('index.html', 'rb') as file:
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(file.read())
        
        elif self.path == '/get_responses':
            # Return all RSVPs as JSON
            self._set_response_headers('application/json')
            with open(RSVP_FILE, 'rb') as file:
                self.wfile.write(file.read())
        
        else:
            # Handle other static files
            try:
                with open(self.path[1:], 'rb') as file:
                    self._set_response_headers()
                    self.wfile.write(file.read())
            except:
                # File not found
                self.send_response(404)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(b"404 Not Found")
    
    def do_POST(self):
        if self.path == '/submit_rsvp':
            # Get content length
            content_length = int(self.headers['Content-Length'])
            # Read and decode the POST data
            post_data = self.rfile.read(content_length).decode('utf-8')
            
            try:
                # Parse the JSON data
                rsvp_data = json.loads(post_data)
                
                # Load existing RSVPs
                with open(RSVP_FILE, 'r') as file:
                    rsvps = json.load(file)
                
                # Add the new RSVP
                rsvps.append(rsvp_data)
                
                # Save RSVPs back to file
                with open(RSVP_FILE, 'w') as file:
                    json.dump(rsvps, file, indent=2)
                
                # Send success response
                self._set_response_headers('application/json')
                self.wfile.write(json.dumps({"success": True}).encode())
                
                # Log the RSVP
                print(f"New RSVP received from {rsvp_data.get('name')}")
                
            except Exception as e:
                # Error handling
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"success": False, "error": str(e)}).encode())
                print(f"Error processing RSVP: {str(e)}")
        else:
            # Invalid endpoint
            self.send_response(404)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b"404 Not Found")

def run_server(server_class=HTTPServer, handler_class=PartyServer, port=8000):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f"Starting party invitation server on port {port}...")
    print(f"Open http://localhost:{port} in your browser")
    print(f"RSVP data will be stored in {RSVP_FILE}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    print("Server stopped.")

if __name__ == '__main__':
    run_server()
