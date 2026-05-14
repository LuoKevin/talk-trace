import logging
from queue import Empty, Queue
from threading import Event, Thread

from app.jobs.job_runner import run_job


logger = logging.getLogger(__name__)

_job_queue: Queue[str] = Queue()
_stop_event = Event()
_worker_thread: Thread | None = None


def enqueue(job_id: str) -> None:
    """Add a job to the in-process processing queue."""
    _job_queue.put(job_id)
    logger.info("job_enqueued job_id=%s queue_size=%s", job_id, _job_queue.qsize())


def start_worker() -> None:
    """Start the single in-process queue worker."""
    global _worker_thread

    if _worker_thread is not None and _worker_thread.is_alive():
        return

    _stop_event.clear()
    _worker_thread = Thread(target=_worker_loop, daemon=True)
    _worker_thread.start()
    logger.info("job_queue_worker_started")


def stop_worker() -> None:
    """Stop the queue worker after its current job finishes."""
    _stop_event.set()
    if _worker_thread is not None:
        _worker_thread.join(timeout=5)
    logger.info("job_queue_worker_stopped")


def queue_size() -> int:
    return _job_queue.qsize()


def clear_pending_jobs() -> None:
    """Remove queued jobs that have not started yet.

    This is mainly useful for tests and local development resets. It does not
    cancel a job that the worker has already dequeued.
    """
    while True:
        try:
            _job_queue.get_nowait()
        except Empty:
            return
        else:
            _job_queue.task_done()


def _worker_loop() -> None:
    while not _stop_event.is_set():
        try:
            job_id = _job_queue.get(timeout=1)
        except Empty:
            continue

        try:
            logger.info("job_dequeued job_id=%s queue_size=%s", job_id, _job_queue.qsize())
            run_job(job_id)
        except Exception:
            logger.exception("job_queue_worker_failed job_id=%s", job_id)
        finally:
            _job_queue.task_done()
