# Distributed Systems Lab 2 – Customizable Load Balancer

## Task 1: Web Server Implementation with FastAPI

This repository contains the implementation of a lightweight HTTP web server written in **FastAPI**, designed to be used in a distributed system managed by a load balancer.

---

## 🚀 Features

- **`/home` Endpoint (GET)**  
  Returns a unique message indicating the identity of the server instance.

  Example Response:
  ```json
  {
    "message": "Hello from Server: 1",
    "status": "successful"
  }
  ```

- **`/heartbeat` Endpoint (GET)**  
  A lightweight endpoint used by the load balancer to check server availability. Returns HTTP 200.

---

## ⚙️ Environment

- **Language**: Python 3.10
- **Framework**: FastAPI
- **Containerization**: Docker
- **Port**: 5000

---

## 🐳 Docker Instructions

### Build Image
```bash
docker build -t fastapi-server .
```

### Run Container
```bash
docker run -e SERVER_ID=1 -p 5000:5000 fastapi-server
```

This command exposes the FastAPI server on `localhost:5000`.

---

## 🛠️ Makefile Commands

Use the included `Makefile` for easier management.

| Command       | Description                        |
|---------------|------------------------------------|
| `make build`  | Build the Docker image             |
| `make run`    | Run the container with SERVER_ID=1 |
| `make stop`   | Stop and remove the container      |
| `make rebuild`| Rebuild and run again              |
| `make clean`  | Remove unused Docker images        |

---

## 📁 Project Structure

```
.
├── Dockerfile
├── Makefile
├── README.md
├── requirements.txt
└── server.py
```

---

## 🔧 Design Notes

- The server ID is passed via the `SERVER_ID` environment variable during container startup.
- The app uses FastAPI for high performance and automatic OpenAPI docs (available at `/docs`).
- The server runs on port `5000` inside the container as specified in the assignment.

---

## 📚 References

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Docker Documentation](https://docs.docker.com/)




