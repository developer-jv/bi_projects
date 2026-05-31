from datetime import datetime, timezone

import pytest

from pipeline.common.config import RunContext, build_run_context, resolve_process_date


def test_run_context_type() -> None:
    ctx = RunContext(
        batch_id="b1",
        ingestion_date="2026-05-22",
        started_at="2026-05-22T00:00:00Z",
        logical_date="2026-05-22T00:00:00Z",
    )
    assert ctx.batch_id == "b1"


def test_resolve_process_date_prefers_override() -> None:
    assert (
        resolve_process_date(
            process_date="2026-05-24",
            logical_date=datetime(2026, 5, 26, 15, 0, tzinfo=timezone.utc),
        )
        == "2026-05-24"
    )


def test_build_run_context_uses_logical_date_for_idempotency() -> None:
    logical_date = datetime(2026, 5, 26, 15, 30, tzinfo=timezone.utc)
    ctx = build_run_context(logical_date=logical_date, started_at=logical_date)

    assert ctx.ingestion_date == "2026-05-26"
    assert ctx.batch_id == "batch_20260526"
    assert ctx.logical_date == logical_date.isoformat()


def test_resolve_process_date_rejects_invalid_date() -> None:
    with pytest.raises(ValueError):
        resolve_process_date(process_date="2026-13-40")
