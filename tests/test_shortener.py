"""Tests for URL shortening functionality."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_shorten_url_success(client: AsyncClient, sample_url):
    """Test successful URL shortening."""
    response = await client.post(
        "/shorten",
        json={"original_url": sample_url}
    )

    assert response.status_code == 201
    data = response.json()
    assert "short_url" in data
    assert "short_code" in data
    assert "created_at" in data
    assert data["expires_at"] is None
    assert len(data["short_code"]) == 7


@pytest.mark.asyncio
async def test_shorten_url_with_ttl(client: AsyncClient, sample_url):
    """Test URL shortening with TTL."""
    response = await client.post(
        "/shorten",
        json={
            "original_url": sample_url,
            "ttl_seconds": 3600
        }
    )

    assert response.status_code == 201
    data = response.json()
    assert data["expires_at"] is not None


@pytest.mark.asyncio
async def test_shorten_url_with_custom_alias(client: AsyncClient, sample_url):
    """Test URL shortening with custom alias."""
    custom_alias = "my-custom-link"
    response = await client.post(
        "/shorten",
        json={
            "original_url": sample_url,
            "custom_alias": custom_alias
        }
    )

    assert response.status_code == 201
    data = response.json()
    assert data["short_code"] == custom_alias


@pytest.mark.asyncio
async def test_shorten_url_with_ab_test(client: AsyncClient, sample_url, sample_url_b):
    """Test URL shortening with A/B test configuration."""
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
    data = response.json()
    assert "short_code" in data


@pytest.mark.asyncio
async def test_custom_alias_invalid_chars(client: AsyncClient, sample_url):
    """Test custom alias with invalid characters."""
    response = await client.post(
        "/shorten",
        json={
            "original_url": sample_url,
            "custom_alias": "invalid@alias!"
        }
    )

    assert response.status_code == 422  # Pydantic validation error


@pytest.mark.asyncio
async def test_custom_alias_too_short(client: AsyncClient, sample_url):
    """Test custom alias that is too short."""
    response = await client.post(
        "/shorten",
        json={
            "original_url": sample_url,
            "custom_alias": "ab"
        }
    )

    assert response.status_code == 422  # Pydantic validation error


@pytest.mark.asyncio
async def test_custom_alias_duplicate(client: AsyncClient, sample_url):
    """Test duplicate custom alias rejection."""
    custom_alias = "duplicate-test"

    # Create first URL
    response1 = await client.post(
        "/shorten",
        json={
            "original_url": sample_url,
            "custom_alias": custom_alias
        }
    )
    assert response1.status_code == 201

    # Try to create second URL with same alias
    response2 = await client.post(
        "/shorten",
        json={
            "original_url": "https://different.com",
            "custom_alias": custom_alias
        }
    )
    assert response2.status_code == 400
    assert "already taken" in response2.json()["detail"]


@pytest.mark.asyncio
async def test_invalid_url(client: AsyncClient):
    """Test invalid URL format."""
    response = await client.post(
        "/shorten",
        json={"original_url": "not-a-valid-url"}
    )

    assert response.status_code == 422  # Pydantic validation error


@pytest.mark.asyncio
async def test_custom_alias_reserved_word(client: AsyncClient, sample_url):
    """Test custom alias with reserved word."""
    response = await client.post(
        "/shorten",
        json={
            "original_url": sample_url,
            "custom_alias": "admin"
        }
    )

    assert response.status_code == 400
    assert "reserved" in response.json()["detail"]


@pytest.mark.asyncio
async def test_ab_test_invalid_split(client: AsyncClient, sample_url, sample_url_b):
    """Test A/B test with invalid split percentage."""
    response = await client.post(
        "/shorten",
        json={
            "original_url": sample_url,
            "ab_test": {
                "url_b": sample_url_b,
                "split": 150  # Invalid: > 100
            }
        }
    )

    assert response.status_code == 422  # Pydantic validation error
