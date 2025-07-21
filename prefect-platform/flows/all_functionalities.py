"""
all_functionalities.py  —  Prefect 3.4.9 demo
──────────────────────────────────────────────
• parámetros tipados
• tareas con reintentos, back-off y caché
• mapping + sub-flows
• pausa manual (QA)
• hook on_failure
• escritura de resultados a disco
• deploy() embebido
"""

from datetime import timedelta, datetime
import json, os, random, time, httpx
from pathlib import Path

from prefect import (
    flow, task, get_run_logger, pause_flow_run, tags
)
from prefect.tasks import task_input_hash

RESULTS_DIR = Path(__file__).parent / ".." / "results"
RESULTS_DIR.mkdir(exist_ok=True)

# ──────── tareas ────────
@task(
    retries=3,
    retry_delay_seconds=5,
    retry_jitter_factor=0.4,              # back-off aleatorio extra
    cache_key_fn=task_input_hash,
    cache_expiration=timedelta(hours=6),
)
def fetch(url: str) -> str:
    r = httpx.get(url, timeout=10)
    r.raise_for_status()
    return r.text[:120]


@task
def summarize(text: str) -> dict:
    words = text.split()
    return {"preview": " ".join(words[:20]), "length": len(text)}


@task
def store(summary: dict):
    fname = RESULTS_DIR / f"row_{int(time.time()*1000)}.json"
    fname.write_text(json.dumps(summary, ensure_ascii=False))
    get_run_logger().info("Saved ► %s", fname.name)

# ──────── sub-flow ────────
@flow
def ingest(urls: list[str]):
    summaries = summarize.map(fetch.map(urls))
    _ = store.map(summaries)
    return summaries

# ──────── hook de fallo ────────
def on_failure(flow, flow_run, state):
    get_run_logger().error(
        "❌ Flow FAILED (%s). UI link: %s",
        state.type.value,
        flow_run.prefect_ui_url(),
    )
    return state

# ──────── flow principal ────────
@flow(name="etl", on_failure=[on_failure], log_prints=True)
def etl(
    urls: list[str] = (
        "https://prefect.io",
        "https://docs.prefect.io",
    ),
    require_approval: bool = False,
):
    run_id = datetime.utcnow().strftime("%H%M%S")
    with tags(f"etl-run-{run_id}"):
        summaries = ingest(urls)

        if require_approval:
            pause_flow_run(
                reschedule=True,
                wait_for_input=dict(approved=bool),
                reason="Esperando aprobación de QA",
            )

    print("Summaries:", summaries)

# ──────── deploy embebido ────────
if __name__ == "__main__":
    etl.deploy(
        name="etl-dev",
        work_pool_name="dev-pool",
        entrypoint="flows/all_functionalities.py:etl",
        parameters={
            "urls": [
                "https://prefect.io",
                "https://docs.prefect.io",
                "https://www.python.org",
            ],
            "require_approval": False,
        },
        tags=["demo"],
        path=".",          # el worker monta ./flows
    )
