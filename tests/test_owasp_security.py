"""Offline OWASP security regression tests for TSP_2AFISA_8466."""

from __future__ import annotations

import importlib.util
import io
import pathlib
import sys
import types
from unittest.mock import MagicMock

import pytest

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent


def _load_settings_with_env(monkeypatch: pytest.MonkeyPatch, env: dict[str, str]):
    for key in (
        "DJANGO_ENV",
        "DJANGO_SECRET_KEY",
        "DJANGO_DEBUG",
        "DJANGO_ALLOWED_HOSTS",
        "POSTGRES_PASSWORD",
    ):
        monkeypatch.delenv(key, raising=False)
    for key, val in env.items():
        monkeypatch.setenv(key, val)

    # Lightweight stub for django.utils.translation if Django is not installed
    if "django.utils.translation" not in sys.modules:
        django_mod = types.ModuleType("django")
        utils_mod = types.ModuleType("django.utils")
        trans_mod = types.ModuleType("django.utils.translation")
        trans_mod.gettext_lazy = lambda s: s  # type: ignore[attr-defined]
        monkeypatch.setitem(sys.modules, "django", django_mod)
        monkeypatch.setitem(sys.modules, "django.utils", utils_mod)
        monkeypatch.setitem(sys.modules, "django.utils.translation", trans_mod)

    spec = importlib.util.spec_from_file_location(
        "tsp_settings_probe", str(REPO_ROOT / "config" / "settings.py")
    )
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_production_refuses_default_insecure_secret_key(monkeypatch: pytest.MonkeyPatch):
    with pytest.raises(RuntimeError, match="DJANGO_SECRET_KEY"):
        _load_settings_with_env(
            monkeypatch,
            {"DJANGO_ENV": "production", "POSTGRES_PASSWORD": "strong-prod-password-123"},
        )


def test_production_refuses_default_postgres_password(monkeypatch: pytest.MonkeyPatch):
    with pytest.raises(RuntimeError, match="POSTGRES_PASSWORD"):
        _load_settings_with_env(
            monkeypatch,
            {"DJANGO_ENV": "production", "DJANGO_SECRET_KEY": "prod-random-secret-key-999"},
        )


def test_production_defaults_debug_false_and_sets_security_headers(monkeypatch: pytest.MonkeyPatch):
    settings = _load_settings_with_env(
        monkeypatch,
        {
            "DJANGO_ENV": "production",
            "DJANGO_SECRET_KEY": "prod-random-secret-key-999",
            "POSTGRES_PASSWORD": "strong-prod-password-123",
            "DJANGO_ALLOWED_HOSTS": " example.org , www.example.org , ",
        },
    )
    assert settings.DEBUG is False
    assert settings.ALLOWED_HOSTS == ["example.org", "www.example.org"]
    assert settings.SECURE_CONTENT_TYPE_NOSNIFF is True
    assert settings.X_FRAME_OPTIONS == "DENY"
    assert settings.SECURE_REFERRER_POLICY == "strict-origin-when-cross-origin"
    assert settings.SESSION_COOKIE_SECURE is True
    assert settings.CSRF_COOKIE_SECURE is True


def _load_indexing_views_stubbed(monkeypatch: pytest.MonkeyPatch):
    # Provide lightweight stubs so view logic is testable without heavy ML/DB deps
    django_mod = types.ModuleType("django")
    contrib_mod = types.ModuleType("django.contrib")
    auth_mod = types.ModuleType("django.contrib.auth")
    dec_mod = types.ModuleType("django.contrib.auth.decorators")
    dec_mod.login_required = lambda fn: fn  # type: ignore[attr-defined]
    shortcuts_mod = types.ModuleType("django.shortcuts")
    shortcuts_mod.render = lambda req, tpl, ctx=None, status=200: {  # type: ignore[attr-defined]
        "template": tpl,
        "context": ctx or {},
        "status": status,
    }
    indexing_pkg = types.ModuleType("indexing")
    indexing_models = types.ModuleType("indexing.models")
    indexing_models.Photo = MagicMock()  # type: ignore[attr-defined]
    indexing_tasks = types.ModuleType("indexing.tasks")
    indexing_tasks.index_photo = MagicMock()  # type: ignore[attr-defined]

    for name, mod in (
        ("django", django_mod),
        ("django.contrib", contrib_mod),
        ("django.contrib.auth", auth_mod),
        ("django.contrib.auth.decorators", dec_mod),
        ("django.shortcuts", shortcuts_mod),
        ("indexing", indexing_pkg),
        ("indexing.models", indexing_models),
        ("indexing.tasks", indexing_tasks),
    ):
        monkeypatch.setitem(sys.modules, name, mod)

    spec = importlib.util.spec_from_file_location(
        "tsp_indexing_views_probe", str(REPO_ROOT / "indexing" / "views.py")
    )
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_indexing_view_rejects_missing_or_invalid_upload_without_500(monkeypatch: pytest.MonkeyPatch):
    views = _load_indexing_views_stubbed(monkeypatch)

    # Missing file must return 400 cleanly (no AttributeError on None.seek)
    req_missing = MagicMock(method="POST", FILES={}, user=MagicMock(id=1))
    res_missing = views.index(req_missing)
    assert res_missing["status"] == 400

    # Disallowed extension (.html) must be rejected with 400
    bad_file = io.BytesIO(b"<script>alert(1)</script>")
    bad_file.name = "evil.html"
    bad_file.size = 25
    bad_file.content_type = "text/html"
    req_bad = MagicMock(method="POST", FILES={"photo": bad_file}, user=MagicMock(id=1))
    res_bad = views.index(req_bad)
    assert res_bad["status"] == 400

    # Oversized image (> 10 MiB) must be rejected with 400
    big_file = io.BytesIO(b"\xff\xd8\xff\xe0")
    big_file.name = "huge.jpg"
    big_file.size = 15 * 1024 * 1024
    big_file.content_type = "image/jpeg"
    req_big = MagicMock(method="POST", FILES={"photo": big_file}, user=MagicMock(id=1))
    res_big = views.index(req_big)
    assert res_big["status"] == 400


def test_search_views_enforces_upload_limits():
    src = (REPO_ROOT / "search" / "views.py").read_text(encoding="utf-8")
    assert "MAX_UPLOAD_BYTES" in src
    assert "ALLOWED_IMAGE_EXTENSIONS" in src
