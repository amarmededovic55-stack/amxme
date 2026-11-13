# Signed: ASDHEM | AMXME Web Solutions
"""ASDHEM | Languages: English (default, /), German (/de/), Croatian (/hr/).

UI strings (buttons, labels, form errors) live here. Editable texts live in the
database: settings `<key>__de` / `<key>__hr` and the `i18n` JSON column of collections.
"""
import json

from flask import g, request

LANGS = {"en": "English", "de": "Deutsch", "hr": "Hrvatski"}
LANG_SHORT = {"en": "EN", "de": "DE", "hr": "CRO"}   # ASDHEM | labels in the floating switcher
LANG_ORDER = ("de", "hr", "en")
DEFAULT_LANG = "en"
LOCALES = {"en": "en_US", "de": "de_DE", "hr": "hr_HR"}

UI = {
    # navigation
    "nav_services": {"en": "Services", "de": "Leistungen", "hr": "Usluge"},
    "nav_why": {"en": "Why Us", "de": "Warum wir", "hr": "Zašto mi"},
    "nav_hosting": {"en": "Hosting", "de": "Hosting", "hr": "Hosting"},
    "nav_process": {"en": "How We Work", "de": "Ablauf", "hr": "Kako radimo"},
    "nav_work": {"en": "Our Work", "de": "Projekte", "hr": "Projekti"},
    "nav_about": {"en": "About", "de": "Über uns", "hr": "O nama"},
    "nav_faq": {"en": "FAQ", "de": "FAQ", "hr": "Pitanja"},
    "nav_contact": {"en": "Contact Us", "de": "Kontakt", "hr": "Kontakt"},
    "menu_open": {"en": "Open menu", "de": "Menü öffnen", "hr": "Otvori izbornik"},
    "menu_close": {"en": "Close menu", "de": "Menü schließen", "hr": "Zatvori izbornik"},
    "home": {"en": "Home", "de": "Startseite", "hr": "Početna"},
    "language": {"en": "Language", "de": "Sprache", "hr": "Jezik"},
    "choose_lang": {"en": "Choose language", "de": "Sprache wählen", "hr": "Odaberite jezik"},
    # hero visual
    "chip_ssl": {"en": "SSL Secured", "de": "SSL-gesichert", "hr": "SSL zaštita"},
    "chip_online": {"en": "Servers Online", "de": "Server online", "hr": "Poslužitelji online"},
    "chip_fast": {"en": "Optimized", "de": "Optimiert", "hr": "Optimizirano"},
    "ms_title": {"en": "Your Business<br>Online", "de": "Ihr Business<br>online", "hr": "Vaš posao<br>online"},
    "ms_sub": {"en": "Fast. Secure. Reliable.", "de": "Schnell. Sicher. Zuverlässig.", "hr": "Brzo. Sigurno. Pouzdano."},
    "ms_cta": {"en": "Get Started →", "de": "Jetzt starten →", "hr": "Započnite →"},
    "ms_nav": {"en": "Home|Services|About|Contact", "de": "Start|Leistungen|Über uns|Kontakt", "hr": "Početna|Usluge|O nama|Kontakt"},
    # services / portfolio
    "ask_about": {"en": "Ask about this", "de": "Dazu anfragen", "hr": "Pitajte nas"},
    "filter_all": {"en": "All", "de": "Alle", "hr": "Sve"},
    "filter_label": {"en": "Filter projects", "de": "Projekte filtern", "hr": "Filtriraj projekte"},
    "view_project": {"en": "View Project", "de": "Projekt ansehen", "hr": "Pogledaj projekt"},
    "screenshot_of": {"en": "Screenshot of", "de": "Screenshot von", "hr": "Snimka zaslona:"},
    # hosting panel (illustration)
    "hp_title": {"en": "Hosting Overview", "de": "Hosting-Übersicht", "hr": "Pregled hostinga"},
    "hp_online": {"en": "Online", "de": "Online", "hr": "Online"},
    "hp_sites": {"en": "your-business.com|your-shop.com|your-portfolio.com",
                 "de": "ihre-firma.de|ihr-shop.de|ihr-portfolio.de",
                 "hr": "vasa-tvrtka.hr|vas-shop.hr|vas-portfolio.hr"},
    "hp_ssl": {"en": "Active & auto-renewing", "de": "Aktiv & automatisch erneuert", "hr": "Aktivan i automatski se obnavlja"},
    "hp_backups": {"en": "Backups", "de": "Backups", "hr": "Sigurnosne kopije"},
    "hp_backups_s": {"en": "Scheduled regularly", "de": "Regelmäßig geplant", "hr": "Redovito zakazane"},
    "hp_security": {"en": "Security", "de": "Sicherheit", "hr": "Sigurnost"},
    "hp_security_s": {"en": "Updates applied", "de": "Updates installiert", "hr": "Ažuriranja instalirana"},
    "hp_location": {"en": "Location", "de": "Standort", "hr": "Lokacija"},
    "hp_location_s": {"en": "EU server · GDPR", "de": "EU-Server · DSGVO", "hr": "EU poslužitelj · GDPR"},
    # FAQ
    "faq_search": {"en": "Search questions", "de": "Fragen durchsuchen", "hr": "Pretraži pitanja"},
    "faq_search_ph": {"en": "Search questions, e.g. SSL, domain, price…", "de": "Fragen durchsuchen, z. B. SSL, Domain, Preis…",
                      "hr": "Pretražite pitanja, npr. SSL, domena, cijena…"},
    "faq_cats": {"en": "Question categories", "de": "Kategorien", "hr": "Kategorije pitanja"},
    "faq_copy": {"en": "Copy link to this answer", "de": "Link zu dieser Antwort kopieren", "hr": "Kopiraj poveznicu na ovaj odgovor"},
    "faq_copied": {"en": "Link copied!", "de": "Link kopiert!", "hr": "Poveznica kopirana!"},
    "faq_copy_fail": {"en": "Copy the address from your browser bar", "de": "Kopieren Sie die Adresse aus der Adresszeile",
                      "hr": "Kopirajte adresu iz trake preglednika"},
    "faq_none": {"en": "No answer for “{q}” yet.", "de": "Noch keine Antwort zu „{q}“.", "hr": "Još nema odgovora na „{q}”."},
    "faq_none_text": {"en": "That's a good question – ask us and we'll reply personally.",
                      "de": "Gute Frage – schreiben Sie uns, wir antworten persönlich.",
                      "hr": "Dobro pitanje – pošaljite nam ga i odgovorit ćemo osobno."},
    "faq_ask": {"en": "Ask this question", "de": "Diese Frage stellen", "hr": "Postavite ovo pitanje"},
    "faq_q_prefix": {"en": "Question", "de": "Frage", "hr": "Pitanje"},
    "send_message": {"en": "Send us a message", "de": "Nachricht senden", "hr": "Pošaljite nam poruku"},
    # contact form
    "email_us": {"en": "Email us", "de": "E-Mail an uns", "hr": "Pišite nam"},
    "f_name": {"en": "Full Name", "de": "Vor- und Nachname", "hr": "Ime i prezime"},
    "f_name_ph": {"en": "John Smith", "de": "Max Mustermann", "hr": "Ivan Horvat"},
    "f_email": {"en": "Email Address", "de": "E-Mail-Adresse", "hr": "E-mail adresa"},
    "f_email_ph": {"en": "you@company.com", "de": "sie@firma.de", "hr": "vi@tvrtka.hr"},
    "f_service": {"en": "Service Interested In", "de": "Gewünschte Leistung", "hr": "Usluga koja vas zanima"},
    "f_service_ph": {"en": "Select a service…", "de": "Leistung auswählen…", "hr": "Odaberite uslugu…"},
    "f_other": {"en": "Other / Not sure yet", "de": "Sonstiges / Noch unsicher", "hr": "Ostalo / Još nisam siguran"},
    "f_message": {"en": "Message", "de": "Nachricht", "hr": "Poruka"},
    "f_message_ph": {"en": "Tell us about your project, goals and timeline…",
                     "de": "Erzählen Sie uns von Ihrem Projekt, Ihren Zielen und Ihrem Zeitplan…",
                     "hr": "Opišite nam svoj projekt, ciljeve i rokove…"},
    "f_submit": {"en": "Send Message", "de": "Nachricht senden", "hr": "Pošalji poruku"},
    "f_sending": {"en": "Sending…", "de": "Wird gesendet…", "hr": "Šaljem…"},
    "f_note": {"en": "Your details are only used to reply to your inquiry. See our",
               "de": "Ihre Angaben werden nur zur Beantwortung Ihrer Anfrage verwendet. Siehe",
               "hr": "Vaši podaci koriste se samo za odgovor na upit. Pogledajte"},
    "f_success": {"en": "Thank you! Your message has been sent.", "de": "Vielen Dank! Ihre Nachricht wurde gesendet.",
                  "hr": "Hvala! Vaša poruka je poslana."},
    "err_name": {"en": "Please enter your full name.", "de": "Bitte geben Sie Ihren vollständigen Namen ein.",
                 "hr": "Molimo upišite ime i prezime."},
    "err_name_long": {"en": "Name is too long.", "de": "Der Name ist zu lang.", "hr": "Ime je predugačko."},
    "err_email": {"en": "Please enter a valid email address.", "de": "Bitte geben Sie eine gültige E-Mail-Adresse ein.",
                  "hr": "Molimo upišite ispravnu e-mail adresu."},
    "err_service": {"en": "Please choose the service you are interested in.", "de": "Bitte wählen Sie die gewünschte Leistung.",
                    "hr": "Molimo odaberite uslugu koja vas zanima."},
    "err_message": {"en": "Please write a message of at least 10 characters.",
                    "de": "Bitte schreiben Sie eine Nachricht mit mindestens 10 Zeichen.",
                    "hr": "Molimo napišite poruku od najmanje 10 znakova."},
    "err_message_long": {"en": "Message is too long (max 5000 characters).", "de": "Die Nachricht ist zu lang (max. 5000 Zeichen).",
                         "hr": "Poruka je predugačka (najviše 5000 znakova)."},
    "err_rate": {"en": "Too many messages sent. Please try again later or email us directly.",
                 "de": "Zu viele Nachrichten. Bitte versuchen Sie es später erneut oder schreiben Sie uns direkt eine E-Mail.",
                 "hr": "Previše poslanih poruka. Pokušajte kasnije ili nam pišite izravno e-mailom."},
    "err_unexpected": {"en": "Unexpected server response.", "de": "Unerwartete Antwort des Servers.", "hr": "Neočekivan odgovor poslužitelja."},
    "err_network": {"en": "Could not send your message. Please check your connection or email us directly.",
                    "de": "Ihre Nachricht konnte nicht gesendet werden. Bitte prüfen Sie Ihre Verbindung oder schreiben Sie uns eine E-Mail.",
                    "hr": "Poruka nije poslana. Provjerite vezu ili nam pišite izravno e-mailom."},
    "err_session": {"en": "Your session expired. Please reload the page and try again.",
                    "de": "Ihre Sitzung ist abgelaufen. Bitte laden Sie die Seite neu und versuchen Sie es erneut.",
                    "hr": "Sesija je istekla. Osvježite stranicu i pokušajte ponovno."},
    # footer / legal
    "quick_links": {"en": "Quick Links", "de": "Schnellzugriff", "hr": "Brze poveznice"},
    "about_us": {"en": "About Us", "de": "Über uns", "hr": "O nama"},
    "contact": {"en": "Contact", "de": "Kontakt", "hr": "Kontakt"},
    "imprint": {"en": "Imprint", "de": "Impressum", "hr": "Impressum"},
    "privacy": {"en": "Privacy Policy", "de": "Datenschutz", "hr": "Zaštita privatnosti"},
    "back_top": {"en": "Back to top", "de": "Nach oben", "hr": "Na vrh"},
    "back_site": {"en": "← Back to website", "de": "← Zurück zur Website", "hr": "← Natrag na web stranicu"},
    "back_home": {"en": "Back to homepage", "de": "Zur Startseite", "hr": "Na početnu stranicu"},
    "contact_us_small": {"en": "Contact us", "de": "Kontakt", "hr": "Kontaktirajte nas"},
    "l_owner": {"en": "Owner", "de": "Inhaber", "hr": "Vlasnik"},
    "l_phone": {"en": "Phone", "de": "Telefon", "hr": "Telefon"},
    "l_email": {"en": "Email", "de": "E-Mail", "hr": "E-mail"},
    "l_incomplete": {"en": "Admin notice: the imprint is incomplete. Add your name and address under",
                     "de": "Hinweis für den Admin: Das Impressum ist unvollständig. Name und Adresse eintragen unter",
                     "hr": "Napomena za admina: Impressum nije potpun. Upišite ime i adresu pod"},
    # error pages
    "e404": {"en": "The page you are looking for does not exist.", "de": "Die gesuchte Seite existiert nicht.",
             "hr": "Stranica koju tražite ne postoji."},
    "e500": {"en": "Something went wrong on our side. Please try again later.",
             "de": "Bei uns ist etwas schiefgelaufen. Bitte versuchen Sie es später erneut.",
             "hr": "Nešto je pošlo po zlu kod nas. Pokušajte ponovno kasnije."},
    "e405": {"en": "This action is not allowed.", "de": "Diese Aktion ist nicht erlaubt.", "hr": "Ova radnja nije dopuštena."},
    "e400": {"en": "Your session expired. Please go back, reload the page and try again.",
             "de": "Ihre Sitzung ist abgelaufen. Bitte gehen Sie zurück, laden Sie die Seite neu und versuchen Sie es erneut.",
             "hr": "Sesija je istekla. Vratite se, osvježite stranicu i pokušajte ponovno."},
    "e410": {"en": "This preview link has expired or was deleted. Ask for a new one.",
             "de": "Dieser Vorschau-Link ist abgelaufen oder wurde gelöscht. Bitte fordern Sie einen neuen an.",
             "hr": "Ova poveznica za pregled je istekla ili je obrisana. Zatražite novu."},
}


def current_lang():
    lang = getattr(g, "lang", None)
    return lang if lang in LANGS else DEFAULT_LANG


def t(key, **kw):
    entry = UI.get(key)
    if not entry:
        return key
    text = entry.get(current_lang()) or entry["en"]
    return text.format(**kw) if kw else text


def lang_from_path(path=None):
    """Guess the language from a URL path (used by error pages)."""
    p = (path if path is not None else request.path).strip("/").split("/", 1)[0]
    return p if p in LANGS and p != DEFAULT_LANG else DEFAULT_LANG


def js_strings():
    """Strings needed by site.js, embedded as a non-executable JSON block (CSP friendly)."""
    keys = ["err_name", "err_email", "err_service", "err_message", "err_unexpected", "err_network", "f_sending",
            "f_success", "faq_copied", "faq_copy_fail", "faq_q_prefix", "menu_open", "menu_close"]
    return json.dumps({k: t(k) for k in keys}, ensure_ascii=False).replace("</", "<\\/")


def best_browser_lang():
    """Language from the Accept-Language header, only if it is one we have."""
    best = request.accept_languages.best_match(list(LANGS.keys()) + ["bs", "sr"])
    if best in ("bs", "sr"):
        return "hr"
    return best if best in LANGS else None
