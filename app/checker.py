# Signed: ASDHEM | AMXME Web Solutions
"""ASDHEM | Free website check (lead magnet): HTTPS, SSL, security headers, speed, SEO basics.

Safety (SSRF): only http/https on ports 80/443, the host must resolve to PUBLIC IP addresses only,
every redirect is re-validated, we connect to the validated IP (no DNS rebinding), 8 s timeout,
max 2 MB read, max 5 redirects."""
import gzip
import http.client
import ipaddress
import re
import socket
import ssl
import time
import zlib
from datetime import datetime
from urllib.parse import urljoin, urlparse

MAX_BYTES = 2_000_000
TIMEOUT = 8
UA = "Mozilla/5.0 (compatible; AMXME-WebsiteCheck/1.0; +https://amxme.info)"


class CheckError(Exception):
    pass


def normalize(url):
    url = (url or "").strip()
    if not url:
        raise CheckError("empty")
    if not re.match(r"^https?://", url, re.I):
        url = "https://" + url
    u = urlparse(url)
    host = (u.hostname or "").lower().rstrip(".")
    if not host or len(url) > 300 or not re.fullmatch(r"[a-z0-9.-]+", host) or "." not in host:
        raise CheckError("invalid")
    return url, host


def _public_ip(host):
    try:
        infos = socket.getaddrinfo(host, None, proto=socket.IPPROTO_TCP)
    except socket.gaierror:
        raise CheckError("dns")
    ips = []
    for info in infos:
        ip = ipaddress.ip_address(info[4][0])
        if (ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_multicast or ip.is_reserved
                or ip.is_unspecified or (ip.version == 6 and ip.ipv4_mapped and not ip.ipv4_mapped.is_global)
                or not ip.is_global):
            raise CheckError("blocked")
        ips.append(str(ip))
    if not ips:
        raise CheckError("dns")
    return ips[0]


class _PinnedHTTPS(http.client.HTTPSConnection):
    def __init__(self, host, ip, **kw):
        super().__init__(host, **kw)
        self._ip = ip

    def connect(self):
        sock = socket.create_connection((self._ip, self.port), self.timeout)
        self.sock = self._context.wrap_socket(sock, server_hostname=self.host)
        cert = self.sock.getpeercert()
        self.tls_info = {"version": self.sock.version(),
                         "expires": datetime.strptime(cert["notAfter"], "%b %d %H:%M:%S %Y %Z") if cert else None}


class _PinnedHTTP(http.client.HTTPConnection):
    def __init__(self, host, ip, **kw):
        super().__init__(host, **kw)
        self._ip = ip

    def connect(self):
        self.sock = socket.create_connection((self._ip, self.port), self.timeout)


def _fetch(url):
    """One request without following redirects. Returns (status, headers(lower), body, ms, tls_info)."""
    u = urlparse(url)
    if u.scheme not in ("http", "https"):
        raise CheckError("blocked")
    port = u.port or (443 if u.scheme == "https" else 80)
    if port not in (80, 443):
        raise CheckError("blocked")
    ip = _public_ip(u.hostname)
    path = (u.path or "/") + (f"?{u.query}" if u.query else "")
    t0 = time.monotonic()
    tls = None
    if u.scheme == "https":
        ctx = ssl.create_default_context()
        conn = _PinnedHTTPS(u.hostname, ip, port=port, timeout=TIMEOUT, context=ctx)
    else:
        conn = _PinnedHTTP(u.hostname, ip, port=port, timeout=TIMEOUT)
    try:
        conn.request("GET", path, headers={"User-Agent": UA, "Accept": "text/html,*/*",
                                            "Accept-Encoding": "gzip, deflate", "Accept-Language": "de,en;q=0.8"})
        r = conn.getresponse()
        raw = r.read(MAX_BYTES)
        ms = int((time.monotonic() - t0) * 1000)
        headers = {k.lower(): v for k, v in r.getheaders()}
        if u.scheme == "https":
            tls = getattr(conn, "tls_info", None)
        return r.status, headers, raw, ms, tls
    except ssl.SSLCertVerificationError:
        raise CheckError("ssl")
    except (socket.timeout, TimeoutError):
        raise CheckError("timeout")
    except (OSError, http.client.HTTPException):
        raise CheckError("connect")
    finally:
        conn.close()


def _decode(body, enc):
    try:
        if enc == "gzip":
            body = gzip.decompress(body)
        elif enc == "deflate":
            body = zlib.decompress(body)
    except (OSError, zlib.error):
        pass
    return body.decode("utf-8", "replace")


def run(url):
    url, host = normalize(url)
    https_url = "https://" + host + "/"
    http_url = "http://" + host + "/"
    # 1) does plain http redirect to https?
    redirects_https = False
    try:
        st, hd, _, _, _ = _fetch(http_url)
        loc = hd.get("location", "")
        redirects_https = st in (301, 302, 307, 308) and loc.lower().startswith("https://")
    except CheckError:
        pass
    # 2) follow the https page (re-validating each hop)
    current, hops, ssl_ok = https_url, 0, True
    try:
        while True:
            status, headers, raw, ms, tls = _fetch(current)
            if status in (301, 302, 303, 307, 308) and headers.get("location") and hops < 5:
                current = urljoin(current, headers["location"])
                hops += 1
                continue
            break
    except CheckError as e:
        if str(e) == "ssl":
            ssl_ok = False
            status, headers, raw, ms, tls = _fetch(http_url)
        else:
            raise
    html = _decode(raw, headers.get("content-encoding", ""))
    low = html.lower()
    checks = []

    def add(key, ok, weight, detail=""):
        checks.append({"key": key, "ok": bool(ok), "weight": weight, "detail": detail})

    days = None
    if tls and tls.get("expires"):
        days = (tls["expires"] - datetime.utcnow()).days
    add("https", ssl_ok and tls is not None, 15)
    add("redirect", redirects_https, 8)
    add("ssl_valid", ssl_ok and days is not None and days > 14, 8, f"{days}" if days is not None else "")
    add("hsts", "strict-transport-security" in headers, 6)
    add("csp", "content-security-policy" in headers, 6)
    add("xcto", headers.get("x-content-type-options", "").lower() == "nosniff", 4)
    add("frame", "x-frame-options" in headers or "frame-ancestors" in headers.get("content-security-policy", ""), 4)
    add("referrer", "referrer-policy" in headers, 3)
    add("speed", ms < 800, 12, f"{ms}")
    add("compression", headers.get("content-encoding") in ("gzip", "br", "deflate", "zstd"), 6)
    add("size", len(raw) < 500_000, 4, f"{round(len(raw) / 1024)}")
    title = re.search(r"<title[^>]*>(.*?)</title>", html, re.I | re.S)
    add("title", title and 10 <= len(title.group(1).strip()) <= 70, 6, (title.group(1).strip()[:80] if title else ""))
    add("description", re.search(r'<meta[^>]+name=["\']description["\'][^>]+content=["\'][^"\']{50,}', html, re.I), 6)
    add("viewport", 'name="viewport"' in low or "name='viewport'" in low, 6)
    add("lang", re.search(r"<html[^>]+lang=", html, re.I), 3)
    add("h1", re.search(r"<h1[\s>]", html, re.I), 3)
    score = round(sum(c["weight"] for c in checks if c["ok"]) / sum(c["weight"] for c in checks) * 100)
    server = headers.get("server", "")
    return {"url": current, "host": host, "score": score, "checks": checks, "ms": ms, "status": status,
            "server": server[:60], "checked_at": datetime.utcnow()}
