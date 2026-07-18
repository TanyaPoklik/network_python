"""
Домашнее задание 2: Race Condition и Lock 🔒
"""

import threading
import time


def increment_with_race(counter: list[int], times: int) -> None:
    """Увеличить counter[0] на times, НО с гонкой."""
    for _ in range(times):
        value = counter[0]
        time.sleep(0.000001)
        counter[0] = value + 1


def increment_safe(counter: list[int], times: int, lock: threading.Lock) -> None:
    """Увеличить counter[0] на times, БЕЗ гонки."""
    for _ in range(times):
        with lock:
            value = counter[0]
            counter[0] = value + 1


class InsufficientFundsError(Exception):
    """Исключение: недостаточно средств на счёте."""

    pass


class BankAccount:
    """Потокобезопасный банковский счёт."""

    def __init__(self, initial_balance: float = 0.0) -> None:
        self.balance = float(initial_balance)
        self._lock = threading.Lock()

    def deposit(self, amount: float) -> None:
        if amount <= 0:
            return
        with self._lock:
            self.balance += amount

    def withdraw(self, amount: float) -> None:
        if amount <= 0:
            return
        with self._lock:
            if self.balance < amount:
                raise InsufficientFundsError
            self.balance -= amount

    def get_balance(self) -> float:
        with self._lock:
            return self.balance
