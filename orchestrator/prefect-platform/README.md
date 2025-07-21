# Prefect Platform — Knowledge Base (Last tested on Prefect 3.4.9)

> **Goal**\
> Provide a *single-file* reference you (or a new team‑mate) can follow to rebuild the entire stack in a couple of minutes, understand why each piece exists, and know the day‑to‑day commands for developing and deploying flows.

---

## 1 | High‑level architecture

```text
                 ┌──────────────┐
                 │  Developers  │  ← VS Code, Prefect CLI
                 └──────┬───────┘
                        │ REST / UI
           ┌───────────────────────────────────┐
           │      Prefect Server (4200)        │
           │  • API      • Orion UI            │
           │  • Events   • Schedules           │
           └────┬──────────────┬──────────────┘
                │              │
        Postgres DB      Redis broker/cache
     (metadata, logs)   (heartbeats, queues)
                │              │
                └──┬────────┬──┘
                   ▼        ▼
        Worker (Process)  Worker (Process)
        • polls `dev-pool`    (optionally more pools)
        • starts each flow
          in a subprocess
```

- **Purpose** – *orchestrate* jobs; heavy data crunching lives in the flows (Docker containers, Spark, Snowflake…).
- **Why light** – the server only stores metadata / schedules; workers spin compute elsewhere → tiny CPU/RAM footprint.

---

## 2 | Project layout

```text
prefect-platform/
├─ flows/                 ← all your business logic
│   └─ all_functionalities.py
├─ infra/                 ← infra-as-code
│   ├─ docker-compose.dev.yml
│   ├─ docker-compose.qa.yml
│   └─ docker-compose.prod.yml
├─ results/               ← (git-ignored) task outputs
└─ README.md              ← this file
```

---

## 3 | Spin‑up commands (local‑dev)

```bash
# 0. Clone repo & go to infra
git clone https://github.com/<org>/prefect-platform.git
cd prefect-platform/infra

# 1. Bring up the stack (server + db + redis + worker)
docker compose -f docker-compose.dev.yml up -d

# 2. Create work‑pool once (inside worker)
docker compose -f docker-compose.dev.yml exec prefect-worker \
     prefect work-pool create --type process dev-pool

# 3. Deploy sample flow
docker compose exec prefect-worker \
     prefect deploy /flows/all_functionalities.py:etl \
     -n etl-dev -p dev-pool
```

> **UI** available at [http://localhost:4200](http://localhost:4200) (or the VM / EC2 IP).

---

## 4 | Every‑day development loop

| Step               | Command / Action                                              | Notes                                           |
| ------------------ | ------------------------------------------------------------- | ----------------------------------------------- |
| **Edit code**      | modify anything under `flows/`                                | bind-mount lets worker *see* changes instantly. |
| **(Re)deploy**     | `prefect deploy /flows/my_flow.py:main -n my-dev -p dev-pool` | Repackages latest code into the deployment.     |
| **Run**            | UI ➜ *Deployments* ➜ *Run*or `prefect deployment run my/main` | CLI/CI friendly.                                |
| **Debug logs**     | `prefect logs --flow-run <id>`                                | live tail.                                      |
| **Pause / resume** | click *Pause* banner in UI if flow raises `pause_flow_run()`  | good for QA approvals.                          |

---

## 5 | Writing a new flow quick‑start

```python
from prefect import flow, task

@task(retries=2, retry_delay_seconds=5)
def add(x, y):
    return x + y

@flow
def adder(a: int = 1, b: int = 2):
    print("Result:", add(a, b))

if __name__ == "__main__":
    # one‑liner deployment
    adder.deploy(
        name="adder-dev",
        work_pool_name="dev-pool",
        entrypoint="flows/adder.py:adder",
        parameters={"a": 10, "b": 20},
        tags=["example"],
        path=".",      # required when you run from worker
    )
```

1. Save as `flows/adder.py`.
2. `prefect deploy /flows/adder.py:adder -n adder-dev -p dev-pool`
3. Run it. 🎉

---

## 6 | Promoting to QA / Prod

| Environment | Compose / IaC                      | Differences                                                     |
| ----------- | ---------------------------------- | --------------------------------------------------------------- |
| **QA**      | `docker-compose.qa.yml`            | smaller instance sizes; `qa-pool`; separate Postgres volume.    |
| **Prod**    | Terraform / Helm on ECS/EKS or EC2 | RDS + ElastiCache, TLS behind ALB, worker pools sized per team. |

A single GitHub Action can `prefect deploy` to each API endpoint based on branch/tag rules (example workflow already in `.github/workflows/`).

---

## 7 | Troubleshooting cheatsheet

| Symptom                      | Likely cause                             | Fix                                                             |
| ---------------------------- | ---------------------------------------- | --------------------------------------------------------------- |
| Pool shows **NOT READY**     | no worker heartbeat                      | ensure `prefect-worker` is running & `PREFECT_API_URL` env set. |
| `ImportError` in logs        | wrong module path                        | verify `entrypoint` and re‑deploy.                              |
| Flow stuck in **Late**       | wrong or paused pool                     | edit deployment → correct pool, unpause pool.                   |
| UI shows `0.0.0.0` API error | missing `PREFECT_SERVER_UI_API_URL=/api` | add env var in `prefect-server`.                                |

---

## 8 | Useful one‑liners

```bash
# Tail worker heartbeat & task logs
docker compose logs -f prefect-worker

# List deployments & recent runs
prefect deployment ls
prefect flow-run ls --limit 20

# Resume a paused run
prefect flow-run resume <id> --approved true
```

---

## 9 | Next steps / nice‑to‑haves

- **CI/CD** – GitHub Actions to auto‑deploy on push / tag.
- **Secrets** – save creds with `prefect secret set`.
- **Metrics** – scrape `/metrics` → Prometheus + Grafana.
- **Cloud results** – switch JSON store to S3/GCS if required.
- **Notifications** – extend `on_failure` to Slack/e‑mail.

---

## 10 | References

- Prefect docs — [https://docs.prefect.io/latest/](https://docs.prefect.io/latest/)
- Prefect compose template — [https://github.com/PrefectHQ/prefect-docker-compose](https://github.com/PrefectHQ/prefect-docker-compose)
- GitHub Action — [https://github.com/PrefectHQ/prefect-github-action](https://github.com/PrefectHQ/prefect-github-action)

---

**Happy orchestrating!**

