# TezMindz Backend

Django REST backend for TezMindz — a gamified Olympiad-prep platform for
Grades 1–5 (initially). This backend is frontend-independent: React, a
future mobile app, or anything else can consume the same REST API.

**Current phase: Phase 3 — Database / models only.** There are
deliberately no views, serializers, or URLs beyond Django Admin yet.
This README will grow as later phases land.

---

## What exists right now

| App | Purpose |
|---|---|
| `apps/accounts` | Custom `User`, `StudentProfile`, `ParentProfile`, `MentorProfile` |
| `apps/curriculum` | `Grade` → `Subject` → `Topic` → `Concept`, with a DRAFT→PUBLISHED content lifecycle |
| `apps/games` | `Game` metadata/config, `GameSession` attempt tracking (Django never renders the game itself) |
| `apps/assessments` | `Question`/`Option`/`Hint` bank, `Quiz`, `QuizAttempt`/`QuestionResponse` |
| `apps/gamification` | `CreditAccount`/`CreditTransaction`, `XPAccount`/`XPTransaction` (real ledgers, not a mutable counter), `Badge`/`StudentBadge` |
| `apps/progress` | `TopicProgress` — the source rows that subject/grade performance rollups will aggregate from |
| `apps/subscriptions` | `Plan`, `Subscription`, `TrialGameLog` (3-distinct-games free trial), `Payment` |
| `apps/analytics` | Append-only `Event` log |
| `common/` | `TimeStampedModel`, `UUIDPublicIDMixin`, `PublishableModel`/`PublishedManager`, and the shared DRF exception handler |

Every design decision that isn't obvious from the code has a comment
explaining *why* (e.g. why `Grade` uses `on_delete=PROTECT`, why credit
transactions have a unique `reference` constraint, why `QuestionResponse`
snapshots correctness instead of deriving it live). Read the model files
directly — the comments are part of the deliverable, not just code.

### Confirmed vs. assumed vs. still open

- **CONFIRMED:** free trial = 3 *distinct* games (`TrialGameLog`,
  unique on `student+game` — replays never consume a second slot).
  Auth stack = djoser + simplejwt.
- **ASSUMPTION (flagged in code):** no `date_of_birth` collected on
  `StudentProfile` — grade implies age band, minimizing data collected
  from children. Revisit if a school/partner integration ever needs
  real DOB.
- **TODO — needs your/business confirmation before it's real data:**
  `Plan` names, prices, and features (subscriptions app) — the model
  exists, no real plan rows do. Payment provider (Razorpay/Stripe/etc.)
  is not decided; `Payment.provider` is a free-text field on purpose so
  that decision doesn't require a migration.

---

## Setup

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env            # edit if needed — defaults work for local dev

python manage.py migrate
python manage.py createsuperuser   # optional — Django Admin has nothing to manage yet (Phase 11)
python manage.py runserver
```

With no `DATABASE_URL` set, it runs on local sqlite automatically — no
Postgres install required just to try this out. Set `DATABASE_URL` in
`.env` to point at real Postgres (see `.env.example`); nothing else
changes.

`config/settings/prod.py` is intentionally stricter: it has **no** sqlite
fallback and will fail at startup without `DATABASE_URL`, so a
misconfigured production deploy fails loudly instead of quietly writing
to a throwaway local file.

## How to test what's been built

```bash
python manage.py check          # Django's own system check — should say "no issues"
python manage.py test apps      # 5 tests, all currently passing
```

The tests aren't placeholders — each one proves a specific design
decision actually holds at the database level, not just in a comment:

- `apps/gamification/tests.py` — a `CreditTransaction` with a
  `reference` that's already been used for that account is rejected
  by the DB (`IntegrityError`), which is the foundation Phase 6's
  "don't double-pay a duplicate completion request" logic will sit on.
- `apps/curriculum/tests.py` — a `Grade` with enrolled students cannot
  be deleted (`ProtectedError`), and duplicate topic titles within the
  same subject+grade are rejected.
- `apps/subscriptions/tests.py` — replaying an already-logged trial
  game raises `IntegrityError` rather than quietly consuming a second
  trial slot.

I also verified the whole thing (`check` → `migrate` → `test`) from
`requirements.txt` alone in a completely separate virtual environment,
not just the one I built it in — so a fresh clone is known to work, not
just assumed to.

To poke at the models directly:

```bash
python manage.py shell
>>> from apps.curriculum.models import Grade
>>> Grade.objects.create(name="Grade 4", order=4)
```

---

## What's deliberately NOT here yet

- No views, serializers, permissions, or URLs beyond `admin/` — that's
  Phase 4 onward.
- No Django Admin registration (`admin.py` files are empty stubs) —
  Phase 11.
- No real `Plan`/pricing data, no payment provider integration.
- No seed/demo data — Phase 12 area, and per the project's own rule,
  demo content will never be presented as approved Olympiad syllabus.
- No API documentation generation (drf-spectacular or similar) — added
  when there are actual endpoints to document (Phase 13).

## Next phase

**Phase 4 — Authentication and users**, using the confirmed djoser +
simplejwt stack: wire up `/api/v1/auth/` (register, login, refresh,
logout, password change/reset) and the permission classes
(`IsStudent`, `IsMentor`, `IsAdmin`) that later phases will depend on.
