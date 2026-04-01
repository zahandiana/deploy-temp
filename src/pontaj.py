import os
import json
import hashlib
import secrets
import sqlite3
import calendar
import re
from datetime import datetime, date, time, timedelta

import pandas as pd
import streamlit as st
from io import BytesIO
APP_BUILD_TAG = "pontaj-v3"

def bootstrap_standalone_ui():
    st.set_page_config(
        page_title="Socrates@Pontaj",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    st.markdown(
        """
        <style>
    /* =========================
       FORCE GLOBAL BACKGROUND
    ========================= */

    html, body {
        /* fundal baby-blue cald, prietenos */
        background: #dbeafe !important;  /* baby blue */
        color: #020617 !important;
    }

    /* container principal streamlit – foaie ușor mai deschisă peste baby blue */
    [data-testid="stAppViewContainer"] {
        background: #eff6ff !important;  /* blue-50 */
    }

    /* zona de conținut */
    [data-testid="stAppViewBlockContainer"] {
        background: #eff6ff !important;
    }

    /* bloc intern */
    .block-container {
        background: #eff6ff !important;
    }

    /* main wrapper */
    section.main {
        background: #eff6ff !important;
    }

    /* div-urile interne nu forțează altă culoare */
    div {
        background-color: transparent;
    }

    /* =========================
       SIDEBAR – BUTOANE NAVIGARE
    ========================= */

    section[data-testid="stSidebar"] {
        background: #1E4E63 !important;
        border-right: 1px solid rgba(255,255,255,0.08);
        padding-top: 24px;
    }

    /* ascunde bulinele radio */
    section[data-testid="stSidebar"] input[type="radio"] {
        display: none;
    }

    /* container radio */
    section[data-testid="stSidebar"] div[role="radiogroup"] {
        gap: 6px;
    }

    /* fiecare item devine “buton” de meniu */
    section[data-testid="stSidebar"] div[role="radiogroup"] label {
        background: transparent;
        padding: 8px 12px;
        border-radius: 999px;
        cursor: pointer;
        transition: all 0.2s ease;
        display: block;
    }

    /* ascunde eventuale icoane/buline interne */
    section[data-testid="stSidebar"] div[role="radiogroup"] label svg,
    section[data-testid="stSidebar"] div[role="radiogroup"] label [data-testid*="stRadio"] {
        display: none !important;
    }

    /* text item (etichetele de meniu) */
    section[data-testid="stSidebar"] label p {
        color: #f9fafb !important;
        font-size: 14px;
        font-weight: 500;
    }

    /* tot textul din sidebar (titlu “Navigare”, descrieri, etc.) cu alb aproape pur */
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3,
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] span,
    section[data-testid="stSidebar"] label {
        color: #f9fafb !important;
    }

    /* hover – fără albastru închis, doar highlight discret */
    section[data-testid="stSidebar"] div[role="radiogroup"] label:hover {
        background: rgba(255,255,255,0.08);
    }

    /* activ – fără albastru închis, doar border stânga + highlight discret */
    section[data-testid="stSidebar"] input:checked + div {
        background: rgba(255,255,255,0.06);
        border-left: 3px solid rgba(248,250,252,0.85);
        padding-left: 9px;
        border-radius: 999px;
    }

    /* === Stil butoane sidebar – identic cu aplicația HR === */
    section[data-testid="stSidebar"] label[data-baseweb="radio"]{
      background: rgba(255,255,255,0.04) !important;
      border: 1px solid rgba(255,255,255,0.07) !important;
      border-radius: 12px !important;
      padding: 10px 14px !important;
      margin: 6px 0 !important;
      width: 100% !important;
      min-height: 44px !important;
      box-sizing: border-box !important;
      display: flex !important;
      align-items: center !important;
      transition: transform 160ms ease, background 160ms ease, border-color 160ms ease, box-shadow 160ms ease;
      color: rgba(255,255,255,0.92) !important;
      position: relative;
    }
    section[data-testid="stSidebar"] label[data-baseweb="radio"] > div:last-child{
      color: rgba(255,255,255,0.92) !important;
    }
    section[data-testid="stSidebar"] [data-baseweb="radio-group"]{
      width: 100% !important;
    }
    section[data-testid="stSidebar"] [data-baseweb="radio-group"] label{
      width: 100% !important;
    }
    section[data-testid="stSidebar"] label[data-baseweb="radio"]:hover{
      transform: translateY(-1px);
      background: rgba(255,255,255,0.07) !important;
      border-color: rgba(255,255,255,0.12) !important;
      color: rgba(255,255,255,0.98) !important;
    }
    section[data-testid="stSidebar"] label[data-baseweb="radio"][data-checked="true"],
    section[data-testid="stSidebar"] label[data-baseweb="radio"]:has([aria-checked="true"]),
    section[data-testid="stSidebar"] label[data-baseweb="radio"]:has(input:checked){
      background: rgba(255,255,255,0.08) !important;
      border-color: rgba(255,255,255,0.18) !important;
      box-shadow: none;
      color: rgba(255,255,255,0.98) !important;
    }
    section[data-testid="stSidebar"] label[data-baseweb="radio"] > div:first-child{
      display:none !important;
    }
    section[data-testid="stSidebar"] label[data-baseweb="radio"]:has(input:checked)::before{
      content:"";
      position:absolute;
      left:-1px;
      top:10px;
      bottom:10px;
      width:3px;
      border-radius: 999px;
      background: rgba(255,255,255,0.55);
    }

    /* buton Delogare (și orice alt buton din sidebar): transparent, text alb */
    section[data-testid="stSidebar"] .stButton > button,
    section[data-testid="stSidebar"] div[data-testid="stButton"] > button {
      background: transparent !important;
      background-color: transparent !important;
      color: #f9fafb !important;
      border: 1px solid rgba(255,255,255,0.2) !important;
      border-radius: 10px !important;
      box-shadow: none !important;
    }
    section[data-testid="stSidebar"] .stButton > button:hover,
    section[data-testid="stSidebar"] div[data-testid="stButton"] > button:hover {
      background: rgba(255,255,255,0.08) !important;
      border-color: rgba(255,255,255,0.35) !important;
    }

    /* text general in continut: negru-inchis; sidebar il suprascrie mai jos unde e nevoie */
    h1, h2, h3, p, span, label {
        color: #020617 !important;
    }

    /* =========================
       CONTROLS & TABLES – LIGHT (foarte deschis, text inchis)
    ========================= */

    /* inputuri, selecturi, textarea – foarte deschis, cu border discret */
    div[data-baseweb="input"] > div,
    div[data-baseweb="base-input"] > div,
    div[data-baseweb="textarea"] > div,
    div[data-baseweb="select"] > div {
        background: #ffffff !important;
        border: 1px solid rgba(148,163,184,0.45) !important;
        border-radius: 8px !important;
        box-shadow: none !important;
    }

    input, textarea, select {
        background: transparent !important;
        color: #020617 !important;
    }

    /* tabele/dataframe – aproape alb cu text inchis */
    div[data-testid="stDataFrame"] {
        background: #f9fafb !important;
        border-radius: 10px !important;
        overflow: hidden !important;
    }

    div[data-testid="stDataFrame"] table {
        background: #f9fafb !important;
        color: #020617 !important;
    }

    div[data-testid="stDataFrame"] thead tr th {
        background: #ffffff !important;
        border-bottom: 1px solid rgba(148,163,184,0.45) !important;
    }

    div[data-testid="stDataFrame"] tbody tr td {
        background: #ffffff !important;
        border-color: rgba(203,213,225,0.9) !important;
    }

    /* =========================
       TOP BAR – ACEEAȘI NUANȚĂ
    ========================= */

    header[data-testid="stHeader"] {
        background: transparent !important;
    }

    .topbar {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        height: 60px;
        background: #1E4E63;
        display: flex;
        align-items: center;
        padding: 0 30px;
        border-bottom: 1px solid rgba(255,255,255,0.08);
        z-index: 1000;
    }

    .block-container {
        margin-top: 70px;
    }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="topbar">
            <div class="topbar-left"><strong>Socrates@Pontaj</strong></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

def _parse_iso_date(x):
    """Acceptă str YYYY-MM-DD / date / datetime. Returnează date sau None."""
    from datetime import date, datetime
    if x is None:
        return None
    if isinstance(x, date) and not isinstance(x, datetime):
        return x
    if isinstance(x, datetime):
        return x.date()
    s = str(x).strip()
    if not s:
        return None
    try:
        return date.fromisoformat(s)
    except Exception:
        return None


def _count_weekdays(d1, d2):
    from datetime import timedelta
    if d1 is None or d2 is None:
        return 0
    if d2 < d1:
        d1, d2 = d2, d1
    n = 0
    d = d1
    while d <= d2:
        if d.weekday() < 5:
            n += 1
        d += timedelta(days=1)
    return n


def compute_requested_days(start_dt, end_dt, weekdays_only=True) -> int:
    """Calculează zilele cererii (L-V dacă weekdays_only=True)."""
    from datetime import date
    if start_dt is None or end_dt is None:
        return 0
    if hasattr(start_dt, "date") and not isinstance(start_dt, date):
        start_dt = start_dt.date()
    if hasattr(end_dt, "date") and not isinstance(end_dt, date):
        end_dt = end_dt.date()
    if end_dt < start_dt:
        return 0
    if weekdays_only:
        return int(_count_weekdays(start_dt, end_dt))
    return int((end_dt - start_dt).days + 1)


# ============================================================
# Calendar helpers: weekend + sărbători legale (RO)
# ============================================================

MONTH_NAMES_RO = {
    1: "Ianuarie", 2: "Februarie", 3: "Martie", 4: "Aprilie",
    5: "Mai", 6: "Iunie", 7: "Iulie", 8: "August",
    9: "Septembrie", 10: "Octombrie", 11: "Noiembrie", 12: "Decembrie",
}

def orthodox_easter_gregorian(year: int) -> date:
    """Paștele ortodox (calendar gregorian) pentru anii 1900-2099 (diferență 13 zile).
    Folosește algoritmul Meeus pentru data iuliană + conversie.
    """
    y = int(year)
    a = y % 4
    b = y % 7
    c = y % 19
    d = (19 * c + 15) % 30
    e = (2 * a + 4 * b - d + 34) % 7
    month = (d + e + 114) // 31
    day = ((d + e + 114) % 31) + 1
    julian = date(y, month, day)
    return julian + timedelta(days=13)

def ro_default_legal_holidays(year: int) -> set[date]:
    """Listă implicită (aprox.) de sărbători legale în România.
    IMPORTANT: admin poate ajusta din Configurări (cfg['legal_holidays']).
    """
    y = int(year)
    hol = set()
    # Fixe (cele mai comune)
    fixed = [
        (1, 1), (1, 2),
        (1, 6), (1, 7),
        (1, 24),
        (5, 1),
        (6, 1),
        (8, 15),
        (11, 30),
        (12, 1),
        (12, 25), (12, 26),
    ]
    for m, d in fixed:
        hol.add(date(y, m, d))

    # Mobile: Paște + Rusalii (+ Vinerea Mare)
    easter = orthodox_easter_gregorian(y)
    hol.add(easter)                 # duminică
    hol.add(easter + timedelta(days=1))   # luni
    hol.add(easter - timedelta(days=2))   # vinerea mare (dacă e aplicabil în unitate)

    pentecost = easter + timedelta(days=49)  # duminică
    hol.add(pentecost)
    hol.add(pentecost + timedelta(days=1))   # luni

    return hol


# ============================================================
# Concedii medicale (CM) - coduri indemnizație (RO)
# ============================================================

CM_CODES = {
    "01": {"label": "Boală obișnuită", "procent": 75},
    "02": {"label": "Accident în afara muncii", "procent": 75},
    "03": {"label": "Accident de muncă", "procent": 100},
    "04": {"label": "Boală profesională", "procent": 100},
    "05": {"label": "Boală infectocontagioasă (grupa A)", "procent": 100},
    "06": {"label": "Urgență medico-chirurgicală", "procent": 100},
    "07": {"label": "Carantină", "procent": 100},
    "08": {"label": "Sarcină și lăuzie", "procent": 85},
    "09": {"label": "Îngrijire copil bolnav", "procent": 85},
    "10": {"label": "Reducerea cu 1/4 a duratei normale de lucru", "procent": 75},
    "12": {"label": "Tuberculoză", "procent": 100},
    "13": {"label": "Boală cardiovasculară", "procent": 75},
    "14": {"label": "Neoplazii / SIDA", "procent": 100},
    "15": {"label": "Risc maternal", "procent": 75},
}

# Coduri care, în practică, sunt suportate integral din FNUASS (fără "primele 5 zile" angajator).
# Lista poate fi ajustată după practica unității / legislație.
CM_FULL_FNUASS_CODES = {"03","04","05","06","07","08","09","10","12","14","15"}

# Locul de prescriere (conform certificatului medical)
CM_PRESCRIPTION_PLACES = {
    "1": "1 - Medic familie",
    "2": "2 - Spital",
    "3": "3 - Ambulatoriu",
    "4": "4 - CAS",
}

def cm_code_label(code: str) -> str:
    c = safe_str(code)
    info = CM_CODES.get(c)
    if not info:
        return c
    return f"{c} - {info['label']} ({info['procent']}%)"

def get_legal_holidays(cfg: dict, year: int) -> set[date]:
    """Sărbători legale: union(default + cfg['legal_holidays'])."""
    hol = set(ro_default_legal_holidays(int(year)))
    extra = (cfg or {}).get("legal_holidays", []) or []
    # acceptăm listă de stringuri YYYY-MM-DD
    for x in extra:
        try:
            hol.add(date.fromisoformat(str(x).strip()))
        except Exception:
            pass
    return hol

def is_weekend(d: date) -> bool:
    return d.weekday() >= 5

def is_legal_holiday(d: date, cfg: dict) -> bool:
    try:
        return d in get_legal_holidays(cfg, d.year)
    except Exception:
        return False




def upsert_co_entitlement(conn: sqlite3.Connection, employee_key: str, year: int, days_entitled: float):
    now = datetime.now().isoformat(timespec="seconds")
    conn.execute(
        """INSERT INTO co_entitlements(employee_key, year, days_entitled, created_at, updated_at)
             VALUES(?,?,?,?,?)
             ON CONFLICT(employee_key, year) DO UPDATE SET
                days_entitled=excluded.days_entitled,
                updated_at=excluded.updated_at
        """,
        (str(employee_key), int(year), float(days_entitled or 0), now, now)
    )
    conn.commit()

def get_co_entitlements(conn: sqlite3.Connection, employee_key: str):
    cur = conn.cursor()
    cur.execute("""SELECT year, days_entitled FROM co_entitlements
                     WHERE employee_key=? ORDER BY year""", (str(employee_key),))
    return {int(r[0]): float(r[1] or 0) for r in cur.fetchall()}

def get_co_used_days(conn: sqlite3.Connection, employee_key: str, year: int) -> int:
    """Număr zile CO aprobate în anul `year` (contează doar zilele L-V din interval)."""
    # suport DB compat: start_date/end_date vs date_start/date_end
    cols = _table_columns(conn, "leave_requests")
    start_col = "start_date" if _has_col(cols, "start_date") else ("date_start" if _has_col(cols, "date_start") else "start_date")
    end_col = "end_date" if _has_col(cols, "end_date") else ("date_end" if _has_col(cols, "date_end") else "end_date")

    y_start = f"{int(year)}-01-01"
    y_end = f"{int(year)}-12-31"

    q = f"""SELECT {start_col} AS s, {end_col} AS e, weekdays_only
              FROM leave_requests
              WHERE employee_key=?
                AND request_type='CO'
                AND UPPER(COALESCE(status, status_code, 'PENDING'))='APPROVED'
        """
    df = pd.read_sql_query(q, conn, params=(str(employee_key),))
    if df.empty:
        return 0

    from datetime import date
    total = 0
    for _, r in df.iterrows():
        ds = _parse_iso_date(r["s"])
        de = _parse_iso_date(r["e"])
        if not ds or not de:
            continue
        # intersect cu anul
        a1 = date.fromisoformat(y_start)
        a2 = date.fromisoformat(y_end)
        if de < a1 or ds > a2:
            continue
        ds2 = max(ds, a1)
        de2 = min(de, a2)
        wk_only = bool(int(r.get("weekdays_only", 1) or 0))
        if wk_only:
            total += _count_weekdays(ds2, de2)
        else:
            total += (de2 - ds2).days + 1
    return int(total)

def compute_co_balance_3y(conn: sqlite3.Connection, employee_key: str, year: int):
    """Sold CO pe 3 ani: anul curent, anul-1, anul-2.
    Consumă zilele în ordinea: (an-2) -> (an-1) -> (an).
    Returnează dict cu entitled/used/remaining pe fiecare an + total.
    """
    y = int(year)
    buckets = [y-2, y-1, y]
    ent = get_co_entitlements(conn, employee_key)
    entitled = {yy: float(ent.get(yy, 0)) for yy in buckets}
    used_raw = {yy: float(get_co_used_days(conn, employee_key, yy)) for yy in buckets}

    # consum FIFO (din cel mai vechi)
    remaining = {yy: entitled[yy] for yy in buckets}
    to_consume_total = sum(used_raw.values())

    for yy in buckets:
        take = min(remaining[yy], to_consume_total)
        remaining[yy] -= take
        to_consume_total -= take

    # dacă utilizarea depășește alocările, total poate deveni negativ (semnalăm)
    over = to_consume_total

    return {
        "years": buckets,
        "entitled": entitled,
        "used_by_year": used_raw,
        "remaining": remaining,
        "total_remaining": sum(remaining.values()) - float(over),
        "overuse": float(over),
    }


def get_co_periods_for_year(conn: sqlite3.Connection, employee_key: str, year: int) -> pd.DataFrame:
    """Lista perioadelor de CO aprobate în anul `year` cu nr. zile (intersectate cu anul)."""
    cols = _table_columns(conn, "leave_requests")
    start_col = "start_date" if _has_col(cols, "start_date") else ("date_start" if _has_col(cols, "date_start") else "start_date")
    end_col = "end_date" if _has_col(cols, "end_date") else ("date_end" if _has_col(cols, "date_end") else "end_date")

    y_start = date(int(year), 1, 1)
    y_end = date(int(year), 12, 31)

    q = f"""SELECT id, {start_col} AS s, {end_col} AS e, weekdays_only, notes
              FROM leave_requests
              WHERE employee_key=?
                AND request_type='CO'
                AND UPPER(COALESCE(status, status_code, 'PENDING'))='APPROVED'
              ORDER BY {start_col}
    """
    df = pd.read_sql_query(q, conn, params=(str(employee_key),))
    if df.empty:
        return df

    rows = []
    for _, r in df.iterrows():
        ds = _parse_iso_date(r.get("s"))
        de = _parse_iso_date(r.get("e"))
        if not ds or not de:
            continue
        if de < y_start or ds > y_end:
            continue
        ds2 = max(ds, y_start)
        de2 = min(de, y_end)
        wk = bool(int(r.get("weekdays_only", 1) or 0))
        zile = compute_requested_days(ds2, de2, wk)
        rows.append({
                    "Marca": emp_key,
                    "Nume": str(r.get("nume","") or ""),
                    "Prenume": str(r.get("prenume","") or ""),
                    f"TOTAL CO {y2} (zile)": float(ent.get(y2, 0)),
                    f"TOTAL CO {y1} (zile)": float(ent.get(y1, 0)),
                    f"TOTAL CO {y0} (zile)": float(ent.get(y0, 0)),
                    f"Zile efectuate în {y0} (zile)": used_y0,
                    "Zile rămase (3 ani)": float(bal.get("total_remaining", 0) or 0),
                })
    return pd.DataFrame(rows)

# ============================================================
# CERERI - STARE (UI) 3 opțiuni
# ============================================================
STATUS_RO_MAP = {
    "APPROVED": "Aprobat",
    "REJECTED": "Respins",
    "PENDING": "În așteptare",
    "CANCELLED": "Anulat",
}

STATUS_LABEL_TO_CODE = {
    "în așteptare": "PENDING",
    "aprobat": "APPROVED",
    "respins": "REJECTED",
}
STATUS_CODE_TO_LABEL = {v: k for k, v in STATUS_LABEL_TO_CODE.items()}


def _row_get(row, key, default=None):
    """Robust getter for pandas Series/dict/tuple."""
    try:
        # pandas Series / dict-like
        if hasattr(row, "get"):
            return row.get(key, default)
        # namedtuple from itertuples
        if hasattr(row, "_asdict"):
            return row._asdict().get(key, default)
        # tuple (fallback by known position is not safe)
        return default
    except Exception:
        return default



# Opțiuni tip pontaj lunar (folosite la completare pe interval)
# NOTE: păstrează aici lista de coduri/etichete folosite în aplicație
LUNAR_STATUS_OPTIUNI = [
    "CO",       # concediu de odihnă
    "CM",       # concediu medical
    "CFS",      # concediu fără salariu
    "CIC",      # concediu creștere copil
    "NEPL",     # absență nemotivată / neplătit
    "Deleg.",   # delegație
    "Sarb.",    # sărbătoare legală
    "Sam./D",   # weekend (sâmbătă/duminică)
    "Liber",    # liber (compatibilitate)
]



# ============================================================
# CERERI CONCEDII / ABSENTE
# ============================================================

LEAVE_REQUEST_TYPES = [
    "CO",        # concediu odihnă
    "CM",        # concediu medical
    "CFS",       # concediu fără salariu
    "CIC",       # concediu creștere copil
    "NEPL",      # absență nemotivată / neplătită
    "Liber",     # zile libere (ex: liber legal / recuperare)
    "Telemunca", # telemuncă
    "Deleg.",    # delegație
    "Sarb.",     # sărbătoare legală
    "Sam./D",    # sâmbătă/duminică (marcare)
]

# cum se scrie în timesheets.status (păstrăm aceleași valori)
LEAVE_TYPE_TO_TS_STATUS = {t: t for t in LEAVE_REQUEST_TYPES}


# ============================================================
# DB helpers for schema drift (existing DB compatibility)
# ============================================================

def _table_columns(conn: sqlite3.Connection, table: str) -> set[str]:
    """Return set of column names for a table (lowercase)."""
    cur = conn.cursor()
    try:
        cur.execute(f"PRAGMA table_info({table})")
        return {str(r[1]).lower() for r in cur.fetchall()}
    finally:
        try:
            cur.close()
        except Exception:
            pass

def _has_col(cols: set[str], name: str) -> bool:
    return name.lower() in cols


# ============================================================
# APP PATHS
# ============================================================

APP_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(APP_DIR, "assets")
SIGN_DIR = os.path.join(ASSETS_DIR, "signatures")
CONFIG_FILE = os.path.join(APP_DIR, "pontaj_config.json")
DATA_DIR = os.path.join(APP_DIR, "data")

def ensure_dirs():
    os.makedirs(ASSETS_DIR, exist_ok=True)
    os.makedirs(SIGN_DIR, exist_ok=True)
    os.makedirs(DATA_DIR, exist_ok=True)

def save_uploaded_file(uploaded_file, target_path: str) -> str:
    if not target_path:
        raise ValueError("Calea tinta este goala.")
    parent = os.path.dirname(os.path.abspath(target_path))
    os.makedirs(parent, exist_ok=True)
    with open(target_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return target_path

def safe_str(x) -> str:
    return "" if x is None else str(x).strip()


def get_effective_db_path(cfg: dict) -> str:
    """
    DB path folosit efectiv:
    - daca user a selectat/încărcat un DB in UI -> st.session_state["db_path_override"]
    - altfel -> cfg["db_path"]
    """
    return safe_str(st.session_state.get("db_path_override") or cfg.get("db_path") or DEFAULT_CONFIG["db_path"])

def save_uploaded_db(uploaded_file) -> str:
    """
    Salveaza fisierul DB incarcat in folderul local ./data si intoarce calea absoluta.
    """
    if uploaded_file is None:
        raise ValueError("Nu a fost incarcat niciun fisier.")
    ensure_dirs()
    fname = os.path.basename(uploaded_file.name)
    if not fname.lower().endswith((".db", ".sqlite", ".sqlite3")):
        raise ValueError("Fisier invalid. Accept: .db / .sqlite / .sqlite3")
    target_path = os.path.join(DATA_DIR, fname)
    save_uploaded_file(uploaded_file, target_path)
    return target_path

def db_browser_ui(conn: sqlite3.Connection):
    """
    Explorer simplu: listeaza tabele + coloane + preview.
    """
    st.markdown("### 🔎 Explorer baza de date")
    try:
        tables = pd.read_sql_query(
            "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;",
            conn
        )["name"].tolist()
    except Exception as e:
        st.error(f"Nu pot lista tabelele: {e}")
        return

    if not tables:
        st.info("Baza nu are tabele.")
        return

    table = st.selectbox("Alege tabel", tables, index=0, key="dbb_table")
    c1, c2 = st.columns([1, 2])
    with c1:
        try:
            cols = pd.read_sql_query(f"PRAGMA table_info({table});", conn)
            st.caption("Coloane")
            st.dataframe(cols, use_container_width=True, height=260)
        except Exception as e:
            st.error(f"Eroare PRAGMA: {e}")

    with c2:
        limit = st.number_input("Preview rows", min_value=5, max_value=500, value=50, step=5, key="dbb_limit")
        try:
            dfp = pd.read_sql_query(f"SELECT * FROM {table} LIMIT {int(limit)};", conn)
            st.caption("Preview")
            st.dataframe(dfp, use_container_width=True, height=260)
        except Exception as e:
            st.error(f"Eroare preview: {e}")

# ============================================================
# VERSION
# ============================================================
APP_VERSION = "Pontaj HR v3"
# ============================================================
# CONFIG
# ============================================================

DEFAULT_CONFIG = {
    # DB
    "use_db": True,
    "db_path": "./data/pontaj.db",

    # Date unitate / institutie
    "company_name": "",
    "company_cui": "",
    "company_regcom": "",
    "company_address": "",
    "company_phone": "",
    "company_email": "",

    # Sigla (ABS)
    "logo_path": "/home/vzahan/socrates/pontaj/assets/logo.png",

    # Semnatura (activare + semnare electronica)
    "sign_enabled": False,
    "sign_mode": "vizual",          # vizual / calificat
    "e_sign_provider": "",
    "e_sign_endpoint": "",
    "e_sign_api_key": "",

    # Ore implicite
    "default_start": "08:00",
    "default_end": "16:00",
    "standard_daily_hours": 8.0,

    # Optiuni
    "allow_cross_day_shift": True,
}

def load_config() -> dict:
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                cfg = json.load(f) or {}
        except Exception:
            cfg = {}
    else:
        cfg = {}
    merged = dict(DEFAULT_CONFIG)
    merged.update(cfg)
    return merged

def save_config(cfg: dict) -> None:
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(cfg, f, ensure_ascii=False, indent=2)

def _parse_hhmm_to_time(s: str, fallback: time) -> time:
    try:
        s = (s or "").strip()
        if not s:
            return fallback
        return datetime.strptime(s, "%H:%M").time()
    except Exception:
        return fallback

def _time_to_hhmm(t: time) -> str:
    return t.strftime("%H:%M")


# ============================================================
# DB CORE
# ============================================================

def get_db_conn(db_path: str):
    conn = sqlite3.connect(db_path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA foreign_keys=ON;")
    return conn

def table_exists(conn: sqlite3.Connection, name: str) -> bool:
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name=? LIMIT 1", (name,))
    return cur.fetchone() is not None


def migrate_timesheets_employee_key(conn: sqlite3.Connection):
    """
    Migrare pentru DB-uri vechi unde tabela `timesheets` exista, dar nu are coloana `employee_key`.
    - adauga coloana employee_key daca lipseste
    - o populeaza dintr-o coloana existenta (cnp/marca), iar daca nu exista, foloseste id
    - creeaza index unic pe (employee_key, work_date) daca lipseste
    """
    if not table_exists(conn, "timesheets"):
        return

    cur = conn.cursor()
    cols = [r[1] for r in cur.execute("PRAGMA table_info(timesheets)").fetchall()]
    if "employee_key" not in cols:
        cur.execute("ALTER TABLE timesheets ADD COLUMN employee_key TEXT")
        conn.commit()
        cols.append("employee_key")

    # backfill (alegem cea mai buna coloana disponibila)
    source_col = None
    for cand in ("cnp", "CNP", "marca", "Marca", "employee", "employee_id"):
        if cand in cols:
            source_col = cand
            break

    if source_col:
        cur.execute(f"""
            UPDATE timesheets
            SET employee_key = COALESCE(NULLIF(employee_key,''), CAST({source_col} AS TEXT))
            WHERE employee_key IS NULL OR employee_key = '';
        """)
    else:
        # fallback: folosim id ca sa avem mereu o cheie
        cur.execute("""
            UPDATE timesheets
            SET employee_key = COALESCE(NULLIF(employee_key,''), CAST(id AS TEXT))
            WHERE employee_key IS NULL OR employee_key = '';
        """)

    # Cereri (workflow)
    conn.execute("""
    CREATE TABLE IF NOT EXISTS leave_requests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        employee_key TEXT NOT NULL,
        request_type TEXT NOT NULL,         -- CO/CM/Liber/Telemunca/etc
        start_date TEXT NOT NULL,           -- YYYY-MM-DD
        end_date TEXT NOT NULL,             -- YYYY-MM-DD
        weekdays_only INTEGER NOT NULL DEFAULT 1,
        hours_per_day REAL DEFAULT 0,

        status TEXT NOT NULL DEFAULT 'PENDING',  -- PENDING/APPROVED/REJECTED/CANCELLED
        notes TEXT DEFAULT NULL,

        created_by TEXT NOT NULL,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL,

        decision_by TEXT DEFAULT NULL,
        decision_at TEXT DEFAULT NULL,
        decision_reason TEXT DEFAULT NULL,

        -- câmpuri specifice CM (pregătite pentru etapa următoare)
        cm_series TEXT DEFAULT NULL,
        cm_number TEXT DEFAULT NULL,
        cm_type TEXT DEFAULT NULL,
        cm_diag TEXT DEFAULT NULL,
        cm_issuer TEXT DEFAULT NULL,

        UNIQUE(employee_key, request_type, start_date, end_date, created_at)
    );
    """)

    # Certificate medicale (CM) - registru (pentru datele certificatului)
    conn.execute("""
    CREATE TABLE IF NOT EXISTS medical_certificates (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        employee_key TEXT NOT NULL,

        serie TEXT NOT NULL,
        numar TEXT NOT NULL,
        issued_date TEXT DEFAULT NULL,          -- YYYY-MM-DD (data eliberării)
        prescription_place TEXT DEFAULT NULL,  -- 1/2/3/4 (Medic familie/Spital/Ambulatoriu/CAS)

        cod_indemnizatie TEXT NOT NULL,         -- 01/02/03...
        procent INTEGER DEFAULT NULL,           -- 75/85/100 (informativ)
        diagnostic_code TEXT DEFAULT NULL,      -- ex: 503/653

        start_date TEXT NOT NULL,               -- YYYY-MM-DD
        days_calendar INTEGER NOT NULL,         -- nr zile calendaristice
        end_date TEXT NOT NULL,                 -- YYYY-MM-DD (calculat)

        is_continuation INTEGER NOT NULL DEFAULT 0,
        initial_serie TEXT DEFAULT NULL,
        initial_numar TEXT DEFAULT NULL,
        initial_date TEXT DEFAULT NULL,

        fara_stagiu INTEGER NOT NULL DEFAULT 0,
        pay_employer_days INTEGER DEFAULT NULL,
        pay_fnuass_days INTEGER DEFAULT NULL,
        notes TEXT DEFAULT NULL,

        created_by TEXT NOT NULL,
        created_at TEXT NOT NULL,

        leave_request_id INTEGER DEFAULT NULL,  -- legătură opțională către leave_requests.id

        UNIQUE(serie, numar)
    );
    """)

    # Tipuri de cereri configurabile (persistente)
    cur.execute("""CREATE TABLE IF NOT EXISTS request_types (
            code TEXT PRIMARY KEY,
            label TEXT NOT NULL,
            is_active INTEGER NOT NULL DEFAULT 1,
        
            -- configurare comportament la aplicare in pontaj
            apply_mode TEXT NOT NULL DEFAULT 'ABSENCE',   -- ABSENCE / WORK / MARK_ONLY
            ts_status TEXT NOT NULL DEFAULT '',          -- ce scriem in timesheets.status (ex: CO, CM, ZI_LIBERA, Lucrat)
            hours_per_day REAL NOT NULL DEFAULT 0,        -- pentru WORK, daca 0 -> norma standard
            weekdays_only_default INTEGER NOT NULL DEFAULT 1,
        
            -- contoare/flag-uri in timesheets
            co_day INTEGER NOT NULL DEFAULT 0,
            cm_day INTEGER NOT NULL DEFAULT 0,
            cfp_day INTEGER NOT NULL DEFAULT 0,
            nemotivat_day INTEGER NOT NULL DEFAULT 0,
            liber_day INTEGER NOT NULL DEFAULT 0,
            telemunca_day INTEGER NOT NULL DEFAULT 0,
            samd_day INTEGER NOT NULL DEFAULT 0,
        
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )""")


    conn.commit()

    # --- CO entitlements (manual per an, la inițializare DB) ---
    cur.execute("""CREATE TABLE IF NOT EXISTS co_entitlements (
        employee_key TEXT NOT NULL,
        year INTEGER NOT NULL,
        days_entitled REAL NOT NULL DEFAULT 0,  -- se introduce manual (ex: 20/21/25)
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL,
        PRIMARY KEY(employee_key, year)
    )""")

    # index unic pentru upsert-uri si rapoarte
    cur.execute("""
        CREATE UNIQUE INDEX IF NOT EXISTS idx_timesheets_employee_day
        ON timesheets(employee_key, work_date);
    """)
    conn.commit()



def migrate_timesheets_extra_cols(conn: sqlite3.Connection):
    """Adaugă coloane noi în `timesheets` pentru compatibilitate (fără a strica DB-ul existent)."""
    if not table_exists(conn, "timesheets"):
        return
    cur = conn.cursor()
    cols = [r[1] for r in cur.execute("PRAGMA table_info(timesheets)").fetchall()]
    # coloane noi pe care le folosim în pontaj/cereri
    wanted = {
        "telemunca_day": "INTEGER DEFAULT 0",
        "samd_day": "INTEGER DEFAULT 0",
    }
    changed = False
    for col, ddl in wanted.items():
        if col not in cols:
            cur.execute(f"ALTER TABLE timesheets ADD COLUMN {col} {ddl}")
            changed = True
    if changed:
        conn.commit()



def migrate_request_types_extra_cols(conn: sqlite3.Connection):
    """Asigură coloanele de configurare pentru request_types (compatibilitate DB)."""
    if not table_exists(conn, "request_types"):
        return
    cur = conn.cursor()
    cols = [r[1] for r in cur.execute("PRAGMA table_info(request_types)").fetchall()]
    wanted = {
        "apply_mode": "TEXT NOT NULL DEFAULT 'ABSENCE'",
        "ts_status": "TEXT NOT NULL DEFAULT ''",
        "weekdays_only_default": "INTEGER NOT NULL DEFAULT 1",
        "co_day": "INTEGER NOT NULL DEFAULT 0",
        "cm_day": "INTEGER NOT NULL DEFAULT 0",
        "cfp_day": "INTEGER NOT NULL DEFAULT 0",
        "nemotivat_day": "INTEGER NOT NULL DEFAULT 0",
        "liber_day": "INTEGER NOT NULL DEFAULT 0",
        "telemunca_day": "INTEGER NOT NULL DEFAULT 0",
        "samd_day": "INTEGER NOT NULL DEFAULT 0",
    }
    changed = False
    for c, ddl in wanted.items():
        if c not in cols:
            cur.execute(f"ALTER TABLE request_types ADD COLUMN {c} {ddl}")
            changed = True
    if changed:
        conn.commit()


def get_table_columns(conn: sqlite3.Connection, table: str) -> list[str]:
    try:
        df = pd.read_sql_query(f"PRAGMA table_info({table});", conn)
        return [str(x) for x in df["name"].tolist()]
    except Exception:
        return []

def migrate_leave_requests_extra_cols(conn: sqlite3.Connection):
    """Asigură compatibilitatea tabelei `leave_requests` cu schema așteptată (fără a strica DB-ul existent)."""
    if not table_exists(conn, "leave_requests"):
        return
    cols = set(get_table_columns(conn, "leave_requests"))
    wanted: dict[str, str] = {
        "employee_key": "TEXT",
        "request_type": "TEXT",
        "start_date": "TEXT",
        "end_date": "TEXT",
        "weekdays_only": "INTEGER NOT NULL DEFAULT 1",
        "status": "TEXT NOT NULL DEFAULT 'PENDING'",
        "status_code": "TEXT NOT NULL DEFAULT 'PENDING'",
        "notes": "TEXT DEFAULT NULL",
        "created_by": "TEXT",
        "created_at": "TEXT",
        "updated_at": "TEXT",
        "decision_by": "TEXT DEFAULT NULL",
        "decision_at": "TEXT DEFAULT NULL",
        "decision_reason": "TEXT DEFAULT NULL",
        "cm_series": "TEXT DEFAULT NULL",
        "cm_number": "TEXT DEFAULT NULL",
        "cm_type": "TEXT DEFAULT NULL",
        "cm_diag": "TEXT DEFAULT NULL",
        "cm_issuer": "TEXT DEFAULT NULL",
    }
    changed = False
    cur = conn.cursor()
    for col, ddl in wanted.items():
        if col not in cols:
            cur.execute(f"ALTER TABLE leave_requests ADD COLUMN {col} {ddl}")
            changed = True
    if changed:
        conn.commit()



def init_db(conn: sqlite3.Connection):
    migrate_timesheets_employee_key(conn)
    migrate_timesheets_extra_cols(conn)
    # Timesheets
    conn.execute("""
    CREATE TABLE IF NOT EXISTS timesheets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        employee_key TEXT NOT NULL,
        work_date TEXT NOT NULL,        -- YYYY-MM-DD
        start_time TEXT,                -- HH:MM
        end_time TEXT,                  -- HH:MM
        status TEXT NOT NULL,           -- Lucrat / CO / CM / CFP / Nemotivat / Liber
        total_hours REAL DEFAULT 0,
        normal_hours REAL DEFAULT 0,
        night_hours REAL DEFAULT 0,
        weekend_hours REAL DEFAULT 0,
        holiday_hours REAL DEFAULT 0,
        overtime_hours REAL DEFAULT 0,
        co_day INTEGER DEFAULT 0,
        cm_day INTEGER DEFAULT 0,
        cfp_day INTEGER DEFAULT 0,
        nemotivat_day INTEGER DEFAULT 0,
        liber_day INTEGER DEFAULT 0,
        telemunca_day INTEGER DEFAULT 0,
        samd_day INTEGER DEFAULT 0,

        -- snapshot (nume/structura)
        nume TEXT,
        prenume TEXT,
        cnp TEXT,
        locatie TEXT,
        directie TEXT,
        departament TEXT,
        birou TEXT,

        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL,
        UNIQUE(employee_key, work_date)
    );
    """)

    # Fallback employees cache
    conn.execute("""
    CREATE TABLE IF NOT EXISTS employees_cache (
        employee_key TEXT PRIMARY KEY,
        nume TEXT,
        prenume TEXT,
        cnp TEXT,
        locatie TEXT,
        directie TEXT,
        departament TEXT,
        birou TEXT
    );
    """)

    # Users
    conn.execute("""
    CREATE TABLE IF NOT EXISTS pontaj_users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_salt TEXT NOT NULL,
        password_hash TEXT NOT NULL,
        role TEXT NOT NULL DEFAULT 'user',   -- admin / manager / user
        employee_key TEXT DEFAULT NULL,      -- daca e setat -> vede DOAR acel angajat
        is_active INTEGER NOT NULL DEFAULT 1,
        created_at TEXT NOT NULL
    );
    """)

    # Scopes
    conn.execute("""
    CREATE TABLE IF NOT EXISTS pontaj_user_scopes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        locatie TEXT DEFAULT NULL,
        directie TEXT DEFAULT NULL,
        departament TEXT DEFAULT NULL,
        birou TEXT DEFAULT NULL,
        FOREIGN KEY(username) REFERENCES pontaj_users(username) ON DELETE CASCADE
    );
    """)

    # Signatures (CRUD)
    conn.execute("""
    CREATE TABLE IF NOT EXISTS pontaj_signatures (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        label TEXT NOT NULL,           -- ex: "Director"
        signatory_name TEXT NOT NULL,
        signatory_role TEXT NOT NULL,
        image_path TEXT DEFAULT NULL,  -- PNG
        is_active INTEGER NOT NULL DEFAULT 0,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL
    );
    """)
    # ============================================================
    # OVERTIME (Ore suplimentare) - ledger + compensari + plati
    # Tot ce depaseste standard_daily_hours (implicit 8h/zi) este deja calculat in timesheets.overtime_hours.
    # Aici tinem evidenta compensarii in 90 zile / plata daca nu s-a compensat.
    # ============================================================

    conn.execute("""
    CREATE TABLE IF NOT EXISTS overtime_ledger (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        employee_key TEXT NOT NULL,
        work_date TEXT NOT NULL,              -- ziua in care s-au castigat orele suplimentare (YYYY-MM-DD)
        hours_earned REAL NOT NULL DEFAULT 0, -- ore suplimentare castigate (din timesheets.overtime_hours)
        hours_compensated REAL NOT NULL DEFAULT 0, -- ore compensate cu timp liber
        hours_paid REAL NOT NULL DEFAULT 0,         -- ore platite (spor)
        source TEXT NOT NULL DEFAULT 'pontaj_auto',
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL,
        UNIQUE(employee_key, work_date, source)
    );
    """)

    conn.execute("""
    CREATE TABLE IF NOT EXISTS overtime_actions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        employee_key TEXT NOT NULL,
        action_date TEXT NOT NULL,            -- data actiunii (YYYY-MM-DD)
        action_type TEXT NOT NULL CHECK(action_type IN ('COMPENSATE','PAY')),
        hours REAL NOT NULL,
        note TEXT DEFAULT NULL,
        created_by TEXT DEFAULT NULL,
        created_at TEXT NOT NULL
    );
    """)


    # migrare/compatibilitate pentru cereri concedii (DB existent)
    migrate_leave_requests_extra_cols(conn)

    # migrare/compatibilitate pentru registru CM (DB existent)
    _ensure_medical_certificates_cols(conn)

    conn.commit()


# ============================================================
# AUTH
# ============================================================

def _hash_password(password: str, salt: str) -> str:
    return hashlib.sha256((salt + password).encode("utf-8")).hexdigest()

def ensure_default_admin(conn: sqlite3.Connection):
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM pontaj_users WHERE username='admin' LIMIT 1")
    if cur.fetchone():
        return
    salt = secrets.token_hex(16)
    ph = _hash_password("admin123!", salt)
    cur.execute("""
        INSERT INTO pontaj_users(username, password_salt, password_hash, role, employee_key, is_active, created_at)
        VALUES(?,?,?,?,?,?,?)
    """, ("admin", salt, ph, "admin", None, 1, datetime.now().isoformat(timespec="seconds")))
    conn.commit()

def auth_user(conn: sqlite3.Connection, username: str, password: str) -> dict | None:
    cur = conn.cursor()
    cur.execute("""
        SELECT username, password_salt, password_hash, role, employee_key, is_active
        FROM pontaj_users WHERE username=? LIMIT 1
    """, (username,))
    row = cur.fetchone()
    if not row:
        return None
    u, salt, ph, role, employee_key, is_active = row
    if int(is_active) != 1:
        return None
    if _hash_password(password, salt) != ph:
        return None
    return {"username": u, "role": role, "employee_key": employee_key}

def get_user_scopes(conn: sqlite3.Connection, username: str) -> pd.DataFrame:
    return pd.read_sql_query("""
        SELECT id, locatie, directie, departament, birou
        FROM pontaj_user_scopes
        WHERE username=?
        ORDER BY id
    """, conn, params=(username,))


# ============================================================
# EMPLOYEES
# ============================================================

def pick_first_column(cols: list[str], candidates: list[str]) -> str | None:
    cols_lower = {c.lower(): c for c in cols}
    for cand in candidates:
        if cand.lower() in cols_lower:
            return cols_lower[cand.lower()]
    return None

def read_employees(conn: sqlite3.Connection) -> tuple[pd.DataFrame, str]:
    """
    Standard:
    employee_key, Nume, Prenume, CNP, Locatie, Directie, Departament, Birou, FullName
    """
    if table_exists(conn, "employees"):
        cols = get_table_columns(conn, "employees")

        col_marca = pick_first_column(cols, ["marca", "employee_marca", "marcă", "nr_marca"])
        col_id = pick_first_column(cols, ["id", "employee_id"])
        key_col = col_marca or col_id

        col_nume = pick_first_column(cols, ["nume", "last_name", "lastname", "nume_familie"])
        col_prenume = pick_first_column(cols, ["prenume", "first_name", "firstname"])
        col_cnp = pick_first_column(cols, ["cnp", "personal_number"])

        col_loc = pick_first_column(cols, ["locatie", "locație", "location", "punct_lucru", "loc_munca", "locul_muncii"])
        col_dir = pick_first_column(cols, ["directie", "direcție", "directorate"])
        col_dep = pick_first_column(cols, ["departament", "department", "serviciu"])
        col_bir = pick_first_column(cols, ["birou", "office"])

        if not key_col:
            df = pd.DataFrame(columns=["employee_key","Nume","Prenume","CNP","Locatie","Directie","Departament","Birou","FullName"])
            return df, "employees (fara cheie)"

        select_cols = []
        def add(alias, col):
            if col:
                select_cols.append(f"{col} AS {alias}")
            else:
                select_cols.append(f"'' AS {alias}")

        add("employee_key", key_col)
        add("Nume", col_nume)
        add("Prenume", col_prenume)
        add("CNP", col_cnp)
        add("Locatie", col_loc)
        add("Directie", col_dir)
        add("Departament", col_dep)
        add("Birou", col_bir)

        q = f"SELECT {', '.join(select_cols)} FROM employees"
        try:
            df = pd.read_sql_query(q, conn)
        except Exception:
            df = pd.DataFrame(columns=["employee_key","Nume","Prenume","CNP","Locatie","Directie","Departament","Birou","FullName"])
            return df, "employees (query fail)"

        for c in ["employee_key","Nume","Prenume","CNP","Locatie","Directie","Departament","Birou"]:
            df[c] = df[c].astype(str).fillna("").str.strip()

        df = df[df["employee_key"] != ""].copy()
        df["FullName"] = (df["Nume"] + " " + df["Prenume"]).str.strip()
        return df, "employees"

    if table_exists(conn, "employees_cache"):
        df = pd.read_sql_query("""
            SELECT
              employee_key,
              COALESCE(nume,'') AS Nume,
              COALESCE(prenume,'') AS Prenume,
              COALESCE(cnp,'') AS CNP,
              COALESCE(locatie,'') AS Locatie,
              COALESCE(directie,'') AS Directie,
              COALESCE(departament,'') AS Departament,
              COALESCE(birou,'') AS Birou
            FROM employees_cache
            ORDER BY locatie, directie, departament, birou, nume, prenume
        """, conn)
        for c in ["employee_key","Nume","Prenume","CNP","Locatie","Directie","Departament","Birou"]:
            df[c] = df[c].astype(str).fillna("").str.strip()
        df["FullName"] = (df["Nume"] + " " + df["Prenume"]).str.strip()
        return df, "employees_cache"

    return pd.DataFrame(columns=["employee_key","Nume","Prenume","CNP","Locatie","Directie","Departament","Birou","FullName"]), "none"


def load_employees_cached(conn: sqlite3.Connection) -> pd.DataFrame:
    """Compat helper: returns employees dataframe (from employees or employees_cache).
    Older parts of the app expect this function name.
    Also normalizes name columns so UI can display Nume/Prenume everywhere.
    """
    df, _src = read_employees(conn)
    # normalize columns
    if not df.empty:
        if "Nume" in df.columns and "nume" not in df.columns:
            df["nume"] = df["Nume"].astype(str)
        if "Prenume" in df.columns and "prenume" not in df.columns:
            df["prenume"] = df["Prenume"].astype(str)
        if "FullName" not in df.columns:
            if "nume" in df.columns and "prenume" in df.columns:
                df["FullName"] = (df["nume"].fillna("") + " " + df["prenume"].fillna("")).str.strip()
            else:
                df["FullName"] = ""
    return df

def apply_scope_filter(df: pd.DataFrame, role: str, scopes: list[dict], user_employee_key: str | None) -> pd.DataFrame:
    if df is None or df.empty:
        return df
    role = (role or "user").lower()

    if role in ("admin","manager"):
        return df

    if user_employee_key:
        return df[df["employee_key"] == str(user_employee_key)].copy()

    if scopes:
        mask_total = pd.Series(False, index=df.index)
        for s in scopes:
            mask = pd.Series(True, index=df.index)
            for field, col in [("locatie","Locatie"),("directie","Directie"),("departament","Departament"),("birou","Birou")]:
                val = safe_str(s.get(field))
                if val:
                    mask = mask & (df[col] == val)
            mask_total = mask_total | mask
        return df[mask_total].copy()

    return df.iloc[0:0].copy()


# ============================================================
# HOURS / TIMESHEET
# ============================================================

def calculate_hours_segments(work_date, start_time, end_time, standard_daily_hours=8.0, is_weekend=False, is_holiday=False, allow_cross_day=True):
    dt_start = datetime.combine(work_date, start_time)
    dt_end = datetime.combine(work_date, end_time)

    if dt_end <= dt_start:
        if allow_cross_day:
            dt_end += timedelta(days=1)
        else:
            return {"total_hours": 0.0, "normal_hours": 0.0, "night_hours": 0.0, "weekend_hours": 0.0, "holiday_hours": 0.0, "overtime_hours": 0.0}

    total = (dt_end - dt_start).total_seconds() / 3600.0

    night_start = datetime.combine(work_date, time(22, 0))
    night_end = datetime.combine(work_date + timedelta(days=1), time(6, 0))

    overlap_seconds = 0.0
    if dt_end > night_start and dt_start < night_end:
        overlap_start = max(dt_start, night_start)
        overlap_end = min(dt_end, night_end)
        overlap_seconds = max((overlap_end - overlap_start).total_seconds(), 0.0)

    night_hours = round(overlap_seconds / 3600.0, 2)
    normal_hours = round(total - night_hours, 2)

    weekend_hours = total if is_weekend else 0.0
    holiday_hours = total if is_holiday else 0.0
    overtime_hours = max(total - standard_daily_hours, 0.0)

    return {
        "total_hours": round(total, 2),
        "normal_hours": normal_hours,
        "night_hours": night_hours,
        "weekend_hours": round(weekend_hours, 2),
        "holiday_hours": round(holiday_hours, 2),
        "overtime_hours": round(overtime_hours, 2),
    }

def save_timesheet_rows(conn, employee_key: str, df_manual: pd.DataFrame, snapshot: dict):
    now = datetime.now().isoformat(timespec="seconds")
    cur = conn.cursor()

    nume = safe_str(snapshot.get("Nume"))
    prenume = safe_str(snapshot.get("Prenume"))
    cnp = safe_str(snapshot.get("CNP"))
    locatie = safe_str(snapshot.get("Locatie"))
    directie = safe_str(snapshot.get("Directie"))
    departament = safe_str(snapshot.get("Departament"))
    birou = safe_str(snapshot.get("Birou"))

    for _, row in df_manual.iterrows():
        d_str = safe_str(row.get("Data"))
        try:
            d = datetime.strptime(d_str, "%d.%m.%Y").date()
        except Exception:
            continue
        work_date = d.isoformat()

        status = safe_str(row.get("Status"))
        if status.startswith("CO"):
            status_db = "CO"
        elif status.startswith("CM"):
            status_db = "CM"
        elif status.startswith("CFP"):
            status_db = "CFP"
        elif "Nemotivat" in status:
            status_db = "Nemotivat"
        elif status.startswith("Liber"):
            status_db = "Liber"
        elif status == "Lucrat":
            status_db = "Lucrat"
        else:
            status_db = status if status else "Lucrat"

        cur.execute("""
            INSERT INTO timesheets(
                employee_key, work_date,
                start_time, end_time, status,
                total_hours, normal_hours, night_hours,
                weekend_hours, holiday_hours, overtime_hours,
                co_day, cm_day, cfp_day, nemotivat_day, liber_day, telemunca_day, samd_day,
                nume, prenume, cnp, locatie, directie, departament, birou,
                created_at, updated_at
            )
            VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            ON CONFLICT(employee_key, work_date) DO UPDATE SET
                start_time=excluded.start_time,
                end_time=excluded.end_time,
                status=excluded.status,
                total_hours=excluded.total_hours,
                normal_hours=excluded.normal_hours,
                night_hours=excluded.night_hours,
                weekend_hours=excluded.weekend_hours,
                holiday_hours=excluded.holiday_hours,
                overtime_hours=excluded.overtime_hours,
                co_day=excluded.co_day,
                cm_day=excluded.cm_day,
                cfp_day=excluded.cfp_day,
                nemotivat_day=excluded.nemotivat_day,
                liber_day=excluded.liber_day,
                nume=excluded.nume,
                prenume=excluded.prenume,
                cnp=excluded.cnp,
                locatie=excluded.locatie,
                directie=excluded.directie,
                departament=excluded.departament,
                birou=excluded.birou,
                updated_at=excluded.updated_at
        """, (
            safe_str(employee_key), work_date,
            (safe_str(row.get("Ora sosire")) or None),
            (safe_str(row.get("Ora plecare")) or None),
            status_db,
            float(row.get("Ore totale", 0) or 0),
            float(row.get("Ore normale", 0) or 0),
            float(row.get("Ore noapte", 0) or 0),
            float(row.get("Ore weekend", 0) or 0),
            float(row.get("Ore sărbătoare", 0) or 0),
            float(row.get("Ore suplimentare", 0) or 0),
            int(row.get("CO (zile)", 0) or 0),
            int(row.get("CM (zile)", 0) or 0),
            int(row.get("Fără plată (zile)", 0) or 0),
            int(row.get("Nemotivat (zile)", 0) or 0),
            int(row.get("Liber (zile)", 0) or 0),
            int(row.get("Telemunca (zile)", 0) or 0),
            int(row.get("Sam./D (zile)", 0) or 0),
            nume, prenume, cnp, locatie, directie, departament, birou,
            now, now
        ))
    conn.commit()

def set_punch(conn, employee_key: str, work_date: date, punch_type: str):
    now = datetime.now()
    hhmm = now.strftime("%H:%M")
    now_iso = now.isoformat(timespec="seconds")

    # Snapshot minim angajat (pentru scheme DB care cer coloane NOT NULL suplimentare)
    snap = {
        "employee_marca": safe_str(employee_key),
        "marca": safe_str(employee_key),
        "nume": "",
        "prenume": "",
        "cnp": "",
        "locatie": "",
        "directie": "",
        "departament": "",
        "birou": "",
    }
    try:
        df_emp, _ = read_employees(conn)
        if df_emp is not None and not df_emp.empty:
            m = df_emp[df_emp["employee_key"].astype(str) == safe_str(employee_key)]
            if not m.empty:
                r = m.iloc[0]
                snap.update({
                    "nume": safe_str(r.get("Nume", "")),
                    "prenume": safe_str(r.get("Prenume", "")),
                    "cnp": safe_str(r.get("CNP", "")),
                    "locatie": safe_str(r.get("Locatie", "")),
                    "directie": safe_str(r.get("Directie", "")),
                    "departament": safe_str(r.get("Departament", "")),
                    "birou": safe_str(r.get("Birou", "")),
                })
    except Exception:
        pass

    cur = conn.cursor()
    cur.execute("""
        SELECT start_time, end_time, status
        FROM timesheets
        WHERE employee_key=? AND work_date=?
    """, (safe_str(employee_key), work_date.isoformat()))
    existing = cur.fetchone()

    start_time_v = existing[0] if existing else None
    end_time_v = existing[1] if existing else None
    status_v = (existing[2] if existing else "Lucrat") or "Lucrat"

    if punch_type == "IN":
        # Nu suprascriem intrarea dacă există deja pontaj în ziua curentă
        if safe_str(start_time_v).strip():
            return
        # Dacă există deja ieșire fără intrare (date vechi inconsistente), nu alterăm
        if safe_str(end_time_v).strip() and not safe_str(start_time_v).strip():
            return
        start_time_v = hhmm
    else:
        # IESIRE nu este permisă înainte de INTRARE
        if not safe_str(start_time_v).strip():
            return
        # Nu suprascriem dacă ieșirea există deja
        if safe_str(end_time_v).strip():
            return
        # Protecție suplimentară: ora ieșire nu poate fi mai mică decât ora intrării
        if hhmm < safe_str(start_time_v):
            hhmm = safe_str(start_time_v)
        end_time_v = hhmm

    # Insert dinamic pentru compatibilitate cu DB-uri care au coloane NOT NULL extra
    table_info = conn.execute("PRAGMA table_info(timesheets)").fetchall() or []
    fields = ["employee_key", "work_date", "start_time", "end_time", "status", "created_at", "updated_at"]
    values_map = {
        "employee_key": safe_str(employee_key),
        "work_date": work_date.isoformat(),
        "start_time": start_time_v,
        "end_time": end_time_v,
        "status": status_v,
        "created_at": now_iso,
        "updated_at": now_iso,
        "employee_marca": snap.get("employee_marca", ""),
        "marca": snap.get("marca", ""),
        "nume": snap.get("nume", ""),
        "prenume": snap.get("prenume", ""),
        "cnp": snap.get("cnp", ""),
        "locatie": snap.get("locatie", ""),
        "directie": snap.get("directie", ""),
        "departament": snap.get("departament", ""),
        "birou": snap.get("birou", ""),
    }

    # Adăugăm câteva coloane uzuale dacă există în schemă
    existing_cols = {str(r[1]).lower() for r in table_info}
    for c in ["employee_marca", "marca", "nume", "prenume", "cnp", "locatie", "directie", "departament", "birou"]:
        if c in existing_cols and c not in fields:
            fields.append(c)

    # Pentru orice coloană NOT NULL fără default, completăm fallback ca să evităm constraint errors
    for r in table_info:
        col = str(r[1]).lower()
        col_type = str(r[2] or "").upper()
        notnull = int(r[3] or 0) == 1
        default_v = r[4]
        pk = int(r[5] or 0) == 1
        if pk or not notnull or default_v is not None or col in fields:
            continue
        if "INT" in col_type or "REAL" in col_type or "NUM" in col_type:
            values_map[col] = 0
        else:
            values_map[col] = ""
        fields.append(col)

    placeholders = ",".join(["?"] * len(fields))
    updates = "start_time=excluded.start_time, end_time=excluded.end_time, status=excluded.status, updated_at=excluded.updated_at"
    values = [values_map.get(f) for f in fields]
    conn.execute(
        f"""
        INSERT INTO timesheets({', '.join(fields)})
        VALUES({placeholders})
        ON CONFLICT(employee_key, work_date) DO UPDATE SET
            {updates}
        """,
        tuple(values),
    )
    conn.commit()


# ============================================================
# ADMIN USERS (CRUD) + SCOPES
# ============================================================

def admin_get_users(conn: sqlite3.Connection) -> pd.DataFrame:
    return pd.read_sql_query("""
        SELECT username, role, COALESCE(employee_key,'') AS employee_key, is_active, created_at
        FROM pontaj_users
        ORDER BY role DESC, username
    """, conn)

def admin_create_user(conn: sqlite3.Connection, username: str, password: str, role: str, employee_key: str | None, is_active: int):
    username = username.strip()
    if not username:
        raise ValueError("Username gol.")
    salt = secrets.token_hex(16)
    ph = _hash_password(password, salt)
    conn.execute("""
        INSERT INTO pontaj_users(username, password_salt, password_hash, role, employee_key, is_active, created_at)
        VALUES(?,?,?,?,?,?,?)
    """, (username, salt, ph, role, (employee_key if employee_key else None), int(is_active), datetime.now().isoformat(timespec="seconds")))
    conn.commit()

def admin_update_user_basic(conn: sqlite3.Connection, username: str, role: str, employee_key: str | None, is_active: int):
    conn.execute("""
        UPDATE pontaj_users
        SET role=?, employee_key=?, is_active=?
        WHERE username=?
    """, (role, (employee_key if employee_key else None), int(is_active), username))
    conn.commit()

def admin_reset_password(conn: sqlite3.Connection, username: str, new_password: str):
    salt = secrets.token_hex(16)
    ph = _hash_password(new_password, salt)
    conn.execute("""
        UPDATE pontaj_users
        SET password_salt=?, password_hash=?
        WHERE username=?
    """, (salt, ph, username))
    conn.commit()

def admin_delete_user(conn: sqlite3.Connection, username: str):
    conn.execute("DELETE FROM pontaj_users WHERE username=?", (username,))
    conn.commit()

def admin_add_scope(conn: sqlite3.Connection, username: str, locatie: str | None, directie: str | None, departament: str | None, birou: str | None):
    conn.execute("""
        INSERT INTO pontaj_user_scopes(username, locatie, directie, departament, birou)
        VALUES(?,?,?,?,?)
    """, (username, locatie, directie, departament, birou))
    conn.commit()

def admin_delete_scope(conn: sqlite3.Connection, scope_id: int):
    conn.execute("DELETE FROM pontaj_user_scopes WHERE id=?", (int(scope_id),))
    conn.commit()


# ============================================================
# SIGNATURES CRUD
# ============================================================

def sig_list(conn: sqlite3.Connection) -> pd.DataFrame:
    return pd.read_sql_query("""
        SELECT id, label, signatory_name, signatory_role, COALESCE(image_path,'') AS image_path, is_active, created_at, updated_at
        FROM pontaj_signatures
        ORDER BY is_active DESC, id DESC
    """, conn)

def sig_set_active(conn: sqlite3.Connection, sig_id: int):
    conn.execute("UPDATE pontaj_signatures SET is_active=0")
    conn.execute("UPDATE pontaj_signatures SET is_active=1, updated_at=? WHERE id=?", (datetime.now().isoformat(timespec="seconds"), int(sig_id)))
    conn.commit()

def sig_add(conn: sqlite3.Connection, label: str, name: str, role: str, image_path: str | None):
    now = datetime.now().isoformat(timespec="seconds")
    conn.execute("""
        INSERT INTO pontaj_signatures(label, signatory_name, signatory_role, image_path, is_active, created_at, updated_at)
        VALUES(?,?,?,?,0,?,?)
    """, (label.strip(), name.strip(), role.strip(), (image_path if image_path else None), now, now))
    conn.commit()

def sig_update(conn: sqlite3.Connection, sig_id: int, label: str, name: str, role: str, image_path: str | None):
    now = datetime.now().isoformat(timespec="seconds")
    conn.execute("""
        UPDATE pontaj_signatures
        SET label=?, signatory_name=?, signatory_role=?, image_path=?, updated_at=?
        WHERE id=?
    """, (label.strip(), name.strip(), role.strip(), (image_path if image_path else None), now, int(sig_id)))
    conn.commit()

def sig_delete(conn: sqlite3.Connection, sig_id: int):
    # nu stergem automat fisierul, doar inregistrarea
    conn.execute("DELETE FROM pontaj_signatures WHERE id=?", (int(sig_id),))
    conn.commit()

def sig_get_active(conn: sqlite3.Connection) -> dict | None:
    df = pd.read_sql_query("""
        SELECT id, label, signatory_name, signatory_role, image_path
        FROM pontaj_signatures
        WHERE is_active=1
        LIMIT 1
    """, conn)
    if df.empty:
        return None
    return df.iloc[0].to_dict()


# ============================================================
# UI SECTIONS
# ============================================================

def render_admin_users(conn: sqlite3.Connection):
    st.markdown("## 🛡️ Admin → Utilizatori")
    st.caption("Creezi useri (mobil individual) si setezi exact ce locatie/directie/departament/birou vede fiecare.")

    df_emp, src = read_employees(conn)
    if not df_emp.empty:
        st.caption(f"Sursa angajati: **{src}**")

    users_df = admin_get_users(conn)
    st.dataframe(users_df, use_container_width=True)

    st.markdown("---")
    col_left, col_right = st.columns([1.1, 1.4])

    with col_left:
        st.markdown("### ➕ Creeaza utilizator")
        with st.form("create_user_form"):
            new_username = st.text_input("Username (unic)")
            new_role = st.selectbox("Rol", ["user", "manager", "admin"], index=0)
            new_is_active = st.checkbox("Activ", value=True)

            employee_key = None
            if not df_emp.empty:
                st.caption("Daca setezi employee_key -> userul vede DOAR acel angajat (ideal pentru mobil).")
                keys_list = [str(x) for x in df_emp["employee_key"].tolist()]
                label_map = {}
                if "FullName" in df_emp.columns:
                    for _, rr in df_emp.iterrows():
                        k = str(rr.get("employee_key", ""))
                        fn = str(rr.get("FullName", "") or "").strip()
                        if fn:
                            label_map[k] = f"{k} — {fn}"
                opts = ["(fara)"] + keys_list
                ek = st.selectbox(
                    "Angajat (employee_key/marca) - optional",
                    opts,
                    index=0,
                    format_func=lambda x: x if x == "(fara)" else label_map.get(str(x), str(x)),
                )
                employee_key = None if ek == "(fara)" else str(ek)
            else:
                employee_key = st.text_input("employee_key (optional)").strip() or None

            pw1 = st.text_input("Parola", type="password")
            pw2 = st.text_input("Confirma parola", type="password")

            ok = st.form_submit_button("Creeaza")

        if ok:
            try:
                if not pw1 or pw1 != pw2:
                    st.error("Parolele nu coincid.")
                else:
                    admin_create_user(conn, new_username, pw1, new_role, employee_key, 1 if new_is_active else 0)
                    st.success("Utilizator creat.")
                    st.rerun()
            except Exception as e:
                st.error(f"Eroare: {e}")

    with col_right:
        st.markdown("### ✏️ Editeaza utilizator")
        usernames = users_df["username"].tolist() if not users_df.empty else []
        if not usernames:
            st.info("Nu exista utilizatori.")
            return

        sel_user = st.selectbox("Selecteaza user", usernames, index=0)
        user_row = users_df[users_df["username"] == sel_user].iloc[0].to_dict()

        role = st.selectbox(
            "Rol",
            ["user", "manager", "admin"],
            index=["user","manager","admin"].index(str(user_row.get("role","user")) if str(user_row.get("role","user")) in ["user","manager","admin"] else "user"),
        )
        is_active = st.checkbox("Activ", value=bool(int(user_row.get("is_active", 1))))

        if not df_emp.empty:
            keys_list = [str(x) for x in df_emp["employee_key"].tolist()]
            label_map = {}
            if "FullName" in df_emp.columns:
                for _, rr in df_emp.iterrows():
                    k = str(rr.get("employee_key", ""))
                    fn = str(rr.get("FullName", "") or "").strip()
                    if fn:
                        label_map[k] = f"{k} — {fn}"
            opts = ["(fara)"] + keys_list
            current = safe_str(user_row.get("employee_key"))
            idx = opts.index(current) if current in opts else 0
            employee_key_edit = st.selectbox(
                "employee_key (daca e setat -> vede doar acel angajat)",
                opts,
                index=idx,
                format_func=lambda x: x if x == "(fara)" else label_map.get(str(x), str(x)),
            )
            employee_key_edit = None if employee_key_edit == "(fara)" else str(employee_key_edit)
        else:
            employee_key_edit = st.text_input("employee_key (optional)", value=safe_str(user_row.get("employee_key"))).strip() or None

        c1, c2, c3 = st.columns(3)
        with c1:
            if st.button("💾 Salveaza user"):
                admin_update_user_basic(conn, sel_user, role, employee_key_edit, 1 if is_active else 0)
                st.success("User actualizat.")
                st.rerun()
        with c2:
            if st.button("🧯 Dezactiveaza"):
                admin_update_user_basic(conn, sel_user, role, employee_key_edit, 0)
                st.warning("User dezactivat.")
                st.rerun()
        with c3:
            if sel_user == "admin":
                st.caption("Nu stergem admin implicit.")
            else:
                if st.button("🗑 Sterge user"):
                    admin_delete_user(conn, sel_user)
                    st.warning("User sters.")
                    st.rerun()

        st.markdown("---")
        st.markdown("### 🔁 Resetare parola")
        pw_new1 = st.text_input("Parola noua", type="password", key="pwnew1")
        pw_new2 = st.text_input("Confirma parola noua", type="password", key="pwnew2")
        if st.button("Reseteaza parola"):
            if not pw_new1 or pw_new1 != pw_new2:
                st.error("Parolele nu coincid.")
            else:
                admin_reset_password(conn, sel_user, pw_new1)
                st.success("Parola resetata.")

        st.markdown("---")
        st.markdown("### 🔒 Permisiuni (Scopes) pe structura")
        st.caption("✅ Daca user are employee_key -> vede doar el. Pentru manager: lași employee_key gol si adaugi reguli.")

        scopes_df = get_user_scopes(conn, sel_user)
        if scopes_df.empty:
            st.info("Nu exista reguli (scopes).")
        else:
            st.dataframe(scopes_df, use_container_width=True)

        if df_emp.empty:
            st.warning("Nu am lista de structuri din angajati. Completeaza manual.")
            loc = st.text_input("locatie (optional)")
            dire = st.text_input("directie (optional)")
            dep = st.text_input("departament (optional)")
            bir = st.text_input("birou (optional)")
            if st.button("➕ Adauga regula"):
                admin_add_scope(conn, sel_user, loc or None, dire or None, dep or None, bir or None)
                st.success("Regula adaugata.")
                st.rerun()
        else:
            def uniq(col, df):
                vals = sorted([x for x in df[col].unique().tolist() if safe_str(x)])
                return ["(Oricare)"] + vals

            loc_list = uniq("Locatie", df_emp)
            loc_sel = st.selectbox("Locatie", loc_list, index=0, key="scope_loc")

            df_l = df_emp if loc_sel == "(Oricare)" else df_emp[df_emp["Locatie"] == loc_sel]
            dir_list = uniq("Directie", df_l)
            dir_sel = st.selectbox("Directie", dir_list, index=0, key="scope_dir")

            df_d = df_l if dir_sel == "(Oricare)" else df_l[df_l["Directie"] == dir_sel]
            dep_list = uniq("Departament", df_d)
            dep_sel = st.selectbox("Departament", dep_list, index=0, key="scope_dep")

            df_p = df_d if dep_sel == "(Oricare)" else df_d[df_d["Departament"] == dep_sel]
            bir_list = uniq("Birou", df_p)
            bir_sel = st.selectbox("Birou", bir_list, index=0, key="scope_bir")

            loc_val = None if loc_sel == "(Oricare)" else loc_sel
            dir_val = None if dir_sel == "(Oricare)" else dir_sel
            dep_val = None if dep_sel == "(Oricare)" else dep_sel
            bir_val = None if bir_sel == "(Oricare)" else bir_sel

            if st.button("➕ Adauga regula (scope)"):
                admin_add_scope(conn, sel_user, loc_val, dir_val, dep_val, bir_val)
                st.success("Regula adaugata.")
                st.rerun()

        if not scopes_df.empty:
            st.markdown("### 🗑 Sterge regula existenta")
            sid = st.selectbox("Alege ID regula", scopes_df["id"].tolist(), index=0, key="del_scope_id")
            if st.button("Sterge regula"):
                admin_delete_scope(conn, int(sid))
                st.warning("Regula stearsa.")
                st.rerun()

def render_signatures(conn: sqlite3.Connection):
    st.markdown("## ✍️ Semnaturi (adauga / modifica / sterge)")
    st.caption("Semnaturile sunt multiple. Poti seta una ca **Activa** (folosita pe documente/rapoarte).")

    sig_df = sig_list(conn)
    st.dataframe(sig_df, use_container_width=True)

    active = sig_get_active(conn)
    if active:
        st.success(f"Semnatura activa: {active.get('label','')} - {active.get('signatory_name','')} ({active.get('signatory_role','')})")
        img = safe_str(active.get("image_path"))
        if img and os.path.exists(img):
            st.image(img, width=240, caption="Semnatura activa")
    else:
        st.warning("Nu este setata nicio semnatura activa.")

    st.markdown("---")
    colA, colB = st.columns(2)

    with colA:
        st.markdown("### ➕ Adauga semnatura")
        with st.form("sig_add"):
            label = st.text_input("Eticheta (ex: Director / Sef serviciu)", key="sig_add_label")
            name = st.text_input("Nume semnatar", key="sig_add_name")
            role = st.text_input("Functie semnatar", key="sig_add_role")
            up = st.file_uploader("Browse → imagine semnatura (PNG)", type=["png"], key="sig_add_file")
            make_active = st.checkbox("Seteaza ca activa dupa salvare", value=False, key="sig_add_active")
            ok = st.form_submit_button("Adauga")

        if ok:
            try:
                if not label.strip() or not name.strip() or not role.strip():
                    st.error("Completeaza: eticheta + nume + functie.")
                else:
                    img_path = None
                    if up is not None:
                        # salvam in assets/signatures cu nume random
                        fname = f"sig_{secrets.token_hex(8)}.png"
                        img_path = os.path.join(SIGN_DIR, fname)
                        save_uploaded_file(up, img_path)

                    sig_add(conn, label, name, role, img_path)
                    # set active daca s-a bifat
                    if make_active:
                        new_id = pd.read_sql_query("SELECT MAX(id) AS id FROM pontaj_signatures", conn).iloc[0]["id"]
                        if pd.notna(new_id):
                            sig_set_active(conn, int(new_id))
                    st.success("Semnatura adaugata.")
                    st.rerun()
            except Exception as e:
                st.error(f"Eroare: {e}")

    with colB:
        st.markdown("### ✏️ Modifica / 🗑 Sterge semnatura")
        if sig_df.empty:
            st.info("Nu exista semnaturi.")
        else:
            ids = sig_df["id"].tolist()
            sid = st.selectbox("Alege semnatura", ids, index=0, format_func=lambda x: f"ID {x}", key="sig_edit_id")
            row = sig_df[sig_df["id"] == sid].iloc[0].to_dict()

            label = st.text_input("Eticheta", value=safe_str(row.get("label")), key="sig_edit_label")
            name = st.text_input("Nume", value=safe_str(row.get("signatory_name")), key="sig_edit_name")
            role = st.text_input("Functie", value=safe_str(row.get("signatory_role")), key="sig_edit_role")

            current_img = safe_str(row.get("image_path"))
            if current_img and os.path.exists(current_img):
                st.image(current_img, width=240, caption="Imagine curenta")
            else:
                st.caption("Fara imagine (sau fisier lipsa).")

            up2 = st.file_uploader("Browse → inlocuieste imagine (PNG) (optional)", type=["png"], key="sig_edit_file")

            c1, c2, c3 = st.columns(3)
            with c1:
                if st.button("💾 Salveaza modificari", key="sig_save_btn"):
                    try:
                        img_path = current_img if current_img else None
                        if up2 is not None:
                            # salvam in alt fisier ca sa nu stricam vechiul (optional)
                            fname = f"sig_{secrets.token_hex(8)}.png"
                            img_path = os.path.join(SIGN_DIR, fname)
                            save_uploaded_file(up2, img_path)
                        sig_update(conn, int(sid), label, name, role, img_path)
                        st.success("Semnatura modificata.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Eroare: {e}")

            with c2:
                if st.button("⭐ Seteaza ca activa", key="sig_active_btn"):
                    try:
                        sig_set_active(conn, int(sid))
                        st.success("Semnatura activata.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Eroare: {e}")

            with c3:
                if st.button("🗑 Sterge", key="sig_delete_btn"):
                    try:
                        sig_delete(conn, int(sid))
                        st.warning("Semnatura stearsa.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Eroare: {e}")



# ============================================================
# LEAVE REQUESTS -> APPLY TO TIMESHEETS (business rules)
# ============================================================

def _daterange(d1: date, d2: date):
    d = d1
    while d <= d2:
        yield d
        d += timedelta(days=1)

def _is_weekday(d: date) -> bool:
    return d.weekday() < 5

def get_leave_request_by_id(conn: sqlite3.Connection, req_id: int) -> dict | None:
    cols = _table_columns(conn, "leave_requests")
    status_expr = "COALESCE(status, status_code) AS status" if (_has_col(cols, "status") and _has_col(cols, "status_code")) else ("status AS status" if _has_col(cols, "status") else ("status_code AS status" if _has_col(cols, "status_code") else "NULL AS status"))
    df = pd.read_sql_query(
        f"""SELECT
                id, employee_key, request_type, start_date, end_date,
                weekdays_only, hours_per_day,
                {status_expr},
                notes,
                created_by, created_at,
                decision_by, decision_at, decision_reason,
                cm_series, cm_number, cm_type, cm_diag, cm_issuer
             FROM leave_requests
             WHERE id=?
             LIMIT 1""",
        conn,
        params=(int(req_id),)
    )
    if df.empty:
        return None
    return df.iloc[0].to_dict()

def _ts_upsert_absence(conn: sqlite3.Connection, employee_key: str, d: date, status: str, flags: dict):
    now = datetime.now().isoformat(timespec="seconds")
    conn.execute(
        """INSERT INTO timesheets(
                employee_key, work_date,
                start_time, end_time, status,
                total_hours, normal_hours, night_hours,
                weekend_hours, holiday_hours, overtime_hours,
                co_day, cm_day, cfp_day, nemotivat_day, liber_day, telemunca_day, samd_day,
                created_at, updated_at
            ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            ON CONFLICT(employee_key, work_date) DO UPDATE SET
                start_time=excluded.start_time,
                end_time=excluded.end_time,
                status=excluded.status,
                total_hours=excluded.total_hours,
                normal_hours=excluded.normal_hours,
                night_hours=excluded.night_hours,
                weekend_hours=excluded.weekend_hours,
                holiday_hours=excluded.holiday_hours,
                overtime_hours=excluded.overtime_hours,
                co_day=excluded.co_day,
                cm_day=excluded.cm_day,
                cfp_day=excluded.cfp_day,
                nemotivat_day=excluded.nemotivat_day,
                liber_day=excluded.liber_day,
                telemunca_day=excluded.telemunca_day,
                samd_day=excluded.samd_day,
                updated_at=excluded.updated_at
        """,
        (
            safe_str(employee_key), d.isoformat(),
            None, None, status,
            0.0, 0.0, 0.0,
            0.0, 0.0, 0.0,
            int(flags.get("co_day", 0)),
            int(flags.get("cm_day", 0)),
            int(flags.get("cfp_day", 0)),
            int(flags.get("nemotivat_day", 0)),
            int(flags.get("liber_day", 0)),
            int(flags.get("telemunca_day", 0)),
            int(flags.get("samd_day", 0)),
            now, now
        )
    )

def _ts_upsert_telemunca(conn: sqlite3.Connection, cfg: dict, employee_key: str, d: date, hours_per_day: float):
    now = datetime.now().isoformat(timespec="seconds")
    standard_daily_hours = float((cfg or DEFAULT_CONFIG).get("standard_daily_hours", 8.0))
    h = float(hours_per_day or 0.0) or standard_daily_hours
    conn.execute(
        """INSERT INTO timesheets(
                employee_key, work_date,
                start_time, end_time, status,
                total_hours, normal_hours, night_hours,
                weekend_hours, holiday_hours, overtime_hours,
                co_day, cm_day, cfp_day, nemotivat_day, liber_day, telemunca_day, samd_day,
                created_at, updated_at
            ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            ON CONFLICT(employee_key, work_date) DO UPDATE SET
                status=excluded.status,
                total_hours=excluded.total_hours,
                normal_hours=excluded.normal_hours,
                night_hours=excluded.night_hours,
                telemunca_day=excluded.telemunca_day,
                updated_at=excluded.updated_at
        """,
        (
            safe_str(employee_key), d.isoformat(),
            None, None, "Lucrat",
            h, h, 0.0,
            0.0, 0.0, 0.0,
            0, 0, 0, 0, 0, 1, 0,
            now, now
        )
    )


def apply_leave_request_to_timesheets(conn: sqlite3.Connection, cfg: dict, req_row: dict):
    employee_key = safe_str(req_row.get("employee_key"))
    rt = safe_str(req_row.get("request_type"))
    start_date = date.fromisoformat(safe_str(req_row.get("start_date")))
    end_date = date.fromisoformat(safe_str(req_row.get("end_date")))
    weekdays_only = bool(int(req_row.get("weekdays_only", 1) or 0))

    # Dacă există configurare pentru tip, o folosim
    type_cfg = None
    if table_exists(conn, "request_types"):
        migrate_request_types_extra_cols(conn)
        try:
            df = pd.read_sql_query(
                "SELECT * FROM request_types WHERE code=? AND is_active=1 LIMIT 1",
                conn,
                params=(rt,)
            )
            if not df.empty:
                type_cfg = df.iloc[0].to_dict()
        except Exception:
            type_cfg = None

    if type_cfg:
        apply_mode = safe_str(type_cfg.get("apply_mode")).upper() or "ABSENCE"
        ts_status = safe_str(type_cfg.get("ts_status")) or rt
        weekdays_only_default = int(type_cfg.get("weekdays_only_default", 1) or 0)

        # cererea poate override weekdays_only doar dacă există explicit; altfel folosim default
        if "weekdays_only" not in req_row or req_row.get("weekdays_only") is None:
            weekdays_only = bool(weekdays_only_default)

        # ore/zi: dacă cererea are value >0, are prioritate peste config
        if 0.0 > 0:
            hours_per_day = 0.0

        flags = {
            "co_day": int(type_cfg.get("co_day", 0) or 0),
            "cm_day": int(type_cfg.get("cm_day", 0) or 0),
            "cfp_day": int(type_cfg.get("cfp_day", 0) or 0),
            "nemotivat_day": int(type_cfg.get("nemotivat_day", 0) or 0),
            "liber_day": int(type_cfg.get("liber_day", 0) or 0),
            "telemunca_day": int(type_cfg.get("telemunca_day", 0) or 0),
            "samd_day": int(type_cfg.get("samd_day", 0) or 0),
        }

        for d in _daterange(start_date, end_date):
            if weekdays_only and not _is_weekday(d):
                continue
            if apply_mode == "WORK":
                # zi lucrata (ex: telemunca), status=Lucrat + flag
                _ts_upsert_telemunca(conn, cfg, employee_key, d, hours_per_day)
                # asigurăm flag-uri suplimentare dacă sunt setate (telemunca_day etc.)
                if any(v for v in flags.values()):
                    # update flags
                    conn.execute(
                        """UPDATE timesheets
                            SET co_day=?, cm_day=?, cfp_day=?, nemotivat_day=?, liber_day=?,
                                telemunca_day=?, samd_day=?, updated_at=?
                            WHERE employee_key=? AND work_date=?""",
                        (
                            flags["co_day"], flags["cm_day"], flags["cfp_day"], flags["nemotivat_day"], flags["liber_day"],
                            flags["telemunca_day"], flags["samd_day"],
                            datetime.now().isoformat(timespec="seconds"),
                            employee_key, d.isoformat()
                        )
                    )
            elif apply_mode == "MARK_ONLY":
                # doar marcaj status, fără ore/flag-uri (dar putem păstra status)
                _ts_upsert_absence(conn, employee_key, d, ts_status, flags)
            else:
                # ABSENCE (default)
                _ts_upsert_absence(conn, employee_key, d, ts_status, flags)

        conn.commit()
        return

    # Fallback: reguli implicite (compatibil)
    for d in _daterange(start_date, end_date):
        if weekdays_only and not _is_weekday(d):
            continue

        if rt == "CO":
            _ts_upsert_absence(conn, employee_key, d, "CO", {"co_day": 1})
        elif rt == "CM":
            _ts_upsert_absence(conn, employee_key, d, "CM", {"cm_day": 1})
        elif rt == "CFS":
            _ts_upsert_absence(conn, employee_key, d, "CFP", {"cfp_day": 1})
        elif rt == "NEPL":
            _ts_upsert_absence(conn, employee_key, d, "Nemotivat", {"nemotivat_day": 1})
        elif rt == "Liber":
            _ts_upsert_absence(conn, employee_key, d, "ZI_LIBERA", {"liber_day": 1})
        elif rt == "Telemunca":
            _ts_upsert_telemunca(conn, cfg, employee_key, d, 0.0)
        elif rt == "Sam./D":
            _ts_upsert_absence(conn, employee_key, d, "Sam./D", {"samd_day": 1})
        else:
            _ts_upsert_absence(conn, employee_key, d, rt, {})

    conn.commit()
def rollback_leave_request_from_timesheets(conn: sqlite3.Connection, req_row: dict):
    employee_key = safe_str(req_row.get("employee_key"))
    rt = safe_str(req_row.get("request_type"))
    start_date = date.fromisoformat(safe_str(req_row.get("start_date")))
    end_date = date.fromisoformat(safe_str(req_row.get("end_date")))
    weekdays_only = bool(int(req_row.get("weekdays_only", 1) or 0))

    if rt == "Liber":
        status = "ZI_LIBERA"
    elif rt == "CFS":
        status = "CFP"
    elif rt == "NEPL":
        status = "Nemotivat"
    elif rt == "Telemunca":
        status = "Lucrat"
    else:
        status = rt

    cur = conn.cursor()
    for d in _daterange(start_date, end_date):
        if weekdays_only and not _is_weekday(d):
            continue
        if rt == "Telemunca":
            cur.execute("DELETE FROM timesheets WHERE employee_key=? AND work_date=? AND telemunca_day=1", (employee_key, d.isoformat()))
        else:
            cur.execute("DELETE FROM timesheets WHERE employee_key=? AND work_date=? AND status=?", (employee_key, d.isoformat(), status))
    conn.commit()


# ============================================================
# OVERTIME HELPERS
# ============================================================

def _today_iso() -> str:
    return datetime.now().date().isoformat()

def ensure_overtime_ledger_from_timesheets(conn: sqlite3.Connection, employee_keys: list[str] | None = None,
                                          start: str | None = None, end: str | None = None) -> None:
    """Upsert in overtime_ledger orele suplimentare (earned) din timesheets.overtime_hours.
    - pastreaza orele compensate/platite existente (nu le reseteaza)
    - ruleaza rapid: doar interval / doar employee_keys daca sunt date
    """
    cols_ts = get_table_columns(conn, "timesheets")
    if "overtime_hours" not in [c.lower() for c in cols_ts]:
        return

    where = []
    params: list = []
    if employee_keys:
        q = ",".join(["?"] * len(employee_keys))
        where.append(f"employee_key IN ({q})")
        params.extend([str(x) for x in employee_keys])
    if start and end:
        where.append("work_date BETWEEN ? AND ?")
        params.extend([start, end])

    wsql = ("WHERE " + " AND ".join(where)) if where else ""
    df = pd.read_sql_query(
        f"""SELECT employee_key, work_date, COALESCE(overtime_hours,0) AS overtime_hours
              FROM timesheets
              {wsql}
              AND COALESCE(overtime_hours,0) > 0
           """ if where else
        """SELECT employee_key, work_date, COALESCE(overtime_hours,0) AS overtime_hours
              FROM timesheets
              WHERE COALESCE(overtime_hours,0) > 0
           """,
        conn,
        params=params if where else None
    )

    if df.empty:
        return

    now = datetime.now().isoformat(timespec="seconds")
    cur = conn.cursor()

    # upsert earned hours; do not overwrite compensated/paid
    for _, r in df.iterrows():
        ek = str(r["employee_key"])
        wd = str(r["work_date"])
        earned = float(r["overtime_hours"] or 0.0)

        cur.execute("""
            INSERT INTO overtime_ledger (employee_key, work_date, hours_earned, hours_compensated, hours_paid, source, created_at, updated_at)
            VALUES (?, ?, ?, 0, 0, 'pontaj_auto', ?, ?)
            ON CONFLICT(employee_key, work_date, source) DO UPDATE SET
                hours_earned = excluded.hours_earned,
                updated_at = excluded.updated_at
        """, (ek, wd, earned, now, now))

    # optional cleanup: dacă în timesheets nu mai există overtime într-o zi, nu ștergem automat (ar putea exista acțiuni).
    conn.commit()


def overtime_fifo_consume(conn: sqlite3.Connection, employee_key: str, hours: float, mode: str,
                          action_date: str, note: str, created_by: str | None) -> None:
    """Consuma orele suplimentare din ledger FIFO (cele mai vechi primele).
    mode: 'COMPENSATE' sau 'PAY'
    """
    if hours <= 0:
        return
    mode = mode.upper().strip()
    if mode not in ("COMPENSATE", "PAY"):
        raise ValueError("mode invalid")

    # luăm toate intrările cu ore disponibile
    df = pd.read_sql_query(
        """SELECT id, work_date, hours_earned, hours_compensated, hours_paid,
                     (hours_earned - hours_compensated - hours_paid) AS available
              FROM overtime_ledger
              WHERE employee_key=? AND source='pontaj_auto'
              ORDER BY work_date ASC
           """,
        conn,
        params=(str(employee_key),)
    )
    if df.empty:
        return

    remain = float(hours)
    now = datetime.now().isoformat(timespec="seconds")
    cur = conn.cursor()

    for _, r in df.iterrows():
        if remain <= 1e-9:
            break
        avail = float(r["available"] or 0.0)
        if avail <= 1e-9:
            continue
        take = min(avail, remain)

        if mode == "COMPENSATE":
            cur.execute(
                "UPDATE overtime_ledger SET hours_compensated = hours_compensated + ?, updated_at=? WHERE id=?",
                (take, now, int(r["id"]))
            )
        else:
            cur.execute(
                "UPDATE overtime_ledger SET hours_paid = hours_paid + ?, updated_at=? WHERE id=?",
                (take, now, int(r["id"]))
            )

        remain -= take

    # log acțiune (ore efectiv alocate)
    allocated = float(hours) - max(remain, 0.0)
    if allocated > 1e-9:
        cur.execute(
            """INSERT INTO overtime_actions (employee_key, action_date, action_type, hours, note, created_by, created_at)
                 VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (str(employee_key), str(action_date), mode, allocated, (note or None), (created_by or None), now)
        )

    conn.commit()


def overtime_summary(conn: sqlite3.Connection, employee_keys: list[str], start: str, end: str) -> pd.DataFrame:
    if not employee_keys:
        return pd.DataFrame(columns=["employee_key","earned","compensated","paid","remaining","expired_90d","to_pay_90d"])

    q = ",".join(["?"] * len(employee_keys))
    df = pd.read_sql_query(
        f"""SELECT employee_key,
                     SUM(hours_earned) AS earned,
                     SUM(hours_compensated) AS compensated,
                     SUM(hours_paid) AS paid,
                     SUM(hours_earned - hours_compensated - hours_paid) AS remaining
              FROM overtime_ledger
              WHERE employee_key IN ({q})
                AND work_date BETWEEN ? AND ?
              GROUP BY employee_key
              ORDER BY employee_key
           """,
        conn,
        params=list(map(str, employee_keys)) + [start, end]
    )
    if df.empty:
        return df

    df = df.fillna(0.0)
    for c in ["earned","compensated","paid","remaining"]:
        df[c] = df[c].astype(float)

    # calcul 90 zile: ore rămase mai vechi de 90 zile (față de azi) => propuse la plată
    cutoff = (date.today() - timedelta(days=90)).isoformat()
    df_exp = pd.read_sql_query(
        f"""SELECT employee_key,
                     SUM(hours_earned - hours_compensated - hours_paid) AS expired_90d
              FROM overtime_ledger
              WHERE employee_key IN ({q})
                AND work_date <= ?
                AND (hours_earned - hours_compensated - hours_paid) > 0
              GROUP BY employee_key
           """,
        conn,
        params=list(map(str, employee_keys)) + [cutoff]
    )
    df_exp = df_exp.fillna(0.0)
    df = df.merge(df_exp, on="employee_key", how="left")
    df["expired_90d"] = df["expired_90d"].fillna(0.0).astype(float)
    df["to_pay_90d"] = df["expired_90d"]  # semantic: ore propuse la plata (depășit 90 zile)

    return df


def page_ore_suplimentare(cfg: dict, conn: sqlite3.Connection, user_ctx: dict):
    st.subheader("⏱ Ore suplimentare")
    st.caption("Regulă: **tot ce depășește 8 ore/zi** (standard_daily_hours) este considerat automat ore suplimentare. "
               "Compensare prioritar prin timp liber în **90 zile**; după 90 zile, orele rămase sunt propuse la **plată**.")

    role = (user_ctx.get("role") or "user").lower()

    # angajați vizibili (respectăm scope/rol)
    df_all = load_employees_cached(conn)
    scopes_df = get_user_scopes(conn, user_ctx["username"])
    scopes = scopes_df.drop(columns=["id"], errors="ignore").to_dict("records")
    df_emp = apply_scope_filter(df_all, user_ctx.get("role"), scopes, user_ctx.get("employee_key"))

    if df_emp.empty:
        st.warning("Nu există angajați vizibili pentru acest utilizator.")
        return

    # selector interval
    today = date.today()
    c1, c2, c3 = st.columns([1, 1, 2])
    with c1:
        year = st.number_input("An", min_value=2000, max_value=2100, value=today.year, step=1, key="ot_year")
    with c2:
        month = st.selectbox("Luna", list(range(1,13)), index=today.month-1, key="ot_month")
    with c3:
        st.caption("Orele sunt preluate automat din pontajul salvat (timesheets.overtime_hours).")

    start = date(int(year), int(month), 1).isoformat()
    end = date(int(year), int(month), calendar.monthrange(int(year), int(month))[1]).isoformat()

    # sync ledger din timesheets pentru intervalul selectat
    emp_keys = [str(x) for x in df_emp["employee_key"].tolist()]
    ensure_overtime_ledger_from_timesheets(conn, employee_keys=emp_keys, start=start, end=end)

    # sumar
    sum_df = overtime_summary(conn, emp_keys, start, end)
    if sum_df.empty:
        st.info("Nu există ore suplimentare în interval.")
        return

    # adaugăm nume/prenume
    emp_map = df_emp.set_index("employee_key")
    def _name_for(k: str) -> str:
        try:
            r = emp_map.loc[str(k)]
            fn = str(r.get("FullName", "") or "").strip()
            if fn:
                return fn
            n = str(r.get("Nume", r.get("nume","")) or "").strip()
            p = str(r.get("Prenume", r.get("prenume","")) or "").strip()
            return (n + " " + p).strip()
        except Exception:
            return ""

    sum_df["Angajat"] = sum_df["employee_key"].astype(str).apply(lambda k: f"{k} — {_name_for(str(k))}".strip(" —"))
    show = sum_df[["Angajat","earned","compensated","paid","remaining","to_pay_90d"]].rename(columns={
        "earned":"Ore câștigate",
        "compensated":"Ore compensate",
        "paid":"Ore plătite",
        "remaining":"Ore rămase",
        "to_pay_90d":"Depășit 90 zile (de plătit)"
    })
    st.dataframe(show, use_container_width=True, hide_index=True)

    # detaliu pe angajat
    st.divider()
    st.markdown("### Detaliu angajat")
    # map etichete
    label_map = {str(k): f"{str(k)} — {_name_for(str(k))}".strip() for k in emp_keys}
    sel_emp = st.selectbox("Selectează angajat", options=emp_keys, format_func=lambda x: label_map.get(str(x), str(x)), key="ot_sel_emp")
    sel_emp = str(sel_emp)

    df_det = pd.read_sql_query(
        """SELECT work_date AS Data,
                     hours_earned AS Castigate,
                     hours_compensated AS Compensate,
                     hours_paid AS Platite,
                     (hours_earned - hours_compensated - hours_paid) AS Ramase
              FROM overtime_ledger
              WHERE employee_key=? AND work_date BETWEEN ? AND ?
              AND hours_earned > 0
              ORDER BY work_date ASC
        """,
        conn,
        params=(sel_emp, start, end)
    ).fillna(0.0)

    st.dataframe(df_det, use_container_width=True, hide_index=True)

    # acțiuni (doar admin/manager)
    st.divider()
    st.markdown("### Compensare / Plată")
    if role not in ("admin", "manager"):
        st.info("Doar admin/manager poate înregistra compensări sau plăți. Tu poți doar vizualiza.")
    else:
        a1, a2, a3, a4 = st.columns([1,1,2,2])
        with a1:
            act = st.selectbox("Tip acțiune", ["COMPENSATE", "PAY"], format_func=lambda x: "Compensare (timp liber)" if x=="COMPENSATE" else "Plată (spor)", key="ot_act_type")
        with a2:
            hrs = st.number_input("Ore", min_value=0.0, max_value=1000.0, value=0.0, step=0.5, key="ot_act_hours")
        with a3:
            act_date = st.date_input("Data acțiunii", value=today, key="ot_act_date").isoformat()
        with a4:
            note = st.text_input("Notă (opțional)", value="", key="ot_act_note")

        if st.button("✅ Aplică acțiunea", key="ot_act_apply"):
            try:
                if hrs <= 0:
                    st.warning("Introdu ore > 0.")
                else:
                    overtime_fifo_consume(conn, sel_emp, float(hrs), act, act_date, note, user_ctx.get("username"))
                    st.success("Acțiune înregistrată (FIFO din cele mai vechi ore).")
                    st.rerun()
            except Exception as e:
                st.error(f"Eroare: {e}")

        st.markdown("#### Istoric acțiuni")
        df_act = pd.read_sql_query(
            """SELECT action_date AS Data, action_type AS Tip, hours AS Ore, note AS Nota, created_by AS Operator, created_at AS Creat
                 FROM overtime_actions
                 WHERE employee_key=?
                 ORDER BY id DESC
                 LIMIT 200
            """,
            conn,
            params=(sel_emp,)
        )
        if df_act.empty:
            st.caption("Nu există acțiuni.")
        else:
            st.dataframe(df_act, use_container_width=True, hide_index=True)

    # export excel
    st.divider()
    st.markdown("### ⬇️ Export (Excel)")
    bio = BytesIO()
    with pd.ExcelWriter(bio, engine="openpyxl") as writer:
        show.to_excel(writer, index=False, sheet_name="Overtime summary")
        df_det.to_excel(writer, index=False, sheet_name=f"Detaliu_{sel_emp}")
    bio.seek(0)
    st.download_button(
        "⬇ Export ore suplimentare (Excel)",
        data=bio.getvalue(),
        file_name=f"ore_suplimentare_{int(year)}_{int(month):02d}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        key="dl_ot_excel"
    )



# ============================================================
# CM: Registru + Raport CAS
# ============================================================

CM_FNUASS_FULL_CODES = {"03","04","05","06","07","08","09","10","12","14","15"}

def cm_split_plata(cod_indemnizatie: str, zile: int) -> tuple[int,int]:
    """Returnează (zile_angajator, zile_fnuass) conform regulii uzuale:
    - implicit: primele 5 zile suportate de angajator, restul FNUASS
    - excepții: anumite coduri sunt suportate integral din FNUASS
    """
    try:
        z = int(zile or 0)
    except Exception:
        z = 0
    cod = str(cod_indemnizatie or "").strip().zfill(2)
    if z <= 0:
        return (0, 0)
    if cod in CM_FNUASS_FULL_CODES:
        return (0, z)
    ang = min(5, z)
    return (ang, z - ang)

def _cm_code_label(cod: str) -> str:
    c = str(cod or "").strip().zfill(2)
    info = CM_CODES.get(c) or {}
    lbl = info.get("label") or ""
    return f"{c} - {lbl}".strip(" -")

def _download_excel(df: pd.DataFrame, filename: str, key: str):
    bio = BytesIO()
    with pd.ExcelWriter(bio, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Raport")
    st.download_button(
        "⬇️ Descarcă Excel",
        data=bio.getvalue(),
        file_name=filename,
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        key=key
    )

def page_registru_cm(cfg: dict, conn: sqlite3.Connection, user_ctx: dict):
    st.subheader("🏥 Registru CM")
    st.caption("Registru certificate medicale introduse în sistem. Filtrează pe lună/an și exportă în Excel.")

    today = date.today()
    c1, c2, c3 = st.columns([1,1,2])
    with c1:
        year = st.number_input("An", min_value=2000, max_value=2100, value=int(today.year), step=1, key="cmreg_y")
    with c2:
        month = st.selectbox(
            "Luna",
            options=list(range(1,13)),
            index=int(today.month)-1,
            format_func=lambda m: f"{m:02d} - {MONTH_NAMES_RO.get(int(m), calendar.month_name[int(m)])}",
            key="cmreg_m"
        )
    start = date(int(year), int(month), 1).isoformat()
    end = date(int(year), int(month), calendar.monthrange(int(year), int(month))[1]).isoformat()

    df = pd.read_sql_query(
        """SELECT mc.id AS ID,
                     mc.employee_key AS Marca,
                     MAX(ts.nume) AS Nume,
                     MAX(ts.prenume) AS Prenume,
                     mc.serie AS Serie,
                     mc.numar AS Numar,
                     mc.issued_date AS Data_eliberare,
                     mc.cod_indemnizatie AS Cod,
                     mc.procent AS Procent,
                     mc.diagnostic_code AS Diagnostic,
                     mc.start_date AS Data_inceput,
                     mc.end_date AS Data_sfarsit,
                     mc.days_calendar AS Zile,
                     mc.is_continuation AS Continuare,
                     mc.initial_serie AS Serie_initiala,
                     mc.initial_numar AS Numar_initial,
                     mc.initial_date AS Data_initiala,
                     mc.fara_stagiu AS Fara_stagiu,
                     mc.created_by AS Creat_de,
                     mc.created_at AS Creat_la
              FROM medical_certificates mc
              LEFT JOIN timesheets ts
                     ON ts.employee_key = mc.employee_key
              WHERE mc.start_date BETWEEN ? AND ?
              GROUP BY mc.id
              ORDER BY mc.start_date DESC, mc.id DESC
        """,
        conn,
        params=(start, end)
    )

    # Respectăm scope/rol: filtrăm după angajații vizibili
    df_all = load_employees_cached(conn)
    scopes_df = get_user_scopes(conn, user_ctx.get("username", ""))
    scopes = scopes_df.drop(columns=["id"], errors="ignore").to_dict("records")
    df_vis = apply_scope_filter(df_all, user_ctx.get("role"), scopes, user_ctx.get("employee_key"))

    allowed = set([safe_str(x) for x in df_vis.get("employee_key", []).tolist()]) if not df_vis.empty else set()
    if allowed:
        df = df[df["Marca"].astype(str).isin(allowed)].copy()

    if df.empty:
        st.info("Nu există certificate medicale în perioada selectată.")
        return

    # Coloane derivate
    df["Angajat"] = df["Marca"].astype(str) + " — " + (df["Nume"].fillna("") + " " + df["Prenume"].fillna("")).str.strip()
    df["Cod"] = df["Cod"].astype(str).apply(lambda x: str(x).strip().zfill(2))
    df["Tip indemnizație"] = df["Cod"].apply(_cm_code_label)
    df["Continuare"] = df["Continuare"].fillna(0).astype(int).map({0:"Nu",1:"Da"})
    df["Fara_stagiu"] = df["Fara_stagiu"].fillna(0).astype(int).map({0:"Nu",1:"Da"})

    # Rearanjare pentru afișare
    show_cols = [
        "ID","Angajat","Serie","Numar","Data_eliberare",
        "Tip indemnizație","Diagnostic","Data_inceput","Data_sfarsit","Zile",
        "Continuare","Serie_initiala","Numar_initial","Data_initiala","Fara_stagiu",
        "Creat_de","Creat_la"
    ]
    df_ui = df[[c for c in show_cols if c in df.columns]].copy()
    st.dataframe(df_ui, use_container_width=True, hide_index=True)

    st.divider()
    _download_excel(df_ui, f"registru_cm_{int(year)}_{int(month):02d}.xlsx", key="dl_cmreg_xlsx")

def page_raport_cas_cm(cfg: dict, conn: sqlite3.Connection, user_ctx: dict):
    st.subheader("📄 Raport CAS (CM)")
    st.caption("Raport automat pe certificate medicale pentru decont / centralizare. Include împărțirea zilelor: angajator vs FNUASS.")

    today = date.today()
    c1, c2, c3 = st.columns([1,1,2])
    with c1:
        year = st.number_input("An", min_value=2000, max_value=2100, value=int(today.year), step=1, key="cmcas_y")
    with c2:
        month = st.selectbox(
            "Luna",
            options=list(range(1,13)),
            index=int(today.month)-1,
            format_func=lambda m: f"{m:02d} - {MONTH_NAMES_RO.get(int(m), calendar.month_name[int(m)])}",
            key="cmcas_m"
        )
    start = date(int(year), int(month), 1).isoformat()
    end = date(int(year), int(month), calendar.monthrange(int(year), int(month))[1]).isoformat()

    df = pd.read_sql_query(
        """SELECT mc.employee_key AS Marca,
                     MAX(ts.nume) AS Nume,
                     MAX(ts.prenume) AS Prenume,
                     MAX(ts.cnp) AS CNP,
                     mc.serie AS Serie,
                     mc.numar AS Numar,
                     mc.cod_indemnizatie AS Cod,
                     mc.start_date AS Data_inceput,
                     mc.end_date AS Data_sfarsit,
                     mc.days_calendar AS Zile
              FROM medical_certificates mc
              LEFT JOIN timesheets ts
                     ON ts.employee_key = mc.employee_key
              WHERE mc.start_date BETWEEN ? AND ?
              GROUP BY mc.id
              ORDER BY mc.employee_key, mc.start_date
        """,
        conn,
        params=(start, end)
    )

    # Scope filter
    df_all = load_employees_cached(conn)
    scopes_df = get_user_scopes(conn, user_ctx.get("username", ""))
    scopes = scopes_df.drop(columns=["id"], errors="ignore").to_dict("records")
    df_vis = apply_scope_filter(df_all, user_ctx.get("role"), scopes, user_ctx.get("employee_key"))
    allowed = set([safe_str(x) for x in df_vis.get("employee_key", []).tolist()]) if not df_vis.empty else set()
    if allowed:
        df = df[df["Marca"].astype(str).isin(allowed)].copy()

    if df.empty:
        st.info("Nu există certificate medicale în perioada selectată.")
        return

    df["Cod"] = df["Cod"].astype(str).apply(lambda x: str(x).strip().zfill(2))
    df["Tip indemnizație"] = df["Cod"].apply(_cm_code_label)

    # Split zile
    splits = df.apply(lambda r: cm_split_plata(r.get("Cod"), r.get("Zile")), axis=1, result_type="expand")
    df["Zile_angajator"] = splits[0].astype(int)
    df["Zile_FNUASS"] = splits[1].astype(int)

    df["Angajat"] = df["Marca"].astype(str) + " — " + (df["Nume"].fillna("") + " " + df["Prenume"].fillna("")).str.strip()

    cols = [
        "Marca","Nume","Prenume","CNP",
        "Serie","Numar","Tip indemnizație",
        "Data_inceput","Data_sfarsit","Zile","Zile_angajator","Zile_FNUASS"
    ]
    df_ui = df[[c for c in cols if c in df.columns]].copy()

    st.dataframe(df_ui, use_container_width=True, hide_index=True)

    st.divider()
    # sumar pe angajat
    st.markdown("### Sumar pe angajat")
    df_sum = df_ui.groupby(["Marca","Nume","Prenume","CNP"], dropna=False)[["Zile","Zile_angajator","Zile_FNUASS"]].sum().reset_index()
    st.dataframe(df_sum, use_container_width=True, hide_index=True)
    _download_excel(df_ui, f"raport_cas_cm_{int(year)}_{int(month):02d}.xlsx", key="dl_cmcas_xlsx")


# ============================================================
# PAGES
# ============================================================


def page_admin_utilizatori(conn: sqlite3.Connection, user_ctx: dict):
    role = (user_ctx.get("role") or "user").lower()
    st.subheader("🛡️ Administrare utilizatori")
    if role not in ("admin", "manager"):
        st.warning("Nu ai drepturi pentru administrarea utilizatorilor.")
        return
    render_admin_users(conn)

def page_configurari_pontaj(cfg: dict, conn: sqlite3.Connection, user_ctx: dict):
    role = (user_ctx.get("role") or "user").lower()

    st.subheader("⚙️ Configurari pontaj")
    if role not in ("admin","manager"):
        st.info("Ai acces doar la vizualizare. Doar admin/manager poate modifica setările și utilizatorii.")

    with st.expander("🗄️ Baza de date (DB)", expanded=True):
        cfg["use_db"] = st.checkbox("Foloseste DB", value=bool(cfg.get("use_db", True)), disabled=(role not in ("admin","manager")))
        cfg["db_path"] = st.text_input("Cale DB", value=safe_str(cfg.get("db_path", DEFAULT_CONFIG["db_path"])), disabled=(role not in ("admin","manager")))
        st.caption(f"Config file: {CONFIG_FILE}")

        st.markdown("---")
        st.markdown("**Deschide / schimbă DB (local)**")
        st.caption("Rulezi local: poți încărca un fișier .db/.sqlite; îl salvăm în ./data și îl folosim imediat.")
        up_db = st.file_uploader("Încarcă DB existent", type=["db","sqlite","sqlite3"], disabled=(role not in ("admin","manager")), key="upl_db")
        if role == "admin" and up_db is not None:
            try:
                saved = save_uploaded_db(up_db)
                st.session_state["db_path_override"] = saved
                st.success(f"DB selectat: {saved}")
                st.warning("Te deloghez ca să se redeschidă conexiunea pe noul DB.")
                st.session_state.authenticated = False
                st.session_state.user_ctx = None
                st.rerun()
            except Exception as e:
                st.error(f"Eroare încărcare DB: {e}")

        # setare manuală override (doar local)
        if role == "admin":
            manual = st.text_input("Sau calea către DB (override pentru sesiunea curentă)", value=safe_str(st.session_state.get("db_path_override","")), key="db_override_path")
            cO1, cO2 = st.columns(2)
            with cO1:
                if st.button("Folosește override", key="btn_use_override"):
                    if manual.strip():
                        st.session_state["db_path_override"] = manual.strip()
                        st.session_state.authenticated = False
                        st.session_state.user_ctx = None
                        st.success("Override aplicat. Redeschid conexiunea...")
                        st.rerun()
            with cO2:
                if st.button("Șterge override", key="btn_clear_override"):
                    st.session_state.pop("db_path_override", None)
                    st.session_state.authenticated = False
                    st.session_state.user_ctx = None
                    st.success("Override șters.")
                    st.rerun()

    with st.expander("🏢 Date unitate / institutie", expanded=False):
        cfg["company_name"] = st.text_input("Denumire", value=safe_str(cfg.get("company_name")), disabled=(role not in ("admin","manager")))
        c1, c2 = st.columns(2)
        with c1:
            cfg["company_cui"] = st.text_input("CUI/CIF", value=safe_str(cfg.get("company_cui")), disabled=(role not in ("admin","manager")))
        with c2:
            cfg["company_regcom"] = st.text_input("Reg. Com.", value=safe_str(cfg.get("company_regcom")), disabled=(role not in ("admin","manager")))
        cfg["company_address"] = st.text_input("Adresa", value=safe_str(cfg.get("company_address")), disabled=(role not in ("admin","manager")))
        c3, c4 = st.columns(2)
        with c3:
            cfg["company_phone"] = st.text_input("Telefon", value=safe_str(cfg.get("company_phone")), disabled=(role not in ("admin","manager")))
        with c4:
            cfg["company_email"] = st.text_input("Email", value=safe_str(cfg.get("company_email")), disabled=(role not in ("admin","manager")))

    with st.expander("🖼️ Sigla institutie", expanded=False):
        cfg["logo_path"] = st.text_input("Cale sigla (logo_path)", value=safe_str(cfg.get("logo_path", DEFAULT_CONFIG["logo_path"])), disabled=(role not in ("admin","manager")))
        if os.path.exists(cfg["logo_path"]):
            st.image(cfg["logo_path"], caption="Sigla curenta", width=180)
        else:
            st.info("Nu exista sigla la calea setata.")

        if role == "admin":
            up_logo = st.file_uploader("Browse → incarca sigla (PNG/JPG)", type=["png", "jpg", "jpeg"], key="upl_logo")
            if up_logo is not None:
                try:
                    save_uploaded_file(up_logo, cfg["logo_path"])
                    st.success(f"Sigla salvata in: {cfg['logo_path']}")
                    st.rerun()
                except Exception as e:
                    st.error(f"Eroare salvare sigla: {e}")

    with st.expander("✍️ Semnaturi & Semnare electronica", expanded=False):
        cfg["sign_enabled"] = st.checkbox("Afiseaza bloc semnatura pe documente", value=bool(cfg.get("sign_enabled", False)), disabled=(role not in ("admin","manager")))
        cfg["sign_mode"] = st.selectbox("Mod semnare", ["vizual", "calificat"], index=0 if safe_str(cfg.get("sign_mode","vizual"))=="vizual" else 1, disabled=(role not in ("admin","manager")))
        st.caption(
            "• vizual = semnatura afisata (imagine + nume) – NU este semnatura calificata.\n"
            "• calificat = necesita integrare cu certificat/furnizor; aici pastram doar setarile."
        )

        cfg["e_sign_provider"] = st.text_input("Furnizor (optional)", value=safe_str(cfg.get("e_sign_provider")), disabled=(role not in ("admin","manager")))
        cfg["e_sign_endpoint"] = st.text_input("Endpoint/API URL (optional)", value=safe_str(cfg.get("e_sign_endpoint")), disabled=(role not in ("admin","manager")))
        cfg["e_sign_api_key"] = st.text_input("API Key (optional)", value=safe_str(cfg.get("e_sign_api_key")), type="password", disabled=(role not in ("admin","manager")))

        if role == "admin":
            st.markdown("---")
            render_signatures(conn)
        else:
            st.info("Doar admin poate gestiona semnaturile (adauga/modifica/sterge).")

    with st.expander("⏱ Ore implicite", expanded=True):
        ds = _parse_hhmm_to_time(cfg.get("default_start"), time(8,0))
        de = _parse_hhmm_to_time(cfg.get("default_end"), time(16,0))
        c1, c2, c3 = st.columns(3)
        with c1:
            cfg["default_start"] = _time_to_hhmm(st.time_input("Ora sosire", value=ds, disabled=(role not in ("admin","manager"))))
        with c2:
            cfg["default_end"] = _time_to_hhmm(st.time_input("Ora plecare", value=de, disabled=(role not in ("admin","manager"))))
        with c3:
            cfg["standard_daily_hours"] = float(st.number_input(
                "Norma (ore/zi)",
                min_value=1.0, max_value=24.0,
                value=float(cfg.get("standard_daily_hours", 8.0)),
                step=0.5,
                disabled=(role not in ("admin","manager"))
            ))

    with st.expander("🔧 Optiuni", expanded=False):
        cfg["allow_cross_day_shift"] = st.checkbox(
            "Permite tura peste miezul noptii (ex: 22:00–06:00)",
            value=bool(cfg.get("allow_cross_day_shift", True)),
            disabled=(role not in ("admin","manager"))
        )


    with st.expander("🎉 Weekend & sărbători legale (auto)", expanded=False):
        st.caption("Completează automat în pontaj: **Sam./D** pentru sâmbătă/duminică și **Sarb.** pentru sărbători legale, doar pe celulele goale.")
        cfg["auto_mark_weekends"] = st.checkbox(
            "Marchează automat sâmbătă/duminică",
            value=bool(cfg.get("auto_mark_weekends", True)),
            disabled=(role not in ("admin","manager"))
        )
        cfg["auto_mark_legal_holidays"] = st.checkbox(
            "Marchează automat sărbători legale",
            value=bool(cfg.get("auto_mark_legal_holidays", True)),
            disabled=(role not in ("admin","manager"))
        )

        # editor listă sărbători (ISO YYYY-MM-DD), una pe linie
        cur_list = cfg.get("legal_holidays", [])
        if not isinstance(cur_list, list):
            cur_list = []
        cur_list = [str(x).strip() for x in cur_list if str(x).strip()]
        cur_text = "\n".join(cur_list)

        txt = st.text_area(
            "Listă sărbători legale (YYYY-MM-DD) — una pe linie",
            value=cur_text,
            height=160,
            disabled=(role not in ("admin","manager")),
            key="cfg_legal_holidays_text"
        )

        # parse + validate
        lines = [l.strip() for l in (txt or "").splitlines() if l.strip()]
        parsed = []
        bad = []
        for l in lines:
            try:
                d = date.fromisoformat(l)
                parsed.append(d.isoformat())
            except Exception:
                bad.append(l)

        # normalize: unique + sort
        parsed = sorted(set(parsed))
        cfg["legal_holidays"] = parsed

        if bad:
            st.warning("Linii invalide (corectează formatul YYYY-MM-DD): " + ", ".join(bad))
        st.info(f"Total sărbători setate: **{len(parsed)}**")
    if role == "admin":
        st.markdown("---")
        cA, cB = st.columns(2)
        with cA:
            if st.button("💾 Salveaza configurarea"):
                save_config(cfg)
                st.success("Configurare salvata.")
                st.rerun()
        with cB:
            if st.button("↩ Reset configurare"):
                save_config(dict(DEFAULT_CONFIG))
                st.warning("Reset efectuat.")
                st.rerun()

        st.markdown("---")
        with st.expander("🔎 Explorer DB", expanded=False):
            db_browser_ui(conn)

def page_pontaj(cfg: dict, conn: sqlite3.Connection, user_ctx: dict):
    st.subheader("🗓️ Pontaj")

    df_all, src = read_employees(conn)
    scopes_df = get_user_scopes(conn, user_ctx["username"])
    scopes = scopes_df.drop(columns=["id"], errors="ignore").to_dict("records")
    df = apply_scope_filter(df_all, user_ctx.get("role"), scopes, user_ctx.get("employee_key"))

    if df.empty:
        st.warning(
            "Nu exista angajati vizibili pentru acest utilizator.\n\n"
            "• admin: verifica tabela employees / employees_cache\n"
            "• user: seteaza employee_key in pontaj_users\n"
            "• manager: adauga cel putin un scope"
        )
        return

    st.caption(f"Sursa angajati: **{src}** | User: **{user_ctx['username']}** | Rol: **{user_ctx.get('role','')}**")

    # select angajat (auto pentru user conectat + memorie sesiune)
    username = safe_str(user_ctx.get("username", "")).strip()
    role_l = safe_str(user_ctx.get("role", "user")).strip().lower()
    pref_emp_key_ss = safe_str(st.session_state.get(f"pontaj_pref_emp_{username}", "")).strip() if username else ""
    preferred_employee_key = safe_str(user_ctx.get("employee_key", "")).strip() or pref_emp_key_ss

    # fallback: dacă username coincide cu employee_key, preluăm direct
    if not preferred_employee_key and username:
        _m = df[df["employee_key"].astype(str).str.lower() == username.lower()]
        if len(_m) == 1:
            preferred_employee_key = safe_str(_m.iloc[0]["employee_key"]).strip()

    auto_emp_row = None
    if preferred_employee_key:
        _auto = df[df["employee_key"].astype(str) == preferred_employee_key]
        if not _auto.empty:
            auto_emp_row = _auto.iloc[0]

    if auto_emp_row is not None:
        emp = auto_emp_row
        employee_key = safe_str(emp["employee_key"])
    elif user_ctx.get("employee_key"):
        emp = df.iloc[0]
        employee_key = emp["employee_key"]
    else:
        colF1, colF2, colF3, colF4 = st.columns(4)

        loc_options = ["(Toate)"] + sorted([x for x in df["Locatie"].unique().tolist() if safe_str(x)])
        with colF1:
            sel_loc = st.selectbox("Locatie", loc_options, index=0)
        df1 = df if sel_loc == "(Toate)" else df[df["Locatie"] == sel_loc]

        dir_options = ["(Toate)"] + sorted([x for x in df1["Directie"].unique().tolist() if safe_str(x)])
        with colF2:
            sel_dir = st.selectbox("Directie", dir_options, index=0)
        df2 = df1 if sel_dir == "(Toate)" else df1[df1["Directie"] == sel_dir]

        dep_options = ["(Toate)"] + sorted([x for x in df2["Departament"].unique().tolist() if safe_str(x)])
        with colF3:
            sel_dep = st.selectbox("Departament/Serviciu", dep_options, index=0)
        df3 = df2 if sel_dep == "(Toate)" else df2[df2["Departament"] == sel_dep]

        bir_options = ["(Toate)"] + sorted([x for x in df3["Birou"].unique().tolist() if safe_str(x)])
        with colF4:
            sel_bir = st.selectbox("Birou", bir_options, index=0)
        df4 = df3 if sel_bir == "(Toate)" else df3[df3["Birou"] == sel_bir]

        st.markdown("---")
        emp_options = df4.index.tolist()
        emp_idx = st.selectbox(
            "Angajat",
            emp_options,
            format_func=lambda i: f"{df4.loc[i,'employee_key']} - {df4.loc[i,'FullName']}  [{df4.loc[i,'Departament']} / {df4.loc[i,'Birou']}]"
        )
        emp = df4.loc[emp_idx]
        employee_key = emp["employee_key"]

    if username and employee_key:
        st.session_state[f"pontaj_pref_emp_{username}"] = safe_str(employee_key)

    snapshot = {
        "Nume": safe_str(emp.get("Nume","")),
        "Prenume": safe_str(emp.get("Prenume","")),
        "CNP": safe_str(emp.get("CNP","")),
        "Locatie": safe_str(emp.get("Locatie","")),
        "Directie": safe_str(emp.get("Directie","")),
        "Departament": safe_str(emp.get("Departament","")),
        "Birou": safe_str(emp.get("Birou","")),
    }

    st.markdown("### 👤 Date angajat (importate)")
    a1, a2, a3, a4 = st.columns(4)
    with a1:
        st.text_input("Nume", value=snapshot["Nume"], disabled=True)
    with a2:
        st.text_input("Prenume", value=snapshot["Prenume"], disabled=True)
    with a3:
        st.text_input("CNP", value=snapshot["CNP"], disabled=True)
    with a4:
        st.text_input("Marca/Key", value=safe_str(employee_key), disabled=True)

    b1, b2, b3, b4 = st.columns(4)
    with b1:
        st.text_input("Locatie", value=snapshot["Locatie"], disabled=True)
    with b2:
        st.text_input("Directie", value=snapshot["Directie"], disabled=True)
    with b3:
        st.text_input("Departament/Serviciu", value=snapshot["Departament"], disabled=True)
    with b4:
        st.text_input("Birou", value=snapshot["Birou"], disabled=True)

    st.markdown("---")
    st.subheader("📱 Pontaj rapid")

    # Prima deschidere din zi: popup pontaj intrare (doar pentru utilizatori non-admin)
    today_local = date.today()
    popup_key = f"pontaj_daily_popup_done_{username}_{today_local.isoformat()}"
    show_popup = False
    if username and role_l not in ("admin", "manager"):
        if not st.session_state.get(popup_key, False):
            try:
                cur = conn.cursor()
                cur.execute(
                    "SELECT start_time FROM timesheets WHERE employee_key=? AND work_date=? LIMIT 1",
                    (safe_str(employee_key), today_local.isoformat()),
                )
                r = cur.fetchone()
                already_in = bool(r and safe_str(r[0]).strip())
            except Exception:
                already_in = False
            show_popup = not already_in

    if show_popup:
        @st.dialog("PONTAJ")
        def _pontaj_daily_dialog():
            st.write("Prima deschidere din zi. Înregistrezi acum ora de intrare?")
            c1, c2 = st.columns(2)
            with c1:
                if st.button("🟢 Pontaj intrare acum", use_container_width=True, key=f"pontaj_daily_in_{employee_key}_{today_local.isoformat()}"):
                    set_punch(conn, employee_key, today_local, "IN")
                    st.session_state[popup_key] = True
                    st.rerun()
            with c2:
                if st.button("Închide", use_container_width=True, key=f"pontaj_daily_close_{employee_key}_{today_local.isoformat()}"):
                    st.session_state[popup_key] = True
                    st.rerun()

        _pontaj_daily_dialog()

    cA, cB = st.columns(2)
    with cA:
        if st.button("🟢 Pontaj INTRARE", use_container_width=True):
            set_punch(conn, employee_key, today_local, "IN")
            st.rerun()
    with cB:
        if st.button("🔴 Pontaj IEȘIRE", use_container_width=True):
            set_punch(conn, employee_key, today_local, "OUT")
            st.rerun()

    st.markdown("---")
    st.subheader("🧾 Pontaj manual pe luna selectata")

    today = date.today()
    year = st.number_input("An", min_value=2000, max_value=2100, value=today.year, step=1)
    month = st.selectbox(
        "Luna",
        options=list(range(1, 13)),
        index=today.month - 1,
        format_func=lambda m: f"{m:02d} - {MONTH_NAMES_RO.get(int(m), str(m))}"
    )


    # ------------------------------------------------------------
    # FIX IMPORTANT: chei stabile pe "pagina" (angajat + an + luna)
    # Evita NotFoundError: removeChild (DOM mismatch la rerun).
    # ------------------------------------------------------------
    page_uid = f"{safe_str(employee_key)}_{int(year)}_{int(month)}"

    # Render guard: cand se schimba page_uid, facem rerun curat o singura data.
    if st.session_state.get("pontaj_page_uid") != page_uid:
        st.session_state["pontaj_page_uid"] = page_uid
        st.rerun()

    default_start = _parse_hhmm_to_time(cfg.get("default_start"), time(8,0))
    default_end = _parse_hhmm_to_time(cfg.get("default_end"), time(16,0))
    standard_daily_hours = float(cfg.get("standard_daily_hours", 8.0))
    allow_cross_day = bool(cfg.get("allow_cross_day_shift", True))

    num_days = calendar.monthrange(int(year), int(month))[1]
    dates_list = [date(int(year), int(month), d) for d in range(1, num_days + 1)]

    status_options = [
        "Lucrat",
        "CO - Concediu de odihna",
        "CM - Concediu medical",
        "CFP - Fara plata",
        "Nemotivat",
        "Liber (weekend / sarbatoare)"
    ]

    rows = []
    totals = {k: 0.0 for k in ["total_hours","normal_hours","night_hours","weekend_hours","holiday_hours","overtime_hours"]}
    days = {k: 0 for k in ["co","cm","cfp","nem","liber"]}

    for d in dates_list:
        weekday = d.weekday()
        weekday_name = ["Luni", "Marti", "Miercuri", "Joi", "Vineri", "Sambata", "Duminica"][weekday]
        is_weekend = weekday >= 5
        is_holiday = False

        with st.container():
            col_date, col_status, col_start, col_end, col_hours = st.columns([1.8, 2.8, 1.5, 1.5, 3.0])

            with col_date:
                st.markdown(f"**{d.strftime('%d.%m.%Y')}**")
                st.caption(weekday_name + (" (Weekend)" if is_weekend else ""))

            default_status_index = status_options.index("Liber (weekend / sarbatoare)" if is_weekend else "Lucrat")
            with col_status:
                status = st.selectbox(
                    "Status",
                    options=status_options,
                    index=default_status_index,
                    key=f"status_{page_uid}_{d.isoformat()}"
                )

            start_t = None
            end_t = None
            seg = {k: 0.0 for k in totals.keys()}
            co = cm = cfp = nem = liber = 0

            if status == "Lucrat":
                with col_start:
                    start_t = st.time_input("Sosire", key=f"start_{page_uid}_{d.isoformat()}", value=default_start)
                with col_end:
                    end_t = st.time_input("Plecare", key=f"end_{page_uid}_{d.isoformat()}", value=default_end)

                seg = calculate_hours_segments(
                    d, start_t, end_t,
                    standard_daily_hours,
                    is_weekend=is_weekend,
                    is_holiday=is_holiday,
                    allow_cross_day=allow_cross_day
                )
                with col_hours:
                    st.markdown(f"**{seg['total_hours']}h** | Noapte: {seg['night_hours']} | Supl.: {seg['overtime_hours']}")
            else:
                with col_start:
                    st.text("-")
                with col_end:
                    st.text("-")
                with col_hours:
                    st.markdown("0h")

                if status.startswith("CO"):
                    co = 1
                elif status.startswith("CM"):
                    cm = 1
                elif status.startswith("CFP"):
                    cfp = 1
                elif status.startswith("Nemotivat"):
                    nem = 1
                else:
                    liber = 1

            for k in totals.keys():
                totals[k] += float(seg[k])

            days["co"] += co
            days["cm"] += cm
            days["cfp"] += cfp
            days["nem"] += nem
            days["liber"] += liber

            rows.append({
                "Data": d.strftime("%d.%m.%Y"),
                "Zi": weekday_name,
                "Status": status,
                "Ora sosire": start_t.strftime("%H:%M") if start_t else "",
                "Ora plecare": end_t.strftime("%H:%M") if end_t else "",
                "Ore totale": seg["total_hours"],
                "Ore normale": seg["normal_hours"],
                "Ore noapte": seg["night_hours"],
                "Ore weekend": seg["weekend_hours"],
                "Ore sarbatoare": seg["holiday_hours"],
                "Ore suplimentare": seg["overtime_hours"],
                "CO (zile)": co,
                "CM (zile)": cm,
                "Fara plata (zile)": cfp,
                "Nemotivat (zile)": nem,
                "Liber (zile)": liber,
            })

    df_manual = pd.DataFrame(rows)
    st.markdown("---")
    st.dataframe(df_manual, use_container_width=True)

    st.write(
        f"Total ore: {totals['total_hours']} | Normale: {totals['normal_hours']} | "
        f"Noapte: {totals['night_hours']} | Supl.: {totals['overtime_hours']}"
    )
    st.write(f"Zile: CO {days['co']} | CM {days['cm']} | CFP {days['cfp']} | Nemotivat {days['nem']} | Liber {days['liber']}")

    if st.button("💾 Salveaza luna in DB"):
        save_timesheet_rows(conn, employee_key, df_manual, snapshot)
        st.success("Luna salvata in DB (cu nume/structura).")


def page_cereri_concedii(cfg: dict, conn: sqlite3.Connection, user_ctx: dict):
    st.subheader("📝 Cereri")

    # ------------------------------------------------------------
    # Admin/Manager: configurare tipuri de cereri (persistente)
    # ------------------------------------------------------------
    role = (user_ctx.get("role") or "user").lower()
    if role in ("admin", "manager"):
        with st.expander("⚙️ Gestionare tipuri de cereri", expanded=False):
            st.caption("Adaugă tipuri noi de cereri. Acestea rămân salvate și pot fi selectate ulterior.")
            c1, c2, c3 = st.columns([1,3,1])
            with c1:
                new_code = st.text_input("Cod", value="", placeholder="ex: EV", key="rt_new_code")
            with c2:
                new_label = st.text_input("Denumire", value="", placeholder="ex: Eveniment", key="rt_new_label")
            with c3:
                active = st.checkbox("Activ", value=True, key="rt_new_active")
            if st.button("➕ Salvează tip", key="rt_save_btn"):
                try:
                    upsert_request_type(conn, new_code, new_label, is_active=active)
                    st.success("Tip salvat.")
                    st.rerun()
                except Exception as e:
                    st.error(f"Eroare: {e}")

            st.markdown("#### Tipuri existente")
            rts = list_request_types(conn, active_only=False)
            if rts:
                import pandas as pd
                df_rt = pd.DataFrame(rts, columns=["code","label"])
                st.dataframe(df_rt, use_container_width=True)

                st.markdown("#### ⚙️ Configurare comportament (aplicare în pontaj)")
                st.caption("Editează regulile după care un tip APPROVED se aplică în pontaj. Modificările se salvează în DB.")

                df_full = list_request_types_full(conn)
                # ascundem coloanele tehnice de timp
                show_cols = ["code","label","is_active","apply_mode","ts_status","weekdays_only_default", "co_day","cm_day","cfp_day","nemotivat_day","liber_day","telemunca_day","samd_day"]
                df_edit = df_full[show_cols].copy()

                edited_cfg = st.data_editor(
                    df_edit,
                    use_container_width=True,
                    num_rows="fixed",
                    column_config={
                        "code": st.column_config.TextColumn("Cod", disabled=True),
                        "label": st.column_config.TextColumn("Denumire"),
                        "is_active": st.column_config.CheckboxColumn("Activ"),
                        "apply_mode": st.column_config.SelectboxColumn("Aplicare", options=["ABSENCE","WORK","MARK_ONLY"]),
                        "ts_status": st.column_config.TextColumn("Status în pontaj"),
                        "weekdays_only_default": st.column_config.SelectboxColumn("Doar L-V", options=[0,1]),
                        "co_day": st.column_config.NumberColumn("CO", min_value=0, max_value=1, step=1),
                        "cm_day": st.column_config.NumberColumn("CM", min_value=0, max_value=1, step=1),
                        "cfp_day": st.column_config.NumberColumn("CFP", min_value=0, max_value=1, step=1),
                        "nemotivat_day": st.column_config.NumberColumn("Nemot.", min_value=0, max_value=1, step=1),
                        "liber_day": st.column_config.NumberColumn("Liber", min_value=0, max_value=1, step=1),
                        "telemunca_day": st.column_config.NumberColumn("Telem.", min_value=0, max_value=1, step=1),
                        "samd_day": st.column_config.NumberColumn("Sam./D", min_value=0, max_value=1, step=1),
                    },
                    key="rt_behavior_editor"
                )

                if st.button("💾 Salvează configurarea tipurilor", key="rt_behavior_save"):
                    try:
                        # upsert each row
                        for _, row in edited_cfg.iterrows():
                            flags = {
                                "co_day": int(row.get("co_day", 0) or 0),
                                "cm_day": int(row.get("cm_day", 0) or 0),
                                "cfp_day": int(row.get("cfp_day", 0) or 0),
                                "nemotivat_day": int(row.get("nemotivat_day", 0) or 0),
                                "liber_day": int(row.get("liber_day", 0) or 0),
                                "telemunca_day": int(row.get("telemunca_day", 0) or 0),
                                "samd_day": int(row.get("samd_day", 0) or 0),
                            }
                            upsert_request_type_behavior(
                                conn,
                                code=str(row["code"]),
                                label=str(row["label"]),
                                is_active=bool(row.get("is_active", True)),
                                apply_mode=str(row.get("apply_mode","ABSENCE")),
                                ts_status=str(row.get("ts_status","") or ""),
                                weekdays_only_default=int(row.get("weekdays_only_default", 1) or 0),
                                flags=flags
                            )
                        st.success("Configurare salvată.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Eroare la salvare: {e}")
                del_code = st.selectbox("Dezactivează tip (cod)", options=[""] + [c for c,_ in rts], key="rt_del_code")
                if del_code and st.button("Dezactivează", key="rt_del_btn"):
                    deactivate_request_type(conn, del_code)
                    st.success("Tip dezactivat.")
                    st.rerun()
            else:
                st.info("Nu există tipuri.")
    role = (user_ctx.get("role") or "user").lower()

    df_all, _ = read_employees(conn)
    scopes_df = get_user_scopes(conn, user_ctx["username"])
    scopes = scopes_df.drop(columns=["id"], errors="ignore").to_dict("records")
    df_emp = apply_scope_filter(df_all, user_ctx.get("role"), scopes, user_ctx.get("employee_key"))

    tabs = ["Depune cerere", "Istoric"]
    if role in ("admin","manager"):
        tabs.append("Aprobări")
        tabs.append("🏥 Registru CM")
        tabs.append("📄 Raport CAS (CM)")
    # Sold CO (ultimii 3 ani) – disponibil pentru toți utilizatorii
    tabs.append("🏖️ Sold CO")
    t = st.tabs(tabs)
    idx_sold = len(tabs) - 1
    

    # ---------------------------
    # Depune cerere
    # ---------------------------
    with t[0]:
        if df_emp.empty:
            st.warning("Nu există angajați vizibili pentru acest utilizator.")
            return

        if user_ctx.get("employee_key"):
            employee_key = str(user_ctx["employee_key"])
            row = df_emp[df_emp["employee_key"] == employee_key]
            label = f"{employee_key} — {row.iloc[0].get('FullName','')}" if not row.empty else employee_key
            st.info(f"Cerere pentru angajat: **{label}** (fixat pe user)")
        else:
            emp_options = df_emp["employee_key"].tolist()
            emp_labels = [f"{r['employee_key']} — {r.get('FullName','')}" for _, r in df_emp.iterrows()]
            sel = st.selectbox("Alege angajat", options=list(range(len(emp_options))), format_func=lambda i: emp_labels[i])
            employee_key = str(emp_options[sel])

        rt_list = list_request_types(conn, active_only=True)
        rt_labels = [f"{lbl} ({code})" for code, lbl in rt_list]
        rt_map = {f"{lbl} ({code})": code for code, lbl in rt_list}
        rt_choice = st.selectbox("Tip cerere", options=rt_labels)
        tip = rt_map.get(rt_choice, "")
        req_type = tip  # folosit mai jos (ex: CM)

                # ------------------------------------------------------------
        # Date cerere / CM
        # ------------------------------------------------------------
        cm_fields = {}
        if req_type == "CM":
            st.markdown("### 🏥 Certificat medical (CM)")

            c1, c2 = st.columns(2)
            with c1:
                cm_fields["cm_series"] = st.text_input("Serie certificat", value="", placeholder="ex: CM", key="cm_series")
            with c2:
                cm_fields["cm_number"] = st.text_input("Număr certificat", value="", placeholder="ex: 123456", key="cm_number")

            c3, c4 = st.columns(2)
            with c3:
                cm_issued = st.date_input("Data eliberării (opțional)", value=date.today(), key="cm_issued")
                cm_place = st.selectbox("Locul de prescriere (opțional)", options=list(CM_PRESCRIPTION_PLACES.keys()), format_func=lambda k: CM_PRESCRIPTION_PLACES.get(k,k), key="cm_place")
            with c4:
                cod = st.selectbox("Cod indemnizație", options=list(CM_CODES.keys()),
                                   format_func=lambda x: cm_code_label(x), key="cm_code")
            diag = st.text_input("Cod diagnostic (opțional)", value="", placeholder="ex: 503", key="cm_diag_code")

            c5, c6 = st.columns(2)
            with c5:
                start_dt = st.date_input("Concediu medical începe la data", value=date.today(), key="cm_start")
            with c6:
                end_dt = st.date_input("Concediu medical până la data", value=date.today(), key="cm_end")

            if end_dt < start_dt:
                st.error("Data de sfârșit nu poate fi înainte de data de început.")
                days_calendar = 0
            else:
                days_calendar = int((end_dt - start_dt).days + 1)

            st.info(f"📌 Perioadă CM: **{start_dt.isoformat()} → {end_dt.isoformat()}** (zile calendaristice: **{int(days_calendar)}**)")
            weekdays_only = False
            req_days = int(days_calendar)
            hours_per_day = 0.0  # CM

            c7, c8 = st.columns(2)
            with c7:
                is_cont = st.checkbox('Certificatul medical este "în continuare"', value=False, key="cm_cont")
            with c8:
                fara_stagiu = st.checkbox("Fără stagiu de cotizare", value=False, key="cm_fara_stagiu")

            if is_cont:
                st.markdown("#### Seria și numărul certificatului medical inițial")
                d1, d2, d3 = st.columns(3)
                with d1:
                    initial_serie = st.text_input("Serie certificat inițial", value="", key="cm_init_series")
                with d2:
                    initial_numar = st.text_input("Număr certificat inițial", value="", key="cm_init_number")
                with d3:
                    initial_date = st.date_input("Data certificatului inițial (opțional)", value=start_dt, key="cm_init_date")
            else:
                initial_serie = ""
                initial_numar = ""
                initial_date = None

            notes = st.text_area("Observații (opțional)", value="", key="cm_notes")

            cm_fields["cm_type"] = str(cod)
            cm_fields["cm_diag"] = safe_str(diag)
            cm_fields["cm_issuer"] = ""
            cm_fields["_prescription_place"] = safe_str(cm_place)
            cm_fields["_issued_date"] = cm_issued
            cm_fields["_cod_indemnizatie"] = str(cod)
            cm_fields["_procent"] = int(CM_CODES.get(str(cod), {}).get("procent") or 0) or None
            cm_fields["_diagnostic_code"] = safe_str(diag)
            cm_fields["_days_calendar"] = int(days_calendar)
            cm_fields["_is_continuation"] = 1 if is_cont else 0
            cm_fields["_initial_serie"] = safe_str(initial_serie)
            cm_fields["_initial_numar"] = safe_str(initial_numar)
            cm_fields["_initial_date"] = initial_date

            # Previzualizare: zile plătite din fond salarii vs FNUASS (pe baza codului + istoric)
            if int(cm_fields.get("_days_calendar", 0) or 0) > 0:
                try:
                    pe, pf = compute_cm_payment_split(
                        conn,
                        str(employee_key),
                        str(cm_fields.get("_cod_indemnizatie","")),
                        safe_str(cm_fields.get("cm_series","")),
                        safe_str(cm_fields.get("cm_number","")),
                        start_dt,
                        end_dt,
                        bool(int(cm_fields.get("_is_continuation",0) or 0)),
                        safe_str(cm_fields.get("_initial_serie","")),
                        safe_str(cm_fields.get("_initial_numar","")),
                    )
                except Exception:
                    pe, pf = (None, None)

                if pe is not None and pf is not None:
                    st.success(f"💰 Calcul automat: **Fond salarii: {int(pe)} zile** | **FNUASS: {int(pf)} zile**")
                    cm_fields["_pay_employer_days"] = int(pe)
                    cm_fields["_pay_fnuass_days"] = int(pf)
            cm_fields["_fara_stagiu"] = 1 if fara_stagiu else 0

        else:
            start_dt = st.date_input("Data început", value=date.today())
            end_dt = st.date_input("Data sfârșit", value=date.today())

            try:
                beh = get_request_type_behavior(conn, req_type)
                default_weekdays = bool(int(beh.get("weekdays_only_default", 1) or 0))
            except Exception:
                default_weekdays = True

            weekdays_only = st.checkbox("Aplică doar luni–vineri", value=default_weekdays)
            req_days = compute_requested_days(start_dt, end_dt, weekdays_only)
            st.info(f"📌 Zile calculate pentru cerere: **{req_days}**")

            hours_per_day = 0.0
            notes = st.text_area("Observații (opțional)", value="")

        approve_now = False
        if role in ("admin","manager"):
            approve_now = st.checkbox("Aprobă imediat (admin/manager)", value=False)

        if st.button("Trimite cererea", type="primary"):
            try:
                if end_dt < start_dt:
                    st.error("Data sfârșit trebuie să fie >= data început.")
                else:

                    # Validare sold CO (ultimii 3 ani) + blocare dacă depășește
                    if req_type == "CO":
                        y = int(start_dt.year)
                        bal = compute_co_balance_3y(conn, str(employee_key), y)
                        remaining_total = float(bal.get("total_remaining", 0) or 0)
                        if req_days <= 0:
                            raise ValueError("Interval invalid. Verifică Data început / Data sfârșit.")
                        if req_days > remaining_total:
                            raise ValueError(f"Cererea depășește soldul disponibil. Zile rămase (3 ani): {remaining_total:.0f}, cerere: {req_days}.")

                    
                    rid = create_leave_request(
                        conn=conn,
                        employee_key=employee_key,
                        request_type=req_type,
                        start_dt=start_dt,
                        end_dt=end_dt,
                        created_by=user_ctx["username"],
                        notes=notes,
                        weekdays_only=weekdays_only,
                        hours_per_day=hours_per_day,
                        cm_fields=cm_fields
                    )

                    # Dacă este CM, salvăm și certificatul medical (registru)
                    if req_type == "CM":
                        try:
                            create_medical_certificate(
                                conn=conn,
                                employee_key=str(employee_key),
                                serie=cm_fields.get("cm_series",""),
                                numar=cm_fields.get("cm_number",""),
                                issued_date=cm_fields.get("_issued_date"),
                                prescription_place=cm_fields.get("_prescription_place") or None,
                                cod_indemnizatie=cm_fields.get("_cod_indemnizatie",""),
                                procent=cm_fields.get("_procent"),
                                diagnostic_code=cm_fields.get("_diagnostic_code",""),
                                start_dt=start_dt,
                                days_calendar=int(cm_fields.get("_days_calendar", req_days) or req_days),
                                end_dt=end_dt,
                                is_continuation=bool(int(cm_fields.get("_is_continuation",0) or 0)),
                                initial_serie=cm_fields.get("_initial_serie",""),
                                initial_numar=cm_fields.get("_initial_numar",""),
                                initial_date=cm_fields.get("_initial_date"),
                                fara_stagiu=bool(int(cm_fields.get("_fara_stagiu",0) or 0)),
                                notes=notes or "",
                                created_by=user_ctx["username"],
                                leave_request_id=int(rid),
                                pay_employer_days=cm_fields.get("_pay_employer_days"),
                                pay_fnuass_days=cm_fields.get("_pay_fnuass_days"),
                            )
                        except Exception as _e_cm:
                            # dacă certificatul nu se poate salva, anulăm cererea ca să nu rămână "orphan"
                            try:
                                conn.execute("DELETE FROM leave_requests WHERE id=?", (int(rid),))
                                conn.commit()
                            except Exception:
                                pass
                            raise

                    if approve_now:

                        decide_leave_request(conn, rid, "APPROVE", user_ctx["username"], reason="Aprobat direct la creare.")
                        st.success(f"Cererea #{rid} a fost creată și aprobată. Zilele au fost completate în pontaj.")
                    else:
                        st.success(f"Cererea #{rid} a fost creată (PENDING).")
                    st.rerun()
            except Exception as e:
                st.error(f"Eroare: {e}")

    # ---------------------------
    # Istoric (pentru angajații vizibili)
    # ---------------------------
    with t[1]:
        if df_emp.empty:
            st.info("Nu există angajați.")
        else:
            keys = [str(x) for x in df_emp["employee_key"].tolist()]
            df_req = list_leave_requests(conn, employee_keys=keys, status=None)
            if df_req.empty:
                st.info("Nu există cereri.")
            else:
                # tabel rapid
                show = df_req.copy()
                # normalizează coloanele date pentru afișare
                if "start_date" not in show.columns and "date_start" in show.columns:
                    show["start_date"] = show["date_start"]
                if "end_date" not in show.columns and "date_end" in show.columns:
                    show["end_date"] = show["date_end"]

                # adaugă nume/prenume în listă (din df_emp)
                try:
                    _emp_map = df_emp.copy()
                    _emp_map["employee_key"] = _emp_map["employee_key"].astype(str)
                    show["employee_key"] = show["employee_key"].astype(str)
                    show = show.merge(
                        _emp_map[["employee_key","Nume","Prenume"]],
                        on="employee_key",
                        how="left"
                    )
                except Exception:
                    # dacă nu putem, nu blocăm afișarea
                    pass

                cols_show = [c for c in ["id","employee_key","Nume","Prenume","request_type","start_date","end_date","status","notes","created_by","created_at"] if c in show.columns]
                show2 = show.copy()
                if 'status' in show2.columns:
                    show2['status'] = show2['status'].astype(str).str.upper().map(STATUS_RO_MAP).fillna(show2['status'])

                # afișare în limba română (titluri coloane)
                col_rename = {
                    "id": "ID",
                    "employee_key": "Marca",
                    "request_type": "Tip cerere",
                    "start_date": "Data început",
                    "end_date": "Data sfârșit",
                    "status": "Stare",
                    "notes": "Observații",
                    "created_by": "Creat de",
                    "created_at": "Creat la",
                }
                st.dataframe(show2[cols_show].rename(columns=col_rename), use_container_width=True, hide_index=True)

                st.divider()
                st.markdown("### ✏️ Modifică / 🗑️ Șterge cerere")

                ids = show["id"].astype(int).tolist()
                sel_id = st.selectbox("Selectează cererea (ID)", options=ids, key="hist_sel_id")

                rr = get_leave_request_by_id(conn, int(sel_id))
                if rr:
                    # date curente
                    cur_start = rr.get("start_date") or rr.get("date_start") or ""
                    cur_end = rr.get("end_date") or rr.get("date_end") or ""
                    cur_type = rr.get("request_type","")
                    cur_notes = rr.get("notes","")
                    cur_wk = bool(int(rr.get("weekdays_only",1) or 0))
                    cur_status = str(rr.get("status","PENDING")).upper()

                    rt_list = list_request_types(conn, active_only=True)
                    rt_labels = [f"{lbl} ({code})" for code, lbl in rt_list]
                    rt_map = {f"{lbl} ({code})": code for code, lbl in rt_list}
                    # preselect
                    pre = 0
                    for idx, lab in enumerate(rt_labels):
                        if lab.endswith(f"({cur_type})"):
                            pre = idx
                            break

                    new_rt_choice = st.selectbox("Tip cerere", options=rt_labels, index=pre, key="hist_rt_choice")
                    new_type = rt_map.get(new_rt_choice, cur_type)

                    from datetime import date as _date
                    def _to_date(x):
                        try:
                            return _date.fromisoformat(str(x))
                        except Exception:
                            return _date.today()

                    new_start = st.date_input("Data început", value=_to_date(cur_start), key="hist_start")
                    new_end = st.date_input("Data sfârșit", value=_to_date(cur_end), key="hist_end")
                    new_wk = st.checkbox("Aplică doar luni–vineri", value=cur_wk, key="hist_wk")
                    new_notes = st.text_area("Observații", value=str(cur_notes or ""), key="hist_notes")

                    cA, cB = st.columns([1,1])
                    with cA:
                        if st.button("💾 Modifică cererea", key="hist_update_btn"):
                            try:
                                if new_end < new_start:
                                    st.error("Data sfârșit trebuie să fie >= data început.")
                                else:
                                    # dacă era aprobată -> rollback înainte
                                    if cur_status == "APPROVED":
                                        rollback_leave_request_from_timesheets(conn, rr)

                                    update_leave_request_by_id(
                                        conn,
                                        int(sel_id),
                                        request_type=new_type,
                                        start_date=new_start.isoformat(),
                                        end_date=new_end.isoformat(),
                                        weekdays_only=1 if new_wk else 0,
                                        notes=new_notes,
                                        updated_at=datetime.now().isoformat(timespec="seconds")
                                    )

                                    rr2 = get_leave_request_by_id(conn, int(sel_id))
                                    # dacă rămâne aprobată -> reaplică
                                    if rr2 and str(rr2.get("status","")).upper() == "APPROVED":
                                        apply_leave_request_to_timesheets(conn, cfg, rr2)

                                    st.success("Cererea a fost modificată.")
                                    st.rerun()
                            except Exception as e:
                                st.error(f"Eroare modificare: {e}")

                    with cB:
                        if st.button("🗑️ Șterge cererea", key="hist_delete_btn"):
                            try:
                                # dacă era aprobată -> rollback
                                if cur_status == "APPROVED":
                                    rollback_leave_request_from_timesheets(conn, rr)
                                delete_leave_request_by_id(conn, int(sel_id))
                                st.success("Cererea a fost ștearsă.")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Eroare ștergere: {e}")

    # ---------------------------
    # Aprobări (admin/manager)
    # ---------------------------
    if role in ("admin","manager") and len(t) >= 3:
        with t[2]:
            st.markdown("### ✅ Aprobări (3 stări)")
            st.caption("Aprobă sau respinge cererile. La **Aprobat**, cererea se aplică automat în pontaj.")

            only_pending = st.checkbox("Afișează doar cererile în așteptare", value=True, key="ap_only_pending")

            # încarcă cereri (pe aria permisă)
            keys = [str(x) for x in df_emp["employee_key"].tolist()] if not df_emp.empty else []
            df_req = list_leave_requests(conn, employee_keys=keys, status=("PENDING" if only_pending else None))

            if df_req.empty:
                st.info("Nu există cereri.")
            else:
                # normalizează date (DB compat)
                if "start_date" not in df_req.columns and "date_start" in df_req.columns:
                    df_req["start_date"] = df_req["date_start"]
                if "end_date" not in df_req.columns and "date_end" in df_req.columns:
                    df_req["end_date"] = df_req["date_end"]

                # adaugă nume/prenume pentru afișare
                try:
                    df_emp2 = load_employees_cached(conn)
                except Exception:
                    df_emp2 = None
                if df_emp2 is not None and not df_emp2.empty:
                    emp_map = {str(r["employee_key"]): (str(r.get("nume","")), str(r.get("prenume",""))) for _, r in df_emp2.iterrows()}
                    df_req["Nume"] = df_req["employee_key"].astype(str).map(lambda k: emp_map.get(k, ("",""))[0])
                    df_req["Prenume"] = df_req["employee_key"].astype(str).map(lambda k: emp_map.get(k, ("",""))[1])
                else:
                    df_req["Nume"] = ""
                    df_req["Prenume"] = ""

                # status în română pentru afișare
                df_req["_status_ro"] = df_req.get("status", "").astype(str).str.upper().map(STATUS_RO_MAP).fillna("În așteptare")

                # tabel sumar (cu culori)
                try:
                    import pandas as pd
                    show = df_req.copy()
                    cols = [c for c in ["id","employee_key","Nume","Prenume","request_type","start_date","end_date","_status_ro","notes","created_by","created_at"] if c in show.columns]
                    show = show[cols].rename(columns={
                        "id":"ID","employee_key":"Angajat","request_type":"Tip",
                        "start_date":"De la","end_date":"Până la",
                        "_status_ro":"Stare","notes":"Observații",
                        "created_by":"Creat de","created_at":"Creat la"
                    })

                    def _style_row(s):
                        stv = str(s.get("Stare",""))
                        if stv == "Aprobat":
                            return ["background-color: #eaf7ea"] * len(s)
                        if stv == "Respins":
                            return ["background-color: #fdeaea"] * len(s)
                        if stv == "În așteptare":
                            return ["background-color: #fff6da"] * len(s)
                        return [""] * len(s)

                    st.dataframe(show.style.apply(_style_row, axis=1), use_container_width=True, hide_index=True)
                except Exception:
                    # fallback fără stilizare
                    st.dataframe(df_req, use_container_width=True, hide_index=True)

                st.divider()
                st.markdown("### Acțiuni rapide (direct pe rând)")

                # acțiuni pe rând
                header_cols = st.columns([0.6, 1.2, 1.6, 1.4, 1.6, 1.4, 1.4])
                header_cols[0].markdown("**ID**")
                header_cols[1].markdown("**Angajat**")
                header_cols[2].markdown("**Nume**")
                header_cols[3].markdown("**Tip**")
                header_cols[4].markdown("**Interval**")
                header_cols[5].markdown("**Stare**")
                header_cols[6].markdown("**Acțiuni**")

                def _badge(st_ro: str) -> str:
                    if st_ro == "Aprobat":
                        return "🟢 Aprobat"
                    if st_ro == "Respins":
                        return "🔴 Respins"
                    return "🟡 În așteptare"

                # buton bulk
                c_bulk1, c_bulk2 = st.columns([1,3])
                with c_bulk1:
                    bulk_approve = st.button("✅ Aprobă toate (vizibile)", key="bulk_approve_visible")
                with c_bulk2:
                    st.caption("Aprobă rapid toate cererile afișate (atenție: se aplică în pontaj).")

                if bulk_approve:
                    ok = 0
                    for _, rr in df_req.iterrows():
                        rid = int(rr["id"])
                        try:
                            decide_leave_request(conn, rid, "APPROVE", user_ctx.get("username"), "bulk")
                            rr2 = get_leave_request_by_id(conn, rid)
                            if rr2:
                                apply_leave_request_to_timesheets(conn, cfg, rr2)
                            ok += 1
                        except Exception as e:
                            st.error(f"Eroare bulk pentru ID {rid}: {e}")
                    if ok:
                        st.success(f"✅ {ok} cereri aprobate și aplicate în pontaj.")
                        st.rerun()

                # acțiuni individuale
                for _, rr in df_req.iterrows():
                    rid = int(rr["id"])
                    emp = str(rr.get("employee_key",""))
                    nm = f"{rr.get('Nume','')} {rr.get('Prenume','')}".strip()
                    tip = str(rr.get("request_type",""))
                    d1 = str(rr.get("start_date","") or "")
                    d2 = str(rr.get("end_date","") or "")
                    st_ro = str(rr.get("_status_ro","În așteptare"))

                    row_cols = st.columns([0.6, 1.2, 1.6, 1.4, 1.6, 1.4, 1.4])
                    row_cols[0].write(rid)
                    row_cols[1].write(emp)
                    row_cols[2].write(nm if nm else "-")
                    row_cols[3].write(tip)
                    row_cols[4].write(f"{d1} → {d2}")
                    row_cols[5].write(_badge(st_ro))

                    with row_cols[6]:
                        b1 = st.button("Aprobă", key=f"ap_ok_{rid}", use_container_width=True)
                        b2 = st.button("Respinge", key=f"ap_no_{rid}", use_container_width=True)

                    if b1:
                        try:
                            decide_leave_request(conn, rid, "APPROVE", user_ctx.get("username"), "manual")
                            rr2 = get_leave_request_by_id(conn, rid)
                            if rr2:
                                apply_leave_request_to_timesheets(conn, cfg, rr2)
                            st.success("✅ Cererea a fost aprobată și aplicată în pontaj.")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Eroare aprobare: {e}")

                    if b2:
                        try:
                            decide_leave_request(conn, rid, "REJECT", user_ctx.get("username"), "manual")
                            st.success("✅ Cererea a fost respinsă.")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Eroare respingere: {e}")

                    return

                only_pending = st.checkbox("Afișează doar cererile în așteptare", value=True, key="lr_only_pending")
                if only_pending:
                    df_req = df_req[df_req["status"].astype(str).str.upper() == "PENDING"].copy()

                df_ui = df_req.copy()
                df_ui["Stare"] = df_ui["status"].astype(str).str.upper().map(STATUS_RO_MAP).fillna(df_ui["status"]).map(lambda s: STATUS_CODE_TO_LABEL.get(str(s).upper(), "în așteptare"))

                show_cols = ["id", "employee_key", "Nume", "Prenume", "request_type", "start_date", "end_date", "Stare", "notes", "created_by", "created_at"]
                for c in show_cols:
                    if c not in df_ui.columns:
                        df_ui[c] = ""

                edited = st.data_editor(
                    df_ui[show_cols],
                    use_container_width=True,
                    num_rows="fixed",
                    column_config={
                        "id": st.column_config.NumberColumn("ID", disabled=True),
                        "employee_key": st.column_config.TextColumn("Angajat", disabled=True),
                        "Nume": st.column_config.TextColumn("Nume", disabled=True),
                        "Prenume": st.column_config.TextColumn("Prenume", disabled=True),
                        "request_type": st.column_config.TextColumn("Tip", disabled=True),
                        "start_date": st.column_config.TextColumn("De la", disabled=True),
                        "end_date": st.column_config.TextColumn("Până la", disabled=True),
                        "Stare": st.column_config.SelectboxColumn("Stare", options=list(STATUS_LABEL_TO_CODE.keys())),
                        "notes": st.column_config.TextColumn("Observații"),
                        "created_by": st.column_config.TextColumn("Creat de", disabled=True),
                        "created_at": st.column_config.TextColumn("Creat la", disabled=True),
                    },
                    key="lr_approvals_grid"
                )

                cA, cB = st.columns([1, 3])
                with cA:
                    if st.button("✅ Aprobă toate (vizibile)", key="lr_approve_all"):
                        try:
                            ids = edited["id"].tolist()
                            for rid in ids:
                                rr = get_leave_request_by_id(conn, int(rid))
                                if not rr:
                                    continue
                                if str(rr.get("status","")).upper() != "PENDING":
                                    continue
                                decide_leave_request(conn=conn, request_id=int(rid), decision="APPROVE", decision_by=user_ctx.get("username"), reason="bulk approve")
                                rr2 = get_leave_request_by_id(conn, int(rid))
                                if rr2:
                                    apply_leave_request_to_timesheets(conn, cfg, rr2)
                            st.success("Aprobate.")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Eroare bulk approve: {e}")

                with cB:
                    if st.button("💾 Salvează modificările", key="lr_save_changes"):
                        try:
                            import pandas as pd
                            # Asigurăm DataFrame (Streamlit poate întoarce și alt tip)
                            if not isinstance(edited, pd.DataFrame):
                                edited = pd.DataFrame(edited)

                            if df_req is None:
                                st.error("Nu există cereri de salvat.")
                                st.stop()

                            # Starea originală (label) pentru comparație
                            orig_label = {}
                            for _, r0 in df_req.iterrows():
                                rid0 = int(_row_get(r0, "id", 0) or 0)
                                st0 = str(_row_get(r0, "status", "PENDING") or "PENDING").upper()
                                orig_label[rid0] = STATUS_CODE_TO_LABEL.get(st0, "în așteptare")

                            for _, r in edited.iterrows():
                                rid = int(_row_get(r, "id", 0) or 0)
                                new_label = str(_row_get(r, "Stare", "în așteptare") or "în așteptare")
                                old_label = orig_label.get(rid, "în așteptare")
                                if new_label == old_label:
                                    continue

                                new_status = STATUS_LABEL_TO_CODE.get(new_label, "PENDING")

                                rr = get_leave_request_by_id(conn, rid)
                                old_status = str((rr or {}).get("status", "PENDING") or "PENDING").upper()

                                # Dacă scădem din APPROVED -> rollback înainte
                                if old_status == "APPROVED" and new_status != "APPROVED" and rr:
                                    rollback_leave_request_from_timesheets(conn, rr)

                                if new_status == "APPROVED":
                                    decide_leave_request(conn, rid, "APPROVE", user_ctx.get("username"), "manual")
                                    rr2 = get_leave_request_by_id(conn, rid)
                                    if rr2:
                                        apply_leave_request_to_timesheets(conn, cfg, rr2)
                                elif new_status == "REJECTED":
                                    decide_leave_request(conn, rid, "REJECT", user_ctx.get("username"), "manual")
                                else:
                                    reset_leave_request_to_pending(conn, rid)

                            st.success("Modificări salvate.")
                            st.rerun()

                        except Exception as e:
                            st.error(f"Eroare salvare: {e}")



    # ---------------------------
    # Registru CM (admin/manager)
    # ---------------------------
    if role in ("admin","manager"):
        try:
            with t[3]:
                page_registru_cm(cfg, conn, user_ctx)
            with t[4]:
                page_raport_cas_cm(cfg, conn, user_ctx)
        except Exception as e:
            st.error(f"Eroare la Registru CM / Raport CAS: {e}")


    with t[idx_sold]:
        st.markdown("### 🏖️ Sold CO (ultimii 3 ani)")
        st.caption("Zilele CO se introduc manual pe an (ex: 2024/2025). Consum calculat automat din cererile **CO aprobate**. Se consumă din anul cel mai vechi (an-2 → an-1 → an).")

        if df_emp.empty:
            st.info("Nu există angajați.")
        else:
            emp_opts = df_emp.copy()
            # afisare peste tot: marca — Nume Prenume (unde exista)
            emp_keys = [str(x) for x in emp_opts["employee_key"].tolist()]
            label_map = {}
            if "FullName" in emp_opts.columns:
                for _, rr in emp_opts.iterrows():
                    k = str(rr.get("employee_key", ""))
                    fn = str(rr.get("FullName", "") or "").strip()
                    if not fn:
                        # fallback la Nume/Prenume sau nume/prenume
                        n1 = str(rr.get("Nume", rr.get("nume", "")) or "").strip()
                        p1 = str(rr.get("Prenume", rr.get("prenume", "")) or "").strip()
                        fn = (n1 + " " + p1).strip()
                    if fn:
                        label_map[k] = f"{k} — {fn}"
            emp_key = st.selectbox(
                "Selectează angajat",
                options=emp_keys,
                key="co_sel_emp",
                format_func=lambda x: label_map.get(str(x), str(x)),
            )
            st.markdown(f"**Angajat:** {label_map.get(str(emp_key), str(emp_key))}")
            emp_key = str(emp_key)

            from datetime import date as _date
            year = st.number_input("An curent", min_value=2000, max_value=2100, value=_date.today().year, step=1, key="co_year")

            bal = compute_co_balance_3y(conn, emp_key, int(year))
            y2, y1, y0 = bal["years"]

            c1, c2, c3 = st.columns(3)
            with c1:
                st.metric(f"{y2} rămas", f"{bal['remaining'][y2]:.0f}")
            with c2:
                st.metric(f"{y1} rămas", f"{bal['remaining'][y1]:.0f}")
            with c3:
                st.metric(f"{y0} rămas", f"{bal['remaining'][y0]:.0f}")

            st.success(f"Total zile CO rămase (3 ani): **{bal['total_remaining']:.0f}**")
            if bal.get("overuse", 0) > 0:
                st.warning(f"Atenție: consumul depășește alocările cu {bal['overuse']:.0f} zile (verifică alocările pe ani).")

            st.divider()
            st.markdown("### ✍️ Setare manuală zile CO / an (inițial)")
            ent = get_co_entitlements(conn, emp_key)

            edit_year = st.number_input("An (de setat)", min_value=2000, max_value=2100, value=int(year), step=1, key="co_edit_year")
            edit_days = st.number_input("Zile CO alocate", min_value=0.0, max_value=60.0, value=float(ent.get(int(edit_year), 0.0)), step=1.0, key="co_edit_days")

            if st.button("💾 Salvează alocarea CO", key="co_save_entitlement"):
                try:
                    upsert_co_entitlement(conn, emp_key, int(edit_year), float(edit_days))
                    st.success("✅ Alocarea CO a fost salvată.")
                    st.rerun()
                except Exception as e:
                    st.error(f"Eroare salvare alocare: {e}")


def page_rapoarte(conn: sqlite3.Connection, user_ctx: dict):
    st.subheader("📈 Rapoarte")

    tab_pontaj, tab_co, tab_cm, tab_cereri = st.tabs(["🕒 Pontaj", "🏖️ Raport CO", "🏥 Raport CM", "🧾 Rapoarte cereri"])

    # ---------------- Pontaj (raport lunar) ----------------
    with tab_pontaj:
        today = date.today()
        year = st.number_input("An", min_value=2000, max_value=2100, value=today.year, step=1, key="ry")
        month = st.selectbox(
            "Luna",
            list(range(1, 13)),
            index=today.month - 1,
            format_func=lambda m: f"{m:02d} - {MONTH_NAMES_RO.get(int(m), str(m))}",
            key="rm",
        )

        start = date(int(year), int(month), 1).isoformat()
        end = date(int(year), int(month), calendar.monthrange(int(year), int(month))[1]).isoformat()

        df = pd.read_sql_query(
            """SELECT employee_key, nume, prenume, locatie, directie, departament, birou,
                      work_date, start_time, end_time, status, total_hours, overtime_hours, night_hours
                 FROM timesheets
                 WHERE work_date BETWEEN ? AND ?
                 ORDER BY employee_key, work_date""",
            conn,
            params=(start, end),
        )

        df_emp_all = load_employees_cached(conn)
        scopes_df = get_user_scopes(conn, user_ctx["username"])
        scopes = scopes_df.drop(columns=["id"], errors="ignore").to_dict("records")
        df_emp = apply_scope_filter(df_emp_all, user_ctx.get("role"), scopes, user_ctx.get("employee_key"))
        allowed_keys = set(df_emp["employee_key"].tolist())
        df = df[df["employee_key"].isin(allowed_keys)].copy()

        st.dataframe(df, use_container_width=True, hide_index=True)

    # ---------------- Raport CO (oficial) ----------------
    with tab_co:
        st.markdown("### 🏖️ Raport Concediu de odihnă (CO)")
        st.caption("TOTAL CO pe ani (an-2 / an-1 / an curent) + zile luate în anul curent (perioade) + zile rămase (sold 3 ani).")

        today = date.today()
        year = st.number_input("An curent", min_value=2000, max_value=2100, value=today.year, step=1, key="co_rep_year")

        # angajați cu drepturi
        df_emp_all = load_employees_cached(conn)
        scopes_df = get_user_scopes(conn, user_ctx["username"])
        scopes = scopes_df.drop(columns=["id"], errors="ignore").to_dict("records")
        df_emp = apply_scope_filter(df_emp_all, user_ctx.get("role"), scopes, user_ctx.get("employee_key"))

        if df_emp.empty:
            st.info("Nu există angajați în aria ta de acces.")
            return

        df_emp = df_emp.copy()
        df_emp["label"] = df_emp.apply(lambda r: f"{r.get('nume','')} {r.get('prenume','')} [{r.get('employee_key','')}]", axis=1)

        mode = st.radio("Mod raport", ["Sumar (toți angajații)", "Detaliat (un angajat)"], horizontal=True, key="co_rep_mode")

        y2, y1, y0 = int(year) - 2, int(year) - 1, int(year)

        if mode == "Sumar (toți angajații)":
            rows = []
            for _, r in df_emp.iterrows():
                emp_key = str(r.get("employee_key",""))
                bal = compute_co_balance_3y(conn, emp_key, int(year))
                ent = bal["entitled"]
                used_y0 = float(get_co_used_days(conn, emp_key, int(year)))
                rows.append({
                    "Marca": emp_key,
                    "Nume": str(r.get("nume","") or ""),
                    "Prenume": str(r.get("prenume","") or ""),
                    f"TOTAL CO {y2} (zile)": float(ent.get(y2, 0)),
                    f"TOTAL CO {y1} (zile)": float(ent.get(y1, 0)),
                    f"TOTAL CO {y0} (zile)": float(ent.get(y0, 0)),
                    f"Zile efectuate în {y0} (zile)": used_y0,
                    "Zile rămase (3 ani)": float(bal.get("total_remaining", 0) or 0),
                })
            df_sum = pd.DataFrame(rows)
            st.dataframe(df_sum, use_container_width=True, hide_index=True)

            c1, c2 = st.columns([1,1])
            with c1:
                bio = BytesIO()
                with pd.ExcelWriter(bio, engine="openpyxl") as writer:
                    df_sum.to_excel(writer, index=False, sheet_name="Raport CO - Sumar")
                bio.seek(0)
                st.download_button(
                    "⬇ Salvează raport CO (Excel)",
                    data=bio.getvalue(),
                    file_name=f"raport_CO_sumar_{int(year)}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    key="dl_co_report_sum",
                )
            with c2:
                if st.button("🖨 Listare raport (pe ecran)", key="co_print_sum"):
                    st.markdown("#### Listare raport CO (sumar)")
                    st.dataframe(df_sum, use_container_width=True, hide_index=True)

        else:
            sel = st.selectbox("Selectează angajat", options=df_emp["label"].tolist(), key="co_rep_emp")
            emp_key = df_emp.loc[df_emp["label"] == sel, "employee_key"].astype(str).iloc[0]
            row_emp = df_emp.loc[df_emp["label"] == sel].iloc[0]

            bal = compute_co_balance_3y(conn, emp_key, int(year))
            ent = bal["entitled"]
            used_y0 = float(get_co_used_days(conn, emp_key, int(year)))

            # sumar "oficial"
            st.markdown("#### 📌 Sumar CO")
            df_one = pd.DataFrame([{
                "Marca": emp_key,
                "Nume": str(row_emp.get("nume","") or ""),
                "Prenume": str(row_emp.get("prenume","") or ""),
                f"TOTAL CO {y2} (zile)": float(ent.get(y2, 0)),
                f"TOTAL CO {y1} (zile)": float(ent.get(y1, 0)),
                f"TOTAL CO {y0} (zile)": float(ent.get(y0, 0)),
                f"Zile efectuate în {y0} (zile)": used_y0,
                "Zile rămase (3 ani)": float(bal.get("total_remaining", 0) or 0),
            }])
            st.dataframe(df_one, use_container_width=True, hide_index=True)

            # perioade CO
            st.markdown(f"#### 📅 Zile efectuate în anul curent ({y0})")
            df_periods = get_co_periods_for_year(conn, emp_key, int(year))
            if df_periods.empty:
                st.info("Nu există CO aprobat în anul curent.")
            else:
                st.dataframe(df_periods, use_container_width=True, hide_index=True)
                st.success(f"Total zile luate în {y0}: **{df_periods['Zile'].sum():.0f}**")

            # export + listare
            c1, c2 = st.columns([1,1])

            with c1:
                bio = BytesIO()
                with pd.ExcelWriter(bio, engine="openpyxl") as writer:
                    df_one.to_excel(writer, index=False, sheet_name="Sumar")
                    df_periods.to_excel(writer, index=False, sheet_name="Perioade CO")
                bio.seek(0)
                st.download_button(
                    "⬇ Salvează raport CO (Excel)",
                    data=bio.getvalue(),
                    file_name=f"raport_CO_{emp_key}_{y0}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    key="dl_co_report_one",
                )

            with c2:
                if st.button("🖨 Listare raport (pe ecran)", key="co_print_one"):
                    st.markdown("#### Listare raport CO")
                    st.dataframe(df_one, use_container_width=True, hide_index=True)
                    if not df_periods.empty:
                        st.markdown("**Perioade CO (an curent):**")
                        for _, rr in df_periods.iterrows():
                            st.write(f"- {rr['De la']} → {rr['Până la']} = {int(rr['Zile'])} zile")


    # ---------------- Raport CM ----------------
    with tab_cm:
        st.markdown("### 🏥 Raport Concedii medicale (CM)")
        st.caption("Rapoartă certificatele medicale care se suprapun peste luna selectată (calendaristic). Include împărțirea zilelor: fond salarii vs FNUASS.")

        today = date.today()
        ry = st.number_input("An", min_value=2000, max_value=2100, value=today.year, step=1, key="cm_rep_year")
        rm = st.selectbox(
            "Luna",
            list(range(1, 13)),
            index=today.month - 1,
            format_func=lambda mm: f"{int(mm):02d} - {MONTH_NAMES_RO.get(int(mm), str(mm))}",
            key="cm_rep_month",
        )

        start = date(int(ry), int(rm), 1)
        end = date(int(ry), int(rm), calendar.monthrange(int(ry), int(rm))[1])

        df_cm = pd.read_sql_query(
            """SELECT
                    id,
                    employee_key,
                    serie,
                    numar,
                    issued_date,
                    prescription_place,
                    cod_indemnizatie,
                    procent,
                    diagnostic_code,
                    start_date,
                    end_date,
                    days_calendar,
                    is_continuation,
                    initial_serie,
                    initial_numar,
                    initial_date,
                    fara_stagiu,
                    pay_employer_days,
                    pay_fnuass_days,
                    created_by,
                    created_at
                FROM medical_certificates
                WHERE date(start_date) <= date(?)
                  AND date(end_date) >= date(?)
                ORDER BY date(start_date), employee_key""",
            conn,
            params=(end.isoformat(), start.isoformat()),
        )

        df_emp_all = load_employees_cached(conn)
        scopes_df = get_user_scopes(conn, user_ctx["username"])
        scopes = scopes_df.drop(columns=["id"], errors="ignore").to_dict("records")
        df_emp = apply_scope_filter(df_emp_all, user_ctx.get("role"), scopes, user_ctx.get("employee_key"))
        allowed_keys = set(df_emp["employee_key"].astype(str).tolist())

        if not df_cm.empty:
            df_cm["employee_key"] = df_cm["employee_key"].astype(str)
            df_cm = df_cm[df_cm["employee_key"].isin(allowed_keys)].copy()

        if df_cm.empty:
            st.info("Nu există certificate medicale în luna selectată (în aria ta de acces).")
        else:
            # map nume
            map_name = df_emp.set_index("employee_key")["FullName"].to_dict()
            df_cm["Angajat"] = df_cm["employee_key"].map(lambda k: f"{k} — {map_name.get(str(k), '')}".strip(" —"))

            # loc prescripție
            loc_map = {"1":"Medic familie","2":"Spital","3":"Ambulatoriu","4":"CAS"}
            df_cm["Loc prescripție"] = df_cm["prescription_place"].astype(str).map(loc_map).fillna(df_cm["prescription_place"].astype(str))

            # afișare
            df_show = df_cm.rename(columns={
                "employee_key":"Marca",
                "serie":"Serie",
                "numar":"Număr",
                "issued_date":"Data eliberării",
                "cod_indemnizatie":"Cod indemnizație",
                "diagnostic_code":"Cod diagnostic",
                "start_date":"De la",
                "end_date":"Până la",
                "days_calendar":"Zile calendaristice",
                "is_continuation":"În continuare",
                "fara_stagiu":"Fără stagiu",
                "pay_employer_days":"Fond salarii (zile)",
                "pay_fnuass_days":"FNUASS (zile)",
                "created_by":"Creat de",
                "created_at":"Creat la",
            })

            cols = ["Marca","Angajat","Serie","Număr","Data eliberării","Loc prescripție","Cod indemnizație","Cod diagnostic",
                    "De la","Până la","Zile calendaristice","Fond salarii (zile)","FNUASS (zile)","În continuare","Fără stagiu","Creat de","Creat la"]
            df_show["În continuare"] = df_show["În continuare"].apply(lambda x: "Da" if int(x or 0)==1 else "Nu")
            df_show["Fără stagiu"] = df_show["Fără stagiu"].apply(lambda x: "Da" if int(x or 0)==1 else "Nu")

            st.dataframe(df_show[cols], use_container_width=True, hide_index=True)

            # sumar
            tot = float(df_show["Zile calendaristice"].fillna(0).astype(float).sum())
            tot_sal = float(df_show["Fond salarii (zile)"].fillna(0).astype(float).sum())
            tot_fnu = float(df_show["FNUASS (zile)"].fillna(0).astype(float).sum())
            c1, c2, c3 = st.columns(3)
            c1.metric("Total zile CM", f"{tot:.0f}")
            c2.metric("Total fond salarii", f"{tot_sal:.0f}")
            c3.metric("Total FNUASS", f"{tot_fnu:.0f}")

            # export excel
            bio = BytesIO()
            with pd.ExcelWriter(bio, engine="openpyxl") as writer:
                df_show[cols].to_excel(writer, index=False, sheet_name="Raport CM")
            bio.seek(0)
            st.download_button(
                "⬇ Salvează Raport CM (Excel)",
                data=bio.getvalue(),
                file_name=f"raport_CM_{int(ry)}_{int(rm):02d}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                key="dl_cm_report",
            )

    # ---------------- Rapoarte cereri (toate tipurile) ----------------
    with tab_cereri:
        st.markdown("### 🧾 Rapoarte cereri (dinamic)")
        st.caption("Generează raport pentru orice tip de cerere existent/configurat (CO/CM/CFP/Telemuncă/etc).")

        today = date.today()
        ry = st.number_input("An", min_value=2000, max_value=2100, value=today.year, step=1, key="req_rep_year")
        rm = st.selectbox(
            "Luna",
            list(range(1, 13)),
            index=today.month - 1,
            format_func=lambda mm: f"{int(mm):02d} - {MONTH_NAMES_RO.get(int(mm), str(mm))}",
            key="req_rep_month",
        )
        start = date(int(ry), int(rm), 1)
        end = date(int(ry), int(rm), calendar.monthrange(int(ry), int(rm))[1])

        only_approved = st.checkbox("Doar aprobate", value=True, key="req_rep_only_appr")

        rt_list = list_request_types(conn, active_only=True)
        # rt_list = [(code,label),...]
        choices = ["Toate tipurile"] + [f"{lbl} ({code})" for code, lbl in rt_list]
        choice = st.selectbox("Tip cerere", options=choices, key="req_rep_type")
        code_sel = ""
        label_sel = ""
        if choice != "Toate tipurile":
            m = re.search(r"\(([^)]+)\)\s*$", choice)
            code_sel = (m.group(1) if m else "").strip()
            label_sel = choice

        # angajați + scope
        df_emp_all = load_employees_cached(conn)
        scopes_df = get_user_scopes(conn, user_ctx["username"])
        scopes = scopes_df.drop(columns=["id"], errors="ignore").to_dict("records")
        df_emp = apply_scope_filter(df_emp_all, user_ctx.get("role"), scopes, user_ctx.get("employee_key"))
        allowed_keys = set(df_emp["employee_key"].astype(str).tolist())
        name_map = df_emp.set_index("employee_key")["FullName"].to_dict()

        def _fetch_requests(code: str | None):
            q = """SELECT id, employee_key, request_type, start_date, end_date, weekdays_only, status, notes, created_by, created_at
                   FROM leave_requests
                   WHERE date(start_date) <= date(?)
                     AND date(end_date) >= date(?)"""
            params = [end.isoformat(), start.isoformat()]
            if code:
                q += " AND request_type = ?"
                params.append(str(code))
            if only_approved:
                q += " AND status = 'APPROVED'"
            q += " ORDER BY date(start_date), employee_key"
            df = pd.read_sql_query(q, conn, params=params)
            if not df.empty:
                df["employee_key"] = df["employee_key"].astype(str)
                df = df[df["employee_key"].isin(allowed_keys)].copy()
            return df

        def _decorate(df):
            if df.empty:
                return df
            df = df.copy()
            df["Angajat"] = df["employee_key"].map(lambda k: f"{k} — {name_map.get(str(k), '')}".strip(" —"))
            # zile calculate
            def _calc(row):
                s = _parse_iso_date(row.get("start_date"))
                e = _parse_iso_date(row.get("end_date"))
                wo = int(row.get("weekdays_only") or 0) == 1
                return int(compute_requested_days(s, e, wo))
            df["Zile"] = df.apply(_calc, axis=1)
            # status ro
            st_map = {"PENDING":"În așteptare","APPROVED":"Aprobat","REJECTED":"Respins","CANCELLED":"Anulat"}
            df["Stare"] = df["status"].astype(str).map(st_map).fillna(df["status"].astype(str))
            df["Aplică doar L-V"] = df["weekdays_only"].apply(lambda x: "Da" if int(x or 0)==1 else "Nu")
            df_show = df.rename(columns={
                "employee_key":"Marca",
                "request_type":"Tip",
                "start_date":"De la",
                "end_date":"Până la",
                "notes":"Observații",
                "created_by":"Creat de",
                "created_at":"Creat la",
            })
            cols = ["id","Marca","Angajat","Tip","De la","Până la","Aplică doar L-V","Zile","Stare","Observații","Creat de","Creat la"]
            # id în RO
            df_show = df_show.rename(columns={"id":"ID"})
            cols[0]="ID"
            return df_show[cols]

        if choice == "Toate tipurile":
            # afișare pe tip + export multi-sheet
            bio = BytesIO()
            any_data = False
            with pd.ExcelWriter(bio, engine="openpyxl") as writer:
                for code, lbl in rt_list:
                    df = _decorate(_fetch_requests(code))
                    if df.empty:
                        continue
                    any_data = True
                    sheet = (f"{code}_{lbl}")[:31]
                    df.to_excel(writer, index=False, sheet_name=sheet)
                if not any_data:
                    pass
            if not any_data:
                st.info("Nu există cereri în luna selectată (în aria ta de acces).")
            else:
                st.success("Raport generat pentru toate tipurile (vezi export).")
                bio.seek(0)
                st.download_button(
                    "⬇ Salvează rapoarte cereri (Excel, multi-sheet)",
                    data=bio.getvalue(),
                    file_name=f"rapoarte_cereri_{int(ry)}_{int(rm):02d}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    key="dl_req_reports_all",
                )
                # și afișăm sumar pe tip
                st.markdown("#### Sumar pe tip")
                rows=[]
                for code, lbl in rt_list:
                    df_raw=_fetch_requests(code)
                    if df_raw.empty:
                        continue
                    df_raw=_decorate(df_raw)
                    rows.append({"Tip": f"{lbl} ({code})", "Număr cereri": int(len(df_raw)), "Total zile": int(df_raw["Zile"].sum())})
                if rows:
                    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
        else:
            df = _decorate(_fetch_requests(code_sel))
            if df.empty:
                st.info("Nu există cereri pentru tipul selectat în luna selectată (în aria ta de acces).")
            else:
                st.dataframe(df, use_container_width=True, hide_index=True)
                st.success(f"Total zile: **{int(df['Zile'].sum())}** | Total cereri: **{len(df)}**")

                bio = BytesIO()
                with pd.ExcelWriter(bio, engine="openpyxl") as writer:
                    df.to_excel(writer, index=False, sheet_name="Raport")
                bio.seek(0)
                st.download_button(
                    "⬇ Salvează raport (Excel)",
                    data=bio.getvalue(),
                    file_name=f"raport_{code_sel}_{int(ry)}_{int(rm):02d}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    key="dl_req_report_one",
                )


def _parse_cell_value(v) -> tuple[str, float]:
    """Returnează (status, ore). Dacă e număr 1..12 -> ('Lucrat', ore). Dacă e text -> (text,0)"""
    s = safe_str(v)
    if not s:
        return "", 0.0
    # numeric?
    try:
        f = float(s.replace(",", "."))
        if 1 <= f <= 12:
            return "Lucrat", float(int(f) if f.is_integer() else f)
        # dacă e 0 => gol
        if f == 0:
            return "", 0.0
    except Exception:
        pass
    # text status
    return s, 0.0

def _read_timesheets_month(conn: sqlite3.Connection, employee_keys: list[str], year: int, month: int):
    """Citește pontajul (timesheets) pentru o listă de employee_key într-o lună.
    Returnează DataFrame cu cel puțin: employee_key, work_date, status, total_hours.
    """
    import pandas as pd
    if not employee_keys:
        return pd.DataFrame(columns=["employee_key","work_date","status","total_hours"])

    start = date(year, month, 1).isoformat()
    last_day = calendar.monthrange(year, month)[1]
    end = date(year, month, last_day).isoformat()

    # SQLite limitation: max vars; facem chunking
    CHUNK = 900
    dfs = []
    for i in range(0, len(employee_keys), CHUNK):
        chunk = employee_keys[i:i+CHUNK]
        qmarks = ",".join(["?"]*len(chunk))
        sql = f"""
            SELECT employee_key, work_date, status, total_hours
            FROM timesheets
            WHERE work_date BETWEEN ? AND ?
              AND employee_key IN ({qmarks})
            ORDER BY employee_key, work_date
        """
        params = [start, end] + list(chunk)
        dfs.append(pd.read_sql_query(sql, conn, params=params))
    if not dfs:
        return pd.DataFrame(columns=["employee_key","work_date","status","total_hours"])
    return pd.concat(dfs, ignore_index=True)

def _upsert_timesheet_simple(conn: sqlite3.Connection, cfg: dict, employee_key: str, work_date: date, status: str, hours: float, snapshot: dict):
    """Upsert minimal în timesheets, fără ore start/end."""
    now = datetime.now().isoformat(timespec="seconds")
    nume = safe_str(snapshot.get("Nume"))
    prenume = safe_str(snapshot.get("Prenume"))
    cnp = safe_str(snapshot.get("CNP"))
    locatie = safe_str(snapshot.get("Locatie"))
    directie = safe_str(snapshot.get("Directie"))
    departament = safe_str(snapshot.get("Departament"))
    birou = safe_str(snapshot.get("Birou"))

    status_db = safe_str(status)
    total_hours = float(hours or 0.0)

    # dacă nu e setat status: alegem automat în funcție de zi (weekend/sărbătoare)
    if not status_db:
        if total_hours > 0:
            status_db = "Lucrat"
        else:
            if is_legal_holiday(work_date, cfg):
                status_db = "Sarb."
            elif is_weekend(work_date):
                status_db = "Sam./D"
            else:
                status_db = "Liber"

    standard_daily_hours = float((cfg or DEFAULT_CONFIG).get("standard_daily_hours", 8.0))
    is_weekend_day = is_weekend(work_date)
    is_holiday_day = is_legal_holiday(work_date, cfg) or (status_db == "Sarb.")

    # calcul ore: normale/suplimentare + weekend/sărbătoare
    if status_db == "Lucrat":
        normal_hours = min(total_hours, standard_daily_hours)
        overtime_hours = max(0.0, total_hours - standard_daily_hours)
    else:
        normal_hours = 0.0
        overtime_hours = 0.0

    night_hours = 0.0
    weekend_hours = total_hours if (status_db == "Lucrat" and is_weekend_day) else 0.0
    holiday_hours = total_hours if (status_db == "Lucrat" and is_holiday_day) else 0.0

    co_day = 1 if status_db == "CO" else 0
    cm_day = 1 if status_db == "CM" else 0
    cfp_day = 1 if status_db == "CFP" else 0
    nemotivat_day = 1 if status_db == "Nemotivat" else 0
    liber_day = 1 if status_db in ("Liber","Sam./D") else 0

    telemunca_day = 1 if status_db == "Telemunca" else 0
    samd_day = 1 if status_db == "Sam./D" else 0

    conn.execute(
        """INSERT INTO timesheets(
                employee_key, work_date,
                start_time, end_time, status,
                total_hours, normal_hours, night_hours,
                weekend_hours, holiday_hours, overtime_hours,
                co_day, cm_day, cfp_day, nemotivat_day, liber_day, telemunca_day, samd_day,
                nume, prenume, cnp, locatie, directie, departament, birou,
                created_at, updated_at
            )
            VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            ON CONFLICT(employee_key, work_date) DO UPDATE SET
                start_time=excluded.start_time,
                end_time=excluded.end_time,
                status=excluded.status,
                total_hours=excluded.total_hours,
                normal_hours=excluded.normal_hours,
                night_hours=excluded.night_hours,
                weekend_hours=excluded.weekend_hours,
                holiday_hours=excluded.holiday_hours,
                overtime_hours=excluded.overtime_hours,
                co_day=excluded.co_day,
                cm_day=excluded.cm_day,
                cfp_day=excluded.cfp_day,
                nemotivat_day=excluded.nemotivat_day,
                liber_day=excluded.liber_day,
                telemunca_day=excluded.telemunca_day,
                samd_day=excluded.samd_day,
                nume=excluded.nume,
                prenume=excluded.prenume,
                cnp=excluded.cnp,
                locatie=excluded.locatie,
                directie=excluded.directie,
                departament=excluded.departament,
                birou=excluded.birou,
                updated_at=excluded.updated_at
        """,
        (
            str(employee_key),
            work_date.isoformat(),
            None, None,
            status_db,
            total_hours, normal_hours, night_hours,
            weekend_hours, holiday_hours, overtime_hours,
            co_day, cm_day, cfp_day, nemotivat_day, liber_day,
            telemunca_day, samd_day,
            nume, prenume, cnp, locatie, directie, departament, birou,
            now, now
        )
    )





# ============================================================
# CERERI - TIPURI CONFIGURABILE
# ============================================================

DEFAULT_REQUEST_TYPES = [
    # code, label, apply_mode, ts_status, hours_per_day, weekdays_only_default, flags dict
    ("CO", "Concediu de odihnă", "ABSENCE", "CO", 0, 1, {"co_day": 1}),
    ("CM", "Concediu medical", "ABSENCE", "CM", 0, 0, {"cm_day": 1}),
    ("CFS", "Concediu fără salariu", "ABSENCE", "CFP", 0, 1, {"cfp_day": 1}),
    ("NEPL", "Absență nemotivată", "ABSENCE", "Nemotivat", 0, 1, {"nemotivat_day": 1}),
    ("Liber", "Zile libere", "ABSENCE", "ZI_LIBERA", 0, 1, {"liber_day": 1}),
    ("Telemunca", "Telemuncă", "WORK", "Lucrat", 8, 1, {"telemunca_day": 1}),
    ("Deleg.", "Delegare", "MARK_ONLY", "Deleg.", 0, 1, {}),
    ("DET", "Detașare", "MARK_ONLY", "DET", 0, 1, {}),
    ("Sam./D", "Weekend", "ABSENCE", "Sam./D", 0, 0, {"samd_day": 1}),
]
def ensure_default_request_types(conn: sqlite3.Connection):
    """Inserează tipurile implicite dacă lipsesc."""
    now = datetime.now().isoformat(timespec="seconds")
    cur = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='request_types'")
    if not cur.fetchone():
        return
    for code, label, apply_mode, ts_status, hours_per_day, weekdays_only_default, flags in DEFAULT_REQUEST_TYPES:
        cur.execute(
            """INSERT OR IGNORE INTO request_types(code, label, is_active, apply_mode, ts_status, hours_per_day, weekdays_only_default, co_day, cm_day, cfp_day, nemotivat_day, liber_day, telemunca_day, samd_day, created_at, updated_at)
                 VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (code, label, 1, apply_mode, ts_status, float(hours_per_day or 0), int(weekdays_only_default or 0), int(flags.get('co_day',0)), int(flags.get('cm_day',0)), int(flags.get('cfp_day',0)), int(flags.get('nemotivat_day',0)), int(flags.get('liber_day',0)), int(flags.get('telemunca_day',0)), int(flags.get('samd_day',0)), now, now)
        )
    # CM: calendaristic (default)
    try:
        cur.execute("UPDATE request_types SET weekdays_only_default=0 WHERE code='CM'")
    except Exception:
        pass
    conn.commit()

def list_request_types(conn: sqlite3.Connection, active_only: bool = True) -> list[tuple[str,str]]:
    """Returnează listă (code,label) ordonată."""
    ensure_default_request_types(conn)
    cur = conn.cursor()
    if active_only:
        cur.execute("SELECT code, label FROM request_types WHERE is_active=1 ORDER BY label COLLATE NOCASE")
    else:
        cur.execute("SELECT code, label FROM request_types ORDER BY label COLLATE NOCASE")
    return [(r[0], r[1]) for r in cur.fetchall()]



def list_request_types_full(conn: sqlite3.Connection) -> 'pd.DataFrame':
    """Returnează toate tipurile cu configurare."""
    ensure_default_request_types(conn)
    migrate_request_types_extra_cols(conn)
    return pd.read_sql_query(
        """SELECT
                code, label, is_active,
                apply_mode, ts_status, hours_per_day, weekdays_only_default,
                co_day, cm_day, cfp_day, nemotivat_day, liber_day, telemunca_day, samd_day,
                created_at, updated_at
             FROM request_types
             ORDER BY label COLLATE NOCASE""",
        conn
    )


def get_request_type_behavior(conn: sqlite3.Connection, code: str) -> dict:
    """Returnează configurarea unui tip de cerere (request_types)."""
    ensure_default_request_types(conn)
    migrate_request_types_extra_cols(conn)
    c = safe_str(code)
    df = pd.read_sql_query(
        """SELECT
                code, label, is_active,
                apply_mode, ts_status, hours_per_day, weekdays_only_default,
                co_day, cm_day, cfp_day, nemotivat_day, liber_day, telemunca_day, samd_day
             FROM request_types
             WHERE code=?
             LIMIT 1""",
        conn,
        params=(c,)
    )
    if df.empty:
        return {}
    return df.iloc[0].to_dict()

def upsert_request_type(conn: sqlite3.Connection, code: str, label: str, is_active: bool = True):
    ensure_default_request_types(conn)
    code = (code or "").strip()
    label = (label or "").strip()
    if not code:
        raise ValueError("Codul tipului este obligatoriu.")
    if not label:
        raise ValueError("Denumirea tipului este obligatorie.")
    now = datetime.now().isoformat(timespec="seconds")
    conn.execute(
        """INSERT INTO request_types(code, label, is_active, created_at, updated_at)
             VALUES(?,?,?,?,?)
             ON CONFLICT(code) DO UPDATE SET
                label=excluded.label,
                is_active=excluded.is_active,
                updated_at=excluded.updated_at
        """,
        (code, label, 1 if is_active else 0, now, now)
    )
    conn.commit()



def upsert_request_type_behavior(
    conn: sqlite3.Connection,
    code: str,
    label: str,
    is_active: bool,
    apply_mode: str,
    ts_status: str,
    hours_per_day: float,
    weekdays_only_default: int,
    flags: dict
):
    """Upsert complet cu configurare de aplicare în pontaj."""
    ensure_default_request_types(conn)
    migrate_request_types_extra_cols(conn)
    code = (code or "").strip()
    label = (label or "").strip()
    if not code:
        raise ValueError("Codul tipului este obligatoriu.")
    if not label:
        raise ValueError("Denumirea tipului este obligatorie.")
    apply_mode = (apply_mode or "ABSENCE").strip().upper()
    if apply_mode not in ("ABSENCE","WORK","MARK_ONLY"):
        raise ValueError("apply_mode invalid (ABSENCE/WORK/MARK_ONLY).")
    ts_status = (ts_status or "").strip()
    if not ts_status:
        # default: use code
        ts_status = code

    now = datetime.now().isoformat(timespec="seconds")
    conn.execute(
        """INSERT INTO request_types(
                code, label, is_active,
                apply_mode, ts_status, hours_per_day, weekdays_only_default,
                co_day, cm_day, cfp_day, nemotivat_day, liber_day, telemunca_day, samd_day,
                created_at, updated_at
            ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            ON CONFLICT(code) DO UPDATE SET
                label=excluded.label,
                is_active=excluded.is_active,
                apply_mode=excluded.apply_mode,
                ts_status=excluded.ts_status,
                hours_per_day=excluded.hours_per_day,
                weekdays_only_default=excluded.weekdays_only_default,
                co_day=excluded.co_day,
                cm_day=excluded.cm_day,
                cfp_day=excluded.cfp_day,
                nemotivat_day=excluded.nemotivat_day,
                liber_day=excluded.liber_day,
                telemunca_day=excluded.telemunca_day,
                samd_day=excluded.samd_day,
                updated_at=excluded.updated_at
        """,
        (
            code, label, 1 if is_active else 0,
            apply_mode, ts_status, float(hours_per_day or 0), int(weekdays_only_default or 0),
            int(flags.get("co_day",0)), int(flags.get("cm_day",0)), int(flags.get("cfp_day",0)), int(flags.get("nemotivat_day",0)),
            int(flags.get("liber_day",0)), int(flags.get("telemunca_day",0)), int(flags.get("samd_day",0)),
            now, now
        )
    )
    conn.commit()

def deactivate_request_type(conn: sqlite3.Connection, code: str):
    now = datetime.now().isoformat(timespec="seconds")
    conn.execute("UPDATE request_types SET is_active=0, updated_at=? WHERE code=?", (now, code))
    conn.commit()

# ============================================================
# CERERI CONCEDII - DB HELPERS
# ============================================================

def _normalize_request_type(rt: str) -> str:
    rt = (rt or "").strip()
    return rt



def update_leave_request_by_id(conn: sqlite3.Connection, req_id: int, **fields):
    """Update cerere: compatibil start_date/end_date vs date_start/date_end."""
    cols = _table_columns(conn, "leave_requests")
    sets = []
    params = []
    # map date fields
    if "start_date" in fields:
        v = fields["start_date"]
        if _has_col(cols, "start_date"):
            sets.append("start_date = ?"); params.append(v)
        if _has_col(cols, "date_start"):
            sets.append("date_start = ?"); params.append(v)
    if "end_date" in fields:
        v = fields["end_date"]
        if _has_col(cols, "end_date"):
            sets.append("end_date = ?"); params.append(v)
        if _has_col(cols, "date_end"):
            sets.append("date_end = ?"); params.append(v)

    # other common fields
    for k in ["request_type","notes","weekdays_only","hours_per_day","updated_at"]:
        if k in fields and _has_col(cols, k):
            sets.append(f"{k} = ?")
            params.append(fields[k])

    if not sets:
        return
    params.append(int(req_id))
    sql = "UPDATE leave_requests SET " + ", ".join(sets) + " WHERE id = ?"
    conn.execute(sql, tuple(params))
    conn.commit()

def delete_leave_request_by_id(conn: sqlite3.Connection, req_id: int):
    conn.execute("DELETE FROM leave_requests WHERE id = ?", (int(req_id),))
    conn.commit()
def create_leave_request(
    conn: sqlite3.Connection,
    employee_key: str,
    request_type: str,
    start_dt: date,
    end_dt: date,
    created_by: str,
    notes: str = "",
    weekdays_only: bool = True,
    hours_per_day: float = 0.0,
    cm_fields: dict | None = None,
) -> int:
    now = datetime.now().isoformat(timespec="seconds")
    rt = _normalize_request_type(request_type)
    cm_fields = cm_fields or {}
    cur = conn.cursor()
    
    cols_lr = _table_columns(conn, "leave_requests")

    # compat DB: start_date/end_date vs date_start/date_end
    start_col = "start_date" if _has_col(cols_lr, "start_date") else ("date_start" if _has_col(cols_lr, "date_start") else "start_date")
    end_col = "end_date" if _has_col(cols_lr, "end_date") else ("date_end" if _has_col(cols_lr, "date_end") else "end_date")

    fields = [
        "employee_key", "request_type", start_col, end_col,
        "weekdays_only", "hours_per_day",
        "notes",
        "created_by", "created_at", "updated_at",
        "cm_series", "cm_number", "cm_type", "cm_diag", "cm_issuer",
    ]

    # dacă DB-ul are și coloanele alternative, le completăm și pe acelea (ca să nu pice pe NOT NULL)
    if _has_col(cols_lr, "date_start") and "date_start" not in fields:
        fields.insert(fields.index(start_col) + 1, "date_start")
    if _has_col(cols_lr, "date_end") and "date_end" not in fields:
        fields.insert(fields.index(end_col) + 1, "date_end")
    if _has_col(cols_lr, "start_date") and "start_date" not in fields:
        fields.insert(fields.index(start_col) + 1, "start_date")
    if _has_col(cols_lr, "end_date") and "end_date" not in fields:
        fields.insert(fields.index(end_col) + 1, "end_date")

    values_map = {
        "employee_key": str(employee_key),
        "request_type": rt,
        "start_date": start_dt.isoformat(),
        "end_date": end_dt.isoformat(),
        "date_start": start_dt.isoformat(),
        "date_end": end_dt.isoformat(),
        "weekdays_only": 1 if weekdays_only else 0,
        "hours_per_day": float(hours_per_day or 0.0),
        "notes": notes or "",
        "created_by": created_by,
        "created_at": now,
        "updated_at": now,
        "cm_series": (cm_fields or {}).get("cm_series"),
        "cm_number": (cm_fields or {}).get("cm_number"),
        "cm_type": (cm_fields or {}).get("cm_type"),
        "cm_diag": (cm_fields or {}).get("cm_diag"),
        "cm_issuer": (cm_fields or {}).get("cm_issuer"),
    }
    values = [values_map.get(f) for f in fields]

    if _has_col(cols_lr, "status"):
        fields.insert(6, "status")
        values.insert(6, "PENDING")
    if _has_col(cols_lr, "status_code"):
        fields.insert(6, "status_code")
        values.insert(6, "PENDING")

    placeholders = ",".join(["?"] * len(fields))
    sql = f"INSERT INTO leave_requests({', '.join(fields)}) VALUES ({placeholders})"
    cur.execute(sql, tuple(values))
    conn.commit()
    return int(cur.lastrowid)


def _cm_has_overlap(conn: sqlite3.Connection, employee_key: str, start_dt: date, end_dt: date, exclude_leave_request_id: int | None = None) -> bool:
    """Verifică dacă există deja un certificat CM care se suprapune pe perioadă."""
    if not table_exists(conn, "medical_certificates"):
        return False
    params = [safe_str(employee_key), start_dt.isoformat(), end_dt.isoformat()]
    sql = """SELECT 1
             FROM medical_certificates
             WHERE employee_key=?
               AND NOT (end_date < ? OR start_date > ?)
          """
    if exclude_leave_request_id is not None:
        sql += " AND COALESCE(leave_request_id, -1) <> ?"
        params.append(int(exclude_leave_request_id))
    sql += " LIMIT 1"
    cur = conn.cursor()
    cur.execute(sql, tuple(params))
    return cur.fetchone() is not None


def _ensure_medical_certificates_cols(conn: sqlite3.Connection):
    """Adaugă coloane noi în medical_certificates pentru compatibilitate DB vechi."""
    if not table_exists(conn, "medical_certificates"):
        return
    cols = _table_columns(conn, "medical_certificates")
    cur = conn.cursor()
    try:
        if not _has_col(cols, "prescription_place"):
            cur.execute("ALTER TABLE medical_certificates ADD COLUMN prescription_place TEXT DEFAULT NULL")
        if not _has_col(cols, "pay_employer_days"):
            cur.execute("ALTER TABLE medical_certificates ADD COLUMN pay_employer_days INTEGER DEFAULT NULL")
        if not _has_col(cols, "pay_fnuass_days"):
            cur.execute("ALTER TABLE medical_certificates ADD COLUMN pay_fnuass_days INTEGER DEFAULT NULL")
        conn.commit()
    finally:
        try:
            cur.close()
        except Exception:
            pass

def compute_cm_payment_split(
    conn: sqlite3.Connection,
    employee_key: str,
    cod_indemnizatie: str,
    serie: str,
    numar: str,
    start_dt: date,
    end_dt: date,
    is_continuation: bool,
    initial_serie: str | None,
    initial_numar: str | None,
) -> tuple[int, int]:
    """Returnează (zile_angajator, zile_fnuass) pentru certificatul curent."""
    days_current = int((end_dt - start_dt).days + 1)
    if days_current <= 0:
        return (0, 0)

    code = safe_str(cod_indemnizatie)
    if code in CM_FULL_FNUASS_CODES:
        return (0, days_current)

    root_serie = safe_str(initial_serie) if is_continuation else safe_str(serie)
    root_numar = safe_str(initial_numar) if is_continuation else safe_str(numar)

    days_before = 0
    if table_exists(conn, "medical_certificates") and root_serie and root_numar:
        df = pd.read_sql_query(
            """SELECT start_date, days_calendar
                 FROM medical_certificates
                 WHERE employee_key=?
                   AND (
                        (COALESCE(serie,'')=? AND COALESCE(numar,'')=?)
                        OR (COALESCE(initial_serie,'')=? AND COALESCE(initial_numar,'')=?)
                   )
            """,
            conn,
            params=(safe_str(employee_key), root_serie, root_numar, root_serie, root_numar),
        )
        if not df.empty:
            cur_start = start_dt.isoformat()
            df["start_date"] = df["start_date"].astype(str)
            df_prev = df[df["start_date"] < cur_start]
            if not df_prev.empty:
                try:
                    days_before = int(df_prev["days_calendar"].fillna(0).astype(int).sum())
                except Exception:
                    days_before = 0

    remaining = max(0, 5 - int(days_before))
    pay_emp = min(days_current, remaining)
    pay_fnuass = max(0, days_current - pay_emp)
    return (int(pay_emp), int(pay_fnuass))
def create_medical_certificate(
    conn: sqlite3.Connection,
    employee_key: str,
    serie: str,
    numar: str,
    issued_date: date | None,
    prescription_place: str | None,
    cod_indemnizatie: str,
    procent: int | None,
    diagnostic_code: str | None,
    start_dt: date,
    days_calendar: int,
    end_dt: date,
    is_continuation: bool,
    initial_serie: str | None,
    initial_numar: str | None,
    initial_date: date | None,
    fara_stagiu: bool,
    notes: str,
    created_by: str,
    leave_request_id: int | None = None,
    pay_employer_days: int | None = None,
    pay_fnuass_days: int | None = None,
) -> int:
    """Creează un certificat medical în registru + validări de bază."""
    _ensure_medical_certificates_cols(conn)
    if not table_exists(conn, "medical_certificates"):
        # DB vechi: dacă dintr-un motiv nu s-a creat, îl inițializăm minimal
        conn.execute("""CREATE TABLE IF NOT EXISTS medical_certificates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_key TEXT NOT NULL,
            serie TEXT NOT NULL,
            numar TEXT NOT NULL,
            issued_date TEXT DEFAULT NULL,
            prescription_place TEXT DEFAULT NULL,
            cod_indemnizatie TEXT NOT NULL,
            procent INTEGER DEFAULT NULL,
            diagnostic_code TEXT DEFAULT NULL,
            start_date TEXT NOT NULL,
            days_calendar INTEGER NOT NULL,
            end_date TEXT NOT NULL,
            is_continuation INTEGER NOT NULL DEFAULT 0,
            initial_serie TEXT DEFAULT NULL,
            initial_numar TEXT DEFAULT NULL,
            initial_date TEXT DEFAULT NULL,
            fara_stagiu INTEGER NOT NULL DEFAULT 0,
            pay_employer_days INTEGER DEFAULT NULL,
            pay_fnuass_days INTEGER DEFAULT NULL,
            notes TEXT DEFAULT NULL,
            created_by TEXT NOT NULL,
            created_at TEXT NOT NULL,
            leave_request_id INTEGER DEFAULT NULL,
            UNIQUE(serie, numar)
        );""")
        conn.commit()

    s = safe_str(serie)
    n = safe_str(numar)
    if not s or not n:
        raise ValueError("Serie și număr certificat sunt obligatorii.")
    if int(days_calendar) <= 0:
        raise ValueError("Numărul de zile trebuie să fie >= 1.")

    # dubluri
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM medical_certificates WHERE serie=? AND numar=? LIMIT 1", (s, n))
    if cur.fetchone():
        raise ValueError("Există deja un certificat cu aceeași serie și număr.")

    # suprapunere (pe același angajat)
    if _cm_has_overlap(conn, employee_key, start_dt, end_dt):
        raise ValueError("Există deja un CM care se suprapune pe perioada selectată pentru acest angajat.")

        # calcul automat: zile plătite din fond salarii vs FNUASS (pe episod)
    if pay_employer_days is None or pay_fnuass_days is None:
        pe, pf = compute_cm_payment_split(conn, employee_key, cod_indemnizatie, serie, numar, start_dt, end_dt, is_continuation, initial_serie, initial_numar)
        pay_employer_days = pe
        pay_fnuass_days = pf

    now = datetime.now().isoformat(timespec="seconds")
    cur.execute(
        """INSERT INTO medical_certificates(
                employee_key, serie, numar, issued_date, prescription_place,
                cod_indemnizatie, procent, diagnostic_code,
                start_date, days_calendar, end_date,
                is_continuation, initial_serie, initial_numar, initial_date,
                fara_stagiu, pay_employer_days, pay_fnuass_days, notes,
                created_by, created_at,
                leave_request_id
            ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        (
            safe_str(employee_key),
            s, n,
            (issued_date.isoformat() if issued_date else None),
            (safe_str(prescription_place) if prescription_place else None),
            safe_str(cod_indemnizatie),
            (int(procent) if procent is not None else None),
            (safe_str(diagnostic_code) if diagnostic_code else None),
            start_dt.isoformat(),
            int(days_calendar),
            end_dt.isoformat(),
            1 if is_continuation else 0,
            (safe_str(initial_serie) if initial_serie else None),
            (safe_str(initial_numar) if initial_numar else None),
            (initial_date.isoformat() if initial_date else None),
            1 if fara_stagiu else 0,
            int(pay_employer_days) if pay_employer_days is not None else None,
            int(pay_fnuass_days) if pay_fnuass_days is not None else None,
            (notes or ""),
            safe_str(created_by),
            now,
            (int(leave_request_id) if leave_request_id is not None else None),
        )
    )
    conn.commit()
    return int(cur.lastrowid)

def list_leave_requests(conn: sqlite3.Connection, employee_keys: list[str] | None = None, status: str | None = None) -> pd.DataFrame:
    sql = """SELECT
                id, employee_key, request_type, start_date, end_date,
                weekdays_only, hours_per_day,
                COALESCE(status, status_code) AS status, notes,
                created_by, created_at,
                decision_by, decision_at, decision_reason,
                cm_series, cm_number, cm_type, cm_diag, cm_issuer
             FROM leave_requests
          """
    clauses = []
    params = []
    if employee_keys:
        placeholders = ",".join(["?"] * len(employee_keys))
        clauses.append(f"employee_key IN ({placeholders})")
        params.extend([str(x) for x in employee_keys])
    if status:
        clauses.append("status = ?")
        params.append(status)
    if clauses:
        sql += " WHERE " + " AND ".join(clauses)
    sql += " ORDER BY created_at DESC"
    return pd.read_sql_query(sql, conn, params=params)

def _apply_leave_to_timesheets(conn: sqlite3.Connection, employee_key: str, request_type: str, start_dt: date, end_dt: date, weekdays_only: bool):
    df_all, _ = read_employees(conn)
    row = df_all[df_all["employee_key"]==str(employee_key)]
    snapshot = row.iloc[0].to_dict() if not row.empty else {}

    status_db = LEAVE_TYPE_TO_TS_STATUS.get(request_type, request_type)

    d = start_dt
    while d <= end_dt:
        if weekdays_only and d.weekday() >= 5:  # 5=sâmbătă, 6=duminică
            d += timedelta(days=1)
            continue
        _upsert_timesheet_simple(conn, cfg, str(employee_key), d, status_db, 0.0, snapshot)
        d += timedelta(days=1)

def decide_leave_request(
    conn: sqlite3.Connection,
    request_id: int,
    decision: str,                 # APPROVE / REJECT / CANCEL
    decision_by: str,
    reason: str = ""
):
    decision = (decision or "").upper().strip()
    now = datetime.now().isoformat(timespec="seconds")

    cur = conn.cursor()
    cur.execute("SELECT * FROM leave_requests WHERE id = ?", (int(request_id),))
    r = cur.fetchone()
    if not r:
        raise ValueError("Cererea nu există.")

    current_status = (r["status"] or "").upper()
    if current_status in ("APPROVED","REJECTED","CANCELLED"):
        raise ValueError(f"Cererea este deja în starea: {current_status}")

    if decision in ("APPROVE","APPROVED"):
        new_status = "APPROVED"
        # aplică în timesheets
        # parsează intervalul; dacă lipsește, nu permite aprobarea
        d1 = _parse_iso_date(r["start_date"])
        d2 = _parse_iso_date(r["end_date"])
        if not d1 or not d2:
            raise ValueError("Cererea nu are interval complet (De la / Până la). Completează datele și reîncearcă aprobarea.")
        _apply_leave_to_timesheets(
            conn,
            r["employee_key"],
            r["request_type"],
            d1,
            d2,
            bool(r["weekdays_only"])
        )
    elif decision in ("REJECT","REJECTED"):
        new_status = "REJECTED"
    elif decision in ("CANCEL","CANCELLED"):
        new_status = "CANCELLED"
    else:
        raise ValueError("Decizie invalidă.")

    cur.execute(
        """UPDATE leave_requests
            SET status=?, decision_by=?, decision_at=?, decision_reason=?, updated_at=?
            WHERE id=?
        """,
        (new_status, decision_by, now, reason or "", now, int(request_id))
    )
    conn.commit()



def reset_leave_request_to_pending(conn: sqlite3.Connection, request_id: int):
    """Revine cererea la PENDING (șterge decizia). Compatibil cu status/status_code."""
    now = datetime.now().isoformat(timespec="seconds")
    cols_lr = _table_columns(conn, "leave_requests")
    set_parts = []
    params = []
    if _has_col(cols_lr, "status"):
        set_parts.append("status = ?")
        params.append("PENDING")
    if _has_col(cols_lr, "status_code"):
        set_parts.append("status_code = ?")
        params.append("PENDING")
    # curățăm câmpurile de decizie dacă există
    for col in ["decision_by", "decision_at", "decision_reason"]:
        if _has_col(cols_lr, col):
            set_parts.append(f"{col} = ?")
            params.append(None if col != "decision_reason" else "")
    if _has_col(cols_lr, "updated_at"):
        set_parts.append("updated_at = ?")
        params.append(now)

    params.append(int(request_id))
    sql = "UPDATE leave_requests SET " + ", ".join(set_parts) + " WHERE id = ?"
    conn.execute(sql, tuple(params))
    conn.commit()


def page_pontaj_lunar(cfg: dict, conn: sqlite3.Connection, user_ctx: dict):
    st.subheader("📅 Pontaj lunar")
    st.caption(f"Build: **{APP_BUILD_TAG}** | User: **{user_ctx['username']}** | Rol: **{user_ctx.get('role','')}**")

    df_all, src = read_employees(conn)
    scopes_df = get_user_scopes(conn, user_ctx["username"])
    scopes = scopes_df.drop(columns=["id"], errors="ignore").to_dict("records")
    df_emp = apply_scope_filter(df_all, user_ctx.get("role"), scopes, user_ctx.get("employee_key"))

    if df_emp.empty:
        st.warning("Nu există angajați vizibili pentru acest utilizator.")
        return

    c1, c2, c3 = st.columns([1,1,2])
    with c1:
        year = st.number_input("An", min_value=2020, max_value=2100, value=date.today().year, step=1)
    with c2:
        month = st.selectbox("Luna", list(range(1,13)), index=date.today().month-1)
    with c3:
        st.caption(f"Sursa angajați: **{src}** | Nr. angajați: **{len(df_emp)}**")

    # Interval din "centralizator" (admin/manager)
    role = (user_ctx.get("role") or "user").lower()
    if role in ("admin", "manager"):
        
        st.info("În celule poți scrie **1..12** (ore lucrate) sau coduri (CO/CM/CFP/Liber/Nemotivat/ZLP/EV/DEL/DET).")

    # ------------------------------------------------------------
    # Construim grila (grid) pentru editorul tip Excel
    # ------------------------------------------------------------
    last_day = calendar.monthrange(int(year), int(month))[1]
    day_cols = [str(d) for d in range(1, last_day + 1)]

    base_cols = ["employee_key", "Nume", "Prenume", "CNP"]
    grid = df_emp[base_cols].copy()
    for c in day_cols:
        grid[c] = ""

    # Preluăm pontajul existent din DB pentru luna selectată
    employee_keys = [str(x) for x in df_emp["employee_key"].tolist()]
    ts = _read_timesheets_month(conn, employee_keys, int(year), int(month))

    def _cell_from_ts(status: str, hours: float) -> str:
        s = safe_str(status)
        h = float(hours or 0.0)
        # Convenții scurte pentru afișare în grilă
        if s in ("Lucrat", ""):
            if h > 0:
                # afișăm 1..12 (ore) - fără .0 dacă e întreg
                return str(int(h)) if abs(h - int(h)) < 1e-9 else str(h)
            return ""
        if s == "ZI_LIBERA":
            return "ZLP"
        if s == "Nemotivat":
            return "Nemotivat"
        return s

    if ts is not None and not ts.empty:
        # index pentru viteză
        for _, r in ts.iterrows():
            ek = str(r.get("employee_key", ""))
            wd = safe_str(r.get("work_date", ""))
            if not ek or not wd:
                continue
            try:
                dnum = int(wd.split("-")[2])
            except Exception:
                continue
            if dnum < 1 or dnum > last_day:
                continue
            val = _cell_from_ts(r.get("status", ""), r.get("total_hours", 0.0))
            if val != "":
                grid.loc[grid["employee_key"] == ek, str(dnum)] = val


    # Auto-completare: weekend + sărbători legale (doar dacă celula e goală)
    hol = get_legal_holidays(cfg, int(year))
    for dnum in range(1, last_day + 1):
        wd = date(int(year), int(month), int(dnum))
        col = str(dnum)
        if wd in hol:
            # prioritar sărbătoare legală
            grid.loc[grid[col].astype(str).str.strip() == "", col] = "Sarb."
        elif is_weekend(wd):
            grid.loc[grid[col].astype(str).str.strip() == "", col] = "Sam./D"


    edited = st.data_editor(
        grid,
        use_container_width=True,
        num_rows="fixed",
        column_config={
            "employee_key": st.column_config.TextColumn("Marca", disabled=True),
            "Nume": st.column_config.TextColumn("Nume", disabled=True),
            "Prenume": st.column_config.TextColumn("Prenume", disabled=True),
            "CNP": st.column_config.TextColumn("CNP", disabled=True),
        },
        key=f"pontaj_lunar_{year}_{month}",
    )

    if st.button("💾 Salvează pontaj lunar", type="primary"):
        # Detect changes vs grid
        changes = 0
        for _, emp_row in df_emp.iterrows():
            ek = str(emp_row["employee_key"])
            snap = emp_row.to_dict()
            row_new = edited[edited["employee_key"]==ek].iloc[0]
            row_old = grid[grid["employee_key"]==ek].iloc[0]
            for d in range(1, last_day+1):
                col = str(d)
                nv = safe_str(row_new[col])
                ov = safe_str(row_old[col])
                if nv == ov:
                    continue
                status, hrs = _parse_cell_value(nv)
                wd = date(int(year), int(month), int(d))
                if status == "" and hrs == 0.0:
                    # ștergem intrarea dacă există
                    conn.execute("DELETE FROM timesheets WHERE employee_key=? AND work_date=?", (ek, wd.isoformat()))
                else:
                    _upsert_timesheet_simple(conn, cfg, ek, wd, status, hrs, snap)
                changes += 1

        conn.commit()
        # sincronizăm orele suplimentare în ledger (pentru pagina ⏱ Ore suplimentare)
        try:
            emp_keys_sync = [str(x) for x in df_emp['employee_key'].tolist()]
            start_iso = date(int(year), int(month), 1).isoformat()
            end_iso = date(int(year), int(month), int(last_day)).isoformat()
            ensure_overtime_ledger_from_timesheets(conn, employee_keys=emp_keys_sync, start=start_iso, end=end_iso)
        except Exception:
            pass

        st.success(f"Salvat. Modificări aplicate: {changes}.")
        st.rerun()

def page_pontaj(cfg: dict, conn: sqlite3.Connection, user_ctx: dict):
    st.subheader("🗓️ Pontaj")

    df_all, src = read_employees(conn)
    scopes_df = get_user_scopes(conn, user_ctx["username"])
    scopes = scopes_df.drop(columns=["id"], errors="ignore").to_dict("records")
    df = apply_scope_filter(df_all, user_ctx.get("role"), scopes, user_ctx.get("employee_key"))

    if df.empty:
        st.warning(
            "Nu exista angajati vizibili pentru acest utilizator.\n\n"
            "• admin: verifica tabela employees / employees_cache\n"
            "• user: seteaza employee_key in pontaj_users\n"
            "• manager: adauga cel putin un scope"
        )
        return

    st.caption(f"Sursa angajati: **{src}** | User: **{user_ctx['username']}** | Rol: **{user_ctx.get('role','')}**")

    # select angajat
    if user_ctx.get("employee_key"):
        emp = df.iloc[0]
        employee_key = emp["employee_key"]
    else:
        colF1, colF2, colF3, colF4 = st.columns(4)

        loc_options = ["(Toate)"] + sorted([x for x in df["Locatie"].unique().tolist() if safe_str(x)])
        with colF1:
            sel_loc = st.selectbox("Locatie", loc_options, index=0)
        df1 = df if sel_loc == "(Toate)" else df[df["Locatie"] == sel_loc]

        dir_options = ["(Toate)"] + sorted([x for x in df1["Directie"].unique().tolist() if safe_str(x)])
        with colF2:
            sel_dir = st.selectbox("Directie", dir_options, index=0)
        df2 = df1 if sel_dir == "(Toate)" else df1[df1["Directie"] == sel_dir]

        dep_options = ["(Toate)"] + sorted([x for x in df2["Departament"].unique().tolist() if safe_str(x)])
        with colF3:
            sel_dep = st.selectbox("Departament/Serviciu", dep_options, index=0)
        df3 = df2 if sel_dep == "(Toate)" else df2[df2["Departament"] == sel_dep]

        bir_options = ["(Toate)"] + sorted([x for x in df3["Birou"].unique().tolist() if safe_str(x)])
        with colF4:
            sel_bir = st.selectbox("Birou", bir_options, index=0)
        df4 = df3 if sel_bir == "(Toate)" else df3[df3["Birou"] == sel_bir]

        st.markdown("---")
        emp_options = df4.index.tolist()
        emp_idx = st.selectbox(
            "Angajat",
            emp_options,
            format_func=lambda i: f"{df4.loc[i,'employee_key']} - {df4.loc[i,'FullName']}  [{df4.loc[i,'Departament']} / {df4.loc[i,'Birou']}]"
        )
        emp = df4.loc[emp_idx]
        employee_key = emp["employee_key"]

    snapshot = {
        "Nume": safe_str(emp.get("Nume","")),
        "Prenume": safe_str(emp.get("Prenume","")),
        "CNP": safe_str(emp.get("CNP","")),
        "Locatie": safe_str(emp.get("Locatie","")),
        "Directie": safe_str(emp.get("Directie","")),
        "Departament": safe_str(emp.get("Departament","")),
        "Birou": safe_str(emp.get("Birou","")),
    }

    st.markdown("### 👤 Date angajat (importate)")
    a1, a2, a3, a4 = st.columns(4)
    with a1:
        st.text_input("Nume", value=snapshot["Nume"], disabled=True)
    with a2:
        st.text_input("Prenume", value=snapshot["Prenume"], disabled=True)
    with a3:
        st.text_input("CNP", value=snapshot["CNP"], disabled=True)
    with a4:
        st.text_input("Marca/Key", value=safe_str(employee_key), disabled=True)

    b1, b2, b3, b4 = st.columns(4)
    with b1:
        st.text_input("Locatie", value=snapshot["Locatie"], disabled=True)
    with b2:
        st.text_input("Directie", value=snapshot["Directie"], disabled=True)
    with b3:
        st.text_input("Departament/Serviciu", value=snapshot["Departament"], disabled=True)
    with b4:
        st.text_input("Birou", value=snapshot["Birou"], disabled=True)

    st.markdown("---")
    st.subheader("📱 Pontaj rapid")
    today_local = date.today()

    # stare curentă pontaj azi
    cur_today = conn.cursor()
    cur_today.execute(
        "SELECT start_time, end_time FROM timesheets WHERE employee_key=? AND work_date=? LIMIT 1",
        (safe_str(employee_key), today_local.isoformat()),
    )
    row_today = cur_today.fetchone()
    start_today = safe_str(row_today[0]) if row_today else ""
    end_today = safe_str(row_today[1]) if row_today else ""

    # Popup zilnic la prima deschidere (dacă nu există încă intrare azi)
    username = safe_str(user_ctx.get("username", "")).strip()
    role_l = safe_str(user_ctx.get("role", "user")).strip().lower()
    seen_on_home_key = f"pontaj_popup_seen_on_home_{username}_{today_local.isoformat()}"
    seen_on_home = bool(st.session_state.get(seen_on_home_key, False))
    popup_key = f"pontaj_daily_popup_done_{username}_{today_local.isoformat()}_{safe_str(employee_key)}"
    # În pagina Pontaj nu mai afișăm popup (rămâne doar pe Acasă).
    show_daily_popup = False

    if show_daily_popup:
        @st.dialog("PONTAJ")
        def _pontaj_daily_dialog():
            st.write("Pontaj rapid pentru azi")
            c1, c2 = st.columns(2)
            with c1:
                if st.button("🟢 INTRARE", use_container_width=True, key=f"pontaj_popup_in_{employee_key}_{today_local.isoformat()}"):
                    set_punch(conn, employee_key, today_local, "IN")
                    st.session_state[popup_key] = True
                    st.rerun()
            with c2:
                if st.button("Închide", use_container_width=True, key=f"pontaj_popup_close_{employee_key}_{today_local.isoformat()}"):
                    st.session_state[popup_key] = True
                    st.rerun()

        _pontaj_daily_dialog()

    if start_today and not end_today:
        st.info(f"Ești deja pontat la intrare azi, la **{start_today}**.")
    elif start_today and end_today:
        st.caption(f"Pontaj complet azi: intrare **{start_today}** · ieșire **{end_today}**")
        try:
            t_in = datetime.strptime(start_today, "%H:%M")
            t_out = datetime.strptime(end_today, "%H:%M")
            mins = int((t_out - t_in).total_seconds() // 60)
            if mins >= 0:
                h = mins // 60
                m = mins % 60
                st.caption(f"Ore lucrate azi: **{h:02d}:{m:02d}**")
        except Exception:
            pass

    cA, cB = st.columns(2)
    with cA:
        if st.button("🟢 INTRARE", use_container_width=True):
            if start_today and not end_today:
                st.warning("Ai deja pontaj de intrare. Dacă vrei depontare, folosește butonul IESIRE.")
            elif start_today and end_today:
                st.warning("Ai deja pontaj complet pentru azi.")
            else:
                set_punch(conn, employee_key, today_local, "IN")
                st.success("Intrarea a fost înregistrată.")
                st.rerun()
    with cB:
        if st.button("🔴 IESIRE", use_container_width=True):
            if not start_today:
                st.warning("Nu există pontaj de intrare azi.")
            elif end_today:
                st.warning("Ieșirea este deja înregistrată pentru azi.")
            else:
                set_punch(conn, employee_key, today_local, "OUT")
                st.success("Ieșirea a fost înregistrată.")
                st.rerun()

    st.markdown("---")
    st.subheader("🧾 Pontaj manual pe luna selectata")

    today = date.today()
    year = st.number_input("An", min_value=2000, max_value=2100, value=today.year, step=1)
    month = st.selectbox(
        "Luna",
        options=list(range(1, 13)),
        index=today.month - 1,
        format_func=lambda m: f"{m:02d} - {MONTH_NAMES_RO.get(int(m), str(m))}"
    )


    # ------------------------------------------------------------
    # FIX IMPORTANT: chei stabile pe "pagina" (angajat + an + luna)
    # Evita NotFoundError: removeChild (DOM mismatch la rerun).
    # ------------------------------------------------------------
    page_uid = f"{safe_str(employee_key)}_{int(year)}_{int(month)}"

    # Render guard: cand se schimba page_uid, facem rerun curat o singura data.
    if st.session_state.get("pontaj_page_uid") != page_uid:
        st.session_state["pontaj_page_uid"] = page_uid
        st.rerun()

    default_start = _parse_hhmm_to_time(cfg.get("default_start"), time(8,0))
    default_end = _parse_hhmm_to_time(cfg.get("default_end"), time(16,0))
    standard_daily_hours = float(cfg.get("standard_daily_hours", 8.0))
    allow_cross_day = bool(cfg.get("allow_cross_day_shift", True))

    num_days = calendar.monthrange(int(year), int(month))[1]
    dates_list = [date(int(year), int(month), d) for d in range(1, num_days + 1)]

    status_options = [
        "Lucrat",
        "CO - Concediu de odihna",
        "CM - Concediu medical",
        "CFP - Fara plata",
        "Nemotivat",
        "Liber (weekend / sarbatoare)"
    ]

    rows = []
    totals = {k: 0.0 for k in ["total_hours","normal_hours","night_hours","weekend_hours","holiday_hours","overtime_hours"]}
    days = {k: 0 for k in ["co","cm","cfp","nem","liber"]}

    for d in dates_list:
        weekday = d.weekday()
        weekday_name = ["Luni", "Marti", "Miercuri", "Joi", "Vineri", "Sambata", "Duminica"][weekday]
        is_weekend = weekday >= 5
        is_holiday = False

        with st.container():
            col_date, col_status, col_start, col_end, col_hours = st.columns([1.8, 2.8, 1.5, 1.5, 3.0])

            with col_date:
                st.markdown(f"**{d.strftime('%d.%m.%Y')}**")
                st.caption(weekday_name + (" (Weekend)" if is_weekend else ""))

            default_status_index = status_options.index("Liber (weekend / sarbatoare)" if is_weekend else "Lucrat")
            with col_status:
                status = st.selectbox(
                    "Status",
                    options=status_options,
                    index=default_status_index,
                    key=f"status_{page_uid}_{d.isoformat()}"
                )

            start_t = None
            end_t = None
            seg = {k: 0.0 for k in totals.keys()}
            co = cm = cfp = nem = liber = 0

            if status == "Lucrat":
                with col_start:
                    start_t = st.time_input("Sosire", key=f"start_{page_uid}_{d.isoformat()}", value=default_start)
                with col_end:
                    end_t = st.time_input("Plecare", key=f"end_{page_uid}_{d.isoformat()}", value=default_end)

                seg = calculate_hours_segments(
                    d, start_t, end_t,
                    standard_daily_hours,
                    is_weekend=is_weekend,
                    is_holiday=is_holiday,
                    allow_cross_day=allow_cross_day
                )
                with col_hours:
                    st.markdown(f"**{seg['total_hours']}h** | Noapte: {seg['night_hours']} | Supl.: {seg['overtime_hours']}")
            else:
                with col_start:
                    st.text("-")
                with col_end:
                    st.text("-")
                with col_hours:
                    st.markdown("0h")

                if status.startswith("CO"):
                    co = 1
                elif status.startswith("CM"):
                    cm = 1
                elif status.startswith("CFP"):
                    cfp = 1
                elif status.startswith("Nemotivat"):
                    nem = 1
                else:
                    liber = 1

            for k in totals.keys():
                totals[k] += float(seg[k])

            days["co"] += co
            days["cm"] += cm
            days["cfp"] += cfp
            days["nem"] += nem
            days["liber"] += liber

            rows.append({
                "Data": d.strftime("%d.%m.%Y"),
                "Zi": weekday_name,
                "Status": status,
                "Ora sosire": start_t.strftime("%H:%M") if start_t else "",
                "Ora plecare": end_t.strftime("%H:%M") if end_t else "",
                "Ore totale": seg["total_hours"],
                "Ore normale": seg["normal_hours"],
                "Ore noapte": seg["night_hours"],
                "Ore weekend": seg["weekend_hours"],
                "Ore sarbatoare": seg["holiday_hours"],
                "Ore suplimentare": seg["overtime_hours"],
                "CO (zile)": co,
                "CM (zile)": cm,
                "Fara plata (zile)": cfp,
                "Nemotivat (zile)": nem,
                "Liber (zile)": liber,
            })

    df_manual = pd.DataFrame(rows)
    st.markdown("---")
    st.dataframe(df_manual, use_container_width=True)

    st.write(
        f"Total ore: {totals['total_hours']} | Normale: {totals['normal_hours']} | "
        f"Noapte: {totals['night_hours']} | Supl.: {totals['overtime_hours']}"
    )
    st.write(f"Zile: CO {days['co']} | CM {days['cm']} | CFP {days['cfp']} | Nemotivat {days['nem']} | Liber {days['liber']}")

    if st.button("💾 Salveaza luna in DB"):
        save_timesheet_rows(conn, employee_key, df_manual, snapshot)
        st.success("Luna salvata in DB (cu nume/structura).")

def page_centralizator(conn: sqlite3.Connection, user_ctx: dict):
    st.subheader("🧾 Centralizator concedii (din DB)")

    today = date.today()
    year = st.number_input("An", min_value=2000, max_value=2100, value=today.year, step=1, key="cy")
    month = st.selectbox("Luna", list(range(1,13)), index=today.month-1,
                        format_func=lambda m: f"{m:02d} - {MONTH_NAMES_RO.get(int(m), str(m))}", key="cm")

    start = date(int(year), int(month), 1).isoformat()
    end = date(int(year), int(month), calendar.monthrange(int(year), int(month))[1]).isoformat()

    df = pd.read_sql_query("""
        SELECT
          employee_key AS Angajat,
          MAX(nume) AS Nume,
          MAX(prenume) AS Prenume,
          MAX(departament) AS Departament,
          MAX(birou) AS Birou,
          SUM(co_day) AS CO,
          SUM(cm_day) AS CM,
          SUM(cfp_day) AS CFP,
          SUM(nemotivat_day) AS Nemotivate,
          SUM(liber_day) AS Libere,
          ROUND(SUM(total_hours),2) AS Ore_totale,
          ROUND(SUM(overtime_hours),2) AS Ore_supl,
          ROUND(SUM(night_hours),2) AS Ore_noapte
        FROM timesheets
        WHERE work_date BETWEEN ? AND ?
        GROUP BY employee_key
        ORDER BY employee_key
    """, conn, params=(start, end))

    df_emp_all = load_employees_cached(conn)
    scopes_df = get_user_scopes(conn, user_ctx["username"])
    scopes = scopes_df.drop(columns=["id"], errors="ignore").to_dict("records")
    df_emp = apply_scope_filter(df_emp_all, user_ctx.get("role"), scopes, user_ctx.get("employee_key"))
    allowed_keys = set(df_emp["employee_key"].tolist())
    df = df[df["Angajat"].isin(allowed_keys)].copy()

    st.dataframe(df, use_container_width=True)


# ============================================================
# LOGIN + MAIN
# ============================================================

def login_page(conn: sqlite3.Connection):
    st.title("🔐 Autentificare Pontaj")

    with st.form("login"):
        username = st.text_input("User")
        password = st.text_input("Parola", type="password")
        ok = st.form_submit_button("Intra")

    if ok:
        user_ctx = auth_user(conn, username.strip(), password)
        if not user_ctx:
            st.error("User sau parola gresite (sau user inactiv).")
            return
        st.session_state.authenticated = True
        st.session_state.user_ctx = user_ctx
        st.rerun()






def page_centralizator_co(cfg, conn, user_ctx):
    st.markdown("## 📊 Centralizator CO (toți angajații)")
    st.caption("Sold CO pe 3 ani (an-2 / an-1 / an). Zilele pe an se introduc manual (Alocare CO), consumul se calculează automat din cererile CO aprobate.")

    df_emp = load_employees_cached(conn)
    if df_emp.empty:
        st.info("Nu există angajați.")
        return

    from datetime import date
    year = st.number_input("An curent", min_value=2000, max_value=2100, value=date.today().year, step=1, key="co_central_year")

    rows = []
    for _, r in df_emp.iterrows():
        emp_key = str(r.get("employee_key", ""))
        nume = str(r.get("nume","") or "")
        prenume = str(r.get("prenume","") or "")

        bal = compute_co_balance_3y(conn, emp_key, int(year))
        y2, y1, y0 = bal["years"]
        ent = bal["entitled"]
        used = bal["used_by_year"]
        rem = bal["remaining"]
        rows.append({
            "Marca": emp_key,
            "Nume": nume,
            "Prenume": prenume,
            f"CO alocat {y2}": ent[y2],
            f"CO folosit {y2}": used[y2],
            f"CO rămas {y2}": rem[y2],
            f"CO alocat {y1}": ent[y1],
            f"CO folosit {y1}": used[y1],
            f"CO rămas {y1}": rem[y1],
            f"CO alocat {y0}": ent[y0],
            f"CO folosit {y0}": used[y0],
            f"CO rămas {y0}": rem[y0],
            "Total CO rămas (3 ani)": bal["total_remaining"],
        })

    df = pd.DataFrame(rows)
    st.dataframe(df, use_container_width=True, hide_index=True)

    st.divider()
    st.markdown("### ⬇️ Export")
    bio = BytesIO()
    with pd.ExcelWriter(bio, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Centralizator CO")
    bio.seek(0)
    st.download_button(
        "⬇ Export centralizator CO (Excel)",
        data=bio.getvalue(),
        file_name=f"centralizator_CO_{int(year)}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        key="dl_co_central"
    )




def _centralizator_days_by_flag(conn: sqlite3.Connection, employee_keys: list[str], year: int, month: int, flag_col: str, status_fallback: str) -> pd.DataFrame:
    """Returnează DF: employee_key, days.
    Încearcă să folosească coloana flag (ex: cm_day / telemunca_day). Dacă nu există, face fallback pe status == status_fallback.
    """
    import pandas as pd
    if not employee_keys:
        return pd.DataFrame(columns=["employee_key", "days"])

    cols = set([c.lower() for c in _table_columns(conn, "timesheets")])
    start = date(int(year), int(month), 1).isoformat()
    last_day = calendar.monthrange(int(year), int(month))[1]
    end = date(int(year), int(month), int(last_day)).isoformat()

    CHUNK = 900
    dfs = []
    for i in range(0, len(employee_keys), CHUNK):
        chunk = employee_keys[i:i+CHUNK]
        qmarks = ",".join(["?"] * len(chunk))

        if flag_col.lower() in cols:
            sql = f"""
                SELECT employee_key, SUM(COALESCE({flag_col},0)) AS days
                FROM timesheets
                WHERE work_date BETWEEN ? AND ?
                  AND employee_key IN ({qmarks})
                GROUP BY employee_key
            """
            params = [start, end] + list(chunk)
        else:
            sql = f"""
                SELECT employee_key,
                       SUM(CASE WHEN COALESCE(status,'') = ? THEN 1 ELSE 0 END) AS days
                FROM timesheets
                WHERE work_date BETWEEN ? AND ?
                  AND employee_key IN ({qmarks})
                GROUP BY employee_key
            """
            params = [status_fallback, start, end] + list(chunk)

        dfs.append(pd.read_sql_query(sql, conn, params=params))

    if not dfs:
        return pd.DataFrame(columns=["employee_key", "days"])
    out = pd.concat(dfs, ignore_index=True)
    out["employee_key"] = out["employee_key"].astype(str)
    out["days"] = out["days"].fillna(0).astype(int)
    return out


def page_centralizatoare(cfg, conn, user_ctx):
    st.markdown("## 📊 Centralizatoare")
    st.caption("Alege tipul de centralizator: **CO / CM / Telemuncă** (pe zile).")

    # angajați vizibili (respectăm scope/rol)
    df_all, src = read_employees(conn)
    scopes_df = get_user_scopes(conn, user_ctx["username"])
    scopes = scopes_df.drop(columns=["id"], errors="ignore").to_dict("records")
    df_emp = apply_scope_filter(df_all, user_ctx.get("role"), scopes, user_ctx.get("employee_key"))

    if df_emp.empty:
        st.warning("Nu există angajați vizibili pentru acest utilizator.")
        return

    c1, c2, c3 = st.columns([1,1,2])
    with c1:
        tip = st.selectbox("Tip centralizator", ["CO", "CM", "T"], format_func=lambda x: {"CO":"CO (Concediu odihnă)","CM":"CM (Concediu medical)","T":"T (Telemuncă)"}[x])
    with c2:
        year = st.number_input("An", min_value=2000, max_value=2100, value=date.today().year, step=1, key="cz_year")
    with c3:
        month = st.selectbox("Luna", list(range(1,13)), index=date.today().month-1, key="cz_month")

    # CO rămâne exact cum era, doar că e sub selector
    if tip == "CO":
        page_centralizator_co(cfg, conn, user_ctx)
        return

    # CM / T pe zile, din timesheets
    employee_keys = [str(x) for x in df_emp["employee_key"].tolist()]
    if tip == "CM":
        df_days = _centralizator_days_by_flag(conn, employee_keys, int(year), int(month), "cm_day", "CM")
        title = "Centralizator CM (zile)"
        export_name = f"centralizator_CM_{int(year)}_{int(month):02d}.xlsx"
        sheet = "Centralizator CM"
    else:
        # T = Telemunca
        df_days = _centralizator_days_by_flag(conn, employee_keys, int(year), int(month), "telemunca_day", "Telemunca")
        title = "Centralizator Telemuncă (zile)"
        export_name = f"centralizator_Telemunca_{int(year)}_{int(month):02d}.xlsx"
        sheet = "Centralizator Telemunca"

    # join cu nume/prenume
    show = df_emp.copy()
    # normalize cols
    for a,b in [("Nume","nume"),("Prenume","prenume")]:
        if a not in show.columns and b in show.columns:
            show[a] = show[b]
    show["employee_key"] = show["employee_key"].astype(str)

    show = show.merge(df_days, on="employee_key", how="left")
    show["days"] = show["days"].fillna(0).astype(int)

    out = show[["employee_key","Nume","Prenume","CNP","days"]].rename(columns={
        "employee_key":"Marca",
        "days":"Zile"
    })

    st.markdown(f"### {title}")
    st.caption(f"Sursa angajați: **{src}** | Interval: **{int(year)}-{int(month):02d}**")
    st.dataframe(out, use_container_width=True, hide_index=True)

    st.divider()
    st.markdown("### ⬇️ Export")
    bio = BytesIO()
    with pd.ExcelWriter(bio, engine="openpyxl") as writer:
        out.to_excel(writer, index=False, sheet_name=sheet)
    bio.seek(0)
    st.download_button(
        f"⬇ Export {title} (Excel)",
        data=bio.getvalue(),
        file_name=export_name,
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        key=f"dl_cz_{tip}"
    )


def run_app():
    bootstrap_standalone_ui()
    ensure_dirs()
    cfg = load_config()

    if not cfg.get("use_db"):
        st.error("DB este dezactivat. Activeaza DB in Configurari.")
        return

    try:
        conn = get_db_conn(get_effective_db_path(cfg))
        init_db(conn)
        ensure_default_admin(conn)
    except Exception as e:
        st.error(f"Nu pot deschide DB: {e}")
        return

    if not st.session_state.get("authenticated"):
        login_page(conn)
        st.info("Admin implicit: user **admin** / parola **admin123!** (schimba imediat).")
        return

    user_ctx = st.session_state.get("user_ctx") or {}
    role = (user_ctx.get("role") or "user").lower()

    st.sidebar.title("📌 Meniu principal")
    pages = get_pontaj_pages(role)

    page = st.sidebar.radio(
        "Navigare",
        pages,
        index=0
    )

    st.sidebar.markdown("---")
    st.sidebar.success(f"Conectat: {user_ctx.get('username','')} ({role})")
    st.sidebar.caption(f"DB: {get_effective_db_path(cfg)}")
    if st.sidebar.button("Delogare"):
        st.session_state.authenticated = False
        st.session_state.user_ctx = None
        st.rerun()

    render_pontaj_page(page, cfg, conn, user_ctx)


def get_pontaj_pages(role: str) -> list[str]:
    pages = [
        "Pontaj",
        "Pontaj lunar",
        "Cereri",
        "Centralizatoare",
        "Ore suplimentare",
        "Rapoarte",
        "Configurari pontaj",
    ]
    pages = list(dict.fromkeys(pages))
    if (role or "").lower() in ("admin", "manager"):
        pages.insert(pages.index("Configurari pontaj"), "Administrare utilizatori")
    return pages


def render_pontaj_page(page: str, cfg: dict, conn: sqlite3.Connection, user_ctx: dict):
    if page == "Pontaj":
        page_pontaj(cfg, conn, user_ctx)
    elif page == "Pontaj lunar":
        page_pontaj_lunar(cfg, conn, user_ctx)
    elif page == "Cereri":
        page_cereri_concedii(cfg, conn, user_ctx)
    elif page == "Centralizatoare":
        page_centralizatoare(cfg, conn, user_ctx)
    elif page == "Ore suplimentare":
        page_ore_suplimentare(cfg, conn, user_ctx)
    elif page == "Rapoarte":
        page_rapoarte(conn, user_ctx)
    elif page == "Administrare utilizatori":
        page_admin_utilizatori(conn, user_ctx)
    else:
        page_configurari_pontaj(cfg, conn, user_ctx)


def apply_embedded_pontaj_theme():
    st.markdown(
        """
        <style>
        .st-key-pontaj_embedded_wrap,
        .pontaj-embedded-wrap{
          background: transparent !important;
          color: rgba(226,232,240,0.96);
        }
        .st-key-pontaj_embedded_wrap h1,
        .st-key-pontaj_embedded_wrap h2,
        .st-key-pontaj_embedded_wrap h3,
        .st-key-pontaj_embedded_wrap h4,
        .st-key-pontaj_embedded_wrap p,
        .st-key-pontaj_embedded_wrap label,
        .st-key-pontaj_embedded_wrap span,
        .pontaj-embedded-wrap h1,
        .pontaj-embedded-wrap h2,
        .pontaj-embedded-wrap h3,
        .pontaj-embedded-wrap h4,
        .pontaj-embedded-wrap p,
        .pontaj-embedded-wrap label,
        .pontaj-embedded-wrap span{
          color: rgba(226,232,240,0.96) !important;
        }
        .st-key-pontaj_embedded_wrap div[data-testid="stRadio"] [role="radiogroup"],
        .st-key-pontaj_embedded_wrap div[data-testid="stRadio"] [data-baseweb="radio-group"]{
          display: flex !important;
          flex-wrap: nowrap !important;
          overflow-x: auto !important;
          overflow-y: hidden !important;
          gap: 0 !important;
          margin: 6px 0 14px 0 !important;
          padding: 0 !important;
          border-bottom: 1px solid rgba(148,163,184,0.28) !important;
          scrollbar-width: thin;
          scrollbar-color: rgba(100,116,139,0.8) transparent;
        }
        .st-key-pontaj_embedded_wrap div[data-testid="stRadio"] [role="radiogroup"]::-webkit-scrollbar,
        .st-key-pontaj_embedded_wrap div[data-testid="stRadio"] [data-baseweb="radio-group"]::-webkit-scrollbar{
          height: 8px;
        }
        .st-key-pontaj_embedded_wrap div[data-testid="stRadio"] [role="radiogroup"]::-webkit-scrollbar-thumb,
        .st-key-pontaj_embedded_wrap div[data-testid="stRadio"] [data-baseweb="radio-group"]::-webkit-scrollbar-thumb{
          background: rgba(100,116,139,0.75);
          border-radius: 999px;
        }
        .st-key-pontaj_embedded_wrap div[data-testid="stRadio"] [role="radiogroup"]::-webkit-scrollbar-track,
        .st-key-pontaj_embedded_wrap div[data-testid="stRadio"] [data-baseweb="radio-group"]::-webkit-scrollbar-track{
          background: transparent;
        }
        .st-key-pontaj_embedded_wrap div[data-testid="stRadio"] label,
        .st-key-pontaj_embedded_wrap div[data-testid="stRadio"] label[data-baseweb="radio"]{
          flex: 0 0 auto !important;
          white-space: nowrap !important;
          min-height: 38px !important;
          height: 38px !important;
          padding: 0 18px !important;
          border: none !important;
          border-radius: 0 !important;
          border-bottom: 2px solid transparent !important;
          background: transparent !important;
          color: rgba(226,232,240,0.78) !important;
          font-size: 0.94rem !important;
          font-weight: 600 !important;
          margin: 0 !important;
          transition: color .18s ease, border-color .18s ease !important;
        }
        .st-key-pontaj_embedded_wrap div[data-testid="stRadio"] label > div:first-child,
        .st-key-pontaj_embedded_wrap div[data-testid="stRadio"] label[data-baseweb="radio"] > div:first-child{
          display: none !important;
        }
        .st-key-pontaj_embedded_wrap div[data-testid="stRadio"] label > div:last-child,
        .st-key-pontaj_embedded_wrap div[data-testid="stRadio"] label[data-baseweb="radio"] > div:last-child{
          color: inherit !important;
        }
        .st-key-pontaj_embedded_wrap div[data-testid="stRadio"] label:hover,
        .st-key-pontaj_embedded_wrap div[data-testid="stRadio"] label[data-baseweb="radio"]:hover{
          color: rgba(248,250,252,0.96) !important;
        }
        .st-key-pontaj_embedded_wrap div[data-testid="stRadio"] label:has(input:checked),
        .st-key-pontaj_embedded_wrap div[data-testid="stRadio"] label[data-baseweb="radio"][data-checked="true"],
        .st-key-pontaj_embedded_wrap div[data-testid="stRadio"] label[data-baseweb="radio"]:has([aria-checked="true"]){
          background: transparent !important;
          color: #ffffff !important;
          border-bottom-color: rgba(56,189,248,0.92) !important;
          box-shadow: none !important;
        }
        .st-key-pontaj_embedded_wrap div[data-baseweb="input"] > div,
        .st-key-pontaj_embedded_wrap div[data-baseweb="base-input"] > div,
        .st-key-pontaj_embedded_wrap div[data-baseweb="textarea"] > div,
        .st-key-pontaj_embedded_wrap div[data-baseweb="select"] > div{
          background: rgba(15,23,42,0.72) !important;
          border: 1px solid rgba(148,163,184,0.28) !important;
          border-radius: 12px !important;
        }
        .st-key-pontaj_embedded_wrap input,
        .st-key-pontaj_embedded_wrap textarea,
        .st-key-pontaj_embedded_wrap [data-baseweb="select"] *{
          color: #ffffff !important;
          -webkit-text-fill-color: #ffffff !important;
        }
        .st-key-pontaj_embedded_wrap input::placeholder,
        .st-key-pontaj_embedded_wrap textarea::placeholder{
          color: rgba(241,245,249,0.88) !important;
          -webkit-text-fill-color: rgba(241,245,249,0.88) !important;
          opacity: 1 !important;
        }
        .st-key-pontaj_embedded_wrap div[data-testid="stDataFrame"],
        .st-key-pontaj_embedded_wrap div[data-testid="stTable"]{
          background: rgba(15,23,42,0.62) !important;
          border: 1px solid rgba(148,163,184,0.22) !important;
          border-radius: 12px !important;
        }
        .st-key-pontaj_embedded_wrap .stButton > button{
          background: rgba(15,23,42,0.64) !important;
          border: 1px solid rgba(148,163,184,0.30) !important;
          border-radius: 12px !important;
          color: rgba(241,245,249,0.96) !important;
        }
        .st-key-pontaj_embedded_wrap .stButton > button:hover{
          border-color: rgba(56,189,248,0.62) !important;
          background: rgba(30,41,59,0.78) !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_embedded_pontaj(conn: sqlite3.Connection, cfg: dict, user_ctx: dict):
    init_db(conn)
    ensure_default_admin(conn)
    apply_embedded_pontaj_theme()
    with st.container(key="pontaj_embedded_wrap"):
        st.markdown('<div class="pontaj-embedded-wrap">', unsafe_allow_html=True)
        role = (user_ctx.get("role") or "user").lower()
        pages = get_pontaj_pages(role)

        page = st.radio(
            "Navigare pontaj",
            pages,
            horizontal=True,
            key="pontaj_embedded_nav",
            label_visibility="collapsed",
        )

        render_pontaj_page(page, cfg, conn, user_ctx)
        st.markdown("</div>", unsafe_allow_html=True)

# entry
if __name__ == "__main__":
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if "user_ctx" not in st.session_state:
        st.session_state.user_ctx = None

    run_app()