import requests
from collections import defaultdict, Counter
import matplotlib.pyplot as plt
import os

N = 1000  # number of simulated client requests
URL = "http://localhost:5000/home"
PLOT_DIR = "analysis/plots"
os.makedirs(PLOT_DIR, exist_ok=True)

counts = Counter()

print("Simulating requests...")

for i in range(N):
    try:
        response = requests.get(URL, timeout=1).json()
        server_msg = response.get("message", "")
        if "Server:" in server_msg:
            server_id = int(server_msg.split("Server:")[-1].strip())
            counts[server_id] += 1
    except Exception as e:
        print(f"Request {i} failed:", e)

# Print summary
print("\n=== Request Distribution ===")
for sid, count in sorted(counts.items()):
    print(f"Server {sid}: {count} requests")

# Plot results
plt.figure(figsize=(8, 5))
plt.bar(counts.keys(), counts.values(), color='steelblue')
plt.xlabel("Server ID")
plt.ylabel("Number of Requests")
plt.title(f"Request Distribution Across Servers (N={N})")
plt.grid(axis='y')
plt.tight_layout()
output_file = os.path.join(PLOT_DIR, "simulate_distribution.png")
plt.savefig(output_file)
plt.close()
print(f"Saved plot: {output_file}")

