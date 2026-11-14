# Signed: ASDHEM | AMXME Web Solutions
"""Editable text content: schema (drives the admin forms) + defaults + seed data.

ASDHEM | Languages: English values are the base. German/Croatian translations of the
default texts are in DEFAULTS_I18N; translations typed in the admin are stored as
settings `<key>__de` / `<key>__hr` and always win.
"""

NOT_TRANSLATED_TYPES = ("email", "bool", "image")


def F(key, label, type="text", default="", help="", i18n=None):
    if i18n is None:
        i18n = type not in NOT_TRANSLATED_TYPES and not key.endswith("_link")
    return {"key": key, "label": label, "type": type, "default": default, "help": help, "i18n": i18n}


SECTIONS = [
    {
        "slug": "hero", "title": "Početna stranica", "icon": "home",
        "intro": "The first thing visitors see at the top of the homepage.",
        "fields": [
            F("hero_title", "Main heading", default="Web Development & Hosting Services"),
            F("hero_highlight", "Highlighted words", default="Hosting",
              help="Part of the main heading shown in the purple gradient."),
            F("hero_subtitle", "Subtitle / description", "textarea",
              default="From the first design to reliable hosting and ongoing care – we build your website and keep it fast, secure and up to date."),
            F("hero_btn1_text", "Primary button text", default="Explore Our Services"),
            F("hero_btn1_link", "Primary button link", default="#services"),
            F("hero_btn2_text", "Secondary button text", default="Contact Us"),
            F("hero_btn2_link", "Secondary button link", default="#contact"),
        ],
    },
    {
        "slug": "headings", "title": "Section Headings", "icon": "file-text",
        "intro": "Small label, heading and intro text for each homepage section.",
        "fields": [
            F("services_eyebrow", "Services – label", default="What we do"),
            F("services_title", "Services – heading", default="Our Services"),
            F("services_intro", "Services – intro", "textarea",
              default="Everything your online presence needs, delivered by one dedicated team – from the first line of code to the server it runs on."),
            F("why_eyebrow", "Why us – label", default="Why AMXME"),
            F("why_title", "Why us – heading", default="Why Choose AMXME?"),
            F("why_intro", "Why us – intro", "textarea",
              default="We combine careful engineering with dependable infrastructure and real, human support."),
            F("portfolio_eyebrow", "Portfolio – label", default="Our work"),
            F("portfolio_title", "Portfolio – heading", default="Projects We're Proud Of"),
            F("portfolio_intro", "Portfolio – intro", "textarea",
              default="A selection of websites and platforms we have designed, built and hosted."),
            F("faq_eyebrow", "FAQ – label", default="Questions & answers"),
            F("faq_title", "FAQ – heading", default="Good Questions, Straight Answers"),
            F("faq_intro", "FAQ – intro", "textarea",
              default="Everything people usually ask before working with us. Type a keyword to find your answer in seconds."),
            F("faq_help_title", "FAQ – help card heading", default="Still have a question?"),
            F("faq_help_text", "FAQ – help card text", "textarea",
              default="Can't find what you are looking for? Ask us directly – a real person reads every message."),
            F("contact_eyebrow", "Contact – label", default="Get in touch"),
            F("contact_title", "Contact – heading", default="Let's Build Something Great"),
            F("contact_intro", "Contact – intro", "textarea",
              default="Tell us about your project. We will get back to you with ideas, a plan and a non-binding offer."),
        ],
    },
    {
        # ASDHEM | "How we work" process steps
        "slug": "process", "title": "How We Work", "icon": "layers",
        "intro": "The step-by-step process shown on the homepage. Clear steps make it easier for visitors to contact you.",
        "fields": [
            F("process_eyebrow", "Label", default="How we work"),
            F("process_title", "Heading", default="From First Message to Live Website"),
            F("process_intro", "Intro", "textarea",
              default="A clear, simple process – you always know what happens next, and nothing starts without your OK."),
            F("process_steps", "Steps (one per line: Title | Text)", "lines",
              default="Tell us what you need | A short message or email is enough: your idea, examples you like and your timeline.\n"
                      "Get a personal offer | We reply with questions and a clear, non-binding offer tailored to your project.\n"
                      "Design & build | We design and build your website and show you previews along the way.\n"
                      "Launch | We put your website online on our hosting with SSL – or move your existing site for you.\n"
                      "Care & updates | We keep everything updated, backed up and secure, and help whenever you need changes.",
              help="One step per line. Write the title, then a vertical bar |, then the text. Leave empty to hide the section."),
        ],
    },
    {
        # ASDHEM | homepage sections: client portal + free website check
        "slug": "extras", "title": "Client Portal & Website Check", "icon": "briefcase",
        "intro": "Homepage sections that present the client portal and the free website check.",
        "fields": [
            F("portal_eyebrow", "Portal – label", default="Client service"),
            F("portal_title", "Portal – heading", default="Your Own Client Portal – Everything in One Place"),
            F("portal_intro", "Portal – intro", "textarea",
              default="Every client gets a personal login. See how your website is doing, download invoices and get help – any time, without searching through emails."),
            F("portal_points", "Portal – features (one per line: Title | Text)", "lines",
              default="Live website status | Uptime, response time and SSL validity of your website – checked every 5 minutes.\n"
                      "Your services at a glance | Hosting, maintenance and domains with renewal dates.\n"
                      "Invoices as PDF | All invoices in one place, ready to download.\n"
                      "Support tickets | Report a problem or request a change – with screenshots, answered personally.\n"
                      "News & maintenance notices | You know in advance when something is planned.\n"
                      "Secure login | Encrypted, with optional two-factor authentication (2FA)."),
            F("portal_btn", "Portal – button", default="Client login"),
            F("check_eyebrow", "Website check – label", default="Free tool"),
            F("check_title", "Website check – heading", default="How Good Is Your Website?"),
            F("check_intro", "Website check – intro", "textarea",
              default="Enter your address and get a free report on security, speed and Google basics in seconds – no registration."),
            F("check_btn", "Website check – button", default="Check my website"),
        ],
    },
    {
        "slug": "hosting", "title": "Hosting Section", "icon": "server",
        "intro": "Text of the dedicated hosting section. Highlights are managed under “Hosting Highlights”.",
        "fields": [
            F("hosting_eyebrow", "Label", default="Web hosting"),
            F("hosting_title", "Heading", default="Hosting That Keeps Your Website Fast & Secure"),
            F("hosting_text", "Text", "textarea",
              default="Your website deserves a solid home. We run carefully maintained servers in the EU with SSL, regular backups and security updates – so you can focus on your business while we take care of the technology."),
            F("hosting_btn_text", "Button text", default="Ask About Hosting"),
            F("hosting_btn_link", "Button link", default="#contact"),
        ],
    },
    {
        "slug": "about", "title": "About Us", "icon": "info",
        "intro": "Company description shown in the About section.",
        "fields": [
            F("about_eyebrow", "Label", default="About us"),
            F("about_title", "Heading", default="Your Complete Partner for Everything Online"),
            F("about_text", "Description", "textarea",
              default="AMXME Web Solutions designs, builds and hosts websites for businesses, entrepreneurs and individuals.\n\nWe create modern, responsive websites, host them on secure servers in the EU and take care of updates, backups and technical support afterwards – so you have one reliable partner for everything online, from the first design to years after launch.",
              help="Separate paragraphs with an empty line."),
            F("company_name", "Company name", default="AMXME Web Solutions", i18n=False),
        ],
    },
    {
        "slug": "contact", "title": "Contact & Footer", "icon": "mail",
        "intro": "Contact details, form messages and footer text.",
        "fields": [
            F("contact_email", "Public contact email", "email", default="support@amxme.info"),
            F("notify_email", "Send form submissions to", "email", default="support@amxme.info",
              help="Where new contact form messages are emailed."),
            F("contact_note", "Note under email", default="We will get back to you as soon as possible."),
            F("form_success", "Form success message", "textarea",
              default="Thank you! Your message has been sent. We'll get back to you shortly."),
            F("footer_text", "Footer description", "textarea",
              default="Web design, hosting and website maintenance for businesses, entrepreneurs and individuals."),
            F("copyright", "Copyright text", default="AMXME Web Solutions. All rights reserved.",
              help="The current year is added automatically."),
        ],
    },
    {
        # ASDHEM | GDPR / German law: Imprint (§ 5 DDG) + Privacy Policy (Art. 13 GDPR)
        "slug": "legal", "title": "Imprint & Privacy (GDPR)", "icon": "shield",
        "intro": "Legal details for the Imprint (required in Germany, § 5 DDG) and the Privacy Policy. "
                 "Both pages are linked in the footer and stay reachable even in “under construction” mode. "
                 "This is a template, not legal advice – have it checked if you are unsure.",
        "fields": [
            F("legal_name", "Full name of the owner", default="", i18n=False,
              help="Required. Your real first and last name (a company name alone is not enough for sole traders)."),
            F("legal_company", "Business name", default="AMXME Web Solutions", i18n=False,
              help="Optional. Trading name / company. For a GmbH/UG also add the legal form, e.g. “AMXME UG (haftungsbeschränkt)”."),
            F("legal_street", "Street and house number", default="", i18n=False,
              help="Required. A real postal address – no P.O. box."),
            F("legal_city", "Postal code and city", default="", i18n=False, help="Required. e.g. 10115 Berlin"),
            F("legal_country", "Country", default="Germany"),
            F("legal_email", "Email (legal contact)", "email", default="support@amxme.info"),
            F("legal_phone", "Phone", default="", i18n=False,
              help="Strongly recommended – the law asks for a fast, direct way to contact you."),
            F("legal_vat", "VAT ID (USt-IdNr.)", default="", i18n=False,
              help="Only if you have one. Leave empty if you are a small business (Kleinunternehmer) without VAT ID."),
            F("legal_register", "Commercial register", default="", i18n=False,
              help="Only for registered companies, e.g. “Amtsgericht Berlin, HRB 123456”. Otherwise leave empty."),
            F("legal_responsible", "Responsible for content (§ 18 (2) MStV)", default="", i18n=False,
              help="Name and address of the person responsible for editorial content. Leave empty to use the owner above."),
            F("legal_authority", "Data protection supervisory authority", "textarea", default="", i18n=False,
              help="Optional. The authority of your German federal state, e.g. “Berliner Beauftragte für Datenschutz und Informationsfreiheit, Alt-Moabit 59-61, 10555 Berlin”."),
            F("legal_host", "Hosting provider", "textarea", i18n=False,
              default="Hostnet B.V., De Ruyterkade 6, 1013 AA Amsterdam, The Netherlands",
              help="The company whose server runs this website. Check it matches your contract (Auftragsverarbeitungsvertrag / DPA)."),
            F("legal_mail_provider", "Email provider", "textarea", i18n=False,
              default="IONOS SE, Elgendorfer Str. 57, 56410 Montabaur, Germany",
              help="The company that sends and stores your emails (contact form notifications and replies)."),
            F("message_retention_months", "Delete contact messages after (months)", default="12", i18n=False,
              help="Messages older than this are deleted automatically. 0 = never delete (not recommended under GDPR)."),
            F("privacy_updated", "Privacy Policy – last updated", default="November 2026"),
            F("privacy_extra", "Privacy Policy – additional section", "textarea", default="",
              help="Optional extra text shown at the end of the Privacy Policy (e.g. if you add new services later). Separate paragraphs with an empty line."),
        ],
    },
    {
        # ASDHEM | invoice generator settings (German § 14 UStG requirements)
        "slug": "invoicing", "title": "Invoice Settings", "icon": "file-text",
        "intro": "Details printed on every generated invoice. Your name and address come from “Imprint & Privacy”. "
                 "German invoices must show your tax number (Steuernummer) or VAT ID.",
        "fields": [
            F("inv_tax_number", "Tax number (Steuernummer)", default="", i18n=False,
              help="From your Finanzamt, e.g. 12/345/67890. Required on invoices (or your VAT ID)."),
            F("inv_small_business", "Small business – no VAT (§ 19 UStG)", "bool", default="1",
              help="On = Kleinunternehmer: no VAT is added and the legal note is printed. Off = VAT is added."),
            F("inv_vat_rate", "VAT rate in % (when VAT applies)", default="19", i18n=False),
            F("inv_payment_days", "Payment term (days)", default="14", i18n=False),
            F("inv_prefix", "Invoice number prefix", default="RE-", i18n=False,
              help="Numbers are created automatically: RE-2026-001, RE-2026-002 …"),
            F("inv_account_holder", "Account holder", default="", i18n=False, help="Leave empty to use your business name."),
            F("inv_iban", "IBAN", default="", i18n=False),
            F("inv_bic", "BIC", default="", i18n=False),
            F("inv_bank", "Bank name", default="", i18n=False),
        ],
    },
    {
        "slug": "maintenance", "title": "Under Construction", "icon": "wrench",
        "intro": "Hide the website from visitors and show an “under construction” page instead. You still see the full site while signed in.",
        "fields": [
            F("maintenance_enabled", "Under construction mode", "bool", default="0",
              help="When enabled, visitors only see the under construction page with your email."),
            F("maintenance_badge", "Badge text", default="Website under construction"),
            F("maintenance_title", "Heading", default="Something great is being built"),
            F("maintenance_highlight", "Highlighted words", default="great",
              help="Part of the heading shown in the purple gradient."),
            F("maintenance_text", "Text", "textarea",
              default="Our new website is on its way. In the meantime we are fully available for web design, hosting, domains and website maintenance – just send us an email."),
            F("maintenance_tags", "Keywords (one per line)", "lines",
              default="Web Design\nWeb Hosting\nSSL Certificates\nWebsite Maintenance\nDomains & DNS\nBackups"),
        ],
    },
    {
        "slug": "autoreply", "title": "Auto-Reply Email", "icon": "send",
        "intro": "Automatic confirmation email sent to everyone who submits the contact form – in the language of the page they used.",
        "fields": [
            F("autoreply_enabled", "Send automatic reply", "bool", default="1",
              help="When enabled, the sender immediately receives this email after submitting the form."),
            F("autoreply_subject", "Email subject", default="We received your message – AMXME Web Solutions"),
            F("autoreply_body", "Email text", "textarea",
              default="Hello {name},\n\nThank you for contacting AMXME Web Solutions. We have received your message regarding \"{service}\" and will get back to you as soon as possible.\n\nIf you have anything to add, simply reply to this email.\n\nBest regards,\nAMXME Web Solutions\nsupport@amxme.info\nhttps://amxme.info",
              help="You can use {name} (sender's name), {service} (selected service) and {email} (sender's email). Replies to this email go to the public contact email."),
        ],
    },
    {
        "slug": "seo", "title": "SEO & Branding", "icon": "globe",
        "intro": "Browser title, search engine description and logo text.",
        "fields": [
            F("site_title", "Page title", default="AMXME Web Solutions – Web Design, Hosting & Maintenance"),
            F("meta_description", "Meta description", "textarea",
              default="AMXME Web Solutions designs modern websites and provides secure web hosting on EU servers, SSL and website maintenance."),
            F("brand_name", "Logo – name", default="AMXME", i18n=False),
            F("brand_sub", "Logo – subtitle", default="Web Solutions"),
        ],
    },
]

SECTION_MAP = {s["slug"]: s for s in SECTIONS}
# ASDHEM | v10 redesign – shorter, clearer default texts (EN). Admin edits still win over these.
REDESIGN_EN = {
    "hero_title": "Professional websites. Reliable hosting.",
    "hero_highlight": "Reliable hosting.",
    "hero_subtitle": "We build, host and maintain websites for businesses, entrepreneurs and individuals. Everything you need for a professional online presence – in one place.",
    "hero_btn1_text": "Request a quote",
    "hero_btn1_link": "#contact",
    "hero_btn2_text": "Our services",
    "hero_btn2_link": "#services",
    "services_eyebrow": "Services",
    "services_title": "What we do for you",
    "services_intro": "From the first draft to ongoing care – one team for your entire website.",
    "hosting_eyebrow": "Web hosting",
    "hosting_title": "Hosting you don't have to think about",
    "hosting_text": "Your website runs on carefully maintained servers in the EU. We take care of certificates, updates and backups – and you have one contact for everything.",
    "hosting_btn_text": "Ask about hosting",
    "process_eyebrow": "How we work",
    "process_title": "From first message to live website",
    "about_eyebrow": "About us",
    "about_title": "Your partner for everything online",
    "about_text": "AMXME Web Solutions designs, builds and hosts websites for businesses, entrepreneurs and individuals – and stays responsible for them after launch: updates, backups and support included.",
    "why_eyebrow": "Why AMXME",
    "portal_eyebrow": "For clients",
    "portal_title": "Client portal",
    "portal_intro": "Every client gets a personal login – services, website status, invoices and support requests in one place.",
    "portal_points": "Your services | Hosting, maintenance and domains with renewal dates.\n"
                     "Website status | Availability and SSL validity of your website.\n"
                     "Invoices | All invoices as PDF, ready to download.\n"
                     "Support requests | Report a problem or request a change, with attachments.\n"
                     "Notices | Planned maintenance and news, announced in advance.\n"
                     "Secure sign-in | Encrypted, with optional two-factor authentication.",
    "portal_btn": "Client login",
    "check_title": "How good is your website?",
    "check_intro": "A free report on security, speed and Google basics – in seconds, without registration.",
    "contact_eyebrow": "Contact",
    "contact_title": "Let's talk about your project",
    "contact_intro": "Tell us briefly what you need. You will receive a personal, non-binding offer.",
}
REDESIGN_I18N = {
    "de": {
        "hero_title": "Professionelle Websites. Zuverlässiges Hosting.",
        "hero_highlight": "Zuverlässiges Hosting.",
        "hero_subtitle": "Wir entwickeln, hosten und betreuen Websites für Unternehmen, Selbstständige und Privatpersonen. Alles, was Sie für einen professionellen Online-Auftritt brauchen – aus einer Hand.",
        "hero_btn1_text": "Angebot anfordern",
        "hero_btn2_text": "Unsere Leistungen",
        "services_eyebrow": "Leistungen",
        "services_title": "Was wir für Sie tun",
        "services_intro": "Vom ersten Entwurf bis zur laufenden Betreuung – ein Team für Ihre gesamte Website.",
        "hosting_eyebrow": "Webhosting",
        "hosting_title": "Hosting, um das Sie sich nicht kümmern müssen",
        "hosting_text": "Ihre Website läuft auf sorgfältig gewarteten Servern in der EU. Wir kümmern uns um Zertifikate, Updates und Backups – und Sie haben einen Ansprechpartner für alles.",
        "hosting_btn_text": "Hosting anfragen",
        "process_eyebrow": "Ablauf",
        "process_title": "Von der ersten Nachricht zur fertigen Website",
        "about_eyebrow": "Über uns",
        "about_title": "Ihr Partner für alles rund ums Web",
        "about_text": "AMXME Web Solutions gestaltet, entwickelt und hostet Websites für Unternehmen, Selbstständige und Privatpersonen – und bleibt auch nach dem Start verantwortlich: Updates, Backups und Support inklusive.",
        "why_eyebrow": "Warum AMXME",
        "portal_eyebrow": "Für Kunden",
        "portal_title": "Kundenportal",
        "portal_intro": "Jeder Kunde erhält einen persönlichen Zugang – Leistungen, Website-Status, Rechnungen und Support-Anfragen an einem Ort.",
        "portal_points": "Ihre Leistungen | Hosting, Wartung und Domains mit Verlängerungsdatum.\n"
                         "Website-Status | Erreichbarkeit und SSL-Gültigkeit Ihrer Website.\n"
                         "Rechnungen | Alle Rechnungen als PDF zum Download.\n"
                         "Support-Anfragen | Problem melden oder Änderung anfragen, mit Anhängen.\n"
                         "Hinweise | Geplante Wartungen und Neuigkeiten, rechtzeitig angekündigt.\n"
                         "Sicherer Login | Verschlüsselt, mit optionaler Zwei-Faktor-Authentifizierung.",
        "portal_btn": "Zum Kundenlogin",
        "check_title": "Wie gut ist Ihre Website?",
        "check_intro": "Kostenloser Bericht zu Sicherheit, Geschwindigkeit und Google-Grundlagen – in Sekunden, ohne Anmeldung.",
        "contact_eyebrow": "Kontakt",
        "contact_title": "Sprechen wir über Ihr Projekt",
        "contact_intro": "Beschreiben Sie kurz, was Sie brauchen. Sie erhalten ein persönliches, unverbindliches Angebot.",
    },
    "hr": {
        "hero_title": "Profesionalne web stranice. Pouzdan hosting.",
        "hero_highlight": "Pouzdan hosting.",
        "hero_subtitle": "Izrađujemo, hostamo i održavamo web stranice za tvrtke, poduzetnike i pojedince. Sve što vam treba za profesionalnu online prisutnost – na jednom mjestu.",
        "hero_btn1_text": "Zatražite ponudu",
        "hero_btn2_text": "Naše usluge",
        "services_eyebrow": "Usluge",
        "services_title": "Što radimo za vas",
        "services_intro": "Od prvog nacrta do redovitog održavanja – jedan tim za cijelu vašu web stranicu.",
        "hosting_eyebrow": "Web hosting",
        "hosting_title": "Hosting o kojem ne morate brinuti",
        "hosting_text": "Vaša stranica radi na pažljivo održavanim poslužiteljima u EU. Mi brinemo o certifikatima, ažuriranjima i sigurnosnim kopijama – a vi imate jednu kontakt osobu za sve.",
        "hosting_btn_text": "Upit za hosting",
        "process_eyebrow": "Kako radimo",
        "process_title": "Od prve poruke do gotove web stranice",
        "about_eyebrow": "O nama",
        "about_title": "Vaš partner za sve online",
        "about_text": "AMXME Web Solutions dizajnira, izrađuje i hosta web stranice za tvrtke, poduzetnike i pojedince – i ostaje odgovoran za njih i nakon pokretanja: ažuriranja, sigurnosne kopije i podrška su uključeni.",
        "why_eyebrow": "Zašto AMXME",
        "portal_eyebrow": "Za klijente",
        "portal_title": "Korisnički portal",
        "portal_intro": "Svaki klijent dobiva osobnu prijavu – usluge, status stranice, računi i zahtjevi za podršku na jednom mjestu.",
        "portal_points": "Vaše usluge | Hosting, održavanje i domene s datumima obnove.\n"
                         "Status stranice | Dostupnost i valjanost SSL certifikata vaše stranice.\n"
                         "Računi | Svi računi u PDF-u, spremni za preuzimanje.\n"
                         "Zahtjevi za podršku | Prijavite problem ili zatražite izmjenu, uz privitke.\n"
                         "Obavijesti | Planirana održavanja i novosti, najavljeni unaprijed.\n"
                         "Sigurna prijava | Šifrirano, uz opcionalnu dvofaktorsku autentifikaciju.",
        "portal_btn": "Prijava u portal",
        "check_title": "Koliko je dobra vaša web stranica?",
        "check_intro": "Besplatno izvješće o sigurnosti, brzini i osnovama za Google – za nekoliko sekundi, bez registracije.",
        "contact_eyebrow": "Kontakt",
        "contact_title": "Razgovarajmo o vašem projektu",
        "contact_intro": "Ukratko opišite što vam treba. Dobit ćete osobnu, neobvezujuću ponudu.",
    },
}
for _s in SECTIONS:
    for _f in _s["fields"]:
        if _f["key"] in REDESIGN_EN:
            _f["default"] = REDESIGN_EN[_f["key"]]

DEFAULTS = {f["key"]: f["default"] for s in SECTIONS for f in s["fields"]}
FIELD_SECTION = {f["key"]: s["slug"] for s in SECTIONS for f in s["fields"]}
TRANSLATABLE = {f["key"] for s in SECTIONS for f in s["fields"] if f["i18n"]}


# ASDHEM | translations of the default texts (used until a translation is typed in the admin)
DEFAULTS_I18N = {
    "de": {
        "hero_title": "Webentwicklung & Hosting-Services",
        "hero_highlight": "Hosting",
        "hero_subtitle": "Vom ersten Entwurf bis zum zuverlässigen Hosting und laufender Betreuung – wir bauen Ihre Website und halten sie schnell, sicher und aktuell.",
        "hero_btn1_text": "Unsere Leistungen",
        "hero_btn2_text": "Kontakt aufnehmen",
        "services_eyebrow": "Was wir tun",
        "services_title": "Unsere Leistungen",
        "services_intro": "Alles, was Ihre Online-Präsenz braucht – von einem engagierten Team, von der ersten Codezeile bis zum Server, auf dem sie läuft.",
        "why_eyebrow": "Warum AMXME",
        "why_title": "Warum AMXME?",
        "why_intro": "Wir verbinden sorgfältige Entwicklung mit verlässlicher Infrastruktur und echtem, persönlichem Support.",
        "portfolio_eyebrow": "Unsere Arbeit",
        "portfolio_title": "Projekte, auf die wir stolz sind",
        "portfolio_intro": "Eine Auswahl an Websites und Plattformen, die wir gestaltet, entwickelt und gehostet haben.",
        "faq_eyebrow": "Fragen & Antworten",
        "faq_title": "Gute Fragen, klare Antworten",
        "faq_intro": "Alles, was Kunden uns vor einer Zusammenarbeit häufig fragen. Geben Sie ein Stichwort ein und finden Sie Ihre Antwort in Sekunden.",
        "faq_help_title": "Noch Fragen?",
        "faq_help_text": "Nicht gefunden, was Sie suchen? Fragen Sie uns direkt – jede Nachricht liest ein echter Mensch.",
        "contact_eyebrow": "Kontakt",
        "contact_title": "Lassen Sie uns etwas Großartiges bauen",
        "contact_intro": "Erzählen Sie uns von Ihrem Projekt. Sie erhalten von uns Ideen, einen Plan und ein unverbindliches Angebot.",
        "process_eyebrow": "So arbeiten wir",
        "process_title": "Von der ersten Nachricht zur fertigen Website",
        "process_intro": "Ein klarer, einfacher Ablauf – Sie wissen immer, was als Nächstes passiert, und nichts startet ohne Ihr OK.",
        "process_steps": "Sie erzählen uns, was Sie brauchen | Eine kurze Nachricht oder E-Mail genügt: Ihre Idee, Beispiele, die Ihnen gefallen, und Ihr Zeitplan.\n"
                         "Persönliches Angebot | Wir melden uns mit Rückfragen und einem klaren, unverbindlichen Angebot für Ihr Projekt.\n"
                         "Design & Entwicklung | Wir gestalten und bauen Ihre Website und zeigen Ihnen unterwegs Zwischenstände.\n"
                         "Go-live | Wir bringen Ihre Website mit SSL auf unser Hosting – oder ziehen Ihre bestehende Seite für Sie um.\n"
                         "Betreuung & Updates | Wir halten alles aktuell, gesichert und sicher und helfen, wann immer Sie Änderungen brauchen.",
        "portal_eyebrow": "Kundenservice",
        "portal_title": "Ihr eigenes Kundenportal – alles an einem Ort",
        "portal_intro": "Jeder Kunde erhält einen persönlichen Zugang. Sehen Sie, wie es Ihrer Website geht, laden Sie Rechnungen herunter und erhalten Sie Hilfe – jederzeit, ohne in E-Mails zu suchen.",
        "portal_points": "Live-Status Ihrer Website | Verfügbarkeit, Antwortzeit und SSL-Laufzeit – alle 5 Minuten geprüft.\n"
                         "Ihre Leistungen im Blick | Hosting, Wartung und Domains mit Verlängerungsdatum.\n"
                         "Rechnungen als PDF | Alle Rechnungen an einem Ort, jederzeit zum Download.\n"
                         "Support-Tickets | Problem melden oder Änderung anfragen – mit Screenshots, persönlich beantwortet.\n"
                         "Neuigkeiten & Wartungshinweise | Sie wissen vorher, wenn etwas geplant ist.\n"
                         "Sicherer Login | Verschlüsselt, mit optionaler Zwei-Faktor-Authentifizierung (2FA).",
        "portal_btn": "Zum Kundenlogin",
        "check_eyebrow": "Kostenloses Tool",
        "check_title": "Wie gut ist Ihre Website?",
        "check_intro": "Adresse eingeben und in Sekunden einen kostenlosen Bericht zu Sicherheit, Geschwindigkeit und Google-Grundlagen erhalten – ohne Anmeldung.",
        "check_btn": "Website prüfen",
        "hosting_eyebrow": "Webhosting",
        "hosting_title": "Hosting, das Ihre Website schnell & sicher hält",
        "hosting_text": "Ihre Website verdient ein solides Zuhause. Wir betreiben sorgfältig gewartete Server in der EU mit SSL, regelmäßigen Backups und Sicherheitsupdates – damit Sie sich auf Ihr Geschäft konzentrieren können, während wir uns um die Technik kümmern.",
        "hosting_btn_text": "Hosting anfragen",
        "about_eyebrow": "Über uns",
        "about_title": "Ihr Partner für alles rund ums Web",
        "about_text": "AMXME Web Solutions gestaltet, entwickelt und hostet Websites für Unternehmen, Selbstständige und Privatpersonen.\n\nWir erstellen moderne, responsive Websites, hosten sie auf sicheren Servern in der EU und kümmern uns danach um Updates, Backups und technischen Support – so haben Sie einen verlässlichen Partner für alles Digitale, vom ersten Entwurf bis Jahre nach dem Start.",
        "contact_note": "Wir melden uns so schnell wie möglich.",
        "form_success": "Vielen Dank! Ihre Nachricht wurde gesendet. Wir melden uns in Kürze.",
        "footer_text": "Webdesign, Hosting und Website-Wartung für Unternehmen, Selbstständige und Privatpersonen.",
        "copyright": "AMXME Web Solutions. Alle Rechte vorbehalten.",
        "legal_country": "Deutschland",
        "privacy_updated": "November 2026",
        "maintenance_badge": "Website im Aufbau",
        "maintenance_title": "Hier entsteht etwas Großartiges",
        "maintenance_highlight": "Großartiges",
        "maintenance_text": "Unsere neue Website ist auf dem Weg. In der Zwischenzeit sind wir für Webdesign, Hosting, Domains und Website-Wartung voll erreichbar – schreiben Sie uns einfach eine E-Mail.",
        "maintenance_tags": "Webdesign\nWebhosting\nSSL-Zertifikate\nWebsite-Wartung\nDomains & DNS\nBackups",
        "autoreply_subject": "Wir haben Ihre Nachricht erhalten – AMXME Web Solutions",
        "autoreply_body": "Hallo {name},\n\nvielen Dank für Ihre Nachricht an AMXME Web Solutions. Wir haben Ihre Anfrage zu „{service}“ erhalten und melden uns so schnell wie möglich.\n\nWenn Sie noch etwas ergänzen möchten, antworten Sie einfach auf diese E-Mail.\n\nViele Grüße\nAMXME Web Solutions\nsupport@amxme.info\nhttps://amxme.info/de/",
        "site_title": "AMXME Web Solutions – Webdesign, Hosting & Wartung",
        "meta_description": "AMXME Web Solutions gestaltet moderne Websites und bietet sicheres Webhosting auf EU-Servern, SSL und Website-Wartung.",
        "brand_sub": "Web Solutions",
    },
    "hr": {
        "hero_title": "Izrada web stranica i hosting usluge",
        "hero_highlight": "hosting",
        "hero_subtitle": "Od prvog dizajna do pouzdanog hostinga i redovitog održavanja – izrađujemo vašu web stranicu i brinemo da bude brza, sigurna i ažurna.",
        "hero_btn1_text": "Pogledajte usluge",
        "hero_btn2_text": "Kontaktirajte nas",
        "services_eyebrow": "Što radimo",
        "services_title": "Naše usluge",
        "services_intro": "Sve što vaša online prisutnost treba, od jednog posvećenog tima – od prve linije koda do poslužitelja na kojem radi.",
        "why_eyebrow": "Zašto AMXME",
        "why_title": "Zašto odabrati AMXME?",
        "why_intro": "Spajamo pažljiv razvoj, pouzdanu infrastrukturu i stvarnu, ljudsku podršku.",
        "portfolio_eyebrow": "Naš rad",
        "portfolio_title": "Projekti na koje smo ponosni",
        "portfolio_intro": "Izbor web stranica i platformi koje smo dizajnirali, izradili i hostali.",
        "faq_eyebrow": "Pitanja i odgovori",
        "faq_title": "Dobra pitanja, jasni odgovori",
        "faq_intro": "Sve što nas klijenti najčešće pitaju prije suradnje. Upišite pojam i pronađite odgovor u nekoliko sekundi.",
        "faq_help_title": "Imate još pitanja?",
        "faq_help_text": "Niste pronašli što tražite? Pitajte nas izravno – svaku poruku čita stvarna osoba.",
        "contact_eyebrow": "Javite se",
        "contact_title": "Napravimo nešto odlično",
        "contact_intro": "Opišite nam svoj projekt. Javit ćemo vam se s idejama, planom i neobvezujućom ponudom.",
        "process_eyebrow": "Kako radimo",
        "process_title": "Od prve poruke do gotove web stranice",
        "process_intro": "Jasan i jednostavan postupak – uvijek znate što slijedi i ništa ne počinje bez vašeg odobrenja.",
        "process_steps": "Recite nam što trebate | Dovoljna je kratka poruka ili e-mail: vaša ideja, primjeri koji vam se sviđaju i rokovi.\n"
                         "Osobna ponuda | Javljamo se s pitanjima i jasnom, neobvezujućom ponudom za vaš projekt.\n"
                         "Dizajn i izrada | Dizajniramo i izrađujemo vašu stranicu te vam usput pokazujemo kako napreduje.\n"
                         "Pokretanje | Stavljamo stranicu online na naš hosting sa SSL-om – ili za vas premještamo postojeću.\n"
                         "Održavanje i ažuriranja | Brinemo da sve bude ažurno, sigurno i redovito kopirano te pomažemo kad god trebate izmjene.",
        "portal_eyebrow": "Korisnička podrška",
        "portal_title": "Vaš vlastiti portal za klijente – sve na jednom mjestu",
        "portal_intro": "Svaki klijent dobiva osobnu prijavu. Pogledajte kako radi vaša stranica, preuzmite račune i dobijte pomoć – bilo kada, bez traženja po e-mailovima.",
        "portal_points": "Status stranice uživo | Dostupnost, vrijeme odziva i trajanje SSL-a – provjera svakih 5 minuta.\n"
                         "Vaše usluge na jednom mjestu | Hosting, održavanje i domene s datumom obnove.\n"
                         "Računi u PDF-u | Svi računi na jednom mjestu, spremni za preuzimanje.\n"
                         "Zahtjevi za podršku | Prijavite problem ili zatražite izmjenu – sa snimkama zaslona, uz osobni odgovor.\n"
                         "Novosti i obavijesti o održavanju | Unaprijed znate kad je nešto planirano.\n"
                         "Sigurna prijava | Šifrirano, uz mogućnost dvofaktorske autentifikacije (2FA).",
        "portal_btn": "Prijava za klijente",
        "check_eyebrow": "Besplatan alat",
        "check_title": "Koliko je dobra vaša web stranica?",
        "check_intro": "Upišite adresu i za nekoliko sekundi dobijte besplatan izvještaj o sigurnosti, brzini i osnovama za Google – bez registracije.",
        "check_btn": "Provjeri moju stranicu",
        "hosting_eyebrow": "Web hosting",
        "hosting_title": "Hosting koji vašu stranicu drži brzom i sigurnom",
        "hosting_text": "Vaša web stranica zaslužuje čvrst dom. Održavamo pažljivo konfigurirane poslužitelje u EU sa SSL-om, redovitim sigurnosnim kopijama i sigurnosnim ažuriranjima – vi se posvetite poslu, a mi brinemo o tehnici.",
        "hosting_btn_text": "Pitajte za hosting",
        "about_eyebrow": "O nama",
        "about_title": "Vaš partner za sve online",
        "about_text": "AMXME Web Solutions dizajnira, izrađuje i hosta web stranice za tvrtke, poduzetnike i pojedince.\n\nIzrađujemo moderne, responzivne web stranice, hostamo ih na sigurnim poslužiteljima u EU i nakon toga brinemo o ažuriranjima, sigurnosnim kopijama i tehničkoj podršci – tako imate jednog pouzdanog partnera za sve online, od prvog dizajna do godinama nakon pokretanja.",
        "contact_note": "Javit ćemo vam se što prije.",
        "form_success": "Hvala! Vaša poruka je poslana. Javit ćemo vam se uskoro.",
        "footer_text": "Web dizajn, hosting i održavanje web stranica za tvrtke, poduzetnike i pojedince.",
        "copyright": "AMXME Web Solutions. Sva prava pridržana.",
        "legal_country": "Njemačka",
        "privacy_updated": "studeni 2026.",
        "maintenance_badge": "Web stranica u izradi",
        "maintenance_title": "Ovdje nastaje nešto odlično",
        "maintenance_highlight": "odlično",
        "maintenance_text": "Naša nova web stranica stiže uskoro. U međuvremenu smo vam na raspolaganju za web dizajn, hosting, domene i održavanje – samo nam pošaljite e-mail.",
        "maintenance_tags": "Web dizajn\nWeb hosting\nSSL certifikati\nOdržavanje web stranica\nDomene i DNS\nSigurnosne kopije",
        "autoreply_subject": "Primili smo vašu poruku – AMXME Web Solutions",
        "autoreply_body": "Pozdrav {name},\n\nhvala što ste kontaktirali AMXME Web Solutions. Primili smo vaš upit u vezi s „{service}” i javit ćemo vam se što prije.\n\nAko želite nešto dodati, jednostavno odgovorite na ovaj e-mail.\n\nLijep pozdrav,\nAMXME Web Solutions\nsupport@amxme.info\nhttps://amxme.info/hr/",
        "site_title": "AMXME Web Solutions – web dizajn, hosting i održavanje",
        "meta_description": "AMXME Web Solutions izrađuje moderne web stranice i nudi siguran web hosting na EU poslužiteljima, SSL i održavanje web stranica.",
        "brand_sub": "Web Solutions",
    },
}

for _lang, _vals in REDESIGN_I18N.items():
    DEFAULTS_I18N[_lang].update(_vals)


# ---------------------------------------------------------------- seed data (fresh installs)
# Each row: (EN values..., {"de": {...}, "hr": {...}})

SEED_SERVICES = [
    ("Custom Website Development", "code",
     "Fast, modern and fully responsive websites designed around your brand and built to convert visitors into customers.",
     "Business websites\nLanding pages\nPortfolio websites\nCustom web applications\nOnline shops",
     {"de": {"title": "Individuelle Website-Entwicklung",
             "description": "Schnelle, moderne und vollständig responsive Websites – passend zu Ihrer Marke und gemacht, um Besucher zu Kunden zu machen.",
             "items": "Unternehmenswebsites\nLandingpages\nPortfolio-Websites\nIndividuelle Webanwendungen\nOnlineshops"},
      "hr": {"title": "Izrada web stranica po mjeri",
             "description": "Brze, moderne i potpuno responzivne web stranice prilagođene vašem brendu, izrađene da posjetitelje pretvore u kupce.",
             "items": "Poslovne web stranice\nLanding stranice\nPortfolio stranice\nWeb aplikacije po mjeri\nWeb trgovine"}}),
    ("Web Hosting", "server",
     "Secure, reliable hosting for business websites, portfolios and online shops – set up and looked after for you.",
     "Website hosting on EU servers\nSSL certificates\nRegular backups\nWebsite migration\nDomain & DNS setup",
     {"de": {"title": "Webhosting",
             "description": "Sicheres, zuverlässiges Hosting für Unternehmenswebsites, Portfolios und Onlineshops – eingerichtet und betreut von uns.",
             "items": "Website-Hosting auf EU-Servern\nSSL-Zertifikate\nRegelmäßige Backups\nWebsite-Umzug\nDomain- & DNS-Einrichtung"},
      "hr": {"title": "Web hosting",
             "description": "Siguran i pouzdan hosting za poslovne stranice, portfolije i web trgovine – postavljen i održavan za vas.",
             "items": "Hosting na EU poslužiteljima\nSSL certifikati\nRedovite sigurnosne kopije\nPreseljenje web stranice\nPostavljanje domene i DNS-a"}}),
    ("Website Maintenance", "wrench",
     "Keep your website secure, up to date and running smoothly while you focus on your business.",
     "Security updates\nRegular backups\nBug fixes\nPerformance optimization\nTechnical support",
     {"de": {"title": "Website-Wartung",
             "description": "Wir halten Ihre Website sicher, aktuell und reibungslos am Laufen – Sie konzentrieren sich auf Ihr Geschäft.",
             "items": "Sicherheitsupdates\nRegelmäßige Backups\nFehlerbehebung\nPerformance-Optimierung\nTechnischer Support"},
      "hr": {"title": "Održavanje web stranica",
             "description": "Održavamo vašu stranicu sigurnom, ažurnom i ispravnom dok se vi posvećujete poslu.",
             "items": "Sigurnosna ažuriranja\nRedovite sigurnosne kopije\nIspravljanje grešaka\nOptimizacija brzine\nTehnička podrška"}}),
]

SEED_FEATURES = {
    "why": [
        ("One Partner for Everything", "layers",
         "Design, development, hosting and maintenance from one hand – no back-and-forth between agency and host.",
         {"de": {"title": "Alles aus einer Hand", "text": "Design, Entwicklung, Hosting und Wartung von einem Partner – kein Hin und Her zwischen Agentur und Hoster."},
          "hr": {"title": "Sve na jednom mjestu", "text": "Dizajn, izrada, hosting i održavanje od jednog partnera – bez prebacivanja odgovornosti između agencije i hostinga."}}),
        ("Direct, Personal Contact", "headphones",
         "You talk to the person who actually builds and hosts your website – quick answers, no ticket ping-pong.",
         {"de": {"title": "Direkter, persönlicher Kontakt", "text": "Sie sprechen mit der Person, die Ihre Website tatsächlich baut und hostet – schnelle Antworten statt Ticket-Pingpong."},
          "hr": {"title": "Izravan, osobni kontakt", "text": "Razgovarate s osobom koja stvarno izrađuje i hosta vašu stranicu – brzi odgovori, bez beskonačnih tiketa."}}),
        ("Hosted in the EU", "globe",
         "Your website and your visitors' data stay on servers in the European Union – GDPR-friendly from day one.",
         {"de": {"title": "Gehostet in der EU", "text": "Ihre Website und die Daten Ihrer Besucher bleiben auf Servern in der Europäischen Union – DSGVO-freundlich vom ersten Tag an."},
          "hr": {"title": "Hostano u EU", "text": "Vaša stranica i podaci vaših posjetitelja ostaju na poslužiteljima u Europskoj uniji – u skladu s GDPR-om od prvog dana."}}),
        ("Security Built In", "shield-check",
         "SSL, updates, hardening and backups are part of everything we build – not an expensive extra.",
         {"de": {"title": "Sicherheit inklusive", "text": "SSL, Updates, Härtung und Backups sind Teil von allem, was wir bauen – kein teures Extra."},
          "hr": {"title": "Sigurnost je uključena", "text": "SSL, ažuriranja, zaštita i sigurnosne kopije dio su svega što izrađujemo – a ne skupi dodatak."}}),
        ("Modern & Fast", "zap",
         "Clean code, responsive design and quick loading times – on phones, tablets and desktops.",
         {"de": {"title": "Modern & schnell", "text": "Sauberer Code, responsives Design und kurze Ladezeiten – auf Smartphone, Tablet und Desktop."},
          "hr": {"title": "Moderno i brzo", "text": "Čist kod, responzivan dizajn i brzo učitavanje – na mobitelu, tabletu i računalu."}}),
        ("Offers on Request", "tag",
         "No fixed packages – every offer is put together for what you actually need. Just ask us by email.",
         {"de": {"title": "Angebote auf Anfrage", "text": "Keine starren Pakete – jedes Angebot wird für das erstellt, was Sie wirklich brauchen. Fragen Sie uns einfach per E-Mail."},
          "hr": {"title": "Ponude na upit", "text": "Bez fiksnih paketa – svaka ponuda izrađuje se prema onome što vam stvarno treba. Samo nas pitajte e-mailom."}}),
    ],
    "hosting": [
        ("Free SSL Certificates", "lock", "Every website runs on https:// with certificates that renew automatically.",
         {"de": {"title": "Kostenlose SSL-Zertifikate", "text": "Jede Website läuft über https:// mit Zertifikaten, die sich automatisch erneuern."},
          "hr": {"title": "Besplatni SSL certifikati", "text": "Svaka stranica radi preko https:// s certifikatima koji se automatski obnavljaju."}}),
        ("Regular Backups", "refresh", "Your website is backed up regularly and can be restored if something goes wrong.",
         {"de": {"title": "Regelmäßige Backups", "text": "Ihre Website wird regelmäßig gesichert und kann im Ernstfall wiederhergestellt werden."},
          "hr": {"title": "Redovite sigurnosne kopije", "text": "Vaša se stranica redovito sigurnosno kopira i može se vratiti ako nešto pođe po zlu."}}),
        ("Secure Server Setup", "shield", "Firewall, hardened configuration and regular security updates.",
         {"de": {"title": "Sichere Serverkonfiguration", "text": "Firewall, gehärtete Konfiguration und regelmäßige Sicherheitsupdates."},
          "hr": {"title": "Sigurna konfiguracija poslužitelja", "text": "Vatrozid, zaštićena konfiguracija i redovita sigurnosna ažuriranja."}}),
        ("Servers in the EU", "server", "Hosted in the European Union – good for loading speed and for GDPR.",
         {"de": {"title": "Server in der EU", "text": "Gehostet in der Europäischen Union – gut für Ladezeiten und für die DSGVO."},
          "hr": {"title": "Poslužitelji u EU", "text": "Hostano u Europskoj uniji – dobro za brzinu učitavanja i za GDPR."}}),
        ("Website Migration", "upload-cloud", "We move your existing website to our hosting for you.",
         {"de": {"title": "Website-Umzug", "text": "Wir ziehen Ihre bestehende Website für Sie auf unser Hosting um."},
          "hr": {"title": "Preseljenje web stranice", "text": "Vašu postojeću stranicu premještamo na naš hosting umjesto vas."}}),
        ("We Handle the Technical Side", "sliders", "Updates, configuration and technical details are our job, not yours.",
         {"de": {"title": "Wir kümmern uns um die Technik", "text": "Updates, Konfiguration und technische Details sind unsere Aufgabe, nicht Ihre."},
          "hr": {"title": "Mi brinemo o tehnici", "text": "Ažuriranja, konfiguracija i tehnički detalji naš su posao, a ne vaš."}}),
    ],
    "badge": [
        ("Servers in the EU · GDPR-ready", "shield-check", "",
         {"de": {"title": "EU-Server · DSGVO-konform"}, "hr": {"title": "Poslužitelji u EU · GDPR"}}),
        ("Direct contact, no call centre", "headphones", "",
         {"de": {"title": "Direkter Kontakt, kein Callcenter"}, "hr": {"title": "Izravan kontakt, bez call centra"}}),
        ("Edit your content yourself", "sliders", "",
         {"de": {"title": "Inhalte selbst bearbeiten"}, "hr": {"title": "Sami uređujete sadržaj"}}),
        ("Design, hosting & care in one place", "layers", "",
         {"de": {"title": "Design, Hosting & Pflege aus einer Hand"}, "hr": {"title": "Dizajn, hosting i održavanje na jednom mjestu"}}),
    ],
}

SEED_PROJECTS = [
    ("Business Website", "Sample project – a modern, responsive company website with service pages and a contact form. Replace it with your own work in the admin panel.",
     "Business Website", "HTML, CSS, JavaScript", "/static/img/samples/business.svg"),
    ("Online Store", "Sample project – an e-commerce website with product catalog, cart and secure checkout.",
     "E-commerce", "E-commerce, Payments, SSL", "/static/img/samples/shop.svg"),
]

# ASDHEM | example FAQ – review and adapt every answer in Admin → FAQ before going live
FAQ_CATEGORY_I18N = {
    "General": {"de": "Allgemein", "hr": "Općenito"},
    "Websites": {"de": "Websites", "hr": "Web stranice"},
    "Hosting": {"de": "Hosting", "hr": "Hosting"},
    "Domains": {"de": "Domains", "hr": "Domene"},
    "Support": {"de": "Support", "hr": "Podrška"},
}

SEED_FAQ = [
    ("General", "What exactly does AMXME do?",
     "We design and build websites and host them on our own carefully maintained servers in the EU. SSL, backups and ongoing maintenance are part of what we offer – one partner for everything online.",
     {"de": ("Was genau macht AMXME?", "Wir gestalten und entwickeln Websites und hosten sie auf unseren eigenen, sorgfältig gewarteten Servern in der EU. SSL, Backups und laufende Wartung gehören dazu – ein Partner für alles Digitale."),
      "hr": ("Čime se točno bavi AMXME?", "Dizajniramo i izrađujemo web stranice te ih hostamo na vlastitim, pažljivo održavanim poslužiteljima u EU. SSL, sigurnosne kopije i redovito održavanje dio su ponude – jedan partner za sve online.")}),
    ("General", "How do we start working together?",
     "Send us a short message through the contact form or by email: what you need, any examples you like and your timeline. We reply with questions or a non-binding proposal. Nothing starts until you agree.",
     {"de": ("Wie beginnt eine Zusammenarbeit?", "Schreiben Sie uns eine kurze Nachricht über das Kontaktformular oder per E-Mail: was Sie brauchen, Beispiele, die Ihnen gefallen, und Ihren Zeitplan. Wir melden uns mit Rückfragen oder einem unverbindlichen Vorschlag. Nichts beginnt ohne Ihre Zustimmung."),
      "hr": ("Kako započinje suradnja?", "Pošaljite nam kratku poruku putem obrasca ili e-mailom: što trebate, primjere koji vam se sviđaju i rokove. Javit ćemo se s pitanjima ili neobvezujućim prijedlogom. Ništa ne počinje bez vašeg pristanka.")}),
    ("General", "What do your services cost?",
     "We do not publish fixed prices, because every project is different. Send us a short description of what you need by email to support@amxme.info or through the contact form, and we will reply with a personal, non-binding offer.",
     {"de": ("Was kosten Ihre Leistungen?", "Wir veröffentlichen keine Festpreise, weil jedes Projekt anders ist. Schicken Sie uns eine kurze Beschreibung Ihres Vorhabens per E-Mail an support@amxme.info oder über das Kontaktformular – Sie erhalten ein persönliches, unverbindliches Angebot."),
      "hr": ("Koliko koštaju vaše usluge?", "Ne objavljujemo fiksne cijene jer je svaki projekt drugačiji. Pošaljite nam kratak opis onoga što trebate e-mailom na support@amxme.info ili putem obrasca i dobit ćete osobnu, neobvezujuću ponudu.")}),
    ("Websites", "How long does it take to build a website?",
     "It depends on the size of the project. A compact business website is much faster than a custom web application. You receive a realistic timeline together with your offer.",
     {"de": ("Wie lange dauert die Erstellung einer Website?", "Das hängt vom Umfang ab. Eine kompakte Unternehmenswebsite ist deutlich schneller fertig als eine individuelle Webanwendung. Mit dem Angebot erhalten Sie einen realistischen Zeitplan."),
      "hr": ("Koliko traje izrada web stranice?", "Ovisi o opsegu projekta. Kompaktna poslovna stranica gotova je puno brže od web aplikacije po mjeri. Uz ponudu dobivate i realan vremenski plan.")}),
    ("Websites", "Will my website work on phones and tablets?",
     "Yes. Every website we build is fully responsive and tested on phones, tablets and desktops, because most visitors arrive on a phone today.",
     {"de": ("Funktioniert meine Website auf Smartphones und Tablets?", "Ja. Jede Website, die wir bauen, ist vollständig responsiv und wird auf Smartphones, Tablets und Desktops getestet – denn die meisten Besucher kommen heute mobil."),
      "hr": ("Hoće li moja stranica raditi na mobitelima i tabletima?", "Da. Svaka stranica koju izradimo potpuno je responzivna i testirana na mobitelima, tabletima i računalima jer većina posjetitelja danas dolazi s mobitela.")}),
    ("Websites", "Can I update the content myself?",
     "Yes, if you want to. We can build your website with a simple admin panel so you can change texts, images and projects yourself – or we take care of updates for you.",
     {"de": ("Kann ich die Inhalte selbst ändern?", "Ja, wenn Sie möchten. Wir können Ihre Website mit einem einfachen Admin-Bereich bauen, in dem Sie Texte, Bilder und Projekte selbst ändern – oder wir übernehmen die Updates für Sie."),
      "hr": ("Mogu li sam mijenjati sadržaj?", "Da, ako želite. Stranicu možemo izraditi s jednostavnim administracijskim sučeljem u kojem sami mijenjate tekstove, slike i projekte – ili ažuriranja preuzimamo mi.")}),
    ("Hosting", "Is an SSL certificate included?",
     "Yes. Every website we host gets a free SSL certificate that renews automatically, so your site always loads securely over https://.",
     {"de": ("Ist ein SSL-Zertifikat enthalten?", "Ja. Jede bei uns gehostete Website erhält ein kostenloses SSL-Zertifikat, das sich automatisch erneuert – Ihre Seite lädt immer sicher über https://."),
      "hr": ("Je li SSL certifikat uključen?", "Da. Svaka stranica koju hostamo dobiva besplatan SSL certifikat koji se automatski obnavlja, pa se stranica uvijek učitava sigurno preko https://.")}),
    ("Hosting", "Where are your servers located?",
     "Our servers are located in the European Union, so your data and your visitors' data stay under GDPR protection.",
     {"de": ("Wo stehen Ihre Server?", "Unsere Server stehen in der Europäischen Union – Ihre Daten und die Ihrer Besucher bleiben damit unter dem Schutz der DSGVO."),
      "hr": ("Gdje se nalaze vaši poslužitelji?", "Naši poslužitelji nalaze se u Europskoj uniji, pa vaši podaci i podaci vaših posjetitelja ostaju pod zaštitom GDPR-a.")}),
    ("Hosting", "Do you make backups?",
     "Yes. Websites are backed up regularly and can be restored if something goes wrong.",
     {"de": ("Machen Sie Backups?", "Ja. Websites werden regelmäßig gesichert und können wiederhergestellt werden, falls etwas schiefgeht."),
      "hr": ("Radite li sigurnosne kopije?", "Da. Stranice se redovito sigurnosno kopiraju i mogu se vratiti ako nešto pođe po zlu.")}),
    ("Hosting", "Can you move my existing website to your hosting?",
     "Yes. We move your website, files and databases for you and switch over with as little downtime as possible.",
     {"de": ("Können Sie meine bestehende Website zu Ihnen umziehen?", "Ja. Wir ziehen Ihre Website mit Dateien und Datenbanken für Sie um und stellen mit möglichst wenig Ausfallzeit um."),
      "hr": ("Možete li premjestiti moju postojeću stranicu na vaš hosting?", "Da. Premještamo vašu stranicu, datoteke i baze podataka umjesto vas, uz što kraći prekid rada.")}),
    ("Domains", "Can I keep my existing domain?",
     "Of course. You can transfer the domain to us, or keep it where it is and we simply point it to your new website.",
     {"de": ("Kann ich meine bestehende Domain behalten?", "Natürlich. Sie können die Domain zu uns übertragen oder dort lassen, wo sie ist – wir verbinden sie einfach mit Ihrer neuen Website."),
      "hr": ("Mogu li zadržati postojeću domenu?", "Naravno. Domenu možete prenijeti k nama ili je ostaviti gdje jest – mi je samo povežemo s novom stranicom.")}),
    ("Support", "How do I get help if something isn't working?",
     "Write to us by email or through the contact form. You talk directly to the people who built and host your website – no call centres, no ticket ping-pong.",
     {"de": ("Wie bekomme ich Hilfe, wenn etwas nicht funktioniert?", "Schreiben Sie uns per E-Mail oder über das Kontaktformular. Sie sprechen direkt mit den Menschen, die Ihre Website gebaut haben und hosten – kein Callcenter, kein Ticket-Pingpong."),
      "hr": ("Kako dobiti pomoć ako nešto ne radi?", "Pišite nam e-mailom ili putem obrasca. Razgovarate izravno s ljudima koji su izradili i hostaju vašu stranicu – bez call centra i beskonačnih tiketa.")}),
]
