from flask import Flask, jsonify, request
import subprocess
import os
import random
import string
from consistent_hash import ConsistentHashRing
import requests

app = Flask(__name__)

# Default params
DEFAULT_SERVERS = ["S1", "S2", "S3"]
DOCKER_IMAGE = "simple-server"
DOCKER_NETWORK = "net1"

# Hash ring
ring = ConsistentHashRing()
active_servers = set()

# Utility: spawn container
def spawn_container(server_id):
    env = f"-e SERVER_ID={server_id}"
    name = f"--name {server_id}"
    net = f"--network {DOCKER_NETWORK} --network-alias {server_id}"
    cmd = f"docker run -d {env} {name} {net} {DOCKER_IMAGE}"
    print(f"Starting: {cmd}")
    result = subprocess.getoutput(cmd)
    if "Error" in result:
        print(f"Failed to start {server_id}: {result}")
        return False
    return True

# Utility: remove container
def remove_container(server_id):
    subprocess.call(f"docker stop {server_id}", shell=True)
    subprocess.call(f"docker rm {server_id}", shell=True)

# INIT: start default servers
for sid in DEFAULT_SERVERS:
    if spawn_container(sid):
        ring.add_server(sid)
        active_servers.add(sid)

# GET /rep – show active servers
@app.route("/rep", methods=["GET"])
def get_replicas():
    return jsonify({
        "message": {
            "N": len(active_servers),
            "replicas": sorted(active_servers)
        },
        "status": "successful"
    }), 200

# POST /add – add new server instances
@app.route("/add", methods=["POST"])
def add_replicas():
    data = request.get_json()
    n = data.get("n")
    hostnames = data.get("hostnames", [])

    if len(hostnames) > n:
        return jsonify({
            "message": "<Error> Length of hostname list is more than newly added instances",
            "status": "failure"
        }), 400

    new_servers = []
    # Use preferred hostnames if given
    for i in range(n):
        if i < len(hostnames):
            sid = hostnames[i]
        else:
            # Generate random server name
            sid = "S" + ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
        if sid in active_servers:
            continue
        if spawn_container(sid):
            ring.add_server(sid)
            active_servers.add(sid)
            new_servers.append(sid)

    return jsonify({
        "message": {
            "N": len(active_servers),
            "replicas": sorted(active_servers)
        },
        "status": "successful"
    }), 200

# DELETE /rm – remove server instances
@app.route("/rm", methods=["DELETE"])
def remove_replicas():
    data = request.get_json()
    n = data.get("n")
    hostnames = data.get("hostnames", [])

    if len(hostnames) > n:
        return jsonify({
            "message": "<Error> Length of hostname list is more than removable instances",
            "status": "failure"
        }), 400

    servers_to_remove = hostnames.copy()

    # Fill with random choices if needed
    remaining = n - len(hostnames)
    if remaining > 0:
        remaining_candidates = list(active_servers - set(hostnames))
        if remaining > len(remaining_candidates):
            return jsonify({
                "message": "<Error> Not enough servers to remove",
                "status": "failure"
            }), 400
        servers_to_remove += random.sample(remaining_candidates, remaining)

    for sid in servers_to_remove:
        if sid in active_servers:
            ring.remove_server(sid)
            remove_container(sid)
            active_servers.remove(sid)

    return jsonify({
        "message": {
            "N": len(active_servers),
            "replicas": sorted(active_servers)
        },
        "status": "successful"
    }), 200

# GET /<path> – proxy to /home or other server endpoint
@app.route("/<path:endpoint>", methods=["GET"])
def route_request(endpoint):
    if not active_servers:
        return jsonify({"message": "<Error> No active servers", "status": "failure"}), 500

    if endpoint != "home":
        return jsonify({
            "message": f"<Error> '/{endpoint}' endpoint does not exist in server replicas",
            "status": "failure"
        }), 400

    # Simulate request ID (e.g., 6-digit random)
    request_id = random.randint(100000, 999999)
    target_server = ring.get_server(request_id)

    try:
        res = requests.get(f"http://{target_server}:5000/{endpoint}", timeout=3)
        return jsonify(res.json()), res.status_code
    except Exception as e:
        return jsonify({
            "message": f"Failed to contact {target_server}: {str(e)}",
            "status": "failure"
        }), 502

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
