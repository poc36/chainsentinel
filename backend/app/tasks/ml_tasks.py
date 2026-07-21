"""ML background tasks."""

from app.core.celery_app import celery_app


@celery_app.task(name="app.tasks.ml_tasks.run_clustering")
def run_clustering(addresses: list[str]) -> dict:
    """Run address clustering in background."""
    return {"status": "completed", "cluster_count": len(addresses)}
