# Signed: ASDHEM | AMXME Web Solutions
"""Editable text content: schema (drives the admin forms) + defaults + seed data."""


def F(key, label, type="text", default="", help=""):
    return {"key": key, "label": label, "type": type, "default": default, "help": help}


SECTIONS = [
    {
        "slug": "hero", "title": "Početna stranica", "icon": "home",
        "intro": "The first thing visitors see at the top of the homepage.",
        "fields": [
            F("hero_promo", "Promotional badge", default="Websites · Forums · Hosting · Domains",
              help="Small pill shown above the heading. Leave empty to hide."),
            F("hero_tagline", "Script tagline", default="Your Website. Our Expertise."),
            F("hero_title", "Main heading", default="Web Development & Hosting Services"),
            F("hero_highlight", "Highlighted words", default="Hosting",
              help="Part of the main heading shown in the purple gradient."),
            F("hero_motto", "Motto", default="Build. Host. Grow."),
            F("hero_subtitle", "Subtitle / description", "textarea",
              default="From custom websites and forums to reliable hosting solutions – we provide everything you need to build and grow your online presence."),
            F("hero_checks", "Checklist (one per line)", "lines",
              default="Fast & Secure Servers\nResponsive Support\nScalable Solutions\nPersonal Offers on Request"),
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
              default="A selection of websites, platforms and communities we have designed, built and hosted."),
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
            F("cta_title", "Call-to-action band – heading", default="Ready to take your business online?"),
            F("cta_text", "Call-to-action band – text", "textarea",
              default="Whether you need a new website, a community forum or a reliable home for your existing project – we're here to help."),
            F("cta_btn_text", "Call-to-action band – button", default="Start Your Project"),
            F("cta_btn_link", "Call-to-action band – button link", default="#contact"),
        ],
    },
    {
        "slug": "hosting", "title": "Hosting Section", "icon": "server",
        "intro": "Text of the dedicated hosting section. Highlights are managed under “Hosting Highlights”.",
        "fields": [
            F("hosting_eyebrow", "Label", default="Web hosting"),
            F("hosting_title", "Heading", default="Hosting That Keeps Your Website Fast & Secure"),
            F("hosting_text", "Text", "textarea",
              default="Your website deserves a solid home. We run carefully maintained servers with SSL, regular backups and proactive monitoring – so you can focus on your business while we take care of the technology."),
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
              default="AMXME Web Solutions is a web development and hosting company helping businesses, entrepreneurs and individuals build a strong presence online.\n\nWe design and develop custom websites and web applications, build and maintain discussion forums and community platforms, and host them on reliable, secure infrastructure. From registering your domain to keeping your website updated years after launch, we offer complete online solutions under one roof.",
              help="Separate paragraphs with an empty line."),
            F("about_points", "Key points (one per line)", "lines",
              default="Websites, forums and web applications\nHosting, domains and SSL in one place\nOngoing maintenance and support\nClear communication, offers on request"),
            F("about_image", "Image", "image", default="",
              help="Optional. Without an image, a designed brand card is shown."),
            F("company_name", "Company name", default="AMXME Web Solutions"),
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
              default="Web development, forum development, hosting and domain services for businesses, entrepreneurs and individuals."),
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
            F("legal_name", "Full name of the owner", default="",
              help="Required. Your real first and last name (a company name alone is not enough for sole traders)."),
            F("legal_company", "Business name", default="AMXME Web Solutions",
              help="Optional. Trading name / company. For a GmbH/UG also add the legal form, e.g. “AMXME UG (haftungsbeschränkt)”."),
            F("legal_street", "Street and house number", default="", help="Required. A real postal address – no P.O. box."),
            F("legal_city", "Postal code and city", default="", help="Required. e.g. 10115 Berlin"),
            F("legal_country", "Country", default="Germany"),
            F("legal_email", "Email (legal contact)", "email", default="support@amxme.info"),
            F("legal_phone", "Phone", default="", help="Strongly recommended – the law asks for a fast, direct way to contact you."),
            F("legal_vat", "VAT ID (USt-IdNr.)", default="",
              help="Only if you have one. Leave empty if you are a small business (Kleinunternehmer) without VAT ID."),
            F("legal_register", "Commercial register", default="",
              help="Only for registered companies, e.g. “Amtsgericht Berlin, HRB 123456”. Otherwise leave empty."),
            F("legal_responsible", "Responsible for content (§ 18 (2) MStV)", default="",
              help="Name and address of the person responsible for editorial content. Leave empty to use the owner above."),
            F("legal_authority", "Data protection supervisory authority", "textarea", default="",
              help="Optional. The authority of your German federal state, e.g. “Berliner Beauftragte für Datenschutz und Informationsfreiheit, Alt-Moabit 59-61, 10555 Berlin”."),
            F("legal_host", "Hosting provider", "textarea",
              default="Hostnet B.V., De Ruyterkade 6, 1013 AA Amsterdam, The Netherlands",
              help="The company whose server runs this website. Check it matches your contract (Auftragsverarbeitungsvertrag / DPA)."),
            F("legal_mail_provider", "Email provider", "textarea",
              default="IONOS SE, Elgendorfer Str. 57, 56410 Montabaur, Germany",
              help="The company that sends and stores your emails (contact form notifications and replies)."),
            F("message_retention_months", "Delete contact messages after (months)", default="12",
              help="Messages older than this are deleted automatically. 0 = never delete (not recommended under GDPR)."),
            F("privacy_updated", "Privacy Policy – last updated", default="November 2026"),
            F("privacy_extra", "Privacy Policy – additional section", "textarea", default="",
              help="Optional extra text shown at the end of the Privacy Policy (e.g. if you add new services later). Separate paragraphs with an empty line."),
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
              default="Our new website is on its way. In the meantime we are fully available for web development, hosting, domains and website maintenance – just send us an email."),
            F("maintenance_tags", "Keywords (one per line)", "lines",
              default="Web Hosting\nVPS & Servers\nDomains\nSSL Certificates\nWebsite Development\nForums"),
        ],
    },
    {
        "slug": "autoreply", "title": "Auto-Reply Email", "icon": "send",
        "intro": "Automatic confirmation email sent to everyone who submits the contact form.",
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
            F("site_title", "Page title", default="AMXME Web Solutions – Web Development & Hosting Services"),
            F("meta_description", "Meta description", "textarea",
              default="AMXME Web Solutions builds custom websites, forums and web applications and provides reliable web hosting, domains, SSL and website maintenance."),
            F("brand_name", "Logo – name", default="AMXME"),
            F("brand_sub", "Logo – subtitle", default="Web Solutions"),
        ],
    },
]

SECTION_MAP = {s["slug"]: s for s in SECTIONS}
DEFAULTS = {f["key"]: f["default"] for s in SECTIONS for f in s["fields"]}
FIELD_SECTION = {f["key"]: s["slug"] for s in SECTIONS for f in s["fields"]}


SEED_SERVICES = [
    ("Custom Website Development", "code",
     "Fast, modern and fully responsive websites designed around your brand and built to convert visitors into customers.",
     "Business websites\nLanding pages\nPortfolio websites\nCustom web applications\nE-commerce websites"),
    ("Forum Development", "messages",
     "Engaging discussion forums and community platforms – installed, configured, themed and maintained for you.",
     "Custom discussion forums\nCommunity platforms\nForum installation and configuration\nCustom themes and modifications\nForum maintenance and support"),
    ("Web Hosting", "server",
     "Secure, reliable hosting for websites of every size – from a first personal site to demanding business projects.",
     "Shared web hosting\nProfessional hosting solutions\nVPS hosting\nDedicated server solutions\nWebsite migration"),
    ("Domain Services", "globe",
     "Find, register and manage the perfect domain, with DNS and SSL configured correctly from day one.",
     "Domain registration\nDNS configuration\nDomain transfers\nSSL certificates"),
    ("Website Maintenance", "wrench",
     "Keep your website secure, up to date and running smoothly while you focus on your business.",
     "Security updates\nRegular backups\nBug fixes\nPerformance optimization\nTechnical support"),
]

SEED_FEATURES = {
    "why": [
        ("Professional Development", "code", "Clean, modern code and thoughtful design, built to industry best practices."),
        ("Fast & Reliable Hosting", "zap", "Optimized servers that keep your website quick and consistently available."),
        ("Security-Focused Solutions", "shield-check", "SSL, updates, hardening and backups are part of everything we build."),
        ("Responsive Customer Support", "headphones", "Real people who know your project and answer quickly and clearly."),
        ("Scalable Infrastructure", "layers", "Start small and grow – your hosting and website scale with your business."),
        ("Offers on Request", "tag", "No fixed packages – every offer is put together for what you actually need. Just ask us by email."),
    ],
    "hosting": [
        ("Reliable Server Infrastructure", "server", "Carefully maintained, monitored servers you can count on."),
        ("Fast Loading Performance", "gauge", "Tuned web servers and caching for snappy page loads."),
        ("Secure Hosting Environment", "shield", "Firewalls, isolation and regular security updates."),
        ("SSL Support", "lock", "Free, auto-renewing SSL certificates for every website."),
        ("Regular Backups", "refresh", "Your data is backed up regularly and can be restored."),
        ("Easy Website Management", "sliders", "We handle the technical side so you don't have to."),
        ("Scalable Hosting Solutions", "trending-up", "Move from shared hosting to VPS or dedicated as you grow."),
    ],
    "badge": [
        ("Secure & Reliable", "shield-check", ""),
        ("Expert Support", "headphones", ""),
        ("Blazing Fast Speed", "zap", ""),
        ("Your Success, Our Priority", "heart", ""),
    ],
}

SEED_PROJECTS = [
    ("Business Website", "Sample project – a modern, responsive company website with service pages and a contact form. Replace it with your own work in the admin panel.",
     "Business Website", "HTML, CSS, JavaScript", "/static/img/samples/business.svg"),
    ("Community Forum", "Sample project – a themed discussion forum with categories, member profiles and moderation tools.",
     "Forum", "Forum software, Custom theme", "/static/img/samples/forum.svg"),
    ("Online Store", "Sample project – an e-commerce website with product catalog, cart and secure checkout.",
     "E-commerce", "E-commerce, Payments, SSL", "/static/img/samples/shop.svg"),
]


# ASDHEM | example FAQ – review and adapt every answer in Admin → FAQ before going live
SEED_FAQ = [
    ("General", "What exactly does AMXME do?",
     "We build websites, web applications and discussion forums, and we host them on our own carefully maintained servers. Domains, SSL, backups and ongoing maintenance are included in what we offer – one partner for everything online."),
    ("General", "How do we start working together?",
     "Send us a short message through the contact form: what you need, any examples you like and your timeline. We reply with questions or a non-binding proposal. Nothing starts until you agree."),
    ("General", "What do your services cost?",
     "We do not publish fixed prices, because every project is different. Send us a short description of what you need by email or through the contact form, and we will reply with a personal, non-binding offer."),
    ("Websites", "How long does it take to build a website?",
     "It depends on the size of the project. A compact business website is much faster than a custom web application. You receive a realistic timeline together with your quote."),
    ("Websites", "Will my website work on phones and tablets?",
     "Yes. Every website we build is fully responsive and tested on phones, tablets and desktops, because most visitors arrive on a phone today."),
    ("Websites", "Can I update the content myself?",
     "Yes, if you want to. We can build your website with a simple admin panel so you can change texts, images and projects yourself – or we take care of updates for you."),
    ("Hosting", "Is an SSL certificate included?",
     "Yes. Every website we host gets a free SSL certificate that renews automatically, so your site always loads securely over https://."),
    ("Hosting", "Where are your servers located?",
     "Our servers are located in the European Union, so your data and your visitors' data stay under GDPR protection."),
    ("Hosting", "Do you make backups?",
     "Yes. Websites are backed up regularly and can be restored if something goes wrong."),
    ("Hosting", "Can you move my existing website to your hosting?",
     "Yes. We migrate your website, files, databases and emails for you and switch over with as little downtime as possible."),
    ("Domains", "Can I keep my existing domain?",
     "Of course. You can transfer the domain to us, or keep it where it is and we simply point it to your new website."),
    ("Support", "How do I get help if something isn't working?",
     "Write to us by email or through the contact form. You talk directly to the people who built and host your website – no call centres, no ticket ping-pong."),
]

