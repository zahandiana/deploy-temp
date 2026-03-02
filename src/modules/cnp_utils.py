from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date
from typing import Any, Dict, Optional, Tuple


# Ponderi oficiale pentru cifra de control
_CONTROL_WEIGHTS = "279146358279"

# Coduri județe (suficient pentru uz practic; include București + sectoare)
COUNTY_MAP: Dict[str, str] = {
    "01": "Alba", "02": "Arad", "03": "Argeș", "04": "Bacău", "05": "Bihor",
    "06": "Bistrița-Năsăud", "07": "Botoșani", "08": "Brașov", "09": "Brăila",
    "10": "Buzău", "11": "Caraș-Severin", "12": "Cluj", "13": "Constanța",
    "14": "Covasna", "15": "Dâmbovița", "16": "Dolj", "17": "Galați",
    "18": "Gorj", "19": "Harghita", "20": "Hunedoara", "21": "Ialomița",
    "22": "Iași", "23": "Ilfov", "24": "Maramureș", "25": "Mehedinți",
    "26": "Mureș", "27": "Neamț", "28": "Olt", "29": "Prahova",
    "30": "Satu Mare", "31": "Sălaj", "32": "Sibiu", "33": "Suceava",
    "34": "Teleorman", "35": "Timiș", "36": "Tulcea", "37": "Vaslui",
    "38": "Vâlcea", "39": "Vrancea", "40": "București",
    "41": "București - Sector 1", "42": "București - Sector 2",
    "43": "București - Sector 3", "44": "București - Sector 4",
    "45": "București - Sector 5", "46": "București - Sector 6",
    "51": "Călărași", "52": "Giurgiu",
}


@dataclass(frozen=True)
class CnpInfo:
    raw: str
    cnp: str
    valid: bool
    error: Optional[str] = None

    sex: Optional[str] = None          # "M" / "F"
    birth_date: Optional[date] = None  # datetime.date
    county_code: Optional[str] = None  # "01".."52"
    county_name: Optional[str] = None
    order: Optional[str] = None        # NNN


def sanitize_cnp(raw: str) -> str:
    """Păstrează doar cifrele (util pentru input cu spații/puncte)."""
    return "".join(ch for ch in (raw or "").strip() if ch.isdigit())


def cnp_clean(s: str) -> str:
    """Doar cifre (alias consistent pentru employees, dependents, search)."""
    return re.sub(r"\D+", "", (s or "").strip())


def _century_from_s(s: int) -> Optional[int]:
    if s in (1, 2):
        return 1900
    if s in (3, 4):
        return 1800
    if s in (5, 6, 7, 8):
        return 2000
    return None


def _sex_from_s(s: int) -> Optional[str]:
    if s in (1, 3, 5, 7):
        return "M"
    if s in (2, 4, 6, 8):
        return "F"
    return None


def _control_digit_ok(cnp13: str) -> bool:
    total = 0
    for i in range(12):
        total += int(cnp13[i]) * int(_CONTROL_WEIGHTS[i])
    r = total % 11
    expected = 1 if r == 10 else r
    return expected == int(cnp13[12])


def decode_cnp(
    raw_cnp: str,
    *,
    strict_county: bool = False,
    allow_s_9: bool = False,
) -> CnpInfo:
    """
    Decodează + validează CNP.
    - strict_county=False: dacă JJ nu e în map, nu invalidăm CNP (doar county_name=None)
    - allow_s_9: dacă vrei să accepți S=9 (caz special) ca valid logic, îl tratezi separat.
      Default: False, îl marcăm invalid.
    """
    cnp = cnp_clean(raw_cnp)

    if len(cnp) != 13:
        return CnpInfo(raw=raw_cnp, cnp=cnp, valid=False, error="CNP trebuie să aibă exact 13 cifre.")

    if not cnp.isdigit():
        return CnpInfo(raw=raw_cnp, cnp=cnp, valid=False, error="CNP trebuie să conțină doar cifre.")

    s = int(cnp[0])
    yy = int(cnp[1:3])
    mm = int(cnp[3:5])
    dd = int(cnp[5:7])
    jj = cnp[7:9]
    nnn = cnp[9:12]

    county_name = COUNTY_MAP.get(jj)

    if s == 9 and allow_s_9:
        # dacă vrei, poți implementa aici regula ta pentru S=9
        # momentan îl lăsăm invalid cu mesaj explicit, ca să nu mințim userul.
        return CnpInfo(raw=raw_cnp, cnp=cnp, valid=False, error="S=9 necesită o regulă specială (nu e implementată).")

    century = _century_from_s(s)
    sex = _sex_from_s(s)
    if century is None or sex is None:
        return CnpInfo(raw=raw_cnp, cnp=cnp, valid=False, error="Cifra S (sex/secol) este invalidă.", county_code=jj, county_name=county_name, order=nnn)

    year = century + yy

    try:
        bdate = date(year, mm, dd)
    except ValueError:
        return CnpInfo(raw=raw_cnp, cnp=cnp, valid=False, error="Data nașterii din CNP este invalidă.", sex=sex, county_code=jj, county_name=county_name, order=nnn)

    if strict_county and county_name is None:
        return CnpInfo(raw=raw_cnp, cnp=cnp, valid=False, error="Cod județ invalid/necunoscut.", sex=sex, birth_date=bdate, county_code=jj, order=nnn)

    if not _control_digit_ok(cnp):
        return CnpInfo(raw=raw_cnp, cnp=cnp, valid=False, error="Cifra de control nu corespunde.", sex=sex, birth_date=bdate, county_code=jj, county_name=county_name, order=nnn)

    return CnpInfo(
        raw=raw_cnp,
        cnp=cnp,
        valid=True,
        sex=sex,
        birth_date=bdate,
        county_code=jj,
        county_name=county_name,
        order=nnn,
        error=None,
    )


def format_cnp(cnp: str) -> str:
    """Afișare mai prietenoasă: SYYMMDD JJ NNN C (doar cosmetizare)."""
    c = cnp_clean(cnp)
    if len(c) != 13:
        return c
    return f"{c[0:7]} {c[7:9]} {c[9:12]} {c[12]}"


def cnp_validate(s: str) -> Tuple[bool, str, Dict[str, Any]]:
    """
    Validează CNP (checksum + S + dată nașterii).
    Returns: (valid, message, info_dict).
    info_dict: cnp, dob (date | None), sex ("M"|"F"|None), raw error dacă e cazul.
    CNP gol: considerat valid cu mesaj "CNP gol (opțional)." pentru câmpuri opționale.
    """
    cnp = cnp_clean(s)
    info: Dict[str, Any] = {"cnp": cnp, "dob": None, "sex": None}

    if not cnp:
        return True, "CNP gol (opțional).", info

    dec = decode_cnp(s, strict_county=False, allow_s_9=False)
    info["dob"] = dec.birth_date
    info["sex"] = dec.sex
    if dec.valid:
        return True, "CNP valid.", info
    return False, dec.error or "CNP invalid.", info


def cnp_parse(s: str) -> Dict[str, Any]:
    """
    Parsează CNP într-un dict: valid, cnp (13 cifre curat), birth_date, sex.
    Aceeași logică ca decode_cnp / cnp_validate, format simplu pentru UI și search.
    """
    dec = decode_cnp(s, strict_county=False, allow_s_9=False)
    return {
        "valid": dec.valid,
        "cnp": dec.cnp,
        "birth_date": dec.birth_date,
        "sex": dec.sex,
    }


def cnp_birthdate(cnp: str) -> Optional[date]:
    """Returnează data nașterii din CNP (13 cifre) sau None. Folosește aceeași logică ca decode_cnp."""
    dec = decode_cnp(cnp, strict_county=False, allow_s_9=False)
    return dec.birth_date if dec.valid else None
