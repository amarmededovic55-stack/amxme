# Signed: ASDHEM | AMXME Web Solutions
# ASDHEM | migration v3: new tables/columns + service pages, blog articles, portfolio, monitors
import json
from sqlalchemy import text
from wsgi import app
from app.extensions import db
from app.models import Monitor, Post, Project, Service, Activity

J = lambda d: json.dumps(d, ensure_ascii=False)

SERVICE_PAGES = {
    "Custom Website Development": ("web-design", {
        "en": """## A website that works as hard as you do
Your website is often the first impression a customer gets. We design and build fast, modern websites that look great on every device and make it easy for visitors to contact you.

## What you get
- A unique design that fits your brand – no generic template look
- Mobile-first, responsive layout and fast loading times
- Clear structure, good texts and a strong call to action
- SEO basics from day one: titles, descriptions, structured data, sitemap
- Imprint and privacy policy pages prepared for German law
- Optional admin panel so you can change texts and images yourself

## How it works
We start with a short conversation about your goals. You receive a non-binding offer, then we design, build and show you previews along the way. Nothing goes live without your OK.""",
        "de": """## Eine Website, die für Sie arbeitet
Ihre Website ist oft der erste Eindruck, den Kunden von Ihnen bekommen. Wir gestalten und entwickeln schnelle, moderne Websites, die auf jedem Gerät gut aussehen und es Besuchern leicht machen, Sie zu kontaktieren.

## Das bekommen Sie
- Ein eigenes Design passend zu Ihrer Marke – kein austauschbarer Baukasten-Look
- Mobile-first, responsives Layout und kurze Ladezeiten
- Klare Struktur, gute Texte und eine deutliche Handlungsaufforderung
- SEO-Grundlagen ab dem ersten Tag: Titel, Beschreibungen, strukturierte Daten, Sitemap
- Impressum und Datenschutzerklärung nach deutschem Recht vorbereitet
- Optionaler Admin-Bereich, damit Sie Texte und Bilder selbst ändern können

## So läuft es ab
Wir starten mit einem kurzen Gespräch über Ihre Ziele. Sie erhalten ein unverbindliches Angebot, dann gestalten und bauen wir und zeigen Ihnen unterwegs Zwischenstände. Nichts geht ohne Ihr OK online.""",
        "hr": """## Web stranica koja radi za vas
Vaša web stranica često je prvi dojam koji kupac dobije. Dizajniramo i izrađujemo brze, moderne stranice koje izgledaju odlično na svakom uređaju i posjetiteljima olakšavaju da vas kontaktiraju.

## Što dobivate
- Vlastiti dizajn prilagođen vašem brendu – bez izgleda generičkog predloška
- Responzivan dizajn prilagođen mobitelima i brzo učitavanje
- Jasnu strukturu, dobre tekstove i jasan poziv na akciju
- Osnove SEO-a od prvog dana: naslovi, opisi, strukturirani podaci, sitemap
- Pripremljene stranice Impressum i zaštite privatnosti prema njemačkom pravu
- Po želji administracijsko sučelje za samostalno mijenjanje tekstova i slika

## Kako to ide
Počinjemo kratkim razgovorom o vašim ciljevima. Dobivate neobvezujuću ponudu, zatim dizajniramo, izrađujemo i usput vam pokazujemo napredak. Ništa ne ide online bez vašeg odobrenja."""}),
    "Web Hosting": ("web-hosting", {
        "en": """## Hosting you never have to think about
We host your website on carefully maintained servers in the European Union – fast, secure and GDPR-friendly. You get one contact person for website and hosting, so nobody points fingers when something needs fixing.

## Included
- Free SSL certificate that renews automatically
- Regular backups of files and databases
- Firewall, hardened server configuration and security updates
- Uptime monitoring – we are alerted when your site is not reachable
- Help with domain and DNS settings
- Moving your existing website to us, with as little downtime as possible

## Status you can check yourself
The availability of our servers is shown publicly on our status page, and clients see their own websites, SSL dates and invoices in the client portal.""",
        "de": """## Hosting, um das Sie sich nicht kümmern müssen
Wir hosten Ihre Website auf sorgfältig gewarteten Servern in der Europäischen Union – schnell, sicher und DSGVO-freundlich. Sie haben einen Ansprechpartner für Website und Hosting, niemand schiebt die Verantwortung hin und her.

## Inklusive
- Kostenloses SSL-Zertifikat mit automatischer Verlängerung
- Regelmäßige Backups von Dateien und Datenbanken
- Firewall, gehärtete Serverkonfiguration und Sicherheitsupdates
- Verfügbarkeits-Monitoring – wir werden informiert, wenn Ihre Seite nicht erreichbar ist
- Hilfe bei Domain- und DNS-Einstellungen
- Umzug Ihrer bestehenden Website zu uns mit möglichst wenig Ausfallzeit

## Status, den Sie selbst prüfen können
Die Verfügbarkeit unserer Server zeigen wir öffentlich auf unserer Statusseite. Kunden sehen im Kundenportal ihre eigenen Websites, SSL-Laufzeiten und Rechnungen.""",
        "hr": """## Hosting o kojem ne morate razmišljati
Vašu web stranicu hostamo na pažljivo održavanim poslužiteljima u Europskoj uniji – brzo, sigurno i u skladu s GDPR-om. Imate jednu kontakt osobu za stranicu i hosting, pa nitko ne prebacuje odgovornost.

## Uključeno
- Besplatan SSL certifikat koji se automatski obnavlja
- Redovite sigurnosne kopije datoteka i baza podataka
- Vatrozid, zaštićena konfiguracija poslužitelja i sigurnosna ažuriranja
- Praćenje dostupnosti – dobivamo obavijest ako stranica nije dostupna
- Pomoć oko postavki domene i DNS-a
- Preseljenje postojeće stranice k nama uz što kraći prekid rada

## Status koji možete sami provjeriti
Dostupnost naših poslužitelja javno prikazujemo na statusnoj stranici, a klijenti u portalu vide svoje stranice, trajanje SSL certifikata i račune."""}),
    "Website Maintenance": ("website-maintenance", {
        "en": """## Your website stays safe and up to date
A website is never really finished. Software needs updates, content changes and small problems should be fixed before visitors notice them. We take care of that for you.

## What we do
- Security and software updates
- Regular backups and restore if something goes wrong
- Fixing bugs and broken links
- Performance checks and optimisation
- Small text and image changes on request
- Personal technical support by email

## Why it matters
Outdated websites are the most common way attackers get in, and slow pages lose visitors and Google rankings. Regular care costs far less than repairing a hacked or broken site.""",
        "de": """## Ihre Website bleibt sicher und aktuell
Eine Website ist nie ganz fertig. Software braucht Updates, Inhalte ändern sich und kleine Probleme sollten behoben werden, bevor Besucher sie bemerken. Darum kümmern wir uns.

## Das übernehmen wir
- Sicherheits- und Software-Updates
- Regelmäßige Backups und Wiederherstellung im Ernstfall
- Behebung von Fehlern und defekten Links
- Performance-Prüfung und Optimierung
- Kleine Text- und Bildänderungen auf Wunsch
- Persönlicher technischer Support per E-Mail

## Warum das wichtig ist
Veraltete Websites sind das häufigste Einfallstor für Angreifer, und langsame Seiten verlieren Besucher und Google-Platzierungen. Regelmäßige Pflege kostet viel weniger als die Reparatur einer gehackten oder defekten Seite.""",
        "hr": """## Vaša stranica ostaje sigurna i ažurna
Web stranica nikad nije posve gotova. Softver treba ažuriranja, sadržaj se mijenja, a male probleme treba riješiti prije nego ih posjetitelji primijete. O tome brinemo mi.

## Što radimo
- Sigurnosna i softverska ažuriranja
- Redovite sigurnosne kopije i vraćanje ako nešto pođe po zlu
- Ispravljanje grešaka i neispravnih poveznica
- Provjera i optimizacija brzine
- Male izmjene tekstova i slika na zahtjev
- Osobna tehnička podrška e-mailom

## Zašto je to važno
Zastarjele stranice najčešći su ulaz za napadače, a spore stranice gube posjetitelje i pozicije na Googleu. Redovito održavanje košta puno manje od popravka hakirane ili pokvarene stranice."""}),
}
OTHER_SERVICES = {
    "Forum Development": {
        "de": {"title": "Forenentwicklung", "description": "Lebendige Diskussionsforen und Community-Plattformen – installiert, eingerichtet, gestaltet und gewartet von uns.",
               "items": "Individuelle Diskussionsforen\nCommunity-Plattformen\nForen-Installation und Konfiguration\nEigene Themes und Anpassungen\nForen-Wartung und Support"},
        "hr": {"title": "Izrada foruma", "description": "Zanimljivi forumi za raspravu i platforme za zajednice – instalirani, postavljeni, dizajnirani i održavani za vas.",
               "items": "Forumi za raspravu po mjeri\nPlatforme za zajednice\nInstalacija i konfiguracija foruma\nVlastite teme i prilagodbe\nOdržavanje i podrška foruma"}},
    "Domain Services": {
        "de": {"title": "Domain-Services", "description": "Die passende Domain finden, registrieren und verwalten – mit korrekt eingerichtetem DNS und SSL ab dem ersten Tag.",
               "items": "Domain-Registrierung\nDNS-Konfiguration\nDomain-Transfers\nSSL-Zertifikate"},
        "hr": {"title": "Usluge domena", "description": "Pronađite, registrirajte i upravljajte pravom domenom – s ispravno postavljenim DNS-om i SSL-om od prvog dana.",
               "items": "Registracija domene\nKonfiguracija DNS-a\nPrijenos domene\nSSL certifikati"}},
}
POSTS = [
    ("website-checklist-germany", {
        "en": ("6 things every business website in Germany needs",
               "Imprint, privacy policy, SSL, mobile layout, speed and a clear contact path – a short checklist to avoid warnings and lost customers.",
               """In Germany a business website is not only a matter of design. Some points are required by law, others decide whether visitors stay or leave.

## 1. A complete imprint (Impressum)
Every commercial website needs an imprint with your full name, a postal address you can be reached at and a fast way to contact you (§ 5 DDG). Missing details are one of the most common reasons for costly warning letters.

## 2. A privacy policy that matches reality
Your privacy policy must describe what your website really does: hosting, contact form, cookies, analytics. Copying a random template is risky – it has to fit your site.

## 3. HTTPS everywhere
An SSL certificate is free today. Without it browsers show "Not secure" and contact forms send data unencrypted.

## 4. Mobile first
Most visitors arrive on a phone. Text must be readable and buttons easy to tap without zooming.

## 5. Speed
Every extra second of loading time costs visitors. Compressed images, caching and a good server make a big difference.

## 6. A clear way to contact you
Visitors should always see how to reach you: a visible contact button, a short form and your email address.

Want to know where your website stands? Try our free [website check](/check) – it takes ten seconds."""),
        "de": ("6 Dinge, die jede Firmen-Website in Deutschland braucht",
               "Impressum, Datenschutzerklärung, SSL, mobile Ansicht, Geschwindigkeit und ein klarer Kontaktweg – eine kurze Checkliste gegen Abmahnungen und verlorene Kunden.",
               """In Deutschland ist eine Firmen-Website nicht nur eine Frage des Designs. Manche Punkte schreibt das Gesetz vor, andere entscheiden darüber, ob Besucher bleiben oder gehen.

## 1. Ein vollständiges Impressum
Jede geschäftliche Website braucht ein Impressum mit vollständigem Namen, einer ladungsfähigen Anschrift und einer schnellen Kontaktmöglichkeit (§ 5 DDG). Fehlende Angaben sind einer der häufigsten Gründe für teure Abmahnungen.

## 2. Eine Datenschutzerklärung, die zur Website passt
Die Datenschutzerklärung muss beschreiben, was Ihre Website wirklich tut: Hosting, Kontaktformular, Cookies, Statistik. Eine beliebige Vorlage zu kopieren ist riskant – sie muss zu Ihrer Seite passen.

## 3. Überall HTTPS
Ein SSL-Zertifikat ist heute kostenlos. Ohne zeigen Browser „Nicht sicher“ an und Kontaktformulare senden Daten unverschlüsselt.

## 4. Mobile zuerst
Die meisten Besucher kommen mit dem Smartphone. Texte müssen ohne Zoomen lesbar und Buttons leicht antippbar sein.

## 5. Geschwindigkeit
Jede zusätzliche Sekunde Ladezeit kostet Besucher. Komprimierte Bilder, Caching und ein guter Server machen einen großen Unterschied.

## 6. Ein klarer Kontaktweg
Besucher sollten immer sehen, wie sie Sie erreichen: ein sichtbarer Kontakt-Button, ein kurzes Formular und Ihre E-Mail-Adresse.

Wie steht Ihre Website da? Testen Sie unseren kostenlosen [Website-Check](/de/check) – er dauert zehn Sekunden."""),
        "hr": ("6 stvari koje treba svaka poslovna web stranica u Njemačkoj",
               "Impressum, izjava o privatnosti, SSL, prikaz na mobitelu, brzina i jasan kontakt – kratka lista za izbjegavanje opomena i izgubljenih kupaca.",
               """U Njemačkoj poslovna web stranica nije samo pitanje dizajna. Neke stvari propisuje zakon, a druge odlučuju hoće li posjetitelji ostati ili otići.

## 1. Potpun Impressum
Svaka poslovna stranica treba Impressum s punim imenom, adresom na kojoj ste dostupni i brzim načinom kontakta (§ 5 DDG). Nepotpuni podaci jedan su od najčešćih razloga za skupe opomene.

## 2. Izjava o privatnosti koja odgovara stranici
Izjava o privatnosti mora opisivati što vaša stranica stvarno radi: hosting, kontaktni obrazac, kolačiće, statistiku. Kopiranje bilo kakvog predloška je rizično – mora odgovarati vašoj stranici.

## 3. HTTPS posvuda
SSL certifikat danas je besplatan. Bez njega preglednici prikazuju „Nije sigurno”, a obrasci šalju podatke nešifrirano.

## 4. Prvo mobitel
Većina posjetitelja dolazi s mobitela. Tekst mora biti čitljiv bez zumiranja, a gumbi laki za dodir.

## 5. Brzina
Svaka dodatna sekunda učitavanja košta posjetitelje. Komprimirane slike, predmemorija i dobar poslužitelj čine veliku razliku.

## 6. Jasan način kontakta
Posjetitelji uvijek trebaju vidjeti kako vas mogu dobiti: vidljiv gumb za kontakt, kratak obrazac i vašu e-mail adresu.

Kako stoji vaša stranica? Isprobajte našu besplatnu [provjeru web stranice](/hr/check) – traje deset sekundi."""),
    }),
    ("is-your-hosting-good", {
        "en": ("Is your hosting good? 5 quick checks",
               "Slow pages, missing backups and nobody to call – five simple ways to find out whether your website is in good hands.",
               """Many small businesses do not know where their website is hosted or who looks after it – until something breaks. These five checks take only a few minutes.

## 1. Does your site load quickly?
Open your website on your phone over mobile data. If it takes more than three seconds, you are losing visitors.

## 2. Is there a lock in the address bar?
Your site should always load with https:// and a valid certificate – also when someone types the address without https.

## 3. Do backups exist – and have they ever been tested?
Ask your provider how often backups are made, where they are stored and how quickly they can be restored.

## 4. Where are the servers?
Servers inside the European Union make GDPR compliance much easier.

## 5. Who do you call when something breaks?
Good hosting means a real person who knows your website and answers quickly.

If one of these answers is "I don't know", let's talk – we are happy to have a look."""),
        "de": ("Ist Ihr Hosting gut? 5 schnelle Checks",
               "Langsame Seiten, fehlende Backups und niemand erreichbar – fünf einfache Wege, um herauszufinden, ob Ihre Website in guten Händen ist.",
               """Viele kleine Unternehmen wissen nicht, wo ihre Website gehostet wird oder wer sich darum kümmert – bis etwas kaputtgeht. Diese fünf Checks dauern nur wenige Minuten.

## 1. Lädt Ihre Seite schnell?
Öffnen Sie Ihre Website auf dem Smartphone über mobile Daten. Dauert es länger als drei Sekunden, verlieren Sie Besucher.

## 2. Ist ein Schloss in der Adresszeile?
Ihre Seite sollte immer mit https:// und gültigem Zertifikat laden – auch wenn jemand die Adresse ohne https eintippt.

## 3. Gibt es Backups – und wurden sie je getestet?
Fragen Sie Ihren Anbieter, wie oft Backups gemacht werden, wo sie liegen und wie schnell sie wiederhergestellt werden können.

## 4. Wo stehen die Server?
Server innerhalb der Europäischen Union machen die DSGVO-Konformität deutlich einfacher.

## 5. Wen rufen Sie an, wenn etwas kaputt ist?
Gutes Hosting bedeutet einen echten Menschen, der Ihre Website kennt und schnell antwortet.

Lautet eine Antwort „Weiß ich nicht“? Dann sprechen Sie uns an – wir schauen gerne drauf."""),
        "hr": ("Je li vaš hosting dobar? 5 brzih provjera",
               "Spore stranice, nepostojeće sigurnosne kopije i nikoga za nazvati – pet jednostavnih načina da saznate je li vaša stranica u dobrim rukama.",
               """Mnoge male tvrtke ne znaju gdje im je stranica hostana ni tko o njoj brine – dok se nešto ne pokvari. Ovih pet provjera traje samo nekoliko minuta.

## 1. Učitava li se stranica brzo?
Otvorite stranicu na mobitelu preko mobilnih podataka. Ako traje dulje od tri sekunde, gubite posjetitelje.

## 2. Postoji li lokot u adresnoj traci?
Stranica se uvijek treba učitavati preko https:// s valjanim certifikatom – i kad netko upiše adresu bez https.

## 3. Postoje li sigurnosne kopije – i jesu li ikad testirane?
Pitajte pružatelja koliko se često rade kopije, gdje se čuvaju i koliko brzo se mogu vratiti.

## 4. Gdje su poslužitelji?
Poslužitelji unutar Europske unije znatno olakšavaju usklađenost s GDPR-om.

## 5. Koga zovete kad se nešto pokvari?
Dobar hosting znači stvarnu osobu koja poznaje vašu stranicu i brzo odgovara.

Ako je neki odgovor „Ne znam”, javite nam se – rado ćemo pogledati."""),
    }),
]

with app.app_context():
    db.create_all()
    con = db.session.connection()
    def add_col(table, col, ddl):
        cols = [r[1] for r in con.execute(text(f"PRAGMA table_info({table})"))]
        if col not in cols:
            con.execute(text(f"ALTER TABLE {table} ADD COLUMN {col} {ddl}"))
            print("added", table, col)
    add_col("admin_user", "role", "VARCHAR(20) NOT NULL DEFAULT 'owner'")
    add_col("service", "slug", "VARCHAR(80) DEFAULT ''")
    add_col("service", "body", "TEXT DEFAULT ''")
    db.session.commit()

    for s in db.session.query(Service):
        tr = s.translations
        if s.title in SERVICE_PAGES:
            slug, bodies = SERVICE_PAGES[s.title]
            s.slug = s.slug or slug
            s.body = s.body or bodies["en"]
            for lang in ("de", "hr"):
                tr.setdefault(lang, {})["body"] = bodies[lang]
        if s.title in OTHER_SERVICES:
            for lang, vals in OTHER_SERVICES[s.title].items():
                tr.setdefault(lang, {}).update(vals)
        s.i18n = J(tr)
        print("service", s.id, s.title, s.slug)

    for i, (slug, langs) in enumerate(POSTS):
        if db.session.query(Post).filter_by(slug=slug).first():
            continue
        en = langs["en"]
        p = Post(slug=slug, title=en[0], excerpt=en[1], body=en[2], enabled=True, position=i,
                 i18n=J({lang: {"title": v[0], "excerpt": v[1], "body": v[2]} for lang, v in langs.items() if lang != "en"}))
        db.session.add(p)
        print("post", slug)

    p4 = db.session.query(Project).filter_by(title="Rent a Car Platform").first()
    if p4:
        p4.enabled = True
        p4.i18n = J({"de": {"title": "Autovermietungs-Plattform", "category": "Webanwendung",
                            "description": "Eine hochwertige Autovermietungs-Website mit Online-Buchung, Fahrzeugkatalog, Reservierungsabfrage und einem kompletten Admin-Bereich für Fahrzeuge, Preise und Buchungen."},
                     "hr": {"title": "Platforma za najam automobila", "category": "Web aplikacija",
                            "description": "Premium web stranica za najam automobila s online rezervacijom, katalogom vozila, provjerom rezervacije i potpunim administracijskim sučeljem za vozila, cijene i rezervacije."}})
        print("project enabled")

    for name, url, public in (("AMXME website", "https://amxme.info/", True),
                              ("Rent a Car platform", "https://testiram.de/", True),
                              ("Rent a Car demo", "https://demo.testiram.de/", False)):
        if not db.session.query(Monitor).filter_by(url=url).first():
            db.session.add(Monitor(name=name, url=url, public=public))
            print("monitor", url)
    db.session.add(Activity(user="system", action="Added service pages, blog, portal, monitoring, dark mode", kind="change"))
    db.session.commit()
    print("done")
