# Atelier — Virtual Fashion Assistant

A full-stack virtual fashion studio. Upload a portrait, get a quick read on
skin tone & face shape, pick a context (gender, city + live weather, occasion,
preferred brand), browse a curated catalog, and try a garment on virtually.

> User-facing copy intentionally never mentions the underlying models or
> service names — they're hidden behind friendly product language.

## Stack

- **Frontend**: React 18 + Vite + Tailwind CSS
- **Backend**: FastAPI (Python 3.11+)
- **Database**: PostgreSQL (SQLAlchemy 2.x)
- **Vision analysis**: OpenRouter (multimodal LLM, configurable)
- **Weather**: OpenWeather
- **Background removal**: `rembg`
- **Virtual try-on**: `yisol/IDM-VTON` HF Space via `gradio_client`

## Project structure

```
fypv2/
├── .env                    # shared API keys & DB URL
├── backend/
│   ├── app/                # FastAPI application
│   ├── uploads/            # originals / extracted garments / try-ons
│   └── requirements.txt
└── frontend/               # Vite + React + Tailwind
```

## 1. Configure secrets

`/.env` already has the keys you supplied. Confirm:

```env
OPEN_ROUTER_API_KEY=...
OPENROUTER_MODEL=google/gemma-3-27b-it:free
HF_TOKEN=...
OPENWEATHER_API_KEY=...
DATABASE_URL=postgresql://abdul-wahid:fashion@localhost:5432/fashion
VTON_SPACE=yisol/IDM-VTON
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
```

> Note on `OPENROUTER_MODEL`: your prompt mentioned `google/gemma-4`, but
> there's no Gemma 4 model on OpenRouter. The default above is the closest
> free, multimodal-capable Gemma model. Swap it for any vision-capable
> OpenRouter model (e.g. `meta-llama/llama-3.2-11b-vision-instruct:free`,
> `google/gemini-2.0-flash-exp:free`) if you prefer.

## 2. Postgres

Make sure the database exists and the role can connect:

```bash
sudo -u postgres psql <<'SQL'
CREATE USER "abdul-wahid" WITH PASSWORD 'fashion';
CREATE DATABASE fashion OWNER "abdul-wahid";
GRANT ALL PRIVILEGES ON DATABASE fashion TO "abdul-wahid";
SQL
```

The schema is created automatically on backend boot via SQLAlchemy
`create_all`.

## 3. Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# seed brands & garments
python -m app.seed

# run the API
uvicorn app.main:app --reload --port 8000
```

API docs at http://localhost:8000/docs.

> The first run of `rembg` downloads its U²-Net model (~170MB) into
> `~/.u2net/`. The first virtual try-on call also has to spin up the HF
> Space (warm-up can take 30–60s).

## 4. Frontend

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173. The Vite dev server proxies `/api` and
`/uploads` to the backend on port 8000, so there's nothing else to wire up.

## API surface (all under `/api`)

| Method | Path                  | Purpose                                                     |
| ------ | --------------------- | ----------------------------------------------------------- |
| GET    | `/health`             | Liveness probe                                              |
| POST   | `/analyze`            | Multipart upload of a portrait → skin tone + face shape     |
| GET    | `/cities`             | Major Pakistan cities                                       |
| GET    | `/weather?city=`      | Current weather for the given city                          |
| POST   | `/context`            | Persists gender / city / occasion / brand on the session    |
| GET    | `/brands`             | List brands                                                 |
| GET    | `/garments`           | Filter by `gender`, `occasion`, optional `brand_id`         |
| POST   | `/tryon`              | Extract garment background + run virtual try-on             |
| GET    | `/sessions`           | Recent session history                                      |

Static files (originals, extracted garments, final try-ons) are served at
`/uploads/...`.

## Schema

- **brands** — `id, name, slug, description, logo_url, website`
- **garments** — `id, brand_id, title, gender, occasion, image_url, price, color, extracted_path`
- **user_sessions** — `id, created_at, portrait_path, skin_tone, face_shape, analysis_raw, gender, city, weather, occasion, brand_id, selected_garment_id, tryon_path`

## Workflow

1. **Upload** — Portrait is saved to `backend/uploads/originals/` and sent
   to the configured multimodal model. The model returns
   `{ skin_tone, face_shape }`, which is shown back to the user.
2. **Context** — Gender, city (Pakistan dropdown), occasion, and (optional)
   brand. The city triggers a live OpenWeather lookup that is also
   persisted on the session.
3. **Catalog** — Garments filtered by `gender × occasion` (and brand if
   chosen) are rendered in a grid.
4. **Try-On** — On selection: `rembg` cuts the garment to a transparent
   PNG, then `gradio_client` calls the IDM-VTON HF Space with the original
   portrait + extracted garment.
5. **Result** — Final image rendered with a save button.
