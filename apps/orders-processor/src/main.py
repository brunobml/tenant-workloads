import os
import time
import threading
import json
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
from http.server import HTTPServer, BaseHTTPRequestHandler

QUEUE_URL = os.environ.get('QUEUE_URL', '')
ENV = os.environ.get('ENVIRONMENT', 'unknown')
APP = os.environ.get('APP_NAME', 'orders')
POD = os.environ.get('HOSTNAME', 'unknown')
MOTO_HOST = os.environ.get('MOTO_ENDPOINT', 'http://moto-cloud:5000')
TABLE_NAME = f"{APP}-{ENV}-history"

def sqs_call(params):
    data = urllib.parse.urlencode(params).encode()
    req = urllib.request.Request(QUEUE_URL, data=data)
    req.add_header('Authorization', 'AWS4-HMAC-SHA256 Credential=mock/20260929/us-east-1/sqs/aws4_request, SignedHeaders=host, Signature=mock')
    with urllib.request.urlopen(req, timeout=5) as resp:
        return resp.read()

def ddb_call(target, payload):
    data = json.dumps(payload).encode()
    req = urllib.request.Request(MOTO_HOST, data=data)
    req.add_header('X-Amz-Target', f'DynamoDB_20120810.{target}')
    req.add_header('Content-Type', 'application/x-amz-json-1.0')
    req.add_header('Authorization', 'AWS4-HMAC-SHA256 Credential=mock/20260929/us-east-1/dynamodb/aws4_request, SignedHeaders=host, Signature=mock')
    with urllib.request.urlopen(req, timeout=5) as resp:
        return json.loads(resp.read().decode())

def init_dynamo():
    try:
        ddb_call('CreateTable', {
            'TableName': TABLE_NAME,
            'KeySchema': [{'AttributeName': 'id', 'KeyType': 'HASH'}],
            'AttributeDefinitions': [{'AttributeName': 'id', 'AttributeType': 'S'}],
            'BillingMode': 'PAY_PER_REQUEST'
        })
        print(f"✔ DynamoDB shared table '{TABLE_NAME}' initialized")
    except Exception:
        pass

def save_order(msg_id, body):
    try:
        ddb_call('PutItem', {
            'TableName': TABLE_NAME,
            'Item': {
                'id': {'S': str(msg_id)},
                'body': {'S': str(body)},
                'pod': {'S': POD},
                'env': {'S': ENV},
                'timestamp': {'N': str(int(time.time()))},
                'time': {'S': time.strftime('%X')}
            }
        })
    except Exception as e:
        print(f"Error saving to DynamoDB: {e}")

def get_orders():
    try:
        res = ddb_call('Scan', {'TableName': TABLE_NAME})
        items = res.get('Items', [])
        items.sort(key=lambda x: int(x.get('timestamp', {}).get('N', '0')), reverse=True)
        return items[:15]
    except Exception:
        return []

def worker_loop():
    print(f"🚀 Worker started for [{ENV}] listening on {QUEUE_URL}")
    init_dynamo()
    while True:
        try:
            raw = sqs_call({'Action': 'ReceiveMessage', 'MaxNumberOfMessages': '5', 'WaitTimeSeconds': '5'})
            root = ET.fromstring(raw)
            ns = {'sqs': 'http://queue.amazonaws.com/doc/2012-11-05/'}
            for msg in root.findall('.//sqs:Message', ns):
                mid = msg.find('sqs:MessageId', ns).text
                body = msg.find('sqs:Body', ns).text
                rh = msg.find('sqs:ReceiptHandle', ns).text
                print(f"📦 [{ENV} on {POD}] Received Order from SQS: {body} (MsgId: {mid})")
                sqs_call({'Action': 'DeleteMessage', 'ReceiptHandle': rh})
                save_order(mid, body)
                print(f"✔ [{ENV} on {POD}] Processed & recorded in DynamoDB: {mid}")
        except Exception:
            pass
        time.sleep(2)

class WebHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass

    def do_GET(self):
        if self.path == '/healthz':
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"OK")
            return

        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.end_headers()

        orders = get_orders()
        badge_color = "#10b981" if ENV == "dev" else ("#f59e0b" if ENV == "test" else "#ef4444")
        orders_rows = "".join(
            f"<tr><td>{o.get('time',{}).get('S','')}</td>"
            f"<td><code>{o.get('id',{}).get('S','')[:12]}...</code></td>"
            f"<td>{o.get('body',{}).get('S','')}</td>"
            f"<td><span style='color:#a7f3d0;font-size:0.85rem;'>{o.get('pod',{}).get('S','')}</span></td></tr>"
            for o in orders
        ) or "<tr><td colspan='4' style='text-align:center;color:#94a3b8;'>No orders processed yet. Use the form above to submit one!</td></tr>"

        html = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>{APP.title()} Microservice - {ENV.upper()}</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #0b1120; color: #f8fafc; padding: 2rem; margin: 0; }}
    .container {{ max-width: 950px; margin: 0 auto; }}
    .card {{ background: #1e293b; border-radius: 12px; padding: 1.5rem; margin-bottom: 1.5rem; border: 1px solid #334155; box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1); }}
    .badge {{ display: inline-block; padding: 4px 14px; border-radius: 9999px; font-weight: 700; font-size: 0.85rem; text-transform: uppercase; background: {badge_color}; color: white; }}
    .stat-num {{ font-size: 2.2rem; font-weight: 800; color: #38bdf8; margin: 0.2rem 0; }}
    input[type="text"] {{ width: 70%; padding: 10px 14px; border-radius: 8px; border: 1px solid #475569; background: #0f172a; color: white; font-size: 1rem; }}
    button {{ padding: 10px 20px; border-radius: 8px; border: none; background: #3b82f6; color: white; font-weight: 600; font-size: 1rem; cursor: pointer; }}
    button:hover {{ background: #2563eb; }}
    table {{ width: 100%; border-collapse: collapse; margin-top: 1rem; }}
    th, td {{ padding: 10px; border-bottom: 1px solid #334155; text-align: left; }}
    th {{ color: #94a3b8; font-size: 0.85rem; text-transform: uppercase; }}
    code {{ background: #0f172a; padding: 2px 6px; border-radius: 4px; font-family: monospace; color: #a5f3fc; }}
  </style>
</head>
<body>
  <div class="container">
    <div class="card">
      <div style="display:flex; justify-content:space-between; align-items:center;">
        <h2 style="margin:0;">📦 {APP.title()} Microservice</h2>
        <span class="badge">{ENV} environment</span>
      </div>
      <hr style="border:0; border-top:1px solid #334155; margin:1rem 0;">
      <div style="display:grid; grid-template-columns:1fr 1fr; gap:1rem;">
        <div>
          <p style="color:#94a3b8; margin:0;">Serving Pod (Load-Balanced)</p>
          <p style="margin:0.2rem 0;"><code>{POD}</code></p>
          <p style="color:#94a3b8; margin:0.8rem 0 0 0;">Connected SQS Queue</p>
          <p style="margin:0.2rem 0; word-break:break-all;"><code>{QUEUE_URL}</code></p>
          <p style="color:#94a3b8; margin:0.8rem 0 0 0;">Shared Storage</p>
          <p style="margin:0.2rem 0;"><code>DynamoDB: {TABLE_NAME}</code></p>
        </div>
        <div style="text-align:right;">
          <p style="color:#94a3b8; margin:0;">Total Orders Recorded in Cloud DB</p>
          <div class="stat-num">{len(orders)}</div>
        </div>
      </div>
    </div>

    <div class="card">
      <h3 style="margin-top:0;">🛒 Submit an Order (Produces to SQS)</h3>
      <form method="POST" action="/order" style="display:flex; gap:10px;">
        <input type="text" name="item" placeholder="Enter item (e.g. Mechanical Keyboard, Ergonomic Chair)" required />
        <button type="submit">Send to SQS Queue</button>
      </form>
    </div>

    <div class="card">
      <h3 style="margin-top:0;">📋 Live Processed Orders Feed (Shared Across All Replicas)</h3>
      <table>
        <thead><tr><th>Time</th><th>Message ID</th><th>Order Content</th><th>Processed By Pod</th></tr></thead>
        <tbody>{orders_rows}</tbody>
      </table>
    </div>
  </div>
</body>
</html>"""
        self.wfile.write(html.encode())

    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length).decode()
        item = post_data
        if 'item=' in post_data:
            item = urllib.parse.unquote_plus(post_data.split('item=')[1])
        msg_body = json.dumps({'order': item, 'timestamp': time.time(), 'client': 'web-dashboard'})
        try:
            sqs_call({'Action': 'SendMessage', 'MessageBody': msg_body})
            print(f"📤 [{ENV} on {POD}] Web dashboard submitted order to SQS: {msg_body}")
        except Exception as e:
            print(f"Error publishing to SQS: {e}")
        self.send_response(303)
        self.send_header('Location', '/')
        self.end_headers()

if __name__ == '__main__':
    threading.Thread(target=worker_loop, daemon=True).start()
    print(f"🌐 HTTP Web Dashboard listening on port 8080 (Pod: {POD})")
    HTTPServer(('0.0.0.0', 8080), WebHandler).serve_forever()
