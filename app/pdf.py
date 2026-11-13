# Signed: ASDHEM | AMXME Web Solutions
"""ASDHEM | Tiny PDF writer with an embedded TrueType font (full Unicode: č ć đ š ž ä ö ü ß €).
No external libraries – used for invoices."""
import struct
import zlib
from datetime import datetime

FONT_DIR = "/usr/share/fonts/truetype/liberation"
A4 = (595.28, 841.89)


class TTF:
    def __init__(self, path, name):
        self.name = name
        with open(path, "rb") as f:
            self.data = f.read()
        d = self.data
        n = struct.unpack(">H", d[4:6])[0]
        self.tables = {}
        for i in range(n):
            tag, _, off, ln = struct.unpack(">4sIII", d[12 + 16 * i: 28 + 16 * i])
            self.tables[tag.decode("latin-1")] = (off, ln)
        head = self.tables["head"][0]
        self.upem = struct.unpack(">H", d[head + 18: head + 20])[0]
        self.bbox = struct.unpack(">hhhh", d[head + 36: head + 44])
        hhea = self.tables["hhea"][0]
        self.ascent, self.descent = struct.unpack(">hh", d[hhea + 4: hhea + 8])
        nmetrics = struct.unpack(">H", d[hhea + 34: hhea + 36])[0]
        hmtx = self.tables["hmtx"][0]
        self.adv = [struct.unpack(">H", d[hmtx + 4 * i: hmtx + 4 * i + 2])[0] for i in range(nmetrics)]
        self.cmap = self._cmap()
        self.used = {}

    def _cmap(self):
        d = self.data
        base = self.tables["cmap"][0]
        n = struct.unpack(">H", d[base + 2: base + 4])[0]
        sub = None
        for i in range(n):
            pid, eid, off = struct.unpack(">HHI", d[base + 4 + 8 * i: base + 12 + 8 * i])
            if (pid, eid) in ((3, 1), (0, 3)) and struct.unpack(">H", d[base + off: base + off + 2])[0] == 4:
                sub = base + off
                break
        segx2 = struct.unpack(">H", d[sub + 6: sub + 8])[0]
        seg = segx2 // 2
        ends = struct.unpack(f">{seg}H", d[sub + 14: sub + 14 + segx2])
        starts = struct.unpack(f">{seg}H", d[sub + 16 + segx2: sub + 16 + 2 * segx2])
        deltas = struct.unpack(f">{seg}h", d[sub + 16 + 2 * segx2: sub + 16 + 3 * segx2])
        ro_pos = sub + 16 + 3 * segx2
        ranges = struct.unpack(f">{seg}H", d[ro_pos: ro_pos + segx2])
        cmap = {}
        for i in range(seg):
            for cp in range(starts[i], min(ends[i], 0xFFFE) + 1):
                if ranges[i] == 0:
                    g = (cp + deltas[i]) & 0xFFFF
                else:
                    p = ro_pos + 2 * i + ranges[i] + 2 * (cp - starts[i])
                    g = struct.unpack(">H", d[p: p + 2])[0]
                    if g:
                        g = (g + deltas[i]) & 0xFFFF
                if g:
                    cmap[cp] = g
        return cmap

    def gid(self, ch):
        g = self.cmap.get(ord(ch), self.cmap.get(ord("?"), 0))
        self.used[g] = ch
        return g

    def width(self, text, size):
        total = 0
        for ch in text:
            g = self.cmap.get(ord(ch), 0)
            total += self.adv[g] if g < len(self.adv) else self.adv[-1]
        return total * size / self.upem

    def encode(self, text):
        return "".join(f"{self.gid(ch):04X}" for ch in text)


class PDF:
    def __init__(self, title="", author=""):
        self.fonts = {"R": TTF(f"{FONT_DIR}/LiberationSans-Regular.ttf", "LiberationSans"),
                      "B": TTF(f"{FONT_DIR}/LiberationSans-Bold.ttf", "LiberationSans-Bold")}
        self.pages = []
        self.title, self.author = title, author
        self.new_page()

    def new_page(self):
        self.ops = []
        self.pages.append(self.ops)

    @staticmethod
    def _rgb(c):
        return " ".join(f"{v / 255:.3f}" for v in c)

    def text(self, x, y, s, size=10, font="R", color=(43, 39, 80), align="left"):
        s = str(s)
        f = self.fonts[font]
        if align == "right":
            x -= f.width(s, size)
        elif align == "center":
            x -= f.width(s, size) / 2
        self.ops.append(f"BT {self._rgb(color)} rg /F{font} {size} Tf {x:.2f} {y:.2f} Td <{f.encode(s)}> Tj ET")

    def width(self, s, size=10, font="R"):
        return self.fonts[font].width(str(s), size)

    def wrap(self, s, max_w, size=10, font="R"):
        lines = []
        for para in str(s).split("\n"):
            line = ""
            for word in para.split(" "):
                test = (line + " " + word).strip()
                if self.width(test, size, font) <= max_w or not line:
                    line = test
                else:
                    lines.append(line)
                    line = word
            lines.append(line)
        return lines

    def line(self, x1, y1, x2, y2, w=0.6, color=(221, 214, 254)):
        self.ops.append(f"{self._rgb(color)} RG {w} w {x1:.2f} {y1:.2f} m {x2:.2f} {y2:.2f} l S")

    def rect(self, x, y, w, h, fill=(245, 243, 255)):
        self.ops.append(f"{self._rgb(fill)} rg {x:.2f} {y:.2f} {w:.2f} {h:.2f} re f")

    def output(self):
        objs = []

        def add(body):
            objs.append(body)
            return len(objs)

        catalog = add(None)
        pages_id = add(None)
        font_ids = {}
        for key, f in self.fonts.items():
            ff = zlib.compress(f.data, 9)
            file_id = add(b"<< /Length %d /Length1 %d /Filter /FlateDecode >>\nstream\n" % (len(ff), len(f.data)) + ff + b"\nendstream")
            sc = 1000 / f.upem
            bbox = " ".join(str(int(v * sc)) for v in f.bbox)
            desc_id = add(f"<< /Type /FontDescriptor /FontName /{f.name} /Flags 32 /FontBBox [{bbox}] /ItalicAngle 0 "
                          f"/Ascent {int(f.ascent * sc)} /Descent {int(f.descent * sc)} /CapHeight {int(f.ascent * sc * .7)} "
                          f"/StemV 80 /FontFile2 {file_id} 0 R >>".encode())
            widths = " ".join(f"{g} [{int((f.adv[g] if g < len(f.adv) else f.adv[-1]) * sc)}]" for g in sorted(f.used))
            cid_id = add(f"<< /Type /Font /Subtype /CIDFontType2 /BaseFont /{f.name} /CIDSystemInfo << /Registry (Adobe) "
                         f"/Ordering (Identity) /Supplement 0 >> /FontDescriptor {desc_id} 0 R /DW 1000 /W [{widths}] "
                         f"/CIDToGIDMap /Identity >>".encode())
            bf = "\n".join(f"<{g:04X}> <{ord(ch):04X}>" for g, ch in sorted(f.used.items()) if ord(ch) <= 0xFFFF)
            cmap = ("/CIDInit /ProcSet findresource begin 12 dict begin begincmap /CIDSystemInfo << /Registry (Adobe) "
                    "/Ordering (UCS) /Supplement 0 >> def /CMapName /Adobe-Identity-UCS def /CMapType 2 def "
                    "1 begincodespacerange <0000> <FFFF> endcodespacerange "
                    f"{len(f.used)} beginbfchar\n{bf}\nendbfchar endcmap CMapName currentdict /CMap defineresource pop end end").encode()
            tu = zlib.compress(cmap)
            tu_id = add(b"<< /Length %d /Filter /FlateDecode >>\nstream\n" % len(tu) + tu + b"\nendstream")
            font_ids[key] = add(f"<< /Type /Font /Subtype /Type0 /BaseFont /{f.name} /Encoding /Identity-H "
                                f"/DescendantFonts [{cid_id} 0 R] /ToUnicode {tu_id} 0 R >>".encode())
        fonts = " ".join(f"/F{k} {v} 0 R" for k, v in font_ids.items())
        page_ids = []
        for ops in self.pages:
            content = zlib.compress("\n".join(ops).encode("latin-1"))
            cid = add(b"<< /Length %d /Filter /FlateDecode >>\nstream\n" % len(content) + content + b"\nendstream")
            page_ids.append(add(f"<< /Type /Page /Parent {pages_id} 0 R /MediaBox [0 0 {A4[0]} {A4[1]}] "
                                f"/Resources << /Font << {fonts} >> >> /Contents {cid} 0 R >>".encode()))
        objs[catalog - 1] = f"<< /Type /Catalog /Pages {pages_id} 0 R >>".encode()
        objs[pages_id - 1] = f"<< /Type /Pages /Kids [{' '.join(f'{p} 0 R' for p in page_ids)}] /Count {len(page_ids)} >>".encode()

        def pdfstr(s):
            return "<FEFF" + s.encode("utf-16-be").hex().upper() + ">"
        info = add(f"<< /Title {pdfstr(self.title)} /Author {pdfstr(self.author)} /Producer {pdfstr('ASDHEM · AMXME Web Solutions')} "
                   f"/CreationDate (D:{datetime.now():%Y%m%d%H%M%S}) >>".encode())
        out = bytearray(b"%PDF-1.7\n%\xe2\xe3\xcf\xd3\n% Signed: ASDHEM | AMXME Web Solutions\n")
        offsets = []
        for i, body in enumerate(objs, 1):
            offsets.append(len(out))
            out += b"%d 0 obj\n" % i + body + b"\nendobj\n"
        xref = len(out)
        out += b"xref\n0 %d\n0000000000 65535 f \n" % (len(objs) + 1)
        out += b"".join(b"%010d 00000 n \n" % o for o in offsets)
        out += b"trailer\n<< /Size %d /Root %d 0 R /Info %d 0 R >>\nstartxref\n%d\n%%%%EOF\n" % (len(objs) + 1, catalog, info, xref)
        return bytes(out)
