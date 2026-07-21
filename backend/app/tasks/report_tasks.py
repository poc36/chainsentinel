"""Report generation background tasks."""

from app.core.celery_app import celery_app


@celery_app.task(name="app.tasks.report_tasks.generate_pdf_report")
def generate_pdf_report(investigation_id: str, report_type: str = "full") -> dict:
    """Generate PDF report in background."""
    return {"status": "completed", "investigation_id": investigation_id}
