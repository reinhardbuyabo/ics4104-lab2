from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel
from typing import List
import docker
import random
import string
import requests
from consistent_hash import ConsistentHashRing

app = FastAPI()
client = docker.from_env()

# Constants
IMAGE_NAME = "fastapi-server"
NETWORK_NAME = "net1"
BASE_PORT = 5000

# Ensure the Docker network exists
try:
    client.networks.get(NETWORK_NAME)
except docker.errors.NotFound:
    client.networks.create(NETWORK_NAME, driver="bridge")

# Consistent hashing ring
ring = ConsistentHashRing()
replicas = {}  # container name → server_id


# Request models
class AddRequest(BaseModel):
    n: int
    hostnames: List[str] = []

class RemoveRequest(BaseModel):
    n: int
    hostnames: List[str] = []

class MapResponse(BaseModel):
    request_id: int
    assigned_server: int


# Utilities
def random_name(length=5):
    return "srv-" + ''.join(random.choices(string.ascii_lowercase, k=length))

def start_server(server_id: int, name: str):
    container = client.containers.run(
        IMAGE_NAME,
        detach=True,
        name=name,
        network=NETWORK_NAME,
        environment={"SERVER_ID": str(server_id)},
    )
    return container

def stop_server(name: str):
    try:
        container = client.containers.get(name)
        container.stop()
        container.remove()
    except docker.errors.NotFound:
        pass


# Endpoints

@app.get("/rep")
def get_replicas():
    return {
        "message": {
            "N": len(replicas),
            "replicas": list(replicas.keys())
        },
        "status": "successful"
    }

@app.post("/add")
def add_servers(req: AddRequest):
    if len(req.hostnames) > req.n:
        raise HTTPException(status_code=400, detail="Length of hostname list is more than newly added instances")

    new_servers = []
    for i in range(req.n):
        name = req.hostnames[i] if i < len(req.hostnames) else random_name()
        server_id = len(ring.ring) + i + 1
        start_server(server_id, name)
        ring.add_server(server_id)
        replicas[name] = server_id
        new_servers.append(name)

    return {
        "message": {
            "N": len(replicas),
            "replicas": list(replicas.keys())
        },
        "status": "successful"
    }

@app.delete("/rm")
def remove_servers(req: RemoveRequest):
    if len(req.hostnames) > req.n:
        raise HTTPException(status_code=400, detail="Length of hostname list is more than removable instances")

    to_remove = req.hostnames[:]
    if len(to_remove) < req.n:
        remaining = list(set(replicas.keys()) - set(to_remove))
        to_remove += random.sample(remaining, req.n - len(to_remove))

    for name in to_remove:
        stop_server(name)
        replicas.pop(name, None)  # optionally remove from hash ring if stored

    return {
        "message": {
            "N": len(replicas),
            "replicas": list(replicas.keys())
        },
        "status": "successful"
    }

@app.get("/{path:path}")
def route_request(path: str, request: Request):
    try:
        request_id = random.randint(100000, 999999)
        server_id = ring.get_server(request_id)

        # Find the corresponding container name
        for name, sid in replicas.items():
            if sid == server_id:
                url = f"http://{name.lower()}:{BASE_PORT}/path"
                res = requests.get(url)
                return res.json()

        raise HTTPException(status_code=500, detail="No matching server found")

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

