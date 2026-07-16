import multiprocessing, time, requests, sys, uvicorn

def run_server():
    from main import app
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="error")

p = multiprocessing.Process(target=run_server, daemon=True)
p.start()
time.sleep(4)

try:
    r = requests.get("http://127.0.0.1:8000/", timeout=5)
    print("Status:", r.status_code)
    print("Content-Type:", r.headers.get("content-type"))
    print("Content length:", len(r.text), "chars")
    print("First 100 chars:", r.text[:100])
except Exception as e:
    print("Error:", e)
finally:
    p.terminate()
