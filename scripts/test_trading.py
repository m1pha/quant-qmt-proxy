# test_trading.py - 放到项目根目录运行
import urllib.request, json

BASE = "http://localhost:1887"
HEADERS = {"Content-Type": "application/json", "X-API-Key": "4C3IuBiiNwDML83v"}
ACCOUNT_ID = "xxxxxxxx"  # ← 改这里

def call(method, path, body=None):
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(BASE + path, data=data, headers=HEADERS, method=method)
    try:
        resp = urllib.request.urlopen(req)
        return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        return json.loads(e.read())

# 1. 连接账户
r = call("POST", "/api/v1/trading/connect", {"account_id": ACCOUNT_ID})
print("=== connect ===", json.dumps(r, ensure_ascii=False, indent=2))
session_id = r.get("session_id")

if session_id:
    # 2. 查询账户信息
    print("=== account ===", json.dumps(call("GET", f"/api/v1/trading/account/{session_id}"), ensure_ascii=False, indent=2))
    # 3. 查询持仓
    print("=== positions ===", json.dumps(call("GET", f"/api/v1/trading/positions/{session_id}"), ensure_ascii=False, indent=2))
    # 4. 查询订单
    print("=== orders ===", json.dumps(call("GET", f"/api/v1/trading/orders/{session_id}"), ensure_ascii=False, indent=2))
    # 5. 查询成交
    print("=== trades ===", json.dumps(call("GET", f"/api/v1/trading/trades/{session_id}"), ensure_ascii=False, indent=2))