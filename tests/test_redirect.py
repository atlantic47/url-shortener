"""Tests for URL redirection functionality."""

import pytest
from httpx import AsyncClient
from datetime import datetime, timedelta


@pytest.mark.asyncio
async def test_redirect_success(client: AsyncClient, sample_url):
    """Test successful redirect."""
    # Create short URL
    response = await client.post(
        "/shorten",
        json={"original_url": sample_url}
    )
    assert response.status_code == 201
    short_code = response.json()["short_code"]

    # Test redirect
    response = await client.get(
        f"/{short_code}",
        follow_redirects=False
    )
    assert response.status_code == 307
    assert response.headers["location"] == sample_url


@pytest.mark.asyncio
async def test_redirect_not_found(client: AsyncClient):
    """Test redirect for non-existent short code."""
    response = await client.get(
        "/nonexistent",
        follow_redirects=False
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_redirect_expired_url(client: AsyncClient, sample_url):
    """Test redirect for expired URL."""
    # Create URL with 1 second TTL
    response = await client.post(
        "/shorten",
        json={
            "original_url": sample_url,
            "ttl_seconds": 1
        }
    )
    assert response.status_code == 201
    short_code = response.json()["short_code"]

    # Wait for expiry
    import asyncio
    await asyncio.sleep(2)

    # Try to redirect
    response = await client.get(
        f"/{short_code}",
        follow_redirects=False
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_redirect_ab_test(client: AsyncClient, sample_url, sample_url_b):
    """Test A/B test redirection distribution."""
    # Create URL with A/B test (50/50 split)
    response = await client.post(
        "/shorten",
        json={
            "original_url": sample_url,
            "ab_test": {
                "url_b": sample_url_b,
                "split": 50
            }
        }
    )
    assert response.status_code == 201
    short_code = response.json()["short_code"]

    # Make multiple requests and track variants
    variant_a_count = 0
    variant_b_count = 0
    num_requests = 100

    for _ in range(num_requests):
        response = await client.get(
            f"/{short_code}",
            follow_redirects=False
        )
        assert response.status_code == 307

        location = response.headers["location"]
        if location == sample_url:
            variant_a_count += 1
        elif location == sample_url_b:
            variant_b_count += 1

    # Check that both variants were served
    assert variant_a_count > 0
    assert variant_b_count > 0

    # Check distribution is roughly 50/50 (with some tolerance)
    # Allow for 30-70% distribution due to randomness
    assert 30 <= variant_a_count <= 70
    assert 30 <= variant_b_count <= 70


@pytest.mark.asyncio
async def test_redirect_analytics_captured(client: AsyncClient, sample_url):
    """Test that analytics are captured during redirect."""
    # Create short URL
    response = await client.post(
        "/shorten",
        json={"original_url": sample_url}
    )
    assert response.status_code == 201
    short_code = response.json()["short_code"]

    # Perform redirect
    response = await client.get(
        f"/{short_code}",
        follow_redirects=False
    )
    assert response.status_code == 307

    # Wait a bit for background task
    import asyncio
    await asyncio.sleep(0.5)

    # Check analytics
    response = await client.get(f"/analytics/{short_code}")
    assert response.status_code == 200
    data = response.json()
    assert data["total_clicks"] == 1


@pytest.mark.asyncio
async def test_redirect_custom_alias(client: AsyncClient, sample_url):
    """Test redirect with custom alias."""
    custom_alias = "test-redirect"

    # Create short URL with custom alias
    response = await client.post(
        "/shorten",
        json={
            "original_url": sample_url,
            "custom_alias": custom_alias
        }
    )
    assert response.status_code == 201

    # Test redirect
    response = await client.get(
        f"/{custom_alias}",
        follow_redirects=False
    )
    assert response.status_code == 307
    assert response.headers["location"] == sample_url


@pytest.mark.asyncio
async def test_redirect_with_headers(client: AsyncClient, sample_url):
    """Test that redirect captures request headers."""
    # Create short URL
    response = await client.post(
        "/shorten",
        json={"original_url": sample_url}
    )
    assert response.status_code == 201
    short_code = response.json()["short_code"]

    # Perform redirect with custom headers
    response = await client.get(
        f"/{short_code}",
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/91.0",
            "Referer": "https://google.com"
        },
        follow_redirects=False
    )
    assert response.status_code == 307
