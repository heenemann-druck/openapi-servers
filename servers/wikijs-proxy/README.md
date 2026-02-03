# Wiki.js Proxy (OpenAPI)

OpenAPI proxy for Wiki.js. Exposes CRUD operations (get, list, create, update) as REST endpoints so Open WebUI can use them as tools.

## Environment

- `WIKIJS_URL` – Base URL of Wiki.js (default: `http://wikijs:3000`)
- `WIKIJS_API_KEY` – API token from Wiki.js **Administration → API Access** (required)

## Endpoints

- `POST /get_page` – Get a page by path (`{"path": "/HW/Workstation-01"}`)
- `POST /list_pages` – List all pages
- `POST /create_page` – Create a page (path, title, content, optional description, locale, tags)
- `POST /update_page` – Update a page by ID (content, title, or description)

## Open WebUI

In **Admin → Tools**, add a **Global Tool Server** with URL `http://wikijs-proxy:8000` (or the host/port where this service runs). Users can then enable the Wiki tools in chat.
