"""Unit tests for the AuthorizedUser filter."""

from unittest.mock import MagicMock, patch

import pytest

from camarilla.bot.filters import AuthorizedUser


class TestAuthorizedUser:
    """Tests for the AuthorizedUser aiogram filter."""

    @pytest.fixture
    def authorized_user_id(self):
        return 42

    @pytest.fixture(autouse=True)
    def patch_config(self, authorized_user_id):
        with patch(
            "camarilla.bot.filters.config.AUTHORIZED_USER_ID", authorized_user_id
        ):
            yield

    @pytest.fixture
    def filter_instance(self):
        return AuthorizedUser()

    @pytest.mark.asyncio
    async def test_authorized_user_returns_true(self, filter_instance, authorized_user_id):
        message = MagicMock()
        message.from_user.id = authorized_user_id
        message.text = "/start"

        result = await filter_instance(message)

        assert result is True

    @pytest.mark.asyncio
    async def test_unauthorized_user_returns_false_and_logs_warning(
        self, filter_instance, caplog
    ):
        message = MagicMock()
        message.from_user.id = 99
        message.text = "/start"

        with caplog.at_level("WARNING", logger="camarilla.bot.filters"):
            result = await filter_instance(message)

        assert result is False
        assert "Unauthorized access attempt" in caplog.text
        assert "user_id=99" in caplog.text

    @pytest.mark.asyncio
    async def test_missing_from_user_returns_false(self, filter_instance, caplog):
        message = MagicMock()
        message.from_user = None
        message.text = "hello"

        with caplog.at_level("WARNING", logger="camarilla.bot.filters"):
            result = await filter_instance(message)

        assert result is False
        assert "Unauthorized access attempt" in caplog.text
        assert "user_id=None" in caplog.text
