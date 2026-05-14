from threading import Event

from app.jobs import job_queue


def setup_function():
    job_queue.stop_worker()
    job_queue.clear_pending_jobs()


def teardown_function():
    job_queue.stop_worker()
    job_queue.clear_pending_jobs()


def test_enqueue_adds_job_to_pending_queue():
    job_queue.enqueue("job-1")

    assert job_queue.queue_size() == 1


def test_worker_processes_jobs_in_fifo_order(monkeypatch):
    processed_job_ids: list[str] = []
    all_jobs_processed = Event()

    def fake_run_job(job_id: str) -> None:
        processed_job_ids.append(job_id)
        if len(processed_job_ids) == 3:
            all_jobs_processed.set()

    monkeypatch.setattr(job_queue, "run_job", fake_run_job)

    job_queue.start_worker()
    job_queue.enqueue("job-1")
    job_queue.enqueue("job-2")
    job_queue.enqueue("job-3")

    assert all_jobs_processed.wait(timeout=2)
    assert processed_job_ids == ["job-1", "job-2", "job-3"]


def test_start_worker_is_idempotent(monkeypatch):
    processed_job_ids: list[str] = []
    job_processed = Event()

    def fake_run_job(job_id: str) -> None:
        processed_job_ids.append(job_id)
        job_processed.set()

    monkeypatch.setattr(job_queue, "run_job", fake_run_job)

    job_queue.start_worker()
    job_queue.start_worker()
    job_queue.enqueue("job-1")

    assert job_processed.wait(timeout=2)
    assert processed_job_ids == ["job-1"]
