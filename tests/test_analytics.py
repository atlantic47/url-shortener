"""Tests for analytics functionality."""

import pytest
from httpx import AsyncClient
import asyncio


@pytest.mark.asyncio
async def test_analytics_empty(client: AsyncClient, sample_url):
    """Test analytics for URL with no clicks."""
    # Create short URL
    response = await client.post(
        "/shorten",
        json={"original_url": sample_url}
    )
    assert response.status_code == 201
    short_code = response.json()["short_code"]

    # Get analytics
    response = await client.get(f"/analytics/{short_code}")
    assert response.status_code == 200

    data = response.json()
    assert data["short_code"] == short_code
    assert data["total_clicks"] == 0
    assert data["unique_visitors"] == 0
    assert data["first_click"] is None
    assert data["last_click"] is None
    assert len(data["clicks_by_day"]) == 0
    assert len(data["top_countries"]) == 0
    assert len(data["top_cities"]) == 0
    assert data["ab_test_results"] is None


@pytest.mark.asyncio
async def test_analytics_with_clicks(client: AsyncClient, sample_url):
    """Test analytics after generating clicks."""
    # Create short URL
    response = await client.post(
        "/shorten",
        json={"original_url": sample_url}
    )
    assert response.status_code == 201
    short_code = response.json()["short_code"]

    # Generate multiple clicks
    num_clicks = 5
    for _ in range(num_clicks):
        await client.get(f"/{short_code}", follow_redirects=False)

    # Wait for background tasks
    await asyncio.sleep(0.5)

    # Get analytics
    response = await client.get(f"/analytics/{short_code}")
    assert response.status_code == 200

    data = response.json()
    assert data["total_clicks"] == num_clicks
    assert data["unique_visitors"] >= 1  # At least one unique IP
    assert data["first_click"] is not None
    assert data["last_click"] is not None
    assert len(data["clicks_by_day"]) > 0


@pytest.mark.asyncio
async def test_analytics_not_found(client: AsyncClient):
    """Test analytics for non-existent short code."""
    response = await client.get("/analytics/nonexistent")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_analytics_ab_test(client: AsyncClient, sample_url, sample_url_b):
    """Test analytics for A/B test."""
    # Create URL with A/B test
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

    # Generate clicks
    for _ in range(10):
        await client.get(f"/{short_code}", follow_redirects=False)

    # Wait for background tasks
    await asyncio.sleep(0.5)

    # Get analytics
    response = await client.get(f"/analytics/{short_code}")
    assert response.status_code == 200

    data = response.json()
    assert data["ab_test_results"] is not None
    assert "variant_a_clicks" in data["ab_test_results"]
    assert "variant_b_clicks" in data["ab_test_results"]

    # Total should equal sum of variants
    total_variant_clicks = (
        data["ab_test_results"]["variant_a_clicks"] +
        data["ab_test_results"]["variant_b_clicks"]
    )
    assert total_variant_clicks == data["total_clicks"]


@pytest.mark.asyncio
async def test_analytics_device_breakdown(client: AsyncClient, sample_url):
    """Test device breakdown in analytics."""
    # Create short URL
    response = await client.post(
        "/shorten",
        json={"original_url": sample_url}
    )
    assert response.status_code == 201
    short_code = response.json()["short_code"]

    # Generate click with user agent
    await client.get(
        f"/{short_code}",
        headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/91.0"},
        follow_redirects=False
    )

    # Wait for background task
    await asyncio.sleep(0.5)

    # Get analytics
    response = await client.get(f"/analytics/{short_code}")
    assert response.status_code == 200

    data = response.json()
    assert len(data["devices"]) > 0
    assert len(data["browsers"]) > 0
    assert len(data["operating_systems"]) > 0


@pytest.mark.asyncio
async def test_analytics_unique_visitors(client: AsyncClient, sample_url):
    """Test unique visitor counting."""
    # Create short URL
    response = await client.post(
        "/shorten",
        json={"original_url": sample_url}
    )
    assert response.status_code == 201
    short_code = response.json()["short_code"]

    # Generate multiple clicks from same client
    for _ in range(3):
        await client.get(f"/{short_code}", follow_redirects=False)

    # Wait for background tasks
    await asyncio.sleep(0.5)

    # Get analytics
    response = await client.get(f"/analytics/{short_code}")
    assert response.status_code == 200

    data = response.json()
    assert data["total_clicks"] == 3
    # All clicks from same test client, so unique visitors should be 1
    assert data["unique_visitors"] == 1


@pytest.mark.asyncio
async def test_analytics_clicks_by_day(client: AsyncClient, sample_url):
    """Test clicks by day aggregation."""
    # Create short URL
    response = await client.post(
        "/shorten",
        json={"original_url": sample_url}
    )
    assert response.status_code == 201
    short_code = response.json()["short_code"]

    # Generate clicks
    for _ in range(5):
        await client.get(f"/{short_code}", follow_redirects=False)

    # Wait for background tasks
    await asyncio.sleep(0.5)

    # Get analytics
    response = await client.get(f"/analytics/{short_code}")
    assert response.status_code == 200

    data = response.json()
    assert len(data["clicks_by_day"]) > 0

    # Verify structure
    for day_data in data["clicks_by_day"]:
        assert "date" in day_data
        assert "count" in day_data
        assert day_data["count"] > 0
