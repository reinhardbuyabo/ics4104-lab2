FROM python:3.10-slim

WORKDIR /app
COPY . .

RUN apt-get update && apt-get install -y docker.io curl
RUN pip install flask requests

CMD ["python", "load_balancer.py"]
