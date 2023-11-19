import http.server
import socketserver
import webbrowser

PORT = 7694
REDIRECT_URI = f'http://localhost:{PORT}/callback'
CLIENT_ID = '7158b9f6b992465fa597983e18e173d2'
CLIENT_SECRET = '09b691ffbabd404a92cf6f1e06c01c57'

# Set up the Spotify OAuth
from spotipy.oauth2 import SpotifyOAuth
sp_oauth = SpotifyOAuth(CLIENT_ID, CLIENT_SECRET, REDIRECT_URI, scope='user-library-read')

# Create a callback handler
class CallbackHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith('/callback'):
            code = self.path.split('=')[1]
            token_info = sp_oauth.get_access_token(code)
            print('Authentication successful!')
            print(f'Access Token: {token_info["access_token"]}')
            print(f'Refresh Token: {token_info["refresh_token"]}')
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b'Authentication successful! You can close this window now.')
        else:
            super().do_GET()

# Start the local server
with socketserver.TCPServer(("", PORT), CallbackHandler) as httpd:
    print(f"Local server started at http://localhost:{PORT}")
    webbrowser.open(sp_oauth.get_authorize_url())
    httpd.handle_request()