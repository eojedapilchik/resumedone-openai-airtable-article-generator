# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A FastAPI backend service that generates AI-powered blog articles, skills, translations, and reviews for ResumeDone. It orchestrates OpenAI for content generation, Airtable as the primary data store, and integrates with external services (Webflow, FrontApp, LemList, Instantly.ai).

## Commands

```bash
# Run the FastAPI server
uvicorn main:app --host 0.0.0.0

# Production server
gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000

# Celery worker (for LemList campaign tasks)
celery -A tasks worker --loglevel=INFO

# Install dependencies
pip install -r requirements.txt
```

## Architecture

**Entry point:** `main.py` — FastAPI app with all route definitions. Most endpoints trigger background tasks via `BackgroundTasks`.

**Core pipeline (article generation):**
1. API receives article request with `record_id`, `job_name`, `language`
2. Prompts are fetched from Airtable (table determined by `TABLE_{TYPE}_PROMPTS` env var)
3. `ArticleProcessor` iterates prompts, using the **Command pattern** to process each one
4. `PromptCommandFactory` selects a `PromptCommand` subclass based on prompt type (metadata, image, HTML, FAQ, example, etc.)
5. Each command calls OpenAI, formats the response as HTML, and stores it back in Airtable

**Key patterns:**
- **Command pattern** for prompt processing: `PromptCommandFactory` → `PromptCommand` subclasses in `models/prompt_commands.py`
- **Blog-specific design variants:** `BlogDesignCommandFactory` selects different FAQ/example HTML formatting based on blog name (e.g., `kreatorcv.com` gets different styling)
- `SkillProcessor` extends `ArticleProcessor` for skill JSON generation with separate Airtable DB configs (`DB1`/`DB2`)

**Handlers (`helpers/`):**
- `openai_handler.py` — Wraps OpenAI API (uses legacy `openai==0.28.1` SDK with `ChatCompletion.create`)
- `airtable_handler.py` — Wraps `pyairtable` for CRUD operations. Airtable fields are referenced by field IDs (e.g., `fld7vn74uF0ZxQhXe`)
- `frontapp_handler.py` — FrontApp API for review conversations. Supports multiple accounts (`great_ponton`, `ozuara`)
- `content_processor.py` — Batch translation using OpenAI vision model with image context
- `prompts_config.py` — Hardcoded prompt templates for URL generation, translation, skill generation, bullet extraction

**Models (`models/`):** Pydantic v2 models (`Article`, `Blog`, `Experience`, webhook payloads)

**Translations:** `translations/` contains JSON files keyed by ISO language codes (e.g., `translations_FR.json`)

## Environment

- Python 3.11, virtual env in `.venv/`
- Uses `.env` for all secrets and configuration (Airtable tokens, OpenAI keys, API tokens)
- Airtable field IDs are hardcoded throughout — when modifying record updates, reference existing field ID patterns
- Celery uses RabbitMQ as broker (`pyamqp://guest:guest@localhost//`)
- `config.json` maps Airtable base IDs to table/field configurations for article categorization
