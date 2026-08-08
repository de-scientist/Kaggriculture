"""Unit tests for the Wallet domain model (chapter 9)."""
from __future__ import annotations

import pytest

from agent.domain.wallet import Wallet


class TestWallet:
    def test_default_balance(self) -> None:
        assert Wallet().balance == 0.0

    def test_custom_balance(self) -> None:
        assert Wallet(balance=500.0).balance == 500.0

    def test_negative_balance_raises(self) -> None:
        with pytest.raises(ValueError, match="negative"):
            Wallet(balance=-1.0)

    def test_can_afford_true(self) -> None:
        w = Wallet(balance=500.0)
        assert w.can_afford(300.0) is True

    def test_can_afford_false(self) -> None:
        w = Wallet(balance=100.0)
        assert w.can_afford(300.0) is False

    def test_deposit(self) -> None:
        w = Wallet(balance=100.0)
        result = w.deposit(50.0)
        assert result.balance == 150.0
        assert w.balance == 100.0  # immutability

    def test_deposit_negative_raises(self) -> None:
        w = Wallet(balance=100.0)
        with pytest.raises(ValueError, match="negative"):
            w.deposit(-10.0)

    def test_withdraw(self) -> None:
        w = Wallet(balance=100.0)
        result = w.withdraw(30.0)
        assert result.balance == 70.0

    def test_withdraw_insufficient_raises(self) -> None:
        w = Wallet(balance=50.0)
        with pytest.raises(ValueError, match="Insufficient funds"):
            w.withdraw(100.0)

    def test_withdraw_negative_raises(self) -> None:
        w = Wallet(balance=100.0)
        with pytest.raises(ValueError, match="negative"):
            w.withdraw(-10.0)
