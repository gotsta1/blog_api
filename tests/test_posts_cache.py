import json

import pytest
from httpx import AsyncClient

from app.redis import redis_client

pytestmark = pytest.mark.asyncio(loop_scope="session")


async def test_create_post(client: AsyncClient):
    resp = await client.post(
        "/posts",
        json={"title": "Test", "content": "Hello"},
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["title"] == "Test"
    assert data["content"] == "Hello"
    assert "id" in data


async def test_get_post_caches_on_first_request(
    client: AsyncClient,
):
    """First GET fetches from DB and stores in Redis."""
    create_resp = await client.post(
        "/posts",
        json={"title": "Cached", "content": "Body"},
    )
    post_id = create_resp.json()["id"]

    assert await redis_client.get(f"post:{post_id}") is None

    resp = await client.get(f"/posts/{post_id}")
    assert resp.status_code == 200
    assert resp.json()["title"] == "Cached"

    cached = await redis_client.get(f"post:{post_id}")
    assert cached is not None
    assert json.loads(cached)["title"] == "Cached"


async def test_get_post_serves_from_cache(
    client: AsyncClient,
):
    """Second GET is served from Redis cache."""
    create_resp = await client.post(
        "/posts",
        json={"title": "From Cache", "content": "Body"},
    )
    post_id = create_resp.json()["id"]

    await client.get(f"/posts/{post_id}")

    resp = await client.get(f"/posts/{post_id}")
    assert resp.status_code == 200
    assert resp.json()["title"] == "From Cache"


async def test_update_invalidates_cache(
    client: AsyncClient,
):
    """PUT /posts/{id} removes post from cache."""
    create_resp = await client.post(
        "/posts",
        json={"title": "Old Title", "content": "Body"},
    )
    post_id = create_resp.json()["id"]

    await client.get(f"/posts/{post_id}")
    assert await redis_client.get(f"post:{post_id}") is not None

    update_resp = await client.put(
        f"/posts/{post_id}",
        json={"title": "New Title"},
    )
    assert update_resp.status_code == 200
    assert update_resp.json()["title"] == "New Title"

    assert await redis_client.get(f"post:{post_id}") is None


async def test_delete_invalidates_cache(
    client: AsyncClient,
):
    """DELETE /posts/{id} removes post from cache."""
    create_resp = await client.post(
        "/posts",
        json={"title": "To Delete", "content": "Body"},
    )
    post_id = create_resp.json()["id"]

    await client.get(f"/posts/{post_id}")
    assert await redis_client.get(f"post:{post_id}") is not None

    del_resp = await client.delete(f"/posts/{post_id}")
    assert del_resp.status_code == 204

    assert await redis_client.get(f"post:{post_id}") is None
    resp = await client.get(f"/posts/{post_id}")
    assert resp.status_code == 404


async def test_get_nonexistent_post(client: AsyncClient):
    response = await client.get("/posts/999999")
    assert response.status_code == 404


async def test_list_posts_pagination(client: AsyncClient):
    for i in range(5):
        await client.post(
            "/posts",
            json={
                "title": f"Post {i}",
                "content": "Body",
            },
        )

    resp = await client.get("/posts", params={"limit": 3})
    assert resp.status_code == 200
    assert len(resp.json()) == 3
