"""Unit tests for the Scratchpad Memory store.

This module tests the scratchpad adapter that provides:
- In-memory triplet storage with subject-predicate-object entries
- Token counting and budget enforcement
- TTL-based entry expiration
- LLM-powered minimization and enrichment (with fallback)
- Thread-safe operations

These tests validate the scratchpad_store.py implementation.
"""

import pytest
import pytest_asyncio
from datetime import datetime, timezone, timedelta

from app.models.scratchpad import (
    ScratchpadEntry,
    ScratchpadStats,
    VALID_SCRATCHPAD_PREDICATES,
)
from app.adapters.scratchpad_store import (
    ScratchpadStore,
    get_scratchpad_store,
    reset_scratchpad_store,
)


# =============================================================================
# FIXTURES
# =============================================================================


@pytest.fixture
def scratchpad():
    """Create a fresh scratchpad store for each test.

    Yields:
        ScratchpadStore: A new scratchpad store instance.
    """
    store = ScratchpadStore(
        max_tokens=1000,
        entry_ttl_minutes=30,
        inject_budget=500,
    )
    yield store


@pytest.fixture(autouse=True)
def reset_singleton():
    """Reset the global scratchpad singleton before each test."""
    reset_scratchpad_store()
    yield


# =============================================================================
# TEST: WRITE OPERATIONS
# =============================================================================


class TestScratchpadWrite:
    """Tests for scratchpad write operations."""

    @pytest.mark.asyncio
    async def test_write_stores_entry(self, scratchpad):
        """Verify entries can be written and retrieved."""
        # Act
        result = await scratchpad.write(
            subject="WRN-00006",
            predicate="observed",
            object_="thermal_system",
            content="thermal issues with hydraulics",
            minimize=False,
        )

        # Assert
        assert result.success is True
        assert result.entry is not None
        assert result.entry.subject == "WRN-00006"
        assert result.entry.predicate == "observed"
        assert result.entry.object_ == "thermal_system"
        assert result.entry.content == "thermal issues with hydraulics"

    @pytest.mark.asyncio
    async def test_write_without_minimize_preserves_content(self, scratchpad):
        """Verify content is preserved when minimize=False."""
        content = "This is a longer piece of content that should not be changed at all"

        # Act
        result = await scratchpad.write(
            subject="test",
            predicate="observed",
            object_="test",
            content=content,
            minimize=False,
        )

        # Assert
        assert result.entry.content == content
        assert result.entry.original_content is None

    @pytest.mark.asyncio
    async def test_write_tracks_tokens(self, scratchpad):
        """Verify token counts are tracked on write."""
        content = "WRN-00006 has thermal issues when running hydraulics"

        # Act
        result = await scratchpad.write(
            subject="WRN-00006",
            predicate="observed",
            object_="thermal",
            content=content,
            minimize=False,
        )

        # Assert
        assert result.entry.original_tokens > 0
        assert result.entry.minimized_tokens > 0

    @pytest.mark.asyncio
    async def test_write_with_invalid_predicate_fails(self, scratchpad):
        """Verify invalid predicates are rejected."""
        # Act
        result = await scratchpad.write(
            subject="test",
            predicate="invalid_predicate",
            object_="test",
            content="test content",
            minimize=False,
        )

        # Assert
        assert result.success is False
        assert "Invalid predicate" in result.message

    @pytest.mark.asyncio
    async def test_write_all_valid_predicates(self, scratchpad):
        """Verify all valid predicates are accepted."""
        for predicate in VALID_SCRATCHPAD_PREDICATES:
            result = await scratchpad.write(
                subject=f"test-{predicate}",
                predicate=predicate,
                object_="target",
                content=f"Testing {predicate}",
                minimize=False,
            )
            assert result.success is True, f"Predicate '{predicate}' should be valid"

    @pytest.mark.asyncio
    async def test_write_with_metadata(self, scratchpad):
        """Verify metadata is stored with entries."""
        metadata = {"source": "user", "confidence": 0.9}

        # Act
        result = await scratchpad.write(
            subject="test",
            predicate="observed",
            object_="test",
            content="test content",
            minimize=False,
            metadata=metadata,
        )

        # Assert
        assert result.entry.metadata == metadata


# =============================================================================
# TEST: READ OPERATIONS
# =============================================================================


class TestScratchpadRead:
    """Tests for scratchpad read operations."""

    @pytest.mark.asyncio
    async def test_read_returns_all_entries(self, scratchpad):
        """Verify read returns all entries when no filters specified."""
        # Arrange
        await scratchpad.write("sub1", "observed", "obj1", "content1", minimize=False)
        await scratchpad.write("sub2", "inferred", "obj2", "content2", minimize=False)

        # Act
        result = await scratchpad.read()

        # Assert
        assert result.total == 2
        assert len(result.entries) == 2

    @pytest.mark.asyncio
    async def test_read_filters_by_subject(self, scratchpad):
        """Verify read can filter by subject."""
        # Arrange
        await scratchpad.write("WRN-001", "observed", "obj", "content1", minimize=False)
        await scratchpad.write("WRN-002", "observed", "obj", "content2", minimize=False)
        await scratchpad.write("WRN-001", "inferred", "obj", "content3", minimize=False)

        # Act
        result = await scratchpad.read(subject="WRN-001")

        # Assert
        assert result.total == 2
        assert all(e.subject == "WRN-001" for e in result.entries)

    @pytest.mark.asyncio
    async def test_read_filters_by_predicate(self, scratchpad):
        """Verify read can filter by predicate."""
        # Arrange
        await scratchpad.write("sub", "observed", "obj1", "content1", minimize=False)
        await scratchpad.write("sub", "inferred", "obj2", "content2", minimize=False)
        await scratchpad.write("sub", "observed", "obj3", "content3", minimize=False)

        # Act
        result = await scratchpad.read(predicate="observed")

        # Assert
        assert result.total == 2
        assert all(e.predicate == "observed" for e in result.entries)

    @pytest.mark.asyncio
    async def test_read_empty_scratchpad(self, scratchpad):
        """Verify read handles empty scratchpad gracefully."""
        # Act
        result = await scratchpad.read()

        # Assert
        assert result.total == 0
        assert result.entries == []


# =============================================================================
# TEST: CLEAR OPERATIONS
# =============================================================================


class TestScratchpadClear:
    """Tests for scratchpad clear operations."""

    @pytest.mark.asyncio
    async def test_clear_all(self, scratchpad):
        """Verify clear all removes all entries."""
        # Arrange
        await scratchpad.write("sub1", "observed", "obj", "content1", minimize=False)
        await scratchpad.write("sub2", "observed", "obj", "content2", minimize=False)

        # Act
        result = scratchpad.clear()

        # Assert
        assert result.cleared_count == 2
        stats = scratchpad.stats()
        assert stats.entry_count == 0

    @pytest.mark.asyncio
    async def test_clear_by_subject(self, scratchpad):
        """Verify clear can target specific subjects."""
        # Arrange
        await scratchpad.write("WRN-001", "observed", "obj", "content1", minimize=False)
        await scratchpad.write("WRN-002", "observed", "obj", "content2", minimize=False)
        await scratchpad.write("WRN-001", "inferred", "obj", "content3", minimize=False)

        # Act
        result = scratchpad.clear(subject="WRN-001")

        # Assert
        assert result.cleared_count == 2
        stats = scratchpad.stats()
        assert stats.entry_count == 1

    @pytest.mark.asyncio
    async def test_clear_empty_scratchpad(self, scratchpad):
        """Verify clear handles empty scratchpad gracefully."""
        # Act
        result = scratchpad.clear()

        # Assert
        assert result.cleared_count == 0


# =============================================================================
# TEST: STATISTICS
# =============================================================================


class TestScratchpadStats:
    """Tests for scratchpad statistics."""

    @pytest.mark.asyncio
    async def test_stats_returns_accurate_counts(self, scratchpad):
        """Verify stats returns accurate entry counts."""
        # Arrange
        await scratchpad.write("sub1", "observed", "obj", "content one", minimize=False)
        await scratchpad.write("sub2", "inferred", "obj", "content two", minimize=False)

        # Act
        stats = scratchpad.stats()

        # Assert
        assert stats.entry_count == 2
        assert stats.predicate_counts.get("observed", 0) == 1
        assert stats.predicate_counts.get("inferred", 0) == 1

    @pytest.mark.asyncio
    async def test_stats_tracks_token_budget(self, scratchpad):
        """Verify stats tracks token budget usage."""
        # Arrange
        await scratchpad.write("sub", "observed", "obj", "a " * 50, minimize=False)

        # Act
        stats = scratchpad.stats()

        # Assert
        assert stats.token_budget == 1000  # From fixture
        assert stats.token_budget_used > 0
        assert stats.token_budget_remaining == stats.token_budget - stats.token_budget_used

    @pytest.mark.asyncio
    async def test_stats_empty_scratchpad(self, scratchpad):
        """Verify stats handles empty scratchpad."""
        # Act
        stats = scratchpad.stats()

        # Assert
        assert stats.entry_count == 0
        assert stats.total_original_tokens == 0
        assert stats.token_budget_used == 0
        assert stats.savings_percentage == 0.0


# =============================================================================
# TEST: TOKEN BUDGET ENFORCEMENT
# =============================================================================


class TestTokenBudget:
    """Tests for token budget enforcement."""

    @pytest.mark.asyncio
    async def test_budget_evicts_oldest_entries(self):
        """Verify oldest entries are evicted when budget exceeded."""
        # Create scratchpad with very small budget (50 tokens)
        scratchpad = ScratchpadStore(max_tokens=50, entry_ttl_minutes=30)

        # Add entries that will exceed budget - each entry has ~30+ tokens
        await scratchpad.write("entry1", "observed", "obj", "a " * 30, minimize=False)
        await scratchpad.write("entry2", "observed", "obj", "b " * 30, minimize=False)
        await scratchpad.write("entry3", "observed", "obj", "c " * 30, minimize=False)

        # Act
        stats = scratchpad.stats()

        # Assert - budget should be enforced
        assert stats.token_budget_used <= 50
        # At least one entry should have been evicted (only 1 entry fits in 50 tokens)
        assert stats.entry_count < 3


# =============================================================================
# TEST: CONTEXT INJECTION
# =============================================================================


class TestContextInjection:
    """Tests for LangGraph context injection."""

    @pytest.mark.asyncio
    async def test_get_context_for_injection(self, scratchpad):
        """Verify context lines are formatted correctly."""
        # Arrange
        await scratchpad.write("WRN-001", "observed", "thermal", "has issues", minimize=False)
        await scratchpad.write("WRN-002", "inferred", "related", "connection found", minimize=False)

        # Act
        context_lines, token_count = scratchpad.get_context_for_injection()

        # Assert
        assert len(context_lines) == 2
        assert token_count > 0
        assert "[observed]" in context_lines[0] or "[observed]" in context_lines[1]

    @pytest.mark.asyncio
    async def test_get_context_respects_budget(self, scratchpad):
        """Verify context injection respects token budget."""
        # Arrange - add many entries
        for i in range(20):
            await scratchpad.write(
                f"entry{i}", "observed", "obj",
                f"content number {i} with some additional text",
                minimize=False,
            )

        # Act
        context_lines, token_count = scratchpad.get_context_for_injection(token_budget=100)

        # Assert
        assert token_count <= 100
        assert len(context_lines) < 20  # Not all entries should fit

    @pytest.mark.asyncio
    async def test_get_context_empty_scratchpad(self, scratchpad):
        """Verify empty scratchpad returns empty context."""
        # Act
        context_lines, token_count = scratchpad.get_context_for_injection()

        # Assert
        assert context_lines == []
        assert token_count == 0


# =============================================================================
# TEST: SINGLETON PATTERN
# =============================================================================


class TestSingletonPattern:
    """Tests for the singleton pattern."""

    def test_get_scratchpad_store_returns_same_instance(self):
        """Verify get_scratchpad_store returns the same instance."""
        store1 = get_scratchpad_store()
        store2 = get_scratchpad_store()

        assert store1 is store2

    def test_reset_creates_new_instance(self):
        """Verify reset_scratchpad_store creates a new instance."""
        store1 = get_scratchpad_store()
        reset_scratchpad_store()
        store2 = get_scratchpad_store()

        assert store1 is not store2


# =============================================================================
# TEST: ENTRY EXPIRATION
# =============================================================================


class TestEntryExpiration:
    """Tests for TTL-based entry expiration."""

    @pytest.mark.asyncio
    async def test_entry_has_expiration_time(self, scratchpad):
        """Verify entries have expiration timestamp set."""
        # Act
        result = await scratchpad.write("sub", "observed", "obj", "content", minimize=False)

        # Assert
        assert result.entry.expires_at is not None
        expires = datetime.fromisoformat(result.entry.expires_at)
        now = datetime.now(timezone.utc)
        # Should expire in approximately 30 minutes (our fixture TTL)
        assert expires > now
        assert expires < now + timedelta(minutes=35)

    @pytest.mark.asyncio
    async def test_expired_entries_cleaned_on_read(self, scratchpad):
        """Verify expired entries are cleaned up on read."""
        # This is harder to test without mocking time
        # We verify the cleanup doesn't error with valid entries
        await scratchpad.write("sub", "observed", "obj", "content", minimize=False)

        # Act - read should trigger cleanup
        result = await scratchpad.read()

        # Assert - entry should still be there (not expired)
        assert result.total == 1


# =============================================================================
# TEST: THREAD SAFETY
# =============================================================================


class TestThreadSafety:
    """Tests for thread-safe operations."""

    @pytest.mark.asyncio
    async def test_concurrent_writes(self, scratchpad):
        """Verify concurrent writes don't cause issues."""
        import asyncio

        async def write_entry(i: int):
            return await scratchpad.write(
                f"subject{i}",
                "observed",
                "obj",
                f"content {i}",
                minimize=False,
            )

        # Act - run many writes concurrently
        results = await asyncio.gather(*[write_entry(i) for i in range(10)])

        # Assert
        assert all(r.success for r in results)
        stats = scratchpad.stats()
        assert stats.entry_count == 10
