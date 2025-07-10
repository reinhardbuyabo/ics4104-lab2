import requests
import matplotlib.pyplot as plt
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

def simulate_requests():
    result = []
    skipped = 0
    for _ in range(N):
        try:
            res = requests.get(f"{BASE_URL}/home", timeout=1)
            data = res.json()
            if "message" not in data:
                skipped += 1
                continue
            msg = data["message"]
            if "Server:" in msg:
                server_id = int(msg.split("Server:")[-1].strip())
                result.append(server_id)
        except Exception as e:
            skipped += 1
    return result, skipped

def plot_distribution(counts, title, filename):
    ids = list(counts.keys())
    values = list(counts.values())

    plt.figure(figsize=(8, 5))
    plt.bar(ids, values, color='skyblue')
    plt.xlabel("Server ID")
    plt.ylabel("Request Count")
    plt.title(title)
    plt.grid(axis='y')
    filepath = os.path.join(PLOT_DIR, filename)
    plt.savefig(filepath)
    plt.close()
    print(f"Saved plot: {filepath}")

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

    min_val = min(counts.values()) if counts else 0
    max_val = max(counts.values()) if counts else 0
    spread = max_val - min_val

    print(f"Spread for {n_servers} servers: {spread} requests")
    print(f"Skipped due to errors: {skipped}")
    for sid, c in sorted(counts.items()):
        print(f"  Server {sid}: {c} requests")

    plot_distribution(counts, f"A2: Distribution with {n_servers} Servers", f"a2_{n_servers}_servers.png")
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
for s_count in [3, 5, 7]:
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

