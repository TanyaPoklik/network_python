"""
Домашнее задание 4: Asyncio 🔄
"""

import asyncio
from concurrent.futures import ThreadPoolExecutor


async def fetch_one_async(url: str) -> str:
    """Асинхронно 'скачать' URL."""
    await asyncio.sleep(0.05)
    return f"data:{url}"


async def fetch_all_async(urls: list[str]) -> list[str]:
    """Скачать все URL конкурентно через asyncio.gather."""
    return await asyncio.gather(*(fetch_one_async(url) for url in urls))


async def fetch_with_delay(name: str, delay: float, fail: bool = False) -> str:
    """Имитация асинхронной загрузки."""
    await asyncio.sleep(delay)
    if fail:
        raise ValueError(f"Ошибка загрузки {name}")
    return f"data:{name}"


async def run_task_group(names: list[str]) -> dict[str, str | None]:
    """Запустить группу загрузок через asyncio.TaskGroup."""

    async def safe_fetch(name: str) -> str | None:
        try:
            return await fetch_with_delay(name, delay=0.1, fail=("bad" in name))
        except ValueError:
            return None

    tasks = {}
    async with asyncio.TaskGroup() as task_group:
        for name in names:
            tasks[name] = task_group.create_task(safe_fetch(name))

    result = {name: task.result() for name, task in tasks.items()}
    if all(value is None for value in result.values()):
        return {}
    return result


async def fetch_with_timeout(url: str, delay: float, timeout: float) -> str:
    """Скачать URL с таймаутом."""

    async def fetch_delayed() -> str:
        await asyncio.sleep(delay)
        return f"data:{url}"

    return await asyncio.wait_for(fetch_delayed(), timeout=timeout)


async def cancellable_worker(name: str, steps: int) -> str:
    """Корутина, которую можно отменить."""
    try:
        for step in range(steps):
            await asyncio.sleep(0.1)
            print(f"  {name}: шаг {step + 1}")
    except asyncio.CancelledError:
        print(f"  {name}: очищаю ресурсы...")
        raise
    return f"{name}: готов после {steps} шагов"


async def run_with_cancel(name: str, steps: int, cancel_after: float) -> str | None:
    """Запустить cancellable_worker и отменить через cancel_after секунд."""
    task = asyncio.create_task(cancellable_worker(name, steps))
    await asyncio.sleep(cancel_after)

    if not task.done():
        task.cancel()

    try:
        return await task
    except asyncio.CancelledError:
        return None


async def fast_or_slow(name: str, delay: float) -> str:
    """Имитация быстрой или медленной загрузки."""
    await asyncio.sleep(delay)
    return f"{name}: готов за {delay}с"


async def fetch_as_completed(tasks: list[tuple[str, float]]) -> list[str]:
    """Запустить загрузки и вернуть результаты по мере готовности."""
    coroutines = [fast_or_slow(name, delay) for name, delay in tasks]
    results = []

    for completed in asyncio.as_completed(coroutines):
        results.append(await completed)

    return results


def blocking_compute(x: int) -> int:
    """CPU-bound функция: проверка на простоту."""
    import math
    import time

    time.sleep(0.01)
    for i in range(2, int(math.sqrt(x)) + 1):
        if x % i == 0:
            return 0
    return x


async def async_process_numbers(numbers: list[int], max_workers: int = 4) -> list[int]:
    """Обработать числа, выгружая CPU-bound код в пул потоков."""
    loop = asyncio.get_running_loop()

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [
            loop.run_in_executor(executor, blocking_compute, number)
            for number in numbers
        ]
        return await asyncio.gather(*futures)
