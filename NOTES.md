# ⚡ SnappCart — Quick Notes (Day 1 → Day 8)

---

## 🏗️ Architecture Decision

| Layer | Tech | Why |
|-------|------|-----|
| Frontend | Next.js 14 + TypeScript | SSR for SEO, file routing |
| State | Redux Toolkit | Global state across components |
| Backend | FastAPI (Python) | Async, auto docs, Pydantic validation |
| Primary DB | PostgreSQL | Relational, ACID, transactions |
| Catalog DB | MongoDB Atlas | Flexible schema for product specs |
| Cache | Redis | Fast, TTL, temporary data |
| Search | Meilisearch | Fuzzy search, typo tolerance |
| Storage | AWS S3 + CloudFront | Images, files, CDN |
| Events | Kafka | Order events pipeline |
| AI | Gemini API | Chatbot, search, moderation |

---

## 🔌 Who Connects What

```
Next.js  →  MongoDB Atlas     (READ only — SEO product pages)
Next.js  →  FastAPI           (everything else via Axios/fetch)

FastAPI  →  PostgreSQL        (users, orders, payments, reviews)
FastAPI  →  MongoDB Atlas     (product CRUD + variants)
FastAPI  →  Redis             (cart, OTP, sessions, cache)
FastAPI  →  Meilisearch       (search index sync after writes)
FastAPI  →  AWS S3            (file uploads)
FastAPI  →  Kafka             (event producer)
```

### Why Next.js reads MongoDB directly?
```
Product pages hit millions of times daily
Extra FastAPI hop = unnecessary latency
Server Component → MongoDB = faster SSR ✅
READ ONLY — never writes directly
All mutations always go through FastAPI
```

---

## 🐳 Docker

### Image vs Container
```
Image     = blueprint (like a class)
Container = running instance (like an object)
Build image once → run 100 containers from it
```

### Dockerfile Layer Caching
```
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .                ← code AFTER packages

Why: code changes → only rebuilds from COPY . .
     packages not reinstalled (cached) ✅
     saves minutes on every rebuild
```

### Docker Compose Key Concepts
```
Service names = hostnames inside network
  postgres → postgres:5432   NOT localhost
  redis    → redis:6379      NOT localhost

volumes:
  Named volume  → postgres_data:/var/lib/... (DB data persists)
  Bind mount    → ./backend:/app (code changes reflect instantly)

depends_on condition: service_healthy
  → waits for healthcheck to PASS
  → not just "container started"

docker compose down    → stops, keeps volumes
docker compose down -v → stops, DELETES volumes (data gone!)
```

---

## 🐘 PostgreSQL

### Why PostgreSQL over MySQL
```
✅ JSONB support (queryable JSON)
✅ UUID generation built in (gen_random_uuid())
✅ Custom ENUM types
✅ Partial indexes
✅ Better for complex queries
✅ Industry standard for serious projects
```

### UUID vs Integer Primary Key
```
Integer: exposes data (user id=3 → 3rd user ever)
         easy to enumerate (/users/1, /users/2...)
UUID:    random, impossible to guess
         can generate client side
         safe for public APIs ✅
```

### Soft Delete Pattern
```
Never DELETE rows in production
Instead: is_deleted=True, deleted_at=now()

Why:
  ✅ Audit trail
  ✅ Account recovery
  ✅ Order history intact
  ✅ Legal compliance (GDPR)
All queries filter WHERE is_deleted=FALSE
```

### server_default vs default
```
default=datetime.now()     → Python sets time (can drift)
server_default=func.now()  → PostgreSQL sets time (consistent) ✅
Always use server_default for timestamps
```

### Transactions (ACID)
```
Atomic     → all or nothing
Consistent → data always valid
Isolated   → transactions don't interfere
Durable    → committed data survives crashes

Critical for payments:
  BEGIN → deduct money → create order → reduce stock → COMMIT
  Any failure → ROLLBACK → nothing happens ✅
```

---

## 🔴 Redis Data Structures

| Structure | SnappCart Use Case | Key Example |
|-----------|-------------------|-------------|
| STRING | OTP, cache, feature flags | `otp:+91983... → "482910" EX 600` |
| HASH | Cart items | `cart:user123 → {product-id: qty}` |
| LIST | Recently viewed | `recent:user123 → [p3, p2, p1]` |
| SET | Unique product views | `views:product-id → {user1, user2}` |
| SORTED SET | Trending products | `trending → {product: score}` |

### TTL (Time To Live)
```
OTP codes        → EX 600    (10 mins)
Password reset   → EX 3600   (1 hour)
Cached pages     → EX 300    (5 mins)
Sessions         → EX 604800 (7 days)
Auto deleted after expiry — no cron job needed ✅
```

### decode_responses=True
```
Redis stores bytes internally
decode_responses=True → auto converts bytes → strings
Without: GET key returns b"hello"
With:    GET key returns "hello" ✅
```

### Distributed Lock (Flash Sales)
```
SET lock:product-uuid "locked" NX EX 5
  NX = only ONE request gets lock
  Others wait/retry
  Prevents overselling ✅
```

### Rate Limiting
```
INCR login:ab@gmail.com
After 5 → block
EXPIRE login:ab@gmail.com 3600 → resets after 1hr
```

---

## ⚡ FastAPI

### Why FastAPI over Node.js/Express
```
✅ Auto Swagger UI at /docs (free)
✅ Pydantic validation (no manual checks)
✅ Async first (handles Kafka, WebSockets)
✅ Python ecosystem (AI/ML libraries)
✅ Type hints everywhere
✅ Dependency injection built in
```

### Dependency Injection (get_db)
```python
def get_db():
    db = SessionLocal()
    try:
        yield db      # gives db to route → PAUSES
    except:
        db.rollback() # error → undo changes
    finally:
        db.close()    # ALWAYS closes ✅

@app.get("/products")
def get_products(db = Depends(get_db)):
    # db automatically provided + closed
```

### pool_pre_ping
```
Connections in pool can go STALE (idle too long)
PostgreSQL closes idle connections silently
Pool doesn't know → gives dead connection → ERROR ❌

pool_pre_ping=True:
  Before giving connection → sends "SELECT 1"
  Alive → give to route ✅
  Dead  → discard → get fresh one → give to route ✅
  Zero "connection closed" errors in production
```

### CORS
```
Browser blocks cross-origin requests by default
Frontend localhost:3000 → Backend localhost:8000
Different ports = different origins = BLOCKED ❌

CORSMiddleware allows it:
  allow_origins=["http://localhost:3000"]
  
  In production:
  allow_origins=["https://snappcart.com"]
  
  NEVER use ["*"] in production → any site can call API ❌
```

### Pydantic Settings
```python
class Settings(BaseSettings):
    database_url: str    # REQUIRED — app crashes if missing
    debug: bool = True   # OPTIONAL — has default

# @lru_cache() = reads .env ONCE on startup
# not on every request → performance ✅
```

### lifespan (startup/shutdown)
```python
@asynccontextmanager
async def lifespan(app):
    # BEFORE yield = startup
    await check_db_connection()
    yield
    # AFTER yield = shutdown
```

---

## 🗄️ SQLAlchemy + Alembic

### ORM Concept
```
Python class  =  Database table
class User(Base):
    __tablename__ = "users"

SQLAlchemy translates Python → SQL automatically
Safe from SQL injection ✅
Returns Python objects not raw tuples ✅
```

### __repr__ in Models
```python
def __repr__(self):
    return f"<User email={self.email} role={self.role}>"

Without: <User object at 0x7f8b...>  ← useless
With:    <User email=ab@gmail.com role=customer> ✅

Used in: terminal debugging, logs, pytest failure messages
```

### __all__ in __init__.py
```python
# models/__init__.py
__all__ = ["User", "UserRole", "OAuthProvider"]

Defines public interface of the package
Controls what exports on "from app.models import *"
Best practice: always define explicitly ✅
```

### pool_size + max_overflow
```
pool_size=10    → keep 10 connections always ready
max_overflow=5  → allow 5 more if all 10 busy
total max = 15 connections in dev
```

### Alembic = Git for Database
```
alembic revision --autogenerate -m "name"
  → detects difference between models and DB
  → generates migration file automatically

alembic upgrade head   → apply all pending migrations
alembic downgrade -1   → undo last migration
alembic current        → see current version
alembic history        → see all migrations
```

### NullPool in Alembic
```
Migrations run once then exit
No need for connection pool
NullPool = simple single connection
Different from app engine (uses pool_size=10)
```

### ⚠️ Alembic ENUM Bug Fix
```python
# ALWAYS add manually in downgrade():
op.execute('DROP TYPE IF EXISTS userrole CASCADE')
op.execute('DROP TYPE IF EXISTS usergender CASCADE')
op.execute('DROP TYPE IF EXISTS oauthprovider CASCADE')

# Alembic creates ENUMs implicitly in upgrade()
# but FORGETS to drop them in downgrade() ← known bug
# downgrade without this → ENUMs stay → next upgrade CRASHES
```

---

## 🍃 MongoDB vs PostgreSQL JSONB

### 1. Partial Updates → MongoDB wins
```
MongoDB  → $set updates ONE field only
JSONB    → rewrites ENTIRE row even for one change
```

### 2. Deep Indexing → MongoDB wins
```
MongoDB  → multikey indexes, memory efficient
JSONB    → GIN indexes, heavy RAM usage at scale
```

### 3. Code Cleanliness → MongoDB wins
```
MongoDB  → product.specs.color     (clean ✅)
JSONB    → specs->>'color'         (cryptic ❌)
```

### 4. Built for the Job → MongoDB wins
```
MongoDB  → document store from day 1
JSONB    → added to PostgreSQL in 2014 as a feature
```

---

## 🔍 Meilisearch

```
Why not PostgreSQL/MongoDB for search?
  LIKE '%iphone%' → misses "iphon" (typo)
  Slow on millions of products
  No relevance ranking

Meilisearch:
  ✅ Typo tolerance ("iphon" → iPhone)
  ✅ Instant results (<50ms)
  ✅ Relevance ranking built in
  ✅ Filters + sort + pagination
  ✅ Self hosted = free forever

NOT a primary DB:
  Source of truth = MongoDB
  Meilisearch = search index only
  Synced from MongoDB after every write
  
Flow:
  Seller creates product → FastAPI saves to MongoDB
  → FastAPI also indexes in Meilisearch
  → User searches → Meilisearch returns ranked results ✅
```

---

## ⚛️ Next.js 14

### Why TypeScript
```
Type safety → catch errors before runtime
All Redux slices typed → no silent bugs
All API responses typed → know exact shape
All component props typed → no wrong props
.ts and .tsx everywhere in frontend ✅
```

### Server vs Client Components
```
Server Component (default):
  → runs on server, zero JS to browser
  → async/await directly
  → fetch data, secrets stay safe
  → better SEO, faster load

Client Component ("use client"):
  → runs in browser
  → useState, useEffect, onClick
  → Redux hooks (useSelector, useDispatch)
  → Socket.io, browser APIs

Rule: default = Server
      add "use client" ONLY when needed
```

### Why Next.js for SnappCart
```
SEO critical:
  Plain React → empty HTML → Google sees nothing ❌
  Next.js SSR → full HTML → products indexed ✅

Performance:
  HTML ready on server → instant display
  No blank screen while JS loads
```

### Redux Provider Pattern
```
Problem: layout.tsx = Server Component
         Redux Provider needs "use client"

Solution:
  providers.tsx → "use client" + Provider
  layout.tsx    → imports Providers (stays Server) ✅
  
Server Components CAN be children of Client Components ✅
```

### Route Groups
```
(auth)/login/page.tsx → URL = /login (NOT /auth/login)
Parentheses = organize files, no URL segment added
```

---

## 🔐 Auth

### JWT Tokens
```
Access Token  → 30 mins  → Redux memory (cleared on tab close)
Refresh Token → 7 days   → Redis + httpOnly cookie
Algorithm     → HS256 (HMAC + SHA256)
SECRET_KEY    → signs tokens
             → python -c "import secrets; print(secrets.token_hex(32))"
```

### httpOnly Cookie for Refresh Token
```
httpOnly = JavaScript CANNOT access this cookie
Prevents XSS attacks stealing refresh token ✅
Only sent automatically by browser on requests
Access token in Redux memory → clears on tab close (safer)
```

### Email Token vs OTP vs Password Reset
```
                Email Verify    Password Reset    Phone OTP
Stored where?   PostgreSQL      PostgreSQL        Redis
Expires in?     24 hours        1 hour            10 mins
Sent via?       Email link      Email link        SMS
After use?      Delete token    Delete token      Auto deleted
```

### Two Avatar Columns
```
oauth_avatar_url → from Google/GitHub (their servers, can expire)
avatar_url       → uploaded to OUR S3 (we control, permanent)

Display: avatar_url → oauth_avatar_url → default placeholder
```

---

## 🎯 Interview Questions (SDE Level)

**Q: Why Redis for cart instead of PostgreSQL?**
```
A: Redis stores in RAM = microsecond reads.
   Cart read on every page load → must be fast.
   PostgreSQL disk reads = slower.
   Redis HASH = perfect structure for cart items.
   Temporary data → Redis TTL handles cleanup.
```

**Q: What is connection pooling and why important?**
```
A: Keep pool of ready DB connections instead of
   opening new one per request (expensive).
   pool_size=10 → 10 connections always ready.
   pool_pre_ping=True → checks alive before use.
   Prevents "connection closed" in production.
```

**Q: Explain soft delete. Why not hard delete?**
```
A: Set is_deleted=True instead of DELETE FROM.
   Preserves: audit trail, account recovery,
   referential integrity (orders reference user),
   legal compliance (GDPR data retention).
```

**Q: JSONB vs JSON in PostgreSQL?**
```
A: JSON = plain text, parsed on every read.
   JSONB = binary, parsed once on write, faster queries.
   JSONB supports indexing (GIN), operators (->>, @>).
   Always use JSONB, never JSON.
```

**Q: Why UUID over auto-increment integer?**
```
A: Integer exposes business data + easy to enumerate.
   UUID = random, impossible to guess.
   Can generate client-side (no DB roundtrip).
   Safe for merging databases (no ID conflicts).
```

**Q: Docker layer caching — why does order matter?**
```
A: Each line = one layer, cached separately.
   Layer changes → all below rebuild.
   COPY requirements.txt first → packages cached.
   COPY . . last → code changes don't reinstall packages.
   Wrong order = reinstall all packages every build.
```

**Q: depends_on vs service_healthy?**
```
A: depends_on alone = waits for container START only.
   Container started ≠ postgres ready (takes 2-3s).
   service_healthy = waits for healthcheck to PASS.
   pg_isready confirms actually accepting connections.
```

**Q: What is ACID? Why critical for payments?**
```
A: Atomic=all or nothing, Consistent=always valid,
   Isolated=no interference, Durable=survives crashes.
   Payment: deduct + create order + reduce stock
   must ALL succeed or ALL rollback. No partial states.
```

**Q: Why separate FastAPI over Next.js API routes?**
```
A: One API for all clients (web, mobile, admin).
   Python ecosystem for AI/ML.
   Kafka, Redis, complex async operations.
   Scale backend independently.
   Business logic in one place.
```

**Q: Server vs Client Components in Next.js 14?**
```
A: Server = runs on server, zero JS to browser,
   async/await, access secrets/DB, better SEO.
   Client = "use client", useState/useEffect/Redux.
   Default is Server. Add "use client" only when needed.
   Server Components CAN be children of Client Components.
```

**Q: createAsyncThunk vs RTK Query?**
```
A: RTK Query → simple GET requests, auto caching,
   auto loading/error states, generated hooks.
   createAsyncThunk → complex operations (login, order),
   multiple steps, complex side effects.
```

**Q: What is a distributed lock?**
```
A: Prevents race conditions in distributed systems.
   100 users buy last item → all see stock=1 → oversell.
   Redis: SET lock:product NX EX 5
   NX = only ONE gets lock. Others wait.
   Critical for flash sales. ✅
```

**Q: What is CORS and why needed?**
```
A: Browser blocks requests to different origins by default.
   Frontend :3000 → Backend :8000 = different origins = blocked.
   CORSMiddleware adds headers allowing specific origins.
   Never use ["*"] in production → any site can call API.
```

**Q: Why Meilisearch over PostgreSQL for search?**
```
A: PostgreSQL LIKE '%iphone%' misses typos ("iphon").
   Slow on millions of products, no relevance ranking.
   Meilisearch: typo tolerance, <50ms results,
   relevance ranking, filters+sort combined.
   Self hosted = free. Not primary DB — index only.
```

---

*Phase 1 Complete → Will update after each phase*