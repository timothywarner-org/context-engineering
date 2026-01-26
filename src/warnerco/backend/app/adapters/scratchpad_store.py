"""Scratchpad Memory Store for WARNERCO Robotics Schematica.

This module implements a session-scoped in-memory working memory that
complements the vector (Chroma) and graph (SQLite + NetworkX) memory layers.

Key Features:
- In-memory triplet storage with subject-predicate-object entries
- LLM-powered minimization on write (reduces token usage)
- LLM-powered enrichment on read (expands context)
- Token tracking using tiktoken for accurate counting
- Automatic TTL-based entry expiration
- Token budget enforcement with oldest-first eviction
- Thread-safe operations using RLock

Usage:
    store = get_scratchpad_store()

    # Write with minimization
    entry = await store.write(
        subject="WRN-00006",
        predicate="observed",
        object_="thermal_system",
        content="WRN-00006 has thermal issues when running hydraulics",
        minimize=True
    )

    # Read with optional enrichment
    entries = await store.read(subject="WRN-00006", enrich=True)

    # Get context for LangGraph injection
    context_lines, token_count = store.get_context_for_injection(token_budget=1500)
"""

import threading
import uuid
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Tuple

import tiktoken

from app.config import settings
from app.models.scratchpad import (
    ScratchpadEntry,
    ScratchpadStats,
    ScratchpadWriteResult,
    ScratchpadReadResult,
    ScratchpadClearResult,
    VALID_SCRATCHPAD_PREDICATES,
)


class ScratchpadStore:
    """In-memory triplet store with LLM minimization and enrichment.

    This store provides session-scoped working memory for observations,
    inferences, and contextual notes. It uses LLM calls to:
    - Minimize content on write (reduce token usage while preserving meaning)
    - Enrich content on read (expand context when detailed information is needed)

    The store enforces a token budget and automatically evicts oldest entries
    when the budget is exceeded.
    """

    def __init__(
        self,
        max_tokens: Optional[int] = None,
        entry_ttl_minutes: Optional[int] = None,
        inject_budget: Optional[int] = None,
    ):
        """Initialize the scratchpad store.

        Args:
            max_tokens: Maximum total tokens allowed (default from settings)
            entry_ttl_minutes: Minutes until entry expires (default from settings)
            inject_budget: Token budget for LangGraph injection (default from settings)
        """
        self._entries: Dict[str, ScratchpadEntry] = {}
        self._lock = threading.RLock()

        # Configuration
        self._max_tokens = max_tokens or settings.scratchpad_max_tokens
        self._entry_ttl_minutes = entry_ttl_minutes or settings.scratchpad_entry_ttl_minutes
        self._inject_budget = inject_budget or settings.scratchpad_inject_budget

        # Token counting - use cl100k_base encoding (GPT-4/GPT-3.5)
        try:
            self._encoding = tiktoken.get_encoding("cl100k_base")
        except Exception:
            # Fallback if tiktoken fails to load
            self._encoding = None

        # Cache for enriched content
        self._enrichment_cache: Dict[str, str] = {}

    def _count_tokens(self, text: str) -> int:
        """Count tokens in text using tiktoken.

        Falls back to word-based estimation if tiktoken unavailable.
        """
        if not text:
            return 0

        if self._encoding:
            return len(self._encoding.encode(text))

        # Fallback: rough estimate (words * 1.3)
        return int(len(text.split()) * 1.3)

    def _generate_id(self) -> str:
        """Generate a unique entry ID."""
        return f"sp-{uuid.uuid4().hex[:12]}"

    def _get_expiration(self) -> str:
        """Calculate expiration timestamp based on TTL."""
        expires = datetime.now(timezone.utc) + timedelta(minutes=self._entry_ttl_minutes)
        return expires.isoformat()

    def _is_expired(self, entry: ScratchpadEntry) -> bool:
        """Check if an entry has expired."""
        try:
            expires_at = datetime.fromisoformat(entry.expires_at)
            return datetime.now(timezone.utc) > expires_at
        except (ValueError, TypeError):
            return False

    def _cleanup_expired(self) -> int:
        """Remove expired entries. Returns count of removed entries."""
        expired_ids = [
            entry_id for entry_id, entry in self._entries.items()
            if self._is_expired(entry)
        ]
        for entry_id in expired_ids:
            del self._entries[entry_id]
            self._enrichment_cache.pop(entry_id, None)
        return len(expired_ids)

    def _current_token_usage(self) -> int:
        """Calculate current total token usage."""
        return sum(entry.minimized_tokens for entry in self._entries.values())

    def _enforce_token_budget(self, needed_tokens: int) -> int:
        """Evict oldest entries until budget allows needed_tokens.

        Returns count of evicted entries.
        """
        evicted = 0
        current_usage = self._current_token_usage()

        while current_usage + needed_tokens > self._max_tokens and self._entries:
            # Find oldest entry
            oldest_entry = min(
                self._entries.values(),
                key=lambda e: e.created_at
            )
            current_usage -= oldest_entry.minimized_tokens
            del self._entries[oldest_entry.id]
            self._enrichment_cache.pop(oldest_entry.id, None)
            evicted += 1

        return evicted

    async def _minimize_content(self, content: str) -> Tuple[str, int, int]:
        """Use LLM to minimize content while preserving meaning.

        Returns (minimized_content, original_tokens, minimized_tokens).
        Falls back to truncation if LLM unavailable.
        """
        original_tokens = self._count_tokens(content)

        # Try LLM minimization if configured
        if settings.has_llm_config:
            try:
                from langchain_openai import AzureChatOpenAI, ChatOpenAI

                if settings.azure_openai_endpoint:
                    llm = AzureChatOpenAI(
                        azure_endpoint=settings.azure_openai_endpoint,
                        api_key=settings.azure_openai_api_key,
                        azure_deployment=settings.azure_openai_deployment,
                        api_version=settings.azure_openai_api_version,
                        temperature=0,
                        max_tokens=100,
                    )
                else:
                    llm = ChatOpenAI(
                        api_key=settings.openai_api_key,
                        model="gpt-4o-mini",
                        temperature=0,
                        max_tokens=100,
                    )

                prompt = f"""Minimize this text to its essential meaning in as few words as possible.
Keep key entities, relationships, and facts. Remove filler words.
Output ONLY the minimized text, nothing else.

Text: {content}"""

                response = await llm.ainvoke(prompt)
                minimized = response.content.strip()
                minimized_tokens = self._count_tokens(minimized)

                # Only use minimized version if it's actually shorter
                if minimized_tokens < original_tokens:
                    return minimized, original_tokens, minimized_tokens

            except Exception as e:
                # Fall through to truncation fallback
                print(f"Scratchpad minimization error (non-fatal): {e}", flush=True)

        # Fallback: truncation to ~75% of original
        if original_tokens > 50:
            words = content.split()
            target_words = int(len(words) * 0.75)
            truncated = " ".join(words[:target_words])
            truncated_tokens = self._count_tokens(truncated)
            return truncated, original_tokens, truncated_tokens

        return content, original_tokens, original_tokens

    async def _enrich_content(
        self,
        entry: ScratchpadEntry,
        query_context: Optional[str] = None
    ) -> str:
        """Use LLM to expand/enrich entry content.

        Returns enriched content. Falls back to original content if LLM unavailable.
        """
        # Check cache first
        cache_key = entry.id
        if cache_key in self._enrichment_cache:
            return self._enrichment_cache[cache_key]

        if not settings.has_llm_config:
            return entry.content

        try:
            from langchain_openai import AzureChatOpenAI, ChatOpenAI

            if settings.azure_openai_endpoint:
                llm = AzureChatOpenAI(
                    azure_endpoint=settings.azure_openai_endpoint,
                    api_key=settings.azure_openai_api_key,
                    azure_deployment=settings.azure_openai_deployment,
                    api_version=settings.azure_openai_api_version,
                    temperature=0.3,
                    max_tokens=200,
                )
            else:
                llm = ChatOpenAI(
                    api_key=settings.openai_api_key,
                    model="gpt-4o-mini",
                    temperature=0.3,
                    max_tokens=200,
                )

            context_note = ""
            if query_context:
                context_note = f"\nCurrent query context: {query_context}"

            prompt = f"""Expand this brief note into a more detailed explanation.
Add relevant context, implications, and connections.
Keep it concise but informative (2-3 sentences max).
{context_note}

Subject: {entry.subject}
Relationship: {entry.predicate}
Target: {entry.object_}
Note: {entry.content}"""

            response = await llm.ainvoke(prompt)
            enriched = response.content.strip()

            # Cache the result
            self._enrichment_cache[cache_key] = enriched

            return enriched

        except Exception as e:
            print(f"Scratchpad enrichment error (non-fatal): {e}", flush=True)
            return entry.content

    async def write(
        self,
        subject: str,
        predicate: str,
        object_: str,
        content: str,
        minimize: bool = True,
        metadata: Optional[Dict] = None,
    ) -> ScratchpadWriteResult:
        """Store an observation with optional LLM minimization.

        Args:
            subject: Entity being described (e.g., "WRN-00006")
            predicate: Cognitive operation type (observed, inferred, etc.)
            object_: Related entity or concept
            content: The text content to store
            minimize: Whether to use LLM to minimize content (default True)
            metadata: Optional additional properties

        Returns:
            ScratchpadWriteResult with the created entry and token savings
        """
        # Validate predicate
        if predicate not in VALID_SCRATCHPAD_PREDICATES:
            return ScratchpadWriteResult(
                success=False,
                entry=None,
                tokens_saved=0,
                message=f"Invalid predicate '{predicate}'. Must be one of: {', '.join(sorted(VALID_SCRATCHPAD_PREDICATES))}"
            )

        with self._lock:
            # Clean up expired entries first
            self._cleanup_expired()

            # Calculate tokens
            if minimize:
                minimized_content, original_tokens, minimized_tokens = await self._minimize_content(content)
            else:
                original_tokens = self._count_tokens(content)
                minimized_content = content
                minimized_tokens = original_tokens

            # Enforce token budget
            evicted = self._enforce_token_budget(minimized_tokens)
            if evicted > 0:
                print(f"Scratchpad: evicted {evicted} entries to stay within budget", flush=True)

            # Create entry
            now = datetime.now(timezone.utc).isoformat()
            entry = ScratchpadEntry(
                id=self._generate_id(),
                subject=subject,
                predicate=predicate,
                object_=object_,
                content=minimized_content,
                original_content=content if minimize and minimized_content != content else None,
                original_tokens=original_tokens,
                minimized_tokens=minimized_tokens,
                enriched_content=None,
                created_at=now,
                expires_at=self._get_expiration(),
                metadata=metadata,
            )

            self._entries[entry.id] = entry

            tokens_saved = original_tokens - minimized_tokens

            return ScratchpadWriteResult(
                success=True,
                entry=entry,
                tokens_saved=tokens_saved,
                message=f"Stored entry (saved {tokens_saved} tokens)" if tokens_saved > 0 else "Stored entry"
            )

    async def read(
        self,
        subject: Optional[str] = None,
        predicate: Optional[str] = None,
        enrich: bool = False,
        query_context: Optional[str] = None,
    ) -> ScratchpadReadResult:
        """Retrieve entries with optional filtering and enrichment.

        Args:
            subject: Filter by subject (optional)
            predicate: Filter by predicate type (optional)
            enrich: Whether to use LLM to expand content (default False)
            query_context: Current query for context-aware enrichment

        Returns:
            ScratchpadReadResult with matching entries
        """
        with self._lock:
            # Clean up expired entries first
            self._cleanup_expired()

            # Filter entries
            entries = list(self._entries.values())

            if subject:
                entries = [e for e in entries if e.subject == subject]

            if predicate:
                entries = [e for e in entries if e.predicate == predicate]

            # Sort by creation time (newest first)
            entries.sort(key=lambda e: e.created_at, reverse=True)

        # Enrich if requested (outside lock to avoid blocking)
        enriched_count = 0
        if enrich:
            for entry in entries:
                enriched = await self._enrich_content(entry, query_context)
                entry.enriched_content = enriched
                enriched_count += 1

        return ScratchpadReadResult(
            entries=entries,
            total=len(entries),
            enriched_count=enriched_count,
        )

    def clear(
        self,
        subject: Optional[str] = None,
        older_than_minutes: Optional[int] = None,
    ) -> ScratchpadClearResult:
        """Clear entries by subject or age.

        Args:
            subject: Clear only entries for this subject (optional)
            older_than_minutes: Clear entries older than N minutes (optional)

        Returns:
            ScratchpadClearResult with count of cleared entries
        """
        with self._lock:
            to_clear = []
            cutoff_time = None

            if older_than_minutes is not None:
                cutoff_time = datetime.now(timezone.utc) - timedelta(minutes=older_than_minutes)

            for entry_id, entry in self._entries.items():
                should_clear = False

                if subject and entry.subject == subject:
                    should_clear = True
                elif cutoff_time:
                    try:
                        created = datetime.fromisoformat(entry.created_at)
                        if created < cutoff_time:
                            should_clear = True
                    except (ValueError, TypeError):
                        pass
                elif not subject and older_than_minutes is None:
                    # Clear all if no filters specified
                    should_clear = True

                if should_clear:
                    to_clear.append(entry_id)

            for entry_id in to_clear:
                del self._entries[entry_id]
                self._enrichment_cache.pop(entry_id, None)

            return ScratchpadClearResult(
                cleared_count=len(to_clear),
                message=f"Cleared {len(to_clear)} entries"
            )

    def stats(self) -> ScratchpadStats:
        """Get scratchpad statistics.

        Returns:
            ScratchpadStats with token usage and entry counts
        """
        with self._lock:
            # Clean up expired entries first
            self._cleanup_expired()

            entries = list(self._entries.values())

            total_original = sum(e.original_tokens for e in entries)
            total_minimized = sum(e.minimized_tokens for e in entries)
            tokens_saved = total_original - total_minimized

            savings_pct = (tokens_saved / total_original * 100) if total_original > 0 else 0.0

            predicate_counts = {}
            for entry in entries:
                predicate_counts[entry.predicate] = predicate_counts.get(entry.predicate, 0) + 1

            oldest = min((e.created_at for e in entries), default=None)
            newest = max((e.created_at for e in entries), default=None)

            return ScratchpadStats(
                entry_count=len(entries),
                total_original_tokens=total_original,
                total_minimized_tokens=total_minimized,
                tokens_saved=tokens_saved,
                savings_percentage=round(savings_pct, 1),
                token_budget=self._max_tokens,
                token_budget_used=total_minimized,
                token_budget_remaining=self._max_tokens - total_minimized,
                predicate_counts=predicate_counts,
                oldest_entry=oldest,
                newest_entry=newest,
            )

    def get_context_for_injection(
        self,
        token_budget: Optional[int] = None,
        query_context: Optional[str] = None,
    ) -> Tuple[List[str], int]:
        """Get formatted context lines for LangGraph injection.

        Returns entries formatted as context lines, respecting token budget.
        Entries are sorted by recency (newest first) and formatted as:
        "[predicate] subject -> object_: content"

        Args:
            token_budget: Maximum tokens to use (default from settings)
            query_context: Optional query for relevance filtering

        Returns:
            Tuple of (context_lines, total_tokens)
        """
        budget = token_budget or self._inject_budget

        with self._lock:
            # Clean up expired entries first
            self._cleanup_expired()

            # Sort by recency (newest first)
            entries = sorted(
                self._entries.values(),
                key=lambda e: e.created_at,
                reverse=True
            )

            context_lines = []
            total_tokens = 0

            for entry in entries:
                line = f"[{entry.predicate}] {entry.subject} -> {entry.object_}: {entry.content}"
                line_tokens = self._count_tokens(line)

                if total_tokens + line_tokens <= budget:
                    context_lines.append(line)
                    total_tokens += line_tokens
                else:
                    # Budget exceeded, stop adding
                    break

            return context_lines, total_tokens


# =============================================================================
# SINGLETON PATTERN
# =============================================================================

_scratchpad_store: Optional[ScratchpadStore] = None
_scratchpad_lock = threading.Lock()


def get_scratchpad_store() -> ScratchpadStore:
    """Get the singleton scratchpad store instance.

    Thread-safe singleton using double-checked locking.
    """
    global _scratchpad_store

    if _scratchpad_store is None:
        with _scratchpad_lock:
            if _scratchpad_store is None:
                _scratchpad_store = ScratchpadStore()

    return _scratchpad_store


def reset_scratchpad_store() -> None:
    """Reset the scratchpad store (useful for testing).

    Creates a new empty store instance.
    """
    global _scratchpad_store

    with _scratchpad_lock:
        _scratchpad_store = ScratchpadStore()
