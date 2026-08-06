from __future__ import annotations

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from fastapi.responses import FileResponse

from app.auth import require_api_key
from app.jobs import OUTPUT_ROOT, job_store, process_job
from app.models import JobRequest, JobResponse
from app.utils import resolve_artifact

router = APIRouter(
    prefix="/api/v1",
    tags=["jobs"],
    dependencies=[Depends(require_api_key)],
)


@router.post("/jobs", response_model=JobResponse, status_code=202)
def create_job(request: JobRequest, background_tasks: BackgroundTasks) -> dict:
    job = job_store.create(request)
    background_tasks.add_task(process_job, job.job_id)
    return job.public()


@router.get("/jobs/{job_id}", response_model=JobResponse)
def get_job(job_id: str) -> dict:
    job = job_store.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job não encontrado.")
    return job.public()


@router.get("/jobs/{job_id}/files/{filename}")
def download_job_file(job_id: str, filename: str) -> FileResponse:
    job = job_store.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job não encontrado.")
    try:
        path = resolve_artifact(OUTPUT_ROOT / job_id, filename)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    if filename not in job.artifacts or not path.is_file():
        raise HTTPException(status_code=404, detail="Arquivo não encontrado.")
    return FileResponse(path, filename=filename, media_type="application/octet-stream")
