"""Analysis background tasks."""

from app.core.celery_app import celery_app


@celery_app.task(name="app.tasks.analysis_tasks.run_full_analysis")
def run_full_analysis(address: str, chain: str | None = None) -> dict:
    """Run full address analysis in background.

    Args:
        address: Blockchain address.
        chain: Optional chain hint.

    Returns:
        Analysis result summary.
    """
    # In production, this would run the async analysis pipeline
    return {"status": "completed", "address": address}
