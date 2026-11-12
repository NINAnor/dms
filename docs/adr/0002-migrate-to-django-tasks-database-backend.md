# Migrate background task execution from procrastinate to Django's native Tasks framework

Replace procrastinate with Django's native Tasks framework (available in Django 6.1+), backed by `django-tasks-db` as the database-backed broker and `django-crontask` for periodic/cron scheduling. This is a big-bang cutover with no dual-run compatibility shim.

## Rationale

Procrastinate has served reliably for on-demand and cron-scheduled task execution, but we are now operating under Django 6.1 with native Tasks support. Moving to the native framework reduces external dependencies, aligns with Django's bundled capabilities, and simplifies the maintenance surface. Django's native Tasks API is stable and production-ready in 6.1+.

## Considered Options

- Keep procrastinate — rejected: adds external dependency when Django now provides native in-process alternatives; increases maintenance burden.
- Use Celery — rejected: too heavy for our current task volume (one on-demand, two periodic tasks); django-tasks-db is lighter and fully sufficient.
- Build custom task executor — rejected: django-tasks-db + django-crontask already solves this and integrates seamlessly with Django's native Task APIs.

## Solution

1. **On-demand tasks**: Use `@task` decorator from `django.tasks`, called via `.enqueue()`.
2. **Periodic/cron tasks**: Combine `@task` with `@cron("<crontab-expr>")` from `django-crontask`, preserving existing schedules (hourly LDAP sync at `* 0 * * *`, hourly metadata re-inference at `0 * * * *`).
3. **Task broker**: Configure `django-tasks-db.DatabaseBackend` in TASKS setting, which persists enqueued tasks in the same Postgres instance.
4. **Worker processes**: Replace single `procrastinate worker` with two long-running processes:
   - `manage.py db_worker`: executes enqueued on-demand tasks (replaces `procrastinate worker`).
   - `manage.py crontask`: scheduler that dispatches registered @cron-decorated tasks on their schedules (new service).
5. **Docker services**: Create `db-worker`, `crontask`, `db-worker-dev`, `crontask-dev` services; remove `queue` and `queue-dev`.

## Migration Steps

- Remove procrastinate from dependencies and INSTALLED_APPS.
- Add django-tasks-db and django-crontask to dependencies.
- Rewrite task functions: swap `@app.task` → `@task`, `@app.periodic(cron="...")` → `@cron("...")` decorator stacking.
- Replace `app.configure_task(...).defer(...)` call sites with direct `.enqueue()` on the migrated task function.
- Add `TASKS` setting with `django-tasks-db.DatabaseBackend`.
- Update docker-compose service definitions for both prod and dev profiles.

## Trade-offs and Constraints

**Django 6.1 Compatibility Caveat**: Neither `django-tasks-db` (dependency floor `django>=6.0`) nor `django-crontask` (dependency floor `django>=6.0`) carry explicit Django 6.1 classifiers in their package metadata. However, both use open-ended dependency declarations and have been tested on Django 6.1+ in upstream projects. **Compatibility must be confirmed via the test suite rather than assumed from package classifiers.** If issues arise, fallback to Celery or procrastinate remains available.

**Dropped In-Flight Tasks**: Any procrastinate job in the queue at cutover time will be dropped. This is acceptable because:
- The on-demand metadata inference task is idempotent; re-triggering it yields the same result.
- Periodic tasks self-heal on their next scheduled tick (e.g., if LDAP sync didn't run at hour N, it will run at hour N+1).
- No drain step is required.

## Consequences

- Reduced external task-queue dependency surface.
- Tasks are persisted in the same database, avoiding separate infrastructure.
- Simpler deployment: two standard Django management commands instead of a bespoke procrastinate CLI.
- Test suite must validate that both frameworks work smoothly under Django 6.1.1.
