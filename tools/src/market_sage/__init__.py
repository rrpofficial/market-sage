"""Market Sage Tools — CLI utilities for Indian stock market analysis."""

# Shared cache convention for the momentum-sage orchestrator (Phase 9).
# The directory is created lazily by consumers via os.makedirs(CACHE_DIR, exist_ok=True).
CACHE_DIR = "/tmp/ms_cache"
CACHE_TTL_SECONDS = 3600  # 1 hour
