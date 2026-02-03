"""Wiki.js GraphQL API client."""
import httpx

from app.config import GRAPHQL_URL, WIKIJS_API_KEY


def _headers() -> dict:
    return {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {WIKIJS_API_KEY}",
    }


async def get_page_by_path(path: str) -> dict | None:
    """Fetch a single page by path. Returns None if not found."""
    query = """
    query GetPage($path: String!) {
      pages {
        singleByPath(path: $path) {
          id
          path
          title
          content
          description
          locale
          createdAt
          updatedAt
        }
      }
    }
    """
    async with httpx.AsyncClient(timeout=30.0) as client:
        r = await client.post(
            GRAPHQL_URL,
            json={"query": query, "variables": {"path": path}},
            headers=_headers(),
        )
        r.raise_for_status()
        data = r.json()
        if "errors" in data:
            return None
        page = (data.get("data") or {}).get("pages", {}).get("singleByPath")
        return page


async def list_pages(order_by: str = "TITLE") -> list[dict]:
    """List all pages. order_by: TITLE, PATH, UPDATED, CREATED."""
    query = """
    query ListPages($orderBy: PageOrderByEnum) {
      pages {
        list(orderBy: $orderBy) {
          id
          path
          title
          description
          updatedAt
        }
      }
    }
    """
    async with httpx.AsyncClient(timeout=30.0) as client:
        r = await client.post(
            GRAPHQL_URL,
            json={"query": query, "variables": {"orderBy": order_by}},
            headers=_headers(),
        )
        r.raise_for_status()
        data = r.json()
        if "errors" in data:
            return []
        items = (data.get("data") or {}).get("pages", {}).get("list") or []
        return items


async def create_page(
    path: str,
    title: str,
    content: str,
    description: str = "",
    locale: str = "en",
    is_published: bool = True,
    tags: list[str] | None = None,
) -> dict:
    """Create a new wiki page. Returns response with responseResult and page."""
    mutation = """
    mutation CreatePage(
      $path: String!,
      $title: String!,
      $content: String!,
      $description: String!,
      $locale: String!,
      $isPublished: Boolean!,
      $tags: [String]!
    ) {
      pages {
        create(
          path: $path,
          title: $title,
          content: $content,
          description: $description,
          editor: "markdown",
          locale: $locale,
          isPublished: $isPublished,
          isPrivate: false,
          tags: $tags
        ) {
          responseResult {
            succeeded
            errorCode
            slug
            message
          }
          page {
            id
            path
            title
          }
        }
      }
    }
    """
    variables = {
        "path": path,
        "title": title,
        "content": content,
        "description": description or title,
        "locale": locale,
        "isPublished": is_published,
        "tags": tags or [],
    }
    async with httpx.AsyncClient(timeout=30.0) as client:
        r = await client.post(
            GRAPHQL_URL,
            json={"query": mutation, "variables": variables},
            headers=_headers(),
        )
        r.raise_for_status()
        return r.json()


async def update_page(
    page_id: int,
    content: str | None = None,
    title: str | None = None,
    description: str | None = None,
) -> dict:
    """Update an existing page by ID. At least one of content, title, description must be set."""
    mutation = """
    mutation UpdatePage(
      $id: Int!,
      $content: String,
      $title: String,
      $description: String
    ) {
      pages {
        update(
          id: $id,
          content: $content,
          title: $title,
          description: $description
        ) {
          responseResult {
            succeeded
            errorCode
            slug
            message
          }
          page {
            id
            path
            title
          }
        }
      }
    }
    """
    variables = {"id": page_id, "content": content, "title": title, "description": description}
    async with httpx.AsyncClient(timeout=30.0) as client:
        r = await client.post(
            GRAPHQL_URL,
            json={"query": mutation, "variables": variables},
            headers=_headers(),
        )
        r.raise_for_status()
        return r.json()
