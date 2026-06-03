# ── database.py — QuantEdge SQLite layer ─────────────────────────────────────
import sqlite3
import hashlib
import json
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "quantedge.db")


# ── Connection ────────────────────────────────────────────────────────────────
def get_conn():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


# ── Schema init ───────────────────────────────────────────────────────────────
def init_db():
    conn = get_conn()
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            username   TEXT    UNIQUE NOT NULL,
            email      TEXT    UNIQUE NOT NULL,
            password   TEXT    NOT NULL,
            created_at TEXT    NOT NULL
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS analyses (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id      INTEGER NOT NULL,
            ticker       TEXT    NOT NULL,
            start_date   TEXT    NOT NULL,
            end_date     TEXT    NOT NULL,
            bb_window    INTEGER NOT NULL,
            bb_mult      REAL    NOT NULL,
            rsi_span     INTEGER NOT NULL,
            rsi_ob       INTEGER NOT NULL,
            rsi_os       INTEGER NOT NULL,
            initial_cap  REAL    NOT NULL,
            signal       TEXT    NOT NULL,
            metrics_json TEXT    NOT NULL,
            trades_json  TEXT    NOT NULL,
            ai_summary   TEXT    NOT NULL,
            created_at   TEXT    NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    conn.commit()
    conn.close()


# ── Password hashing ──────────────────────────────────────────────────────────
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


# ── User operations ───────────────────────────────────────────────────────────
def create_user(username: str, email: str, password: str) -> dict:
    """Returns {"ok": True} or {"error": "..."}"""
    conn = get_conn()
    try:
        conn.execute(
            "INSERT INTO users (username, email, password, created_at) VALUES (?,?,?,?)",
            (username.strip(), email.strip().lower(),
             hash_password(password), datetime.utcnow().isoformat())
        )
        conn.commit()
        return {"ok": True}
    except sqlite3.IntegrityError as e:
        msg = str(e)
        if "username" in msg:
            return {"error": "Username already taken."}
        if "email" in msg:
            return {"error": "Email already registered."}
        return {"error": "Registration failed."}
    finally:
        conn.close()


def login_user(username: str, password: str) -> dict:
    """Returns {"ok": True, "user": row} or {"error": "..."}"""
    conn = get_conn()
    row = conn.execute(
        "SELECT * FROM users WHERE username=? AND password=?",
        (username.strip(), hash_password(password))
    ).fetchone()
    conn.close()
    if row:
        return {"ok": True, "user": dict(row)}
    return {"error": "Invalid username or password."}


# ── Analysis operations ───────────────────────────────────────────────────────
def params_fingerprint(ticker, start_date, end_date, bb_window, bb_mult,
                        rsi_span, rsi_ob, rsi_os, initial_cap) -> str:
    """Unique string for a set of analysis parameters — used for duplicate check."""
    return "|".join(str(x) for x in [
        ticker.upper(), start_date, end_date,
        bb_window, bb_mult, rsi_span, rsi_ob, rsi_os, initial_cap
    ])


def duplicate_analysis(user_id: int, ticker, start_date, end_date,
                        bb_window, bb_mult, rsi_span, rsi_ob, rsi_os,
                        initial_cap):
    """Returns existing analysis row dict if identical params already run, else None."""
    conn = get_conn()
    row = conn.execute("""
        SELECT * FROM analyses
        WHERE user_id=? AND ticker=? AND start_date=? AND end_date=?
          AND bb_window=? AND bb_mult=? AND rsi_span=?
          AND rsi_ob=? AND rsi_os=? AND initial_cap=?
        ORDER BY created_at DESC LIMIT 1
    """, (user_id, ticker.upper(), str(start_date), str(end_date),
          bb_window, bb_mult, rsi_span, rsi_ob, rsi_os, initial_cap)
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def save_analysis(user_id, ticker, start_date, end_date,
                  bb_window, bb_mult, rsi_span, rsi_ob, rsi_os,
                  initial_cap, signal, metrics, trade_log, ai_summary) -> int:
    """Saves analysis and returns new row id."""
    conn = get_conn()
    cur = conn.execute("""
        INSERT INTO analyses
          (user_id, ticker, start_date, end_date, bb_window, bb_mult,
           rsi_span, rsi_ob, rsi_os, initial_cap, signal,
           metrics_json, trades_json, ai_summary, created_at)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    """, (
        user_id, ticker.upper(), str(start_date), str(end_date),
        bb_window, bb_mult, rsi_span, rsi_ob, rsi_os, initial_cap,
        signal,
        json.dumps(metrics),
        json.dumps(trade_log),
        ai_summary,
        datetime.utcnow().isoformat()
    ))
    conn.commit()
    new_id = cur.lastrowid
    conn.close()
    return new_id


def get_user_analyses(user_id: int):
    """All analyses for a user, newest first."""
    conn = get_conn()
    rows = conn.execute(
        "SELECT * FROM analyses WHERE user_id=? ORDER BY created_at DESC",
        (user_id,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_analysis_by_id(analysis_id: int, user_id: int):
    """Fetch one analysis (must belong to the user)."""
    conn = get_conn()
    row = conn.execute(
        "SELECT * FROM analyses WHERE id=? AND user_id=?",
        (analysis_id, user_id)
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def delete_analysis(analysis_id: int, user_id: int) -> bool:
    conn = get_conn()
    conn.execute(
        "DELETE FROM analyses WHERE id=? AND user_id=?",
        (analysis_id, user_id)
    )
    conn.commit()
    conn.close()
    return True