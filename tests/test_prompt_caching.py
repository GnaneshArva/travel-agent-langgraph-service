import time
import pytest
from app.prompts.prompt_cache import PromptCache
from app.config.settings import settings
from app.dto.context import ExecutionContext, PromptContext, MemoryContext, KnowledgeContext
from app.integrations.prompt_management.prompt_management_client import PromptManagementClient
from app.strategies.prompt import PolicyAwareStrategy, DynamicStrategy

def test_prompt_cache_basic_ops():
    cache = PromptCache(default_ttl=10, max_size=5)
    cache.clear()

    # Initial state
    assert cache.stats["size"] == 0
    assert cache.stats["hits"] == 0
    assert cache.stats["misses"] == 0

    # Miss
    assert cache.get("key1") is None
    assert cache.stats["misses"] == 1

    # Set and Hit
    cache.set("key1", "rendered_prompt_value")
    assert cache.get("key1") == "rendered_prompt_value"
    assert cache.stats["hits"] == 1
    assert cache.stats["size"] == 1
    assert cache.stats["hit_rate_pct"] == 50.0

def test_prompt_cache_ttl_expiration():
    cache = PromptCache(default_ttl=1, max_size=5)
    cache.clear()

    cache.set("exp_key", "temp_value", ttl=1)
    assert cache.get("exp_key") == "temp_value"

    # Wait for TTL expiration
    time.sleep(1.1)
    assert cache.get("exp_key") is None

def test_prompt_cache_lru_eviction():
    cache = PromptCache(default_ttl=10, max_size=2)
    cache.clear()

    cache.set("k1", "v1")
    time.sleep(0.01)
    cache.set("k2", "v2")
    assert cache.stats["size"] == 2

    # Adding k3 should evict least recently used (k1)
    time.sleep(0.01)
    cache.set("k3", "v3")
    assert cache.stats["size"] == 2
    assert cache.get("k1") is None
    assert cache.get("k2") == "v2"
    assert cache.get("k3") == "v3"
    assert cache.stats["evictions"] == 1

@pytest.mark.anyio
async def test_prompt_management_client_caching():
    client = PromptManagementClient()
    
    # First call - cache miss
    ctx1 = await client.load_prompt("travel_agent_system", "1.0.0", {"destination": "Tokyo"})
    assert ctx1.rendered_prompt is not None

    # Second call with identical params - cache hit
    ctx2 = await client.load_prompt("travel_agent_system", "1.0.0", {"destination": "Tokyo"})
    assert ctx2.rendered_prompt == ctx1.rendered_prompt

@pytest.mark.anyio
async def test_policy_aware_strategy_prompt_prefix_order():
    strategy = PolicyAwareStrategy()
    prompt_ctx = PromptContext(
        template_name="travel_agent_system",
        rendered_prompt="Base System Instructions Here.",
        variables={}
    )
    exec_ctx = ExecutionContext(
        user_id="u1",
        conversation_id="c1",
        user_request="Plan a trip to Rome",
        session_id="s1",
        request_id="r1",
        trace_id="t1",
        memory_context=MemoryContext(user_preferences={"seat": "window", "meal": "vegan"}),
        knowledge_context=KnowledgeContext(destination="Rome", advisories=["Stay hydrated"])
    )

    rendered = await strategy.render(prompt_ctx, exec_ctx)

    # Verify static base and policy appear BEFORE dynamic context for Provider Prompt Caching
    base_idx = rendered.find("Base System Instructions Here.")
    policy_idx = rendered.find("[CORPORATE TRAVEL POLICY ENFORCEMENT]")
    prefs_idx = rendered.find("[USER PREFERENCES]")
    adv_idx = rendered.find("[TRAVEL ADVISORIES]")

    assert base_idx != -1
    assert policy_idx != -1
    assert prefs_idx != -1
    assert adv_idx != -1

    # Static prefix order check: Base < Policy < Preferences < Advisories
    assert base_idx < policy_idx < prefs_idx < adv_idx
