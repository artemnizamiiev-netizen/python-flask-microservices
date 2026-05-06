# python-flask-microservices

Application source code for the demo storefront and its three backend services.

## What lives here

This repository contains four Flask applications:

| Service | Path | Default port | Responsibility |
| --- | --- | ---: | --- |
| Frontend | `frontend` | `5000` | Server-rendered web UI, calls backend APIs |
| User service | `user-service` | `5001` | User registration, login, API key auth |
| Product service | `product-service` | `5002` | Product catalog |
| Order service | `order-service` | `5003` | Basket and checkout flow |

Each service is packaged as its own Docker image and is deployed independently in Kubernetes.

## Repository structure

Each service follows roughly the same shape:

```text
<service>/
  application/
    ... Flask app package, routes, models, templates, API clients
  tests/
  Dockerfile
  docker-compose.yml
  requirements.txt
  run.py
```

The frontend also contains `frontend/docker-compose.yml`, which is the easiest way to bring up the whole stack locally because it wires the three backend services and their MySQL containers together.

## How the services talk to each other

- `frontend` calls:
  - `user-service`
  - `product-service`
  - `order-service`
- `order-service` also calls `user-service`

In Kubernetes these service-to-service calls are configured through environment variables and in-cluster DNS names. In local Docker runs they share the same Docker network.

## Local development paths

### Option 1: Run the full stack with Docker Compose

From the frontend directory:

```bash
cd frontend
docker network create micro_network || true
docker compose up --build
```

What you get:

- frontend on `http://localhost:5000`
- user-service on `http://localhost:5001`
- product-service on `http://localhost:5002`
- order-service on `http://localhost:5003`
- three MySQL containers on ports `32000`, `32001`, `32002`

This is the best option when you want to test the end-to-end user flow locally.

### Option 2: Run a single service in isolation

Every service directory has its own `docker-compose.yml` and `Dockerfile`.

Example for `user-service`:

```bash
cd user-service
docker network create micro_network || true
docker compose up --build
```

Use this path when you only need to work on one backend service and do not need the full storefront flow.

## Typical local smoke flow

1. Start the full stack from `frontend/`.
2. Seed a couple of products:

```bash
curl -i -d "name=prod1&slug=prod1&image=product1.jpg&price=100" -X POST http://localhost:5002/api/product/create
curl -i -d "name=prod2&slug=prod2&image=product2.jpg&price=200" -X POST http://localhost:5002/api/product/create
```

3. Open:

```text
http://localhost:5000/
http://localhost:5000/register
http://localhost:5000/login
```

## Tests

Each service keeps its own test suite under `tests/`.

Typical workflow:

```bash
cd user-service
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pytest
```

Repeat the same pattern for `frontend`, `product-service`, or `order-service`.

## How this repo fits the rest of the workspace

- `python-flask-microservices-gitops` deploys these services to Kubernetes
- `python-flask-microservices-infra` builds the AWS and EKS environment they run in
- `python-flask-microservices-terraform-modules` contains the reusable infra modules used by Terragrunt

If you change application behavior here, the usual next step is to build and push a new image, then update the image tag in the GitOps repo.
