## Exploration: Phase 2 — Telegram Bot Integration

### Current State

The project has a working **Phase 1** — inventory I/O module (`camarilla/inventario.py`) with:
- `leer_inventario()` / `escribir_inventario()`: read/write `inventario.md` with flock-based file locking, atomic writes, and automatic backup rotation.
- `config.py`: centralized constants (`INVENTARIO_PATH`, `BACKUPS_DIR`, `MAX_BACKUPS`, `BACKUP_PREFIX`).
- `__main__.py`: no-op entry point (`main()` does nothing).
- Comprehensive tests in `tests/test_inventario.py` (254 lines) with `conftest.py` fixtures.
- `pyproject.toml` already declares `aiogram>=3.0` as a runtime dependency and `pytest-asyncio>=0.21` as a dev dependency.
- Installed aiogram v3.28.2 in the venv. pytest-asyncio 1.3.0 is also installed.
- `PRD.md` and `PLAN.md` define Phase 2 goals: Telegram bot with hardcoded `user_id` access control.
- `human.md` documents the deployment plan with env vars `TELEGRAM_BOT_TOKEN` and `TELEGRAM_USER_ID`.
- The data model is nested dicts: `{room: {furniture: {section: [items]}}}`.

### Affected Areas

- `camarilla/__main__.py` — Must change from no-op to starting the bot (async entry point).
- `camarilla/config.py` — Must add `BOT_TOKEN` and `AUTHORIZED_USER_ID` config values from env vars.
- `camarilla/` package — New module(s) needed for bot handlers, routers, and middleware.
- `tests/` — New test files needed for bot handlers and middleware.
- `pyproject.toml` — May need `pytest-aiohttp` or `aiogram-tests` for bot testing if we go beyond unit tests.
- `human.md` / `README.md` — Update instructions for Phase 2 (how to run the bot).

### Approaches

#### 1. Single `bot.py` module — Flat structure

Create `camarilla/bot.py` containing the Dispatcher, all handlers, and the access-control filter. Start it from `__main__.py`.

- **Pros**: Simplest, fewest files, easy to understand for a small bot.
- **Cons**: Gets unwieldy as handlers grow; doesn't separate concerns. Fine for Phase 2 but will need refactoring for Phase 3+.
- **Effort**: Low

#### 2. `bot/` package with routers — Modular structure

Create `camarilla/bot/` package with:
```
camarilla/bot/
  __init__.py    # exports create_bot_and_dispatcher()
  main.py       # Bot + Dispatcher setup, start_polling()
  filters.py    # AuthorizedUser filter
  handlers.py   # /start, /help, echo, /inventario
  middleware.py  # (optional) logging middleware
```

- **Pros**: Clean separation; easy to add handlers in Phase 3/4; follows aiogram best practices with Router pattern.
- **Cons**: More files to create upfront; slight overhead for what is currently a simple bot.
- **Effort**: Medium

#### 3. Single `bot.py` with Router extraction later

Start with `camarilla/bot.py` containing everything. Add a comment marking where routers will be extracted. Refactor into `bot/` package when Phase 3 adds handlers.

- **Pros**: Minimal effort now; no premature abstraction; clear migration path.
- **Cons**: Brief refactor needed later; slightly less idiomatic aiogram v3.
- **Effort**: Low

### Recommendation

**Approach 2: `bot/` package with routers.**

Reasons:
1. aiogram v3's idiomatic pattern is Router-based. A `bot/` package aligns with the framework's design.
2. Phase 3 and 4 will add Ollama integration and inventory-modification handlers. Having `handlers.py` (and eventually more router modules) makes the transition clean.
3. The overhead of 4-5 small files is negligible compared to the clarity and extensibility gained.
4. The `filters.py` file cleanly isolates the `AuthorizedUser` custom filter — a critical security component that deserves its own test file.

### Architecture Details (for Approach 2)

```
camarilla/
  __init__.py          # version (unchanged)
  __main__.py          # async entry point: asyncio.run(main())
  config.py            # adds BOT_TOKEN, AUTHORIZED_USER_ID from env
  inventario.py        # unchanged
  bot/
    __init__.py        # exports create_bot_and_dispatcher()
    main.py            # Bot + Dispatcher setup, register routers, start_polling()
    filters.py         # AuthorizedUser filter class
    handlers.py        # command handlers: /start, /help, /inventario, echo
    middleware.py       # logging middleware (optional, lightweight)
```

#### Key Design Decisions

1. **Bot token + user ID**: Read from environment variables via `config.py`. No hardcoding in source.
   - `BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]`
   - `AUTHORIZED_USER_ID = int(os.environ["TELEGRAM_USER_ID"])`
   - Fail fast with `KeyError` if env vars are missing.

2. **Access control**: Custom `AuthorizedUser` filter subclassing `aiogram.filters.base.Filter`.
   - Applied per-handler with `@router.message(AuthorizedUser(), CommandStart())`.
   - Unauthorized messages: silently ignored (no response, consistent with PLAN.md: "rechazar silenciosamente").
   - Filter checks `message.from_user.id == config.AUTHORIZED_USER_ID`.

3. **Handlers for Phase 2**:
   - `/start` → Welcome message explaining the bot's purpose.
   - `/help` → List available commands.
   - `/inventario` → Read and pretty-print the inventory (calls `leer_inventario()`).
   - Echo fallback → Reply back with the user's text (confirms the bot is alive and listening).

4. **`__main__.py` changes**: Replace no-op with:
   ```python
   import asyncio
   from camarilla.bot import main
   asyncio.run(main())
   ```

5. **Testing strategy**:
   - Unit test the `AuthorizedUser` filter by instantiating it with a mock `Message` object.
   - Test handlers using `aiogram`'s testing utilities or by calling handler functions directly with mock `Message` objects.
   - Use `pytest-asyncio` (already in dev deps) for async handler tests.
   - For `leer_inventario` integration in `/inventario` handler, mock the function.
   - No real Telegram connection in tests — all unit/integration level.

6. **No Ollama**: Phase 2 is strictly the bot layer. No LLM integration yet.

### Risks

- **Environment variable dependency**: Bot won't start without `TELEGRAM_BOT_TOKEN` and `TELEGRAM_USER_ID`. Clear error message needed on missing vars.
- **File locking in async context**: `leer_inventario()` and `escribir_inventario()` use `fcntl.flock` (blocking). Called from async handlers, this could block the event loop. Mitigation: run I/O-bound calls in `asyncio.to_thread()` to avoid blocking the event loop.
- **pytest-asyncio compatibility**: v1.3.0 is installed; aiogram 3.x requires `asyncio_mode = "auto"` in pytest config (already set). Verify no version conflicts.
- **Silent ignore of unauthorized messages**: Could make debugging harder during development. Consider logging unauthorized attempts at WARNING level without responding.

### Ready for Proposal

**Yes.** The exploration is complete. The next step is to create the SDD proposal for `fase2-telegram-bot` with the recommended approach (Approach 2: `bot/` package), covering config changes, new modules, handler definitions, access control filter, and testing strategy.