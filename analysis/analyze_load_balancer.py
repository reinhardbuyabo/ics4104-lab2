import requests
import matplotlib.pyplot as plt
import concurrent.futures
from collections import Counter
import os

BASE_URL = "http://localhost:5000"
N = 10000
PLOT_DIR = "analysis/plots"
os.makedirs(PLOT_DIR, exist_ok=True)

def reset_servers():
    print("Resetting system: removing all servers...")
    try:
        replicas = requests.get(f"{BASE_URL}/rep").json()["message"]["replicas"]
        if replicas:
            requests.delete(f"{BASE_URL}/rm", json={"n": len(replicas), "hostnames": replicas})
    except Exception as e:
        print("Error resetting servers:", e)

def simulate_requests(n_requests=10000):
    server_ids = []
    skipped = 0

    def send_request(_):
        try:
            res = requests.get(f"{BASE_URL}/home", timeout=1)
            data = res.json()
            return data.get("message")  # e.g. "Hello from Server: 21"
        except:
            return None

    with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
        results = executor.map(send_request, range(n_requests))

    for msg in results:
        if msg and "Server:" in msg:
            try:
                sid = int(msg.split("Server:")[1].strip())
                server_ids.append(sid)
            except ValueError:
                skipped += 1
        else:
            skipped += 1

    return server_ids, skipped

def plot_distribution(data: dict, title: str, filename: str):
    # 🧹 Filter out 0-values again (in case)
    filtered = {k: v for k, v in data.items() if v > 0}

    if not filtered:
        print("[WARN] Nothing to plot — all values are zero.")
        return

    keys = sorted(filtered.keys())
    values = [filtered[k] for k in keys]

    plt.figure(figsize=(8, 4))
    plt.bar(keys, values, color="teal")
    plt.xlabel("Server ID")
    plt.ylabel("Request Count")
    plt.title(title)
    plt.xticks(keys) 
    plt.grid(True, axis='y', linestyle='--', alpha=0.3)
    plt.tight_layout()

    out_path = os.path.join(PLOT_DIR, filename)
    plt.savefig(out_path)
    plt.close()


def analyze(counts, title=""):
    total = sum(counts.values())
    print(f"\n=== {title} ===")
    for sid, count in sorted(counts.items()):
        pct = (count / total) * 100 if total > 0 else 0
        print(f"Server {sid}: {count} requests ({pct:.2f}%)")

def simulate_distribution(n_servers):
    print(f"\n[A2] Testing with {n_servers} servers...")
    reset_servers()
    requests.post(f"{BASE_URL}/add", json={"n": n_servers})

    server_ids, skipped = simulate_requests()
    counts = dict(Counter(server_ids))

    # 🔍 Remove 0-counts (if any) — though Counter typically avoids this
    filtered_counts = {sid: c for sid, c in counts.items() if c > 0}

    if not filtered_counts:
        print("[WARN] No valid requests were routed to any server.")
        return 0

    min_val = min(filtered_counts.values())
    max_val = max(filtered_counts.values())
    spread = max_val - min_val

    print(f"Spread for {n_servers} servers: {spread} requests")
    print(f"Skipped due to errors: {skipped}")
    for sid, c in sorted(filtered_counts.items()):
        print(f"  Server {sid}: {c} requests")

    plot_distribution(
        filtered_counts,
        title=f"A2: Distribution with {n_servers} Servers",
        filename=f"a2_{n_servers}_servers.png"
    )
    return spread

# --- A1: Baseline Distribution ---
print("\n--- A1: Baseline Load Distribution ---")
reset_servers()
requests.post(f"{BASE_URL}/add", json={"n": 3})
server_ids_a1, skipped_a1 = simulate_requests()
counts_a1 = dict(Counter(server_ids_a1))
analyze(counts_a1, "A1: 3 Servers")
print(f"Skipped requests: {skipped_a1}")
plot_distribution(counts_a1, "A1: Load Distribution (3 Servers)", "a1_baseline.png")

# --- A2: Server Count vs Spread ---
print("\n--- A2: Spread vs Server Count ---")
spreads = {}
for s_count in range(2, 10):  # 2 to 10 servers
    spreads[s_count] = simulate_distribution(s_count)

plt.figure(figsize=(8, 5))
plt.plot(list(spreads.keys()), list(spreads.values()), marker='o', color='purple')
plt.xlabel("Number of Servers")
plt.ylabel("Request Count Spread (Max - Min)")
plt.title("A2: Server Count vs. Distribution Spread")
plt.grid(True)
plt.savefig(os.path.join(PLOT_DIR, "a2_spread_vs_servers.png"))
plt.close()
print("Saved plot: analysis/plots/a2_spread_vs_servers.png")

# --- A3: Rebalancing After Removing One Server ---
print("\n--- A3: Load After Removing One Server ---")
reset_servers()
requests.post(f"{BASE_URL}/add", json={"n": 3})
server_ids_before_rm, _ = simulate_requests()
requests.delete(f"{BASE_URL}/rm", json={"n": 1})
server_ids_after_rm, skipped_rm = simulate_requests()
counts_rm = dict(Counter(server_ids_after_rm))
analyze(counts_rm, "A3: After Removing One Server")
print(f"Skipped requests: {skipped_rm}")
plot_distribution(counts_rm, "A3: Load Distribution After Removal", "a3_removed_server.png")

# --- A4: Rebalancing After Adding One Server ---
print("\n--- A4: Load After Adding One Server ---")
requests.post(f"{BASE_URL}/add", json={"n": 1})
server_ids_after_add, skipped_add = simulate_requests()
counts_add = dict(Counter(server_ids_after_add))
analyze(counts_add, "A4: After Adding One Server")
print(f"Skipped requests: {skipped_add}")
plot_distribution(counts_add, "A4: Load Distribution After Addition", "a4_added_server.png")