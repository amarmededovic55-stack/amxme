# Signed: ASDHEM | AMXME Web Solutions
"""Editable text content: schema (drives the admin forms) + defaults + seed data."""


def F(key, label, type="text", default="", help=""):
    return {"key": key, "label": label, "type": type, "default": default, "help": help}


SECTIONS = [
    {
        "slug": "hero", "title": "Homepage – Hero", "icon": "home",
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
              default="Fast & Secure Servers\nResponsive Support\nScalable Solutions\nAffordable Prices"),
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
            F("contact_eyebrow", "Contact – label", default="Get in touch"),
            F("contact_title", "Contact – heading", default="Let's Build Something Great"),
            F("contact_intro", "Contact – intro", "textarea",
              default="Tell us about your project. We'll get back to you with ideas, a plan and a clear quote."),
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
              default="Websites, forums and web applications\nHosting, domains and SSL in one place\nOngoing maintenance and support\nClear communication, fair pricing"),
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
        ("Affordable & Flexible", "tag", "Fair, transparent pricing and packages tailored to what you actually need."),
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
