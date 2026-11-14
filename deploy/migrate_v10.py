# Signed: ASDHEM | AMXME Web Solutions
# ASDHEM | migration v10: content for the 2026 redesign.
#   - hero texts: remove the old overrides so the new default texts (EN/DE/HR) apply
#   - services: the six services of the new homepage (forum work is now part of "Web apps")
#   - key advantages under the hero, hosting highlights, "Why AMXME" without duplicates
# Nothing is deleted from collections: items that are no longer shown are only disabled
# (Admin → Services / Features can switch them on again). Every change lands in the
# admin version history.
import json

from wsgi import app
from app.extensions import db
from app.models import Activity, Feature, Service, Setting

OLD_OVERRIDES = ["hero_title", "hero_highlight", "hero_tagline", "hero_motto", "hero_btn1_text", "hero_btn1_link",
                 "hero_btn2_text", "hero_btn2_text__de", "hero_btn2_text__hr", "hero_btn2_link", "contact_intro"]


def set_item(obj, en, de, hr, **extra):
    for field, value in en.items():
        setattr(obj, field, value)
    data = {"de": de, "hr": hr}
    old = obj.translations
    for lang in ("de", "hr"):            # keep translations of fields we do not touch (e.g. service page body)
        for k, v in (old.get(lang) or {}).items():
            data[lang].setdefault(k, v)
    obj.i18n = json.dumps(data, ensure_ascii=False)
    for k, v in extra.items():
        setattr(obj, k, v)


SERVICES = [  # (match by slug or title, icon, EN, DE, HR)
    ("web-design", "layout",
     {"title": "Website Development",
      "description": "Fast, responsive websites built around your business – from a one-page presence to a complete company website."},
     {"title": "Website-Erstellung",
      "description": "Schnelle, responsive Websites, zugeschnitten auf Ihr Unternehmen – vom One-Pager bis zum kompletten Firmenauftritt."},
     {"title": "Izrada web stranica",
      "description": "Brze i responzivne web stranice prilagođene vašem poslovanju – od jednostavne prezentacije do cjelovite stranice tvrtke."}),
    ("web-hosting", "server",
     {"title": "Web Hosting",
      "description": "Managed hosting on servers in the EU – SSL, regular backups and monitoring included."},
     {"title": "Webhosting",
      "description": "Betreutes Hosting auf Servern in der EU – inklusive SSL, regelmäßiger Backups und Überwachung."},
     {"title": "Web hosting",
      "description": "Upravljani hosting na poslužiteljima u EU – uključeni SSL, redovite sigurnosne kopije i nadzor."}),
    ("website-maintenance", "wrench",
     {"title": "Maintenance & Support",
      "description": "Updates, fixes and content changes – handled by people who know your website."},
     {"title": "Wartung & technischer Support",
      "description": "Updates, Fehlerbehebung und Inhaltsänderungen – erledigt von Menschen, die Ihre Website kennen."},
     {"title": "Održavanje i tehnička podrška",
      "description": "Ažuriranja, ispravci i izmjene sadržaja – brinu ljudi koji poznaju vašu stranicu."}),
    ("security-ssl", "shield-check",
     {"title": "Security & SSL",
      "description": "SSL certificates, security updates and hardened server settings – so your site and your visitors stay protected."},
     {"title": "Sicherheit & SSL",
      "description": "SSL-Zertifikate, Sicherheitsupdates und gehärtete Servereinstellungen – zum Schutz Ihrer Website und Ihrer Besucher."},
     {"title": "Sigurnost i SSL",
      "description": "SSL certifikati, sigurnosna ažuriranja i zaštićene postavke poslužitelja – za sigurnost stranice i posjetitelja."}),
    ("website-migration", "upload-cloud",
     {"title": "Website Migration",
      "description": "We move your existing website, data and domain to our hosting – carefully planned to keep downtime minimal."},
     {"title": "Website-Umzug",
      "description": "Wir ziehen Ihre bestehende Website samt Daten und Domain auf unser Hosting um – sorgfältig geplant, mit möglichst kurzer Ausfallzeit."},
     {"title": "Migracija web stranica",
      "description": "Prebacujemo vašu postojeću stranicu, podatke i domenu na naš hosting – pažljivo planirano, uz što kraći prekid rada."}),
    ("web-apps", "code",
     {"title": "Web Apps & Custom Solutions",
      "description": "Booking systems, customer areas, forums and other custom features – developed for the way you work."},
     {"title": "Web-Apps & individuelle Lösungen",
      "description": "Buchungssysteme, Kundenbereiche, Foren und weitere individuelle Funktionen – entwickelt für Ihre Abläufe."},
     {"title": "Web aplikacije i posebna rješenja",
      "description": "Sustavi za rezervacije, korisnička područja, forumi i druge posebne funkcije – razvijeni prema vašem načinu rada."}),
]

BADGES = [  # key advantages under the hero
    ("layout", ("Modern, responsive design", "Modernes, responsives Design", "Moderan i responzivan dizajn")),
    ("server", ("Reliable hosting in the EU", "Zuverlässiges Hosting in der EU", "Pouzdan hosting u EU")),
    ("lock", ("SSL certificates & backups", "SSL-Zertifikate & Backups", "SSL certifikati i sigurnosne kopije")),
    ("headphones", ("Maintenance & personal support", "Wartung & persönlicher Support", "Održavanje i osobna podrška")),
]

HOSTING = {  # feature id -> icon, (EN title, text), (DE), (HR), position
    10: ("globe", ("Hosting in the EU", "Your data stays on servers within the European Union – a solid basis for GDPR compliance."),
         ("Hosting in der EU", "Ihre Daten bleiben auf Servern in der Europäischen Union – eine solide Grundlage für die DSGVO."),
         ("Hosting u EU", "Vaši podaci ostaju na poslužiteljima u Europskoj uniji – dobra osnova za usklađenost s GDPR-om."), 0),
    7: ("lock", ("Free SSL certificates", "HTTPS on every website, renewed automatically."),
        ("Kostenlose SSL-Zertifikate", "HTTPS für jede Website, automatisch erneuert."),
        ("Besplatni SSL certifikati", "HTTPS na svakoj stranici, s automatskom obnovom."), 1),
    8: ("refresh", ("Regular backups", "So your website can be restored if something goes wrong."),
        ("Regelmäßige Backups", "Damit Ihre Website im Ernstfall wiederhergestellt werden kann."),
        ("Redovite sigurnosne kopije", "Kako bi se stranica mogla vratiti ako nešto pođe po zlu."), 2),
    9: ("shield-check", ("Security updates", "Server and software are kept up to date and securely configured."),
        ("Sicherheitsupdates", "Server und Software bleiben aktuell und sicher konfiguriert."),
        ("Sigurnosna ažuriranja", "Poslužitelj i softver redovito ažuriramo i sigurno konfiguriramo."), 3),
    11: ("upload-cloud", ("Website migration", "We move your existing website to our hosting for you."),
         ("Website-Umzug", "Wir ziehen Ihre bestehende Website für Sie um."),
         ("Migracija stranice", "Vašu postojeću stranicu prebacujemo umjesto vas."), 4),
    12: ("headphones", ("Technical support", "Direct help from the people who run your hosting."),
         ("Technischer Support", "Direkte Hilfe von den Menschen, die Ihr Hosting betreiben."),
         ("Tehnička podrška", "Izravna pomoć od ljudi koji vode vaš hosting."), 5),
}

WHY = {  # kept "why" items (the others repeat hosting / advantages and are disabled)
    1: ("layers", ("One partner for everything", "Design, development, hosting and maintenance from one place – no back-and-forth between agency and host."),
        ("Alles aus einer Hand", "Design, Entwicklung, Hosting und Wartung von einem Partner – kein Hin und Her zwischen Agentur und Hoster."),
        ("Sve na jednom mjestu", "Dizajn, izrada, hosting i održavanje kod jednog partnera – bez dopisivanja između agencije i hostinga.")),
    2: ("users", ("Direct, personal contact", "You talk to the people who actually build and look after your website."),
        ("Direkter, persönlicher Kontakt", "Sie sprechen mit den Menschen, die Ihre Website tatsächlich bauen und betreuen."),
        ("Izravan, osoban kontakt", "Razgovarate s ljudima koji vašu stranicu stvarno izrađuju i održavaju.")),
    6: ("tag", ("Offers tailored to you", "No rigid packages – every offer is put together for what you actually need."),
        ("Angebote nach Bedarf", "Keine starren Pakete – jedes Angebot richtet sich nach dem, was Sie wirklich brauchen."),
        ("Ponuda po mjeri", "Bez krutih paketa – svaka ponuda slaže se prema onome što vam stvarno treba.")),
}

with app.app_context():
    # 1) hero / contact: drop old overrides -> new default texts in all three languages
    for key in OLD_OVERRIDES:
        row = db.session.get(Setting, key)
        if row is not None:
            db.session.delete(row)

    # 2) services
    by_slug = {s.slug: s for s in Service.query.all() if s.slug}
    for pos, (slug, icon, en, de, hr) in enumerate(SERVICES):
        svc = by_slug.get(slug)
        if svc is None:
            svc = Service(slug=slug, title=en["title"])
            db.session.add(svc)
        set_item(svc, en, de, hr, icon=icon, position=pos, enabled=True)
    for svc in Service.query.all():
        if svc.slug not in {s[0] for s in SERVICES}:
            svc.enabled = False                      # forum / domain services: kept, but hidden

    # 3) key advantages (badge group)
    badges = Feature.query.filter_by(group="badge").order_by(Feature.position, Feature.id).all()
    for i, (icon, (en, de, hr)) in enumerate(BADGES):
        f = badges[i] if i < len(badges) else Feature(group="badge", title=en)
        if f.id is None:
            db.session.add(f)
        set_item(f, {"title": en, "text": ""}, {"title": de}, {"title": hr}, icon=icon, position=i, enabled=True)
    for extra in badges[len(BADGES):]:
        extra.enabled = False

    # 4) hosting highlights
    for fid, (icon, en, de, hr, pos) in HOSTING.items():
        f = db.session.get(Feature, fid)
        if f is not None and f.group == "hosting":
            set_item(f, {"title": en[0], "text": en[1]}, {"title": de[0], "text": de[1]}, {"title": hr[0], "text": hr[1]},
                     icon=icon, position=pos, enabled=True)

    # 5) why AMXME: keep three, hide duplicates
    for f in Feature.query.filter_by(group="why").all():
        if f.id in WHY:
            icon, en, de, hr = WHY[f.id]
            set_item(f, {"title": en[0], "text": en[1]}, {"title": de[0], "text": de[1]}, {"title": hr[0], "text": hr[1]},
                     icon=icon, enabled=True)
        else:
            f.enabled = False

    db.session.add(Activity(user="system", action="Website redesign (v10): new texts, six services, advantages", kind="change"))
    db.session.commit()
    print("done:", Service.query.filter_by(enabled=True).count(), "services,",
          Feature.query.filter_by(group="badge", enabled=True).count(), "advantages,",
          Feature.query.filter_by(group="why", enabled=True).count(), "why items")
