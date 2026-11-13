<!-- Signed: ASDHEM | AMXME Web Solutions -->
# AMXME Web Solutions – website

Flask web stranica sa admin panelom (sadržaj, usluge, portfolio, poruke, posjetioci, 2FA, Under Construction mod sa preview linkovima).

**Potrebno:** VPS sa Ubuntu 22.04+ ili Debian 12+, root/sudo pristup i domena čiji A zapis (i `www`) pokazuje na IP tog servera.

## Instalacija na novi VPS

```bash
# 1. git
sudo apt update && sudo apt install -y git

# 2. preuzmi kod (privatni repo traži GitHub token kao lozinku – vidi dole)
git clone https://github.com/<KORISNIK>/<REPO>.git ~/amxme
cd ~/amxme

# 3. instaliraj  (domena, tvoj email za SSL, ime admina)
sudo bash install.sh tvojadomena.com tvoj@email.com admin
```

Na kraju skripta ispiše **admin lozinku**. Prijava je na `https://tvojadomena.com/admin`. Odmah promijeni lozinku i uključi 2FA (Admin → Account).

Skripta sama:
- instalira Python, nginx i certbot;
- pravi korisnika `amxme` i kopira kod u `/opt/amxme`;
- generiše tajni ključ u `.env`;
- pravi bazu i admin nalog;
- podiže systemd servis i nginx (rate limit, zaštita, gzip);
- uzima besplatni HTTPS certifikat.

Ako HTTPS ne uspije jer DNS još ne pokazuje na server, kasnije pokreni:
```bash
sudo certbot --nginx --redirect -d tvojadomena.com -d www.tvojadomena.com
```

## Ažuriranje (kad izađe nova verzija na GitHubu)

```bash
cd ~/amxme
git pull
sudo bash update.sh
```
`update.sh` prvo napravi backup koda i baze u `/opt/amxme/backups/`. Ne dira `.env`, bazu ni uploadovane slike.

## Email za kontakt formu (opcionalno)

U `/opt/amxme/.env` popuni `SMTP_*` vrijednosti, pa pokreni `sudo systemctl restart amxme`.

## Prebacivanje postojećeg sadržaja sa starog servera

Baza i slike nisu na GitHubu (tu su poruke, IP adrese posjetilaca i admin nalog). Da preneseš sve:
```bash
# na STAROM serveru
sudo tar -C /opt/amxme -czf ~/amxme-data.tgz data
# kopiraj ~/amxme-data.tgz na novi server (npr. scp), pa na NOVOM:
sudo systemctl stop amxme
sudo tar -C /opt/amxme -xzf ~/amxme-data.tgz
sudo chown -R amxme:amxme /opt/amxme/data && sudo chmod 711 /opt/amxme/data && sudo chmod 755 /opt/amxme/data/uploads
cd ~/amxme && sudo bash update.sh
```
Nakon toga važi stari admin nalog (lozinka i 2FA).

## Privatni repo – kako klonirati

GitHub → Settings → Developer settings → Personal access tokens → **Fine-grained token**:
- pristup samo ovom repou;
- dozvola *Contents: Read-only*.

Kod `git clone` upiši svoje GitHub korisničko ime, a token zalijepi kao lozinku.

## Korisne komande

```bash
sudo systemctl status amxme          # radi li
sudo journalctl -u amxme -n 50       # zadnje greške
sudo -u amxme /opt/amxme/.venv/bin/flask --app wsgi create-admin admin   # reset admin lozinke
```

## Jezici (EN / DE / HR)

- Engleski: `/`, njemački: `/de/`, hrvatski: `/hr/` (isto za `/imprint` i `/privacy`).
- Posjetilac se pri prvoj posjeti automatski preusmjeri na jezik svog browsera; prekidač jezika je u meniju i footeru.
- U adminu svaka stranica s tekstom i svaka stavka (usluge, FAQ, ...) ima tabove **English / Deutsch / Hrvatski**. Prazno polje u prevodu = prikazuje se engleski tekst.
- Tekstovi dugmadi i forme su u `app/i18n.py`, pravne stranice u `app/templates/legal/`.
- Nova baza: `flask init-db` napravi sve tabele. Postojeća baza bez kolone `i18n` treba jednom `ALTER TABLE <tabela> ADD COLUMN i18n TEXT DEFAULT ''` za `service`, `feature`, `project`, `faq`.
