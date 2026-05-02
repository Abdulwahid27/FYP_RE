# Preliminary Report — Atelier: A Virtual Fashion Assistant

**Project Title:** Atelier — An AI-Powered Virtual Fashion Assistant for Personalised Outfit Try-On
**Author:** Abdul Wahid
**Degree:** B.S. (Final Year Project)
**Submission:** Preliminary Report

---

## Abstract

This preliminary report presents the proposed final year project titled **"Atelier — An AI-Powered Virtual Fashion Assistant"**. The main objective of this project is to address the problem of *online apparel shopping uncertainty* — the inability of consumers to see how a garment will actually look on them before purchase — by developing *an end-to-end web application that analyses the user's portrait, recommends context-aware outfits from real Pakistani retail brands, and renders a photo-realistic virtual try-on*. The proposed system aims to improve *consumer confidence, reduce return rates, and personalise the shopping experience* through the use of *multimodal Large Language Models (Google Gemma via OpenRouter), background-removal AI (`rembg`), the IDM-VTON diffusion model on Hugging Face, the OpenWeather API, React, FastAPI, and PostgreSQL*. The methodology involves *iterative full-stack development across five phases: requirement analysis, system design, AI service integration, web scraping for live brand catalogues, and end-to-end testing*. The expected outcome is a functional *web-based virtual fashion assistant* that contributes to *the e-commerce, fashion-tech, and applied computer-vision research areas*.

---

## Introduction

In recent years, **AI-driven personalisation in fashion e-commerce** has gained significant importance due to *the rapid growth of online apparel shopping, the high return rates caused by sizing/styling uncertainty, and the maturation of generative computer-vision models capable of synthesising realistic garment imagery*. According to industry estimates, fashion is the single largest category of online returns, with rates exceeding 30 % — most often because the buyer cannot tell *how the garment will look on them* until it physically arrives.

Many existing systems face challenges such as:

- **Static catalogues** that show only the brand's model wearing the garment, with no personalisation.
- **Generic recommendation engines** that ignore the user's skin tone, face shape, and the local context (weather, occasion, region).
- **No try-before-you-buy** capability — virtual fitting rooms either don't exist or require expensive AR hardware.
- **Locale gaps** — most fashion AI tools are built around Western brands and ignore South-Asian retailers entirely.

This project focuses on addressing these challenges by proposing **Atelier**, a single web application that:

1. Analyses an uploaded user portrait with a multimodal LLM to extract apparent **skin tone** and **face shape**.
2. Asks the user for context — **gender, location (Pakistani city), occasion, brand preference** — and pulls live **weather** for that city.
3. Displays a filtered catalogue of half-body garment images **scraped directly from real brand websites** (Khaadi, Outfitters, Sapphire, Generation, etc.).
4. On selection, automatically removes the garment's background and feeds it, along with the user's portrait, to the **IDM-VTON** diffusion model to render a personalised virtual try-on.

The aim is to provide a more efficient, reliable, and scalable approach to *helping users make confident clothing decisions online*.

---

## Problem Statement

Despite advancements in **e-commerce, computer vision, and generative AI**, there are still limitations such as:

- **Sizing/styling uncertainty.** Users cannot visualise how a specific garment will look on *their own body* before purchase, leading to high return rates and abandoned carts.
- **One-size-fits-all recommendations.** Existing recommendation systems rarely take *skin tone, face shape, weather, and occasion* into account simultaneously.
- **Fragmented user journey.** A typical online buying journey requires visiting several brand sites, manually filtering by occasion, and guessing the fit; no unified assistant exists.
- **Lack of localisation.** Most international virtual try-on tools are built for Western catalogues; South-Asian (specifically Pakistani) brands are absent from public datasets, models, and assistants.
- **AR/3D barriers.** Existing virtual fitting rooms often require AR hardware, in-store kiosks, or 3D body scans — none of which are practical for the average online shopper.

Existing solutions are often **expensive, hardware-dependent, locale-blind, or non-interactive**. Therefore, there is a need for a system that can **(a) accept a single portrait photograph from any device, (b) reason about the user's appearance and the local context, (c) surface relevant garments from actual retail brands, and (d) render a realistic virtual try-on entirely in the browser**. This project aims to bridge this gap by developing **Atelier**, a fully web-based virtual fashion assistant tailored to the Pakistani market.

---

## Objectives

- To **analyse the existing systems** (Amazon Style, Google Virtual Try-On, brand-specific apps) and identify their limitations in personalisation and locale coverage.
- To **design a solution** for context-aware outfit recommendation and virtual try-on suitable for Pakistani retail brands.
- To **develop a web application** (React + Tailwind frontend, FastAPI + PostgreSQL backend) that integrates **Google Gemma (multimodal LLM)**, **`rembg`**, **IDM-VTON**, and the **OpenWeather API**.
- To **scrape live brand catalogues** so that the displayed garments are real, current products rather than placeholder images.
- To **test and evaluate** the performance of the proposed system in terms of analysis accuracy, try-on realism, response time, and user-perceived quality.
- To **document the findings, architecture, and limitations** so the system can be extended or productised after the FYP.

---

## Literature Review

Previous studies have explored various approaches to **virtual try-on (VTON) and AI-driven fashion assistance**:

- **Geometry-based VTON.** Early works such as VITON (Han et al., 2018) and CP-VTON (Wang et al., 2018) used learned warping plus image composition to fit a 2-D garment onto a person. Output quality degraded under pose change and complex textures.
- **GAN-based VTON.** Methods such as ACGPN (Yang et al., 2020) and VITON-HD (Choi et al., 2021) improved high-resolution detail and occlusion handling using generative adversarial networks but still struggled with semantic consistency.
- **Diffusion-based VTON.** Recent work — most notably **IDM-VTON** (Choi et al., 2024) — uses a fine-tuned latent-diffusion backbone with garment encoders, producing photo-realistic results with much better preservation of garment identity. This is the model used in this project.
- **Multimodal LLMs for visual reasoning.** Models like **Google Gemma**, GPT-4V, and Llama-Vision can describe portraits and extract attributes (skin tone, face shape, age cues) from a single image. Their use as a *style-analysis* layer is novel in the VTON pipeline.
- **Background removal.** `rembg` (built on U²-Net) is a well-established open-source library for high-quality alpha-matte segmentation, allowing arbitrary product photos to be turned into transparent garment cut-outs.
- **Recommendation context.** Studies on contextual fashion recommendation (e.g. *Kang et al., 2017 — Visually-Aware Fashion Recommendation*) show that combining user attributes with situational context (weather, occasion) outperforms purely content-based recommendation.

However, these approaches often suffer from limitations such as **closed datasets, no personalisation layer, no live-catalogue integration, lack of South-Asian coverage, and no user-facing application**. Recent research suggests that combining a **multimodal LLM (for analysis) + a diffusion VTON model (for rendering) + live web data (for catalogue freshness)** produces a more useful, deployable assistant. This project builds upon these studies by **stitching them into a single, locally-relevant, end-to-end web product** rather than a research-only notebook.

---

## Methodology

### 1. Requirement Analysis

- Survey of existing fashion AI tools and their gaps for Pakistani users.
- Identification of functional requirements: portrait upload, analysis, context capture, catalogue browsing, try-on rendering, history.
- Identification of non-functional requirements: < 30 s for analysis, < 90 s for try-on, mobile-friendly UI, no name of underlying models exposed to the end-user, ability to cancel long-running operations.

### 2. System Design

The system is split into **frontend**, **backend**, and **external AI services**, communicating via JSON over HTTP:

```
┌──────────────────┐     POST /api/analyze     ┌──────────────────────┐     OpenRouter (Gemma)
│  React Frontend  │ ────────────────────────► │   FastAPI Backend    │ ────────────────────────►
│  (Vite, Tailwind)│                           │  (PostgreSQL, ORM)   │     OpenWeather API
│                  │ ◄──────────────────────── │                      │     IDM-VTON (HF Spaces)
│  Wizard: Upload  │     GET  /api/brands      │  Routes: analysis,   │     rembg (local)
│  → Context →     │     GET  /api/garments    │  brands, weather,    │
│  Catalog →       │     POST /api/tryon       │  tryon, sessions     │
│  Try-on → Save   │                           │                      │
└──────────────────┘                           └──────────────────────┘
                                                         │
                                                         ▼
                                            ┌──────────────────────────┐
                                            │  PostgreSQL              │
                                            │  brands, garments,       │
                                            │  user_sessions tables    │
                                            └──────────────────────────┘
```

**Database schema (high-level):**

- `brands(id, name, slug, gender_focus, occasions, website_url)`
- `garments(id, brand_id, title, occasion, gender, image_url, local_path, scraped_at)`
- `user_sessions(id, portrait_path, skin_tone, face_shape, gender, city, occasion, brand_id, garment_id, tryon_path, created_at)`

**Workflow (multi-step wizard):**

1. **Upload portrait** → backend stores it under `uploads/originals/`, sends to OpenRouter, receives JSON `{skin_tone, face_shape}`.
2. **Context** → user picks gender + city + occasion + brand. Backend calls OpenWeather for current weather.
3. **Catalogue** → backend serves a brand-/occasion-filtered list of garments scraped from real brand sites; images are proxied through the backend to bypass hot-link / CORS protections.
4. **Garment extraction** → on selection, `rembg` converts the chosen garment to a transparent PNG.
5. **Virtual try-on** → backend calls the IDM-VTON Gradio Space with the portrait + garment PNG, persists the result in `uploads/tryons/`, and streams the URL to the frontend.
6. **Save / retry** → user can save the try-on or re-roll a different garment.

### 3. Development

The system is implemented incrementally:

- **Backend.** FastAPI 0.110+, SQLAlchemy 2.x, Pydantic v2, `httpx` (async I/O), `aiofiles`, `rembg`, `gradio_client`, `beautifulsoup4` + `lxml` (catalogue scraping). Routes live in `backend/app/routes/`; AI integrations live in `backend/app/services/`.
- **Frontend.** React 18 + Vite + Tailwind CSS, organised as a multi-step wizard (`UploadStep`, `ContextStep`, `CatalogStep`, `TryOnStep`). Long-running calls are cancellable via `AbortController`; the backend mirrors that with `request.is_disconnected()` so wasted upstream calls are avoided.
- **Database.** PostgreSQL 16, schema managed by SQLAlchemy and seeded with curated brand data (Khaadi, Outfitters, Sapphire, Generation, …).
- **Privacy.** Names of underlying ML models (Gemma, IDM-VTON) are deliberately hidden in the UI; the user only sees neutral copy ("style analysis", "fitting service").

### 4. Testing

- **Unit tests** for the JSON-extraction helper and the `rembg` wrapper.
- **Integration tests** for the FastAPI endpoints using a test PostgreSQL schema.
- **End-to-end tests** by running the wizard with sample portraits of varying skin tones, face shapes, and lighting conditions.
- **Resilience tests** for upstream failures: simulated 429s from OpenRouter, ZeroGPU quota exhaustion from Hugging Face, network/DNS errors, and mid-request cancellation. Each is mapped to a user-safe message.
- **Performance benchmarking** of analysis (target < 15 s) and try-on (target < 90 s) on a typical broadband connection.

### 5. Deployment

- **Dev:** Vite dev server (`localhost:5173`) proxies `/api/*` to FastAPI (`localhost:8000`); PostgreSQL runs locally.
- **Prod (planned):**
  - Backend → Docker container on a VPS (e.g. DigitalOcean / Railway / Render).
  - Frontend → static build served by Nginx or Cloudflare Pages.
  - PostgreSQL → managed instance (Neon / Supabase / RDS).
  - Persistent uploads → object storage (S3-compatible, e.g. Cloudflare R2) instead of the local `uploads/` folder used in development.
  - Secrets managed via environment variables, never committed.

**Tools and technologies to be used include:** Python 3.12, FastAPI, SQLAlchemy, PostgreSQL, React 18, Vite, Tailwind CSS, OpenRouter (Google Gemma), Hugging Face Spaces (IDM-VTON), `rembg`, OpenWeather API, BeautifulSoup, Docker, Nginx.

---

## Expected Results

The expected outcome of this project is a fully functional **web-based virtual fashion assistant** that:

- **Solves the identified problem effectively** — letting any user upload a single portrait and see themselves wearing real, currently-available garments from Pakistani brands.
- **Improves efficiency, accuracy, and personalisation** by combining LLM-driven attribute analysis, weather/occasion context, and diffusion-based try-on in one flow.
- **Provides reliable results** with explicit handling of upstream rate-limits, quota exhaustion, and network errors, plus a user-controlled cancel ("Stop") button.
- **Can be used in real-world applications** — directly by end-users as a styling assistant, or licensed to retailers as an embeddable "try-on" widget. The modular architecture also makes it suitable as a reference platform for future research on locale-specific virtual try-on.

---

## Timeline

| Phase | Weeks |
|---|---|
| Literature Review | Week 1 – Week 3 |
| Requirement Analysis | Week 4 – Week 5 |
| Design Phase | Week 6 – Week 7 |
| Development | Week 8 – Week 12 |
| Testing & Evaluation | Week 13 – Week 14 |
| Documentation | Week 15 – Week 16 |

---

## References

1. Han, X., Wu, Z., Wu, Z., Yu, R., & Davis, L. S. *VITON: An Image-Based Virtual Try-On Network*. CVPR, 2018.
2. Wang, B., Zheng, H., Liang, X., et al. *Toward Characteristic-Preserving Image-Based Virtual Try-On Network (CP-VTON)*. ECCV, 2018.
3. Choi, S., Park, S., Lee, M., & Choo, J. *VITON-HD: High-Resolution Virtual Try-On via Misalignment-Aware Normalization*. CVPR, 2021.
4. Choi, Y., Kwak, S., Lee, K., et al. *Improving Diffusion Models for Authentic Virtual Try-On in the Wild (IDM-VTON)*. ECCV, 2024.
5. Kang, W.-C., Fang, C., Wang, Z., & McAuley, J. *Visually-Aware Fashion Recommendation and Design with Generative Image Models*. ICDM, 2017.
6. Qin, X., Zhang, Z., Huang, C., et al. *U²-Net: Going Deeper with Nested U-Structure for Salient Object Detection*. Pattern Recognition, 2020. (Underlying model of `rembg`.)
7. Google DeepMind. *Gemma: Open Models Based on Gemini Research and Technology*. Technical Report, 2024.
8. Hugging Face. *IDM-VTON Space*. https://huggingface.co/spaces/yisol/IDM-VTON
9. OpenRouter. *Multimodal Chat Completions API Documentation*. https://openrouter.ai/docs
10. OpenWeather. *Current Weather Data API*. https://openweathermap.org/current
11. FastAPI. *Official Documentation*. https://fastapi.tiangolo.com/
12. React. *Official Documentation*. https://react.dev/
13. Tailwind CSS. *Official Documentation*. https://tailwindcss.com/docs
14. PostgreSQL Global Development Group. *PostgreSQL 16 Documentation*. https://www.postgresql.org/docs/16/

---

*End of Preliminary Report.*
