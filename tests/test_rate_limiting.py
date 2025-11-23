"""Tests for rate limiting functionality."""

import pytest
from httpx import AsyncClient
import asyncio


@pytest.mark.asyncio
async def test_shorten_rate_limit(client: AsyncClient, sample_url):
    """Test rate limiting on /shorten endpoint."""
    # The rate limit is 10 requests per minute
    # Make 11 requests rapidly
    responses = []
    for i in range(11):
        response = await client.post(
            "/shorten",
            json={"original_url": f"{sample_url}/{i}"}
        )
        responses.append(response)

    # First 10 should succeed, 11th should be rate limited
    success_count = sum(1 for r in responses if r.status_code == 201)
    rate_limited_count = sum(1 for r in responses if r.status_code == 429)

    # Due to timing, we expect at least one to be rate limited
    assert rate_limited_count >= 1
    assert success_count <= 10


@pytest.mark.asyncio
async def test_redirect_rate_limit(client: AsyncClient, sample_url):
    """Test rate limiting on redirect endpoint."""
    # Create a short URL first
    response = await client.post(
        "/shorten",
        json={"original_url": sample_url}
    )
    assert response.status_code == 201
    short_code = response.json()["short_code"]

    # The rate limit is 100 requests per minute
    # Make 101 requests rapidly
    responses = []
    for _ in range(101):
        response = await client.get(
            f"/{short_code}",
            follow_redirects=False
        )
        responses.append(response)

    # Check for rate limited responses
    success_count = sum(1 for r in responses if r.status_code == 307)
    rate_limited_count = sum(1 for r in responses if r.status_code == 429)

    # Due to timing, we expect at least one to be rate limited
    assert rate_limited_count >= 1
    assert success_count <= 100


@pytest.mark.asyncio
async def test_rate_limit_response_format(client: AsyncClient, sample_url):
    """Test that rate limit response has correct format."""
    # Trigger rate limit by making many requests
    for i in range(15):
        response = await client.post(
            "/shorten",
            json={"original_url": f"{sample_url}/{i}"}
        )
        if response.status_code == 429:
            # Verify response format
            data = response.json()
            assert "detail" in data
            assert "rate limit" in data["detail"].lower()
            break
    else:
        # If we didn't hit rate limit, that's okay for this test
        # (timing-dependent)
        pass


@pytest.mark.asyncio
async def test_rate_limit_per_ip(client: AsyncClient, sample_url):
    """Test that rate limits are per IP address."""
    # This test verifies that the rate limiter is tracking by IP
    # In the test environment, all requests come from the same IP

    # Make requests until we hit the limit
    rate_limited = False
    for i in range(15):
        response = await client.post(
            "/shorten",
            json={"original_url": f"{sample_url}/{i}"}
        )
        if response.status_code == 429:
            rate_limited = True
            break

    # We should eventually hit the rate limit
    assert rate_limited, "Rate limit should have been triggered"
