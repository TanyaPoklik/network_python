"""
Домашнее задание 1: ThreadPoolExecutor 🧵
"""

from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Callable


def fetch_one(url: str) -> str:
    """Заглушка HTTP-запроса. 'Скачивает' URL за ~50 мс."""
    import time

    time.sleep(0.05)
    return f"data:{url}"


def fetch_one_with_delay(url_delay: tuple[str, float]) -> str:
    """Заглушка с кастомной задержкой: (url, delay) -> data."""
    url, delay = url_delay
    import time

    time.sleep(delay)
    return f"data:{url}"


def fetch_all(urls: list[str], max_workers: int = 4) -> list[str]:
    """Скачать все URL через ThreadPoolExecutor."""
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        return list(executor.map(fetch_one, urls))


def fetch_all_with_errors(urls: list[str], max_workers: int = 4) -> list[str | None]:
    """Скачать URL, возвращая None для упавших."""

    def fetch_safe(url: str) -> str | None:
        try:
            if "bad" in url:
                raise ConnectionError("bad url")
            return fetch_one(url)
        except ConnectionError:
            return None

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        return list(executor.map(fetch_safe, urls))


def fetch_all_with_progress(
    urls: list[str],
    max_workers: int = 4,
    progress_callback: Callable[[int, int], None] | None = None,
) -> list[str]:
    """Скачать URL с уведомлением о прогрессе."""
    results = []
    total = len(urls)
    completed = 0

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(fetch_one, url) for url in urls]
        for future in as_completed(futures):
            results.append(future.result())
            completed += 1
            if progress_callback is not None:
                progress_callback(completed, total)

    return results
