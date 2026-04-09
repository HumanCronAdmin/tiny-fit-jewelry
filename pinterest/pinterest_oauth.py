"""Pinterest OAuth 2.0 token retrieval.

Usage:
  1. Save PINTEREST_APP_ID and PINTEREST_APP_SECRET via save_from_clipboard.bat (options 9, 10)
  2. Run this script: python pinterest_oauth.py
  3. Browser opens -> authorize -> token saved to keyring automatically
"""
import http.server
import threading
import urllib.parse
import webbrowser

import keyring
import requests

SERVICE = "claude-workspace"
REDIRECT_PORT = 9876
REDIRECT_URI = f"http://localhost:{REDIRECT_PORT}/callback"
SCOPES = "boards:read,pins:read,pins:write"

auth_code_holder = {"code": None}


class OAuthCallbackHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        params = urllib.parse.parse_qs(parsed.query)
        if "code" in params:
            auth_code_holder["code"] = params["code"][0]
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            self.wfile.write(b"<h1>OK! Token saved. Close this tab.</h1>")
        else:
            self.send_response(400)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            error = params.get("error", ["unknown"])[0]
            self.wfile.write(f"<h1>Error: {error}</h1>".encode())

    def log_message(self, format, *args):
        pass  # suppress server logs


def get_credentials():
    app_id = keyring.get_password(SERVICE, "PINTEREST_APP_ID")
    app_secret = keyring.get_password(SERVICE, "PINTEREST_APP_SECRET")
    if not app_id or not app_secret:
        print("ERROR: PINTEREST_APP_ID / PINTEREST_APP_SECRET not found in keyring.")
        print("Run save_from_clipboard.bat (options 9, 10) first.")
        return None, None
    return app_id, app_secret


def exchange_code_for_token(app_id, app_secret, code):
    resp = requests.post(
        "https://api.pinterest.com/v5/oauth/token",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        auth=(app_id, app_secret),
        data={
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": REDIRECT_URI,
        },
    )
    if resp.status_code != 200:
        print(f"Token exchange failed: {resp.status_code}")
        print(resp.text)
        return None
    data = resp.json()
    return data.get("access_token")


def main():
    app_id, app_secret = get_credentials()
    if not app_id:
        return

    # Start local server for OAuth callback
    server = http.server.HTTPServer(("localhost", REDIRECT_PORT), OAuthCallbackHandler)
    thread = threading.Thread(target=server.handle_request, daemon=True)
    thread.start()

    # Open Pinterest authorization URL
    auth_url = (
        f"https://api.pinterest.com/oauth/?"
        f"client_id={app_id}"
        f"&redirect_uri={urllib.parse.quote(REDIRECT_URI)}"
        f"&response_type=code"
        f"&scope={SCOPES}"
    )
    print("Opening browser for Pinterest authorization...")
    print(f"URL: {auth_url}")
    webbrowser.open(auth_url)

    # Wait for callback
    thread.join(timeout=120)
    server.server_close()

    if not auth_code_holder["code"]:
        print("ERROR: No authorization code received (timeout or denied).")
        return

    print("Authorization code received. Exchanging for access token...")
    token = exchange_code_for_token(app_id, app_secret, auth_code_holder["code"])
    if not token:
        return

    # Save to keyring
    keyring.set_password(SERVICE, "PINTEREST_ACCESS_TOKEN", token)
    print("[OK] Access token saved to keyring as PINTEREST_ACCESS_TOKEN")


if __name__ == "__main__":
    main()
