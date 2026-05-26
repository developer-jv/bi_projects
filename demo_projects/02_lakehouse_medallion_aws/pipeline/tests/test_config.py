from pipeline.common.config import RunContext


def test_run_context_type() -> None:
    ctx = RunContext(batch_id="b1", ingestion_date="2026-05-22", started_at="2026-05-22T00:00:00Z")
    assert ctx.batch_id == "b1"
