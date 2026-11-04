#!/usr/bin/env python3
"""Builds the English and Greek pages of sotkaretsos.github.io.

Content lives in this file (texts in both languages) and in assets/data/publications.json
(the full publication list). Edit them, then run from the repository root:

    python3 scripts/build.py

It writes index.html, posters.html, publications.html, their Greek versions under el/,
sitemap.xml and robots.txt. Commit the generated files; GitHub Pages serves them as they are.
"""
import html
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
SITE = "https://sotkaretsos.github.io"
E = html.escape

SCHOLAR = "https://scholar.google.com/citations?user=FmCZkIkAAAAJ"
SCOPUS = "https://www.scopus.com/authid/detail.uri?authorId=57204351053"
GITHUB = "https://github.com/sotkaretsos"
AUA = "https://w1.aua.gr/aoa/en/faculty/karetsos-sotirios/"
BOOK = "https://www.igi-global.com/book/modern-technological-improvement-agriculture-agribusiness/349988"
EVOO_DEMO = "https://sotkaretsos.github.io/evoo-carbon-ledger/"
EVOO_CODE = "https://github.com/sotkaretsos/evoo-carbon-ledger"
PORK_DEMO = "https://sotkaretsos.github.io/pork-traceability/"
PORK_SIMPLE = "https://sotkaretsos.github.io/pork-traceability/simplified/"
PORK_CODE = "https://github.com/sotkaretsos/pork-traceability"
doi = lambda d: f"https://doi.org/{d}"

ICON = {
    "scholar": '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M12 3 1 9.5l4 2.4V17c0 1.7 3.1 4 7 4s7-2.3 7-4v-5.1l2-1.2V16h2V9.5L12 3Zm0 2.3 7.4 4.2L12 13.7 4.6 9.5 12 5.3ZM7 13.1l5 3 5-3V17c0 .5-1.9 2-5 2s-5-1.5-5-2v-3.9Z"/></svg>',
    "scopus": '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="10.5" cy="10.5" r="6" fill="none" stroke="currentColor" stroke-width="2.2"/><path d="m15 15 5.5 5.5" stroke="currentColor" stroke-width="2.4" stroke-linecap="round"/></svg>',
    "github": '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M12 2a10 10 0 0 0-3.2 19.5c.5.1.7-.2.7-.5v-1.7c-2.8.6-3.4-1.3-3.4-1.3-.4-1.2-1.1-1.5-1.1-1.5-.9-.6.1-.6.1-.6 1 .1 1.5 1 1.5 1 .9 1.5 2.3 1.1 2.9.8.1-.6.3-1.1.6-1.3-2.2-.3-4.6-1.1-4.6-5 0-1.1.4-2 1-2.7-.1-.3-.4-1.3.1-2.7 0 0 .8-.3 2.8 1a9.6 9.6 0 0 1 5 0c1.9-1.3 2.8-1 2.8-1 .5 1.4.2 2.4.1 2.7.6.7 1 1.6 1 2.7 0 3.9-2.3 4.7-4.6 5 .4.3.7.9.7 1.9V21c0 .3.2.6.7.5A10 10 0 0 0 12 2Z"/></svg>',
    "aua": '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M12 3 2 8v2h20V8L12 3Zm-7 9v6H3v2h18v-2h-2v-6h-2v6h-3v-6h-4v6H7v-6H5Z"/></svg>',
}

# --------------------------------------------------------------------------------------------
# Texts. Each entry: {"en": ..., "el": ...}. Strings may contain HTML.
# --------------------------------------------------------------------------------------------
T = {
    "name": {"en": "Sotirios T. Karetsos", "el": "Σωτήριος Θ. Καρέτσος"},
    "eyebrow": {"en": "Agricultural University of Athens", "el": "Γεωπονικό Πανεπιστήμιο Αθηνών"},
    "role": {
        "en": "Assistant Professor, Informatics Laboratory, Department of Agricultural Economics and Rural Development",
        "el": "Επίκουρος Καθηγητής, Εργαστήριο Πληροφορικής, Τμήμα Αγροτικής Οικονομίας και Ανάπτυξης",
    },
    "pitch": {
        "en": "I study how digital technologies — blockchain, artificial intelligence and mobile apps — make agri-food supply chains transparent and help farmers make better decisions.",
        "el": "Μελετώ πώς οι ψηφιακές τεχνολογίες —το blockchain, η τεχνητή νοημοσύνη και οι εφαρμογές για κινητά— κάνουν διαφανείς τις αγροδιατροφικές αλυσίδες και βοηθούν τους παραγωγούς να παίρνουν καλύτερες αποφάσεις.",
    },
    "aua_profile": {"en": "University profile", "el": "Σελίδα στο ΓΠΑ"},
    "photo_alt": {"en": "Portrait of Sotirios Karetsos", "el": "Φωτογραφία του Σωτήριου Καρέτσου"},
    "nav": {
        "en": [("news", "News"), ("research", "Research"), ("publications", "Publications"), ("projects", "Projects"), ("teaching", "Teaching"), ("experience", "Experience"), ("posters", "Posters"), ("contact", "Contact")],
        "el": [("news", "Νέα"), ("research", "Έρευνα"), ("publications", "Δημοσιεύσεις"), ("projects", "Έργα"), ("teaching", "Διδασκαλία"), ("experience", "Πορεία"), ("posters", "Αφίσες"), ("contact", "Επικοινωνία")],
    },
    "h_news": {"en": "News", "el": "Νέα"},
    "h_research": {"en": "Research themes", "el": "Ερευνητικές θεματικές"},
    "research_lead": {
        "en": "My current work falls into four themes. Each links to the articles, posters and software behind it.",
        "el": "Η τρέχουσα δουλειά μου χωρίζεται σε τέσσερις θεματικές. Η καθεμία παραπέμπει στα άρθρα, τις αφίσες και το λογισμικό της.",
    },
    "h_publications": {"en": "Publications", "el": "Δημοσιεύσεις"},
    "pubs_lead": {
        "en": "84 peer-reviewed papers — 25 in journals, 12 in edited volumes and 47 in conference proceedings — and 67 reports for the European Commission's Joint Research Centre.",
        "el": "84 εργασίες με κρίση —25 σε περιοδικά, 12 σε συλλογικούς τόμους και 47 σε πρακτικά συνεδρίων— και 67 εκθέσεις για το Joint Research Centre της Ευρωπαϊκής Επιτροπής.",
    },
    "citations": {"en": "citations", "el": "αναφορές"},
    "asof": {"en": "Citation counts as of 3 November 2026.", "el": "Αναφορές στις 3 Νοεμβρίου 2026."},
    "selected": {"en": "Selected journal articles", "el": "Επιλεγμένα άρθρα σε περιοδικά"},
    "all_pubs": {"en": "All 84 publications, by year →", "el": "Όλες οι 84 δημοσιεύσεις ανά έτος →"},
    "book_kind": {"en": "Edited volume", "el": "Συλλογικός τόμος (επιμέλεια)"},
    "book_desc": {
        "en": "Theoretical and applied research on the benefits of modern technological advances in agriculture and agribusiness, with particular attention to the role of information and communication technologies.",
        "el": "Θεωρητική και εφαρμοσμένη έρευνα για τα οφέλη των σύγχρονων τεχνολογιών στη γεωργία και στις αγροτικές επιχειρήσεις, με έμφαση στον ρόλο των τεχνολογιών πληροφορικής και επικοινωνιών.",
    },
    "editors": {"en": "Editors", "el": "Επιμέλεια"},
    "editors_v": {"en": "Sotirios Karetsos, Constantina Costopoulou", "el": "Σωτήριος Καρέτσος, Κωνσταντίνα Κωστοπούλου"},
    "publisher": {"en": "Publisher", "el": "Εκδότης"},
    "chapter": {"en": "Chapter", "el": "Κεφάλαιο"},
    "book_page": {"en": "Book page at IGI Global", "el": "Σελίδα του βιβλίου στο IGI Global"},
    "h_projects": {"en": "Projects and research software", "el": "Έργα και ερευνητικό λογισμικό"},
    "h_selected_projects": {"en": "Selected projects", "el": "Επιλεγμένα έργα"},
    "live_demo": {"en": "Live demo", "el": "Live demo"},
    "code": {"en": "Code", "el": "Κώδικας"},
    "simplified": {"en": "Simplified model", "el": "Απλοποιημένο μοντέλο"},
    "h_teaching": {"en": "Teaching and students", "el": "Διδασκαλία και φοιτητές"},
    "h_courses": {"en": "Courses", "el": "Μαθήματα"},
    "h_supervision": {"en": "Supervision", "el": "Επιβλέψεις"},
    "h_students": {"en": "Thesis topics", "el": "Θέματα εργασιών"},
    "h_experience": {"en": "Experience and education", "el": "Επαγγελματική πορεία και σπουδές"},
    "h_exp": {"en": "Experience", "el": "Επαγγελματική πορεία"},
    "h_edu": {"en": "Education", "el": "Σπουδές"},
    "h_service": {"en": "Editorial service", "el": "Εκδοτικό έργο"},
    "h_posters": {"en": "Posters", "el": "Αφίσες"},
    "posters_more": {"en": "All posters with abstracts and PDFs →", "el": "Όλες οι αφίσες με περιλήψεις και PDF →"},
    "h_contact": {"en": "Contact", "el": "Επικοινωνία"},
    "contact": {
        "en": f'Informatics Laboratory, Department of Agricultural Economics and Rural Development, Agricultural University of Athens, Iera Odos 75, 11855 Athens, Greece. My contact details are listed on my <a href="{AUA}">university profile</a>.',
        "el": f'Εργαστήριο Πληροφορικής, Τμήμα Αγροτικής Οικονομίας και Ανάπτυξης, Γεωπονικό Πανεπιστήμιο Αθηνών, Ιερά Οδός 75, 11855 Αθήνα. Τα στοιχεία επικοινωνίας μου βρίσκονται στη <a href="{AUA}">σελίδα μου στο Πανεπιστήμιο</a>.',
    },
    "tools": {"en": "Tools: farmer revenue calculator", "el": "Εργαλεία: υπολογιστής εσόδων αγρότη"},
    "home": {"en": "Home", "el": "Αρχική"},
    "full_image": {"en": "Full-size image", "el": "Εικόνα σε πλήρες μέγεθος"},
    "open_full": {"en": "Open the poster at full size", "el": "Άνοιγμα της αφίσας σε πλήρες μέγεθος"},
    "posters_lead": {
        "en": "Posters presented by my students and me, newest first. Click a poster to open it at full size.",
        "el": "Αφίσες που παρουσίασαν οι φοιτητές μου και εγώ, οι νεότερες πρώτες. Πατήστε σε μια αφίσα για να ανοίξει σε πλήρες μέγεθος.",
    },
    "pubs_page_lead": {
        "en": "Peer-reviewed publications, newest first, as listed in my CV. Titles appear in the language of publication.",
        "el": "Δημοσιεύσεις με κρίση, οι νεότερες πρώτες, όπως στο βιογραφικό μου. Οι τίτλοι εμφανίζονται στη γλώσσα δημοσίευσης.",
    },
    "f_all": {"en": "All", "el": "Όλες"},
    "f_journal": {"en": "Journals", "el": "Περιοδικά"},
    "f_chapter": {"en": "Book chapters", "el": "Κεφάλαια βιβλίων"},
    "f_conference": {"en": "Conferences", "el": "Συνέδρια"},
    "k_journal": {"en": "Journal", "el": "Περιοδικό"},
    "k_chapter": {"en": "Chapter", "el": "Κεφάλαιο"},
    "k_conference": {"en": "Conference", "el": "Συνέδριο"},
    "search": {"en": "Search title, author or venue", "el": "Αναζήτηση σε τίτλο, συγγραφέα ή περιοδικό"},
    "count_tpl": {"en": "Showing {n} of {total}", "el": "Εμφανίζονται {n} από {total}"},
    "filter_label": {"en": "Filter publications", "el": "Φιλτράρισμα δημοσιεύσεων"},
    "pubs_note": {
        "en": f'Citations and the latest additions: <a href="{SCHOLAR}">Google Scholar</a> · <a href="{SCOPUS}">Scopus</a>.',
        "el": f'Αναφορές και οι πιο πρόσφατες προσθήκες: <a href="{SCHOLAR}">Google Scholar</a> · <a href="{SCOPUS}">Scopus</a>.',
    },
}

NEWS = [
    {"date": {"en": "Nov 2026", "el": "Νοέ 2026"},
     "en": "The second cycle of the online programme <b>Advanced Digital Skills in Blockchain for Trusted Food Supply Chains</b> starts at the Centre for Training and Lifelong Learning of the Agricultural University of Athens (92.5 hours, 3.7 ECTS). I am its academic coordinator.",
     "el": "Ξεκινά ο δεύτερος κύκλος του εξ αποστάσεως προγράμματος <b>«Προηγμένες Ψηφιακές Δεξιότητες σε Blockchain για Αξιόπιστες Εφοδιαστικές Αλυσίδες Τροφίμων»</b> του ΚΕΔΙΒΙΜ του Γεωπονικού Πανεπιστημίου Αθηνών (92,5 ώρες, 3,7 ECTS). Είμαι ο ακαδημαϊκός υπεύθυνος."},
    {"date": {"en": "Oct 2026", "el": "Οκτ 2026"},
     "en": "Joined the research team of <b>AGRINEXT</b>, a Horizon Europe project coordinated by the Agricultural University of Athens on skills and knowledge ecosystems for competitive and sustainable farming.",
     "el": "Εντάχθηκα στην ερευνητική ομάδα του <b>AGRINEXT</b>, έργου Horizon Europe με συντονιστή το Γεωπονικό Πανεπιστήμιο Αθηνών, για τα οικοσυστήματα γνώσης και δεξιοτήτων στη βιώσιμη και ανταγωνιστική γεωργία."},
    {"date": {"en": "Oct 2026", "el": "Οκτ 2026"},
     "en": 'Poster at <a href="{p}posters.html#haicta2026">HAICTA 2026</a> in Kos on blockchain-based carbon-footprint monitoring in olive oil production.',
     "el": 'Αφίσα στο <a href="{p}posters.html#haicta2026">HAICTA 2026</a> στην Κω για την παρακολούθηση του αποτυπώματος άνθρακα στην παραγωγή ελαιολάδου με blockchain.'},
    {"date": {"en": "Jul 2026", "el": "Ιούλ 2026"},
     "en": f'Two papers at EDULEARN26 in Palma on evaluating <a href="{doi("10.21125/edulearn.2026.2194")}">large language models for beekeeping education</a> and <a href="{doi("10.21125/edulearn.2026.2195")}">AI tools for landscape architecture education</a>.',
     "el": f'Δύο εργασίες στο EDULEARN26 στην Πάλμα για την αξιολόγηση <a href="{doi("10.21125/edulearn.2026.2194")}">μεγάλων γλωσσικών μοντέλων στη μελισσοκομική εκπαίδευση</a> και <a href="{doi("10.21125/edulearn.2026.2195")}">εργαλείων τεχνητής νοημοσύνης στην εκπαίδευση αρχιτεκτονικής τοπίου</a>.'},
    {"date": {"en": "2026", "el": "2026"},
     "en": f'<a href="{doi("10.1109/ACCESS.2026.3721509")}">“Chatbots in Agriculture: A Literature Review”</a> published in <i>IEEE Access</i>.',
     "el": f'Δημοσιεύτηκε στο <i>IEEE Access</i> η ανασκόπηση <a href="{doi("10.1109/ACCESS.2026.3721509")}">«Chatbots in Agriculture: A Literature Review»</a>.'},
]

TAGS = {
    "article": {"en": "Article", "el": "Άρθρο"},
    "chapter": {"en": "Chapter", "el": "Κεφάλαιο"},
    "paper": {"en": "Paper", "el": "Εργασία"},
    "poster": {"en": "Poster", "el": "Αφίσα"},
    "demo": {"en": "Demo", "el": "Demo"},
}

THEMES = [
    {"title": {"en": "Blockchain traceability for agri-food", "el": "Ιχνηλασιμότητα τροφίμων με blockchain"},
     "desc": {"en": "Records that travel with the product and can be audited — olive oil, fisheries, dairy, honey and pork — and the skills supply-chain actors need to use them.",
              "el": "Εγγραφές που ακολουθούν το προϊόν και μπορούν να ελεγχθούν —ελαιόλαδο, αλιεία, γάλα, μέλι, χοιρινό— και οι δεξιότητες που χρειάζονται οι φορείς της αλυσίδας για να τις αξιοποιήσουν."},
     "items": [
         ("article", f'<a href="{doi("10.3390/s24248189")}">Blockchain and IoT technologies for food traceability in olive oil supply chains</a> · <i>Sensors</i>, 2024'),
         ("poster", '<a href="{p}posters.html#haicta2026">Carbon-footprint monitoring in early-stage olive oil production</a> · HAICTA 2026'),
         ("poster", '<a href="{p}posters.html#hsce2024">Blockchain-based traceability in fisheries</a> · 2024'),
         ("paper", f'<a href="{doi("10.21125/iceri.2024.2499")}">Evaluating a blockchain training course for food supply-chain stakeholders</a> · ICERI 2024'),
         ("demo", f'<a href="{EVOO_DEMO}">EVOO Carbon Ledger</a> · <a href="{PORK_DEMO}">Pork Traceability</a>'),
     ]},
    {"title": {"en": "AI and chatbots for agriculture", "el": "Τεχνητή νοημοσύνη και chatbots στη γεωργία"},
     "desc": {"en": "How chatbots and large language models can advise farmers and support agricultural education, and how far their answers can be trusted.",
              "el": "Πώς τα chatbots και τα μεγάλα γλωσσικά μοντέλα μπορούν να συμβουλεύουν παραγωγούς και να στηρίζουν τη γεωργική εκπαίδευση, και πόσο αξιόπιστες είναι οι απαντήσεις τους."},
     "items": [
         ("article", f'<a href="{doi("10.1109/ACCESS.2026.3721509")}">Chatbots in agriculture: a literature review</a> · <i>IEEE Access</i>, 2026'),
         ("chapter", f'<a href="{doi("10.4018/979-8-3693-8237-0.ch009")}">GaiaMentor AI for farmers: a conversational solution for smarter agriculture</a> · IGI Global, 2025'),
         ("paper", f'<a href="{doi("10.21125/edulearn.2026.2194")}">Evaluating large language models for educational use in beekeeping</a> · EDULEARN26'),
         ("poster", '<a href="{p}posters.html#wheatbot">WheatBot, a generative-AI assistant for wheat growers</a>'),
         ("poster", '<a href="{p}posters.html#ai-beekeeping-education">AI tools for beekeeping education</a> · 2025'),
     ]},
    {"title": {"en": "Digital farming tools and mobile apps", "el": "Εργαλεία ψηφιακής γεωργίας και εφαρμογές για κινητά"},
     "desc": {"en": "Mapping and building the apps that support growers through the crop cycle, and what makes farmers adopt them.",
              "el": "Χαρτογράφηση και ανάπτυξη εφαρμογών που στηρίζουν τους παραγωγούς σε όλο τον κύκλο καλλιέργειας, και τι κάνει τους αγρότες να τις υιοθετούν."},
     "items": [
         ("article", "A mobile app for supporting citrus fruit growers in Greece · <i>Electronics</i>, 2022"),
         ("article", "Intention to use drones in agriculture: evidence from Greece · <i>Modern Concepts and Developments in Agronomy</i>, 2022"),
         ("article", "Investigating educational mobile apps for agriculture · <i>Int. J. of Sustainable Agricultural Management and Informatics</i>, 2020"),
         ("poster", '<a href="{p}posters.html#strawberry">Digital farming tools in strawberry cultivation and the StrawBot assistant</a>'),
     ]},
    {"title": {"en": "Digital marketing and e-government in agri-food", "el": "Ψηφιακό μάρκετινγκ και ηλεκτρονική διακυβέρνηση στον αγροδιατροφικό τομέα"},
     "desc": {"en": "How agri-food businesses and public services use the web, social media and mobile channels to reach consumers, farmers and citizens.",
              "el": "Πώς οι αγροδιατροφικές επιχειρήσεις και οι δημόσιες υπηρεσίες αξιοποιούν το διαδίκτυο, τα μέσα κοινωνικής δικτύωσης και τα κινητά για να φτάσουν σε καταναλωτές, παραγωγούς και πολίτες."},
     "items": [
         ("article", f'<a href="{doi("10.3390/info17101018")}">Social media analytics for evaluating digital marketing performance: olive oil enterprises in Greece</a> · <i>Information</i>, 2026'),
         ("article", f'<a href="{doi("10.37394/23207.2026.23.78")}">Exploring augmented reality marketing in the food and beverage industry</a> · <i>WSEAS Trans. on Business and Economics</i>, 2026'),
         ("article", "Evaluating social media marketing in the Greek winery industry · <i>Sustainability</i>, 2023"),
         ("article", "Mobile government: a challenge for agriculture · <i>Government Information Quarterly</i>, 2008"),
     ]},
]

SELECTED = [
    f'A. D. Podaras, M. P. Petropoulos, <b>S. T. Karetsos</b>, M. S. Ntaliani, M. I. Xanthoudakis (2026). <span class="t">Chatbots in agriculture: a literature review.</span> <span class="v">IEEE Access</span>, 14. <a href="{doi("10.1109/ACCESS.2026.3721509")}">doi:10.1109/ACCESS.2026.3721509</a>',
    f'<b>S. Karetsos</b>, C. Lianou, C. Costopoulou (2026). <span class="t">Social media analytics for evaluating digital marketing performance: the case of olive oil enterprises in Greece.</span> <span class="v">Information</span>, 17, 1018. <a href="{doi("10.3390/info17101018")}">doi:10.3390/info17101018</a>',
    f'V. Vitaskos, K. Demestichas, <b>S. Karetsos</b>, C. Costopoulou (2024). <span class="t">Blockchain and Internet of Things technologies for food traceability in olive oil supply chains.</span> <span class="v">Sensors</span>, 24(24), 8189. <a href="{doi("10.3390/s24248189")}">doi:10.3390/s24248189</a>',
    'M. van der Velde, B. Baruth, A. Bussay, A. Ceglar, S. Garcia Condado, <b>S. Karetsos</b>, R. Lecerf, R. Lopez, A. Maiorano, L. Nisini, L. Seguini, M. van den Berg (2018). <span class="t">In-season performance of European Union wheat forecasts during extreme impacts.</span> <span class="v">Scientific Reports</span>, 8, 15420.',
    'M. Ntaliani, C. Costopoulou, <b>S. Karetsos</b>, E. Tambouris, K. Tarabanis (2010). <span class="t">Agricultural e-government services: an implementation framework and case study.</span> <span class="v">Computers and Electronics in Agriculture</span>, 70, 337–347.',
    'M. Ntaliani, C. Costopoulou, <b>S. Karetsos</b> (2008). <span class="t">Mobile government: a challenge for agriculture.</span> <span class="v">Government Information Quarterly</span>, 25, 699–716.',
]

PROJECTS = {
    "en": [
        "<b>TALLHEDA</b>: alliances of higher education in digital agriculture <span>· Horizon Europe, grant 101136578, coordinated by the Agricultural University of Athens</span>",
        "<b>AGRINEXT</b>: skills and knowledge ecosystems for competitive and sustainable farming <span>· Horizon Europe, grant 101295606</span>",
        "<b>Trust-Food</b>: advanced digital skills on blockchain for trusted food supply chains <span>· Digital Europe, grant 101100804</span>",
        "Academic coordinator of the programme <b>Advanced Digital Skills in Blockchain for Trusted Food Supply Chains</b> <span>· Centre for Training and Lifelong Learning, Agricultural University of Athens</span>",
    ],
    "el": [
        "<b>TALLHEDA</b>: συμμαχίες ανώτατης εκπαίδευσης στην ψηφιακή γεωργία <span>· Horizon Europe, 101136578, συντονιστής το ΓΠΑ</span>",
        "<b>AGRINEXT</b>: οικοσυστήματα γνώσης και δεξιοτήτων για ανταγωνιστική και βιώσιμη γεωργία <span>· Horizon Europe, 101295606</span>",
        "<b>Trust-Food</b>: προηγμένες ψηφιακές δεξιότητες σε blockchain για αξιόπιστες αλυσίδες τροφίμων <span>· Digital Europe, 101100804</span>",
        "Ακαδημαϊκός υπεύθυνος του προγράμματος <b>«Προηγμένες Ψηφιακές Δεξιότητες σε Blockchain για Αξιόπιστες Εφοδιαστικές Αλυσίδες Τροφίμων»</b> <span>· ΚΕΔΙΒΙΜ ΓΠΑ</span>",
    ],
}

SOFTWARE = [
    {"meta": "Solidity · Hyperledger Besu · IoT", "title": "EVOO Carbon Ledger",
     "desc": {"en": "Auditable carbon-footprint traceability for extra virgin olive oil. The live demo replays an olive-oil case study and lets you try to break the auditability rules.",
              "el": "Ελέγξιμη ιχνηλασιμότητα του αποτυπώματος άνθρακα στο εξαιρετικό παρθένο ελαιόλαδο. Το live demo αναπαράγει μια μελέτη περίπτωσης και σας αφήνει να δοκιμάσετε να παραβιάσετε τους κανόνες."},
     "links": [("live_demo", EVOO_DEMO), ("code", EVOO_CODE)]},
    {"meta": "Solidity · Hyperledger Besu · IoT", "title": "Pork Traceability",
     "desc": {"en": "Pork from the slaughterhouse to the souvlaki restaurant: verifiable origin, cold-chain checks, and recalls that reach every product made from a batch.",
              "el": "Χοιρινό από το σφαγείο ως το σουβλατζίδικο: επαληθεύσιμη προέλευση, έλεγχοι ψυχρής αλυσίδας και ανακλήσεις που φτάνουν σε κάθε προϊόν που προήλθε από μια παρτίδα."},
     "links": [("live_demo", PORK_DEMO), ("simplified", PORK_SIMPLE), ("code", PORK_CODE)]},
]

COURSES = {
    "en": [
        "Introduction to Informatics <span>· undergraduate, Department of Biotechnology</span>",
        "Management Information Systems; E-Commerce and Services <span>· undergraduate, Department of Agricultural Economics and Rural Development</span>",
        "Programming with Python <span>· MSc Systems Biology, Agricultural University of Athens</span>",
        "E-Government Information Systems <span>· MSc Public Administration and E-Government, Hellenic Open University</span>",
    ],
    "el": [
        "Εισαγωγή στην Πληροφορική <span>· προπτυχιακό, Τμήμα Βιοτεχνολογίας</span>",
        "Πληροφοριακά Συστήματα Διοίκησης· Ηλεκτρονικό Εμπόριο και Υπηρεσίες <span>· προπτυχιακά, Τμήμα Αγροτικής Οικονομίας και Ανάπτυξης</span>",
        "Προγραμματισμός με Python <span>· ΠΜΣ «Βιολογία Συστημάτων», ΓΠΑ</span>",
        "Πληροφοριακά Συστήματα Ηλεκτρονικής Διακυβέρνησης <span>· ΠΜΣ «Δημόσια Διοίκηση και Ηλεκτρονική Διακυβέρνηση», ΕΑΠ</span>",
    ],
}
SUPERVISION = {
    "en": [
        "Supervisor of two doctoral candidates <span>· machine-learning models in public administration; mixed-reality methods for adaptive learning in agriculture</span>",
        "Member of three doctoral advisory committees",
        "Supervisor of 35 undergraduate theses",
    ],
    "el": [
        "Επιβλέπων δύο υποψήφιων διδακτόρων <span>· μοντέλα μηχανικής μάθησης στη δημόσια διοίκηση· μέθοδοι μικτής πραγματικότητας για προσαρμοστική μάθηση στον αγροτικό τομέα</span>",
        "Μέλος τριών τριμελών συμβουλευτικών επιτροπών διδακτορικών",
        "Επιβλέπων 35 πτυχιακών εργασιών",
    ],
}
STUDENTS = {
    "en": (["AI tools, chatbots and large language models in agriculture",
            "Blockchain and IoT traceability in food supply chains",
            "Social media analytics and digital marketing of agri-food businesses",
            "Machine learning and data analysis for agriculture",
            "Digital twins and digital farming tools"],
           f'Students of the Agricultural University of Athens interested in a thesis in these areas can contact me through my <a href="{AUA}">university profile</a>.'),
    "el": (["Εργαλεία τεχνητής νοημοσύνης, chatbots και μεγάλα γλωσσικά μοντέλα στη γεωργία",
            "Ιχνηλασιμότητα με blockchain και Διαδίκτυο των Πραγμάτων στις αλυσίδες τροφίμων",
            "Ανάλυση μέσων κοινωνικής δικτύωσης και ψηφιακό μάρκετινγκ αγροδιατροφικών επιχειρήσεων",
            "Μηχανική μάθηση και ανάλυση δεδομένων στη γεωργία",
            "Ψηφιακά δίδυμα και εργαλεία ψηφιακής γεωργίας"],
           f'Φοιτητές και φοιτήτριες του ΓΠΑ που ενδιαφέρονται για πτυχιακή σε αυτά τα θέματα μπορούν να επικοινωνήσουν μαζί μου μέσω της <a href="{AUA}">σελίδας μου στο Πανεπιστήμιο</a>.'),
}

EXPERIENCE = [
    ({"en": "2022 – now", "el": "2022 – σήμερα"},
     {"en": "Assistant Professor, Agricultural University of Athens", "el": "Επίκουρος Καθηγητής, Γεωπονικό Πανεπιστήμιο Αθηνών"},
     {"en": "Informatics Laboratory, Department of Agricultural Economics and Rural Development · Internet Information Systems and Applications",
      "el": "Εργαστήριο Πληροφορικής, Τμήμα Αγροτικής Οικονομίας και Ανάπτυξης · «Πληροφορικά Συστήματα Διαδικτύου και Εφαρμογές»"}),
    ({"en": "2017", "el": "2017"},
     {"en": "Business Analyst, Joint Research Centre, European Commission", "el": "Αναλυτής πληροφοριακών συστημάτων, Joint Research Centre, Ευρωπαϊκή Επιτροπή"},
     {"en": "Ispra, Italy, under a framework contract · analysis of the JRC's project, publication and knowledge-management systems in UML and BPMN",
      "el": "Ίσπρα, Ιταλία, με σύμβαση-πλαίσιο · ανάλυση των συστημάτων διαχείρισης έργων, δημοσιεύσεων και γνώσης του JRC με UML και BPMN"}),
    ({"en": "2013 – 2017", "el": "2013 – 2017"},
     {"en": "Seconded National Expert, Joint Research Centre, European Commission", "el": "Αποσπασμένος Εθνικός Εμπειρογνώμονας, Joint Research Centre, Ευρωπαϊκή Επιτροπή"},
     {"en": "Food Security Unit (MARS, AGRI4CAST) · crop-yield forecasts for Greece, Cyprus, Turkey, Denmark, Sweden and India; AGRI4CAST Data Portal and BIOMA web portal",
      "el": "Μονάδα Επισιτιστικής Ασφάλειας (MARS, AGRI4CAST) · προβλέψεις αγροτικής παραγωγής για Ελλάδα, Κύπρο, Τουρκία, Δανία, Σουηδία και Ινδία· AGRI4CAST Data Portal και BIOMA"}),
    ({"en": "2009 – 2022", "el": "2009 – 2022"},
     {"en": "Ministry of Rural Development and Food", "el": "Υπουργείο Αγροτικής Ανάπτυξης και Τροφίμων"},
     {"en": "Evaluation and monitoring of development programmes run by agricultural cooperatives",
      "el": "Αξιολόγηση και παρακολούθηση αναπτυξιακών προγραμμάτων αγροτικών και κτηνοτροφικών συνεταιρισμών"}),
    ({"en": "2008 – 2009", "el": "2008 – 2009"},
     {"en": "Informatics Laboratory, Agricultural University of Athens", "el": "Εργαστήριο Πληροφορικής, Γεωπονικό Πανεπιστήμιο Αθηνών"},
     {"en": "Web applications, research-project monitoring and laboratory courses",
      "el": "Διαδικτυακές εφαρμογές, παρακολούθηση ερευνητικών έργων και εργαστηριακά μαθήματα"}),
]
EDUCATION = [
    ("2008", {"en": "PhD, Agricultural University of Athens", "el": "Διδακτορικό, Γεωπονικό Πανεπιστήμιο Αθηνών"},
     {"en": "Informatics Laboratory · thesis “Advanced Electronic Services in the Agricultural Sector”, graded Excellent",
      "el": "Εργαστήριο Πληροφορικής · διατριβή «Προηγμένες Ηλεκτρονικές Υπηρεσίες στον Αγροτικό Τομέα», βαθμός «Άριστα»"}),
    ("2001", {"en": "MSc, Techno-Economic Systems", "el": "Μεταπτυχιακό, «Τεχνο-οικονομικά Συστήματα»"},
     {"en": "National Technical University of Athens, University of Piraeus and University of Athens · Management of Technological Systems",
      "el": "ΕΜΠ, Πανεπιστήμιο Πειραιά και ΕΚΠΑ · κατεύθυνση «Διοίκηση Τεχνολογικών Συστημάτων»"}),
    ("1998", {"en": "BSc and integrated MSc, Agricultural Biotechnology", "el": "Πτυχίο (integrated master), Γεωπονική Βιοτεχνολογία"},
     {"en": "Agricultural University of Athens", "el": "Γεωπονικό Πανεπιστήμιο Αθηνών"}),
]
SERVICE = {
    "en": [
        "Guest Editor, <i>Sustainability</i> (MDPI) special issue “Digital Transformation of Agriculture and Rural Areas” <span>· 2023, second volume in preparation</span>",
        "Associate Editor, <i>International Journal of Agricultural and Environmental Information Systems</i> <span>· IGI Global</span>",
        "Outstanding reviewer, <i>Electronic Commerce Research and Applications</i> <span>· Elsevier</span>",
        "Programme committees of ICWI (2009–2026), HAICTA (2022, 2024) and EFITA-WCCA 2017",
    ],
    "el": [
        "Guest Editor, ειδικό τεύχος «Digital Transformation of Agriculture and Rural Areas» του <i>Sustainability</i> (MDPI) <span>· 2023, δεύτερος τόμος υπό έκδοση</span>",
        "Associate Editor, <i>International Journal of Agricultural and Environmental Information Systems</i> <span>· IGI Global</span>",
        "Outstanding reviewer, <i>Electronic Commerce Research and Applications</i> <span>· Elsevier</span>",
        "Επιστημονικές επιτροπές των ICWI (2009–2026), HAICTA (2022, 2024) και EFITA-WCCA 2017",
    ],
}

TALLHEDA = {"en": "Part of the TALLHEDA project, funded by the EU's Horizon Europe programme (grant agreement No. 101136578).",
            "el": "Στο πλαίσιο του έργου TALLHEDA, που χρηματοδοτείται από το πρόγραμμα Horizon Europe της ΕΕ (συμφωνία επιχορήγησης 101136578)."}

# Posters, newest first; posters without a known venue at the end.
POSTERS = [
    {"id": "haicta2026", "img": "haicta2026-olive-oil-carbon-poster", "w": 2000, "h": 1125, "thumb": "-900", "lang": "en",
     "title": {"en": "A Blockchain-Based Approach to Carbon Footprint Monitoring in Early-Stage Olive Oil Production"},
     "venue": {"en": "HAICTA 2026 · Kos · 30 September – 3 October 2026", "el": "HAICTA 2026 · Κως · 30 Σεπτεμβρίου – 3 Οκτωβρίου 2026"},
     "short": {"en": "HAICTA 2026, Kos", "el": "HAICTA 2026, Κως"},
     "authors": {"en": "M. Stavropoulou, S. Karetsos, C. Costopoulou, K. Demestichas", "el": "Μ. Σταυροπούλου, Σ. Καρέτσος, Κ. Κωστοπούλου, Κ. Δεμέστιχας"},
     "note": {"en": "A three-block traceability architecture — cultivation and harvesting, transport to the mill, processing at the mill — with independently countersigned records, applied to a Koroneiki orchard in Western Achaia over the 2022–2024 seasons. The carbon footprint of the studied EVOO is 1.993 kg CO₂eq per litre, 81.5% of it at the orchard.",
              "el": "Αρχιτεκτονική ιχνηλασιμότητας τριών blocks —καλλιέργεια και συγκομιδή, μεταφορά στο ελαιοτριβείο, επεξεργασία— με εγγραφές που προσυπογράφονται από ανεξάρτητους φορείς, σε ελαιώνα Κορωνέικης στη Δυτική Αχαΐα για τις περιόδους 2022–2024. Το αποτύπωμα άνθρακα του ελαιολάδου είναι 1,993 kg CO₂eq ανά λίτρο, το 81,5% του οποίου στον ελαιώνα."},
     "funding": TALLHEDA,
     "alt": "Poster with a three-block traceability architecture for olive oil and a bar chart of emission hotspots; 1.993 kg CO2eq per litre, 70.8% from fertilisation."},
    {"id": "ai-beekeeping-education", "img": "ai-beekeeping-education-poster", "w": 2000, "h": 1125, "thumb": "-900", "lang": "el",
     "title": {"el": "Συγκριτική Αξιολόγηση Εργαλείων Τεχνητής Νοημοσύνης για την Υποστήριξη της Μελισσοκομικής Εκπαίδευσης",
               "en": "Comparative evaluation of artificial intelligence tools supporting beekeeping education"},
     "venue": {"en": "32nd Congress of the Hellenic Society for Horticultural Science · Volos · 20–23 October 2025",
               "el": "32ο Συνέδριο της Ελληνικής Εταιρείας της Επιστήμης των Οπωροκηπευτικών · Βόλος · 20–23 Οκτωβρίου 2025"},
     "short": {"en": "Hellenic Society for Horticultural Science 2025, Volos", "el": "Ε.Ε.Ε.Ο. 2025, Βόλος"},
     "authors": {"en": "E. Kontali, S. Karetsos, C. Costopoulou, K. Demestichas, P. Harizanis", "el": "Ε. Κονταλή, Σ. Καρέτσος, Κ. Κωστοπούλου, Κ. Δεμέστιχας, Π. Χαριζάνης"},
     "note": {"en": "ChatGPT (GPT-3.5), Copilot, Gemini and Planty ChatGPT answered 20 beekeeping questions in Greek and in English, and researchers of the Laboratory of Sericulture and Apiculture judged the answers. Planty ChatGPT scored 19 out of 20 in both languages; in Greek, Copilot followed with 16, Gemini with 10 and ChatGPT-3.5 with 7.",
              "el": "Τα ChatGPT (GPT-3.5), Copilot, Gemini και Planty ChatGPT απάντησαν σε 20 ερωτήσεις μελισσοκομίας στα ελληνικά και στα αγγλικά, και τις απαντήσεις αξιολόγησε το Εργαστήριο Μελισσοκομίας-Σηροτροφίας. Το Planty ChatGPT πέτυχε 19/20 και στις δύο γλώσσες· στα ελληνικά ακολούθησαν το Copilot (16), το Gemini (10) και το ChatGPT-3.5 (7)."},
     "funding": TALLHEDA,
     "alt": "Poster with bar charts comparing ChatGPT 3.5, Gemini, Copilot and Planty ChatGPT in Greek and English."},
    {"id": "hsce2024", "img": "hsce2024-fisheries-blockchain-poster", "w": 1600, "h": 2262, "thumb": "-800", "lang": "en", "portrait": True,
     "title": {"en": "Blockchain-based Traceability Solutions in Fisheries: Insights from Greece"},
     "venue": {"en": "International Conference of the Hellenic Society for Circular Economy · Chania · 12–13 September 2024",
               "el": "Διεθνές Συνέδριο της Ελληνικής Εταιρείας Κυκλικής Οικονομίας · Χανιά · 12–13 Σεπτεμβρίου 2024"},
     "short": {"en": "Hellenic Society for Circular Economy 2024, Chania", "el": "Ελληνική Εταιρεία Κυκλικής Οικονομίας 2024, Χανιά"},
     "authors": {"en": "S. Karetsos, K. Demestichas, C. Costopoulou, G. Pantelis", "el": "Σ. Καρέτσος, Κ. Δεμέστιχας, Κ. Κωστοπούλου, Γ. Παντελής"},
     "note": {"en": "A survey of 21 Greek fish farmers, based on the Technology Acceptance Model, on their intention to adopt blockchain-based traceability. The farmers are open to it; the main barriers are the complexity of the technology, set-up and maintenance costs, and the lack of information and training from public authorities.",
              "el": "Έρευνα σε 21 Έλληνες ιχθυοκαλλιεργητές, βασισμένη στο Technology Acceptance Model, για την πρόθεσή τους να υιοθετήσουν ιχνηλασιμότητα με blockchain. Οι παραγωγοί είναι θετικοί· τα κύρια εμπόδια είναι η πολυπλοκότητα της τεχνολογίας, το κόστος εγκατάστασης και συντήρησης και η έλλειψη ενημέρωσης και κατάρτισης από τις δημόσιες αρχές."},
     "funding": {"en": "Developed in the TRUSTFOOD project, co-funded by the Digital Europe programme (grant agreement No. 101100804).",
                 "el": "Στο πλαίσιο του έργου TRUSTFOOD, που συγχρηματοδοτείται από το πρόγραμμα Digital Europe (συμφωνία επιχορήγησης 101100804)."},
     "alt": "Portrait poster with pie and bar charts from a survey of 21 Greek fish farmers on blockchain traceability."},
    {"id": "llm-beekeeping", "img": "llm-beekeeping-poster", "w": 2000, "h": 1125, "thumb": "-900", "lang": "el",
     "title": {"el": "Συγκριτική Αξιολόγηση Απόδοσης Μεγάλων Γλωσσικών Μοντέλων: Η Περίπτωση της Μελισσοκομίας",
               "en": "Comparative performance evaluation of large language models: the case of beekeeping"},
     "short": {"en": "TALLHEDA project", "el": "Έργο TALLHEDA"},
     "authors": {"en": "E.-N. Karela, S. Karetsos, C. Costopoulou, K. Demestichas", "el": "Ε.-Ν. Καρέλα, Σ. Καρέτσος, Κ. Κωστοπούλου, Κ. Δεμέστιχας"},
     "note": {"en": f'Five LLMs (LLaMA 3.2 3B Instruct, Qwen, Phi, DeepSeek, MiniOrca) answered 20 beekeeping questions using a corpus of 13 beekeeping books in GPT4All. LLaMA 3.2 3B Instruct gave 85% correct answers. Related paper: <a href="{doi("10.21125/edulearn.2026.2194")}">EDULEARN26</a>.',
              "el": f'Πέντε LLMs (LLaMA 3.2 3B Instruct, Qwen, Phi, DeepSeek, MiniOrca) απάντησαν σε 20 ερωτήσεις μελισσοκομίας με βάση 13 μελισσοκομικά βιβλία στο GPT4All. Το LLaMA 3.2 3B Instruct έδωσε 85% σωστές απαντήσεις. Σχετική εργασία: <a href="{doi("10.21125/edulearn.2026.2194")}">EDULEARN26</a>.'},
     "funding": TALLHEDA,
     "alt": "Poster with bar charts of correct answers per language model; LLaMA 3.2 3B Instruct leads with 85% and MiniOrca is last with 25%."},
    {"id": "strawberry", "img": "strawberry-digital-farming-poster", "w": 2000, "h": 1125, "thumb": "-900", "lang": "el",
     "title": {"el": "Εργαλεία Ψηφιακής Γεωργίας στην Καλλιέργεια Φράουλας", "en": "Digital farming tools in strawberry cultivation"},
     "short": {"en": "TALLHEDA project", "el": "Έργο TALLHEDA"},
     "authors": {"en": "Z. Paxinou, C. Costopoulou, S. Karetsos, K. Demestichas", "el": "Ζ. Παξινού, Κ. Κωστοπούλου, Σ. Καρέτσος, Κ. Δεμέστιχας"},
     "note": {"en": "Fifty digital farming tools were recorded, evaluated and mapped to a 16-stage strawberry crop cycle over four seasons, from soil analysis to transport. The StrawBot digital assistant guides growers to the right application for each stage.",
              "el": "Καταγράφηκαν και αξιολογήθηκαν 50 ψηφιακά εργαλεία και αντιστοιχίστηκαν σε 16 στάδια του κύκλου καλλιέργειας της φράουλας σε τέσσερις εποχές, από την ανάλυση εδάφους έως τη μεταφορά. Ο ψηφιακός βοηθός StrawBot καθοδηγεί τον παραγωγό στην κατάλληλη εφαρμογή για κάθε στάδιο."},
     "funding": TALLHEDA,
     "alt": "Poster with a 16-stage strawberry crop cycle, the digital tools mapped to each stage and the StrawBot assistant."},
    {"id": "wheatbot", "img": "wheatbot-poster", "w": 2000, "h": 1125, "thumb": "-900", "lang": "el",
     "title": {"el": "Ανάπτυξη και Αξιολόγηση Εφαρμογής Παραγωγικής Τεχνητής Νοημοσύνης για Υποστήριξη Λήψης Αποφάσεων από Παραγωγούς Σιταριού στην Ελλάδα",
               "en": "Development and evaluation of a generative AI application supporting decision-making by wheat growers in Greece"},
     "short": {"en": "TALLHEDA project", "el": "Έργο TALLHEDA"},
     "authors": {"en": "M. Mimikou, C. Costopoulou, S. Karetsos, K. Demestichas", "el": "Μ. Μιμίκου, Κ. Κωστοπούλου, Σ. Καρέτσος, Κ. Δεμέστιχας"},
     "note": {"en": "WheatBot, a chatbot built with Landbot on 60 questions and answers about sowing, irrigation, fertilisation and plant protection, was evaluated by 55 wheat growers with a questionnaire based on the Technology Acceptance Model. Ease of use scored highest (3.93 out of 5), followed by usefulness and intention to keep using it (3.78–3.80).",
              "el": "Το WheatBot, chatbot που αναπτύχθηκε με το Landbot πάνω σε 60 ερωταπαντήσεις για σπορά, άρδευση, λίπανση και φυτοπροστασία, αξιολογήθηκε από 55 παραγωγούς σιταριού με ερωτηματολόγιο βασισμένο στο Technology Acceptance Model. Η ευκολία χρήσης είχε τον υψηλότερο μέσο όρο (3,93/5), ακολουθούμενη από τη χρησιμότητα και την πρόθεση συνέχισης χρήσης (3,78–3,80)."},
     "funding": TALLHEDA,
     "alt": "Poster with screenshots of the WheatBot chatbot and bar charts of the growers' agreement with statements about it."},
]

# --------------------------------------------------------------------------------------------
# Page parts
# --------------------------------------------------------------------------------------------

def t(key, lang):
    return T[key][lang]


def pick(d, lang):
    return d.get(lang) or d.get("en") or d.get("el")


def url_of(path, lang):
    return f"{SITE}/{'el/' if lang == 'el' else ''}{path}".replace("/index.html", "/")


def head(lang, path, title, desc, extra=""):
    p = "../" if lang == "el" else ""
    other = "en" if lang == "el" else "el"
    return f"""<!doctype html>
<html lang="{lang}">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{E(title)}</title>
  <meta name="description" content="{E(desc)}">
  <meta name="color-scheme" content="light dark">
  <link rel="canonical" href="{url_of(path, lang)}">
  <link rel="alternate" hreflang="{lang}" href="{url_of(path, lang)}">
  <link rel="alternate" hreflang="{other}" href="{url_of(path, other)}">
  <link rel="alternate" hreflang="x-default" href="{url_of(path, 'en')}">
  <meta property="og:type" content="profile">
  <meta property="og:title" content="{E(title)}">
  <meta property="og:description" content="{E(desc)}">
  <meta property="og:url" content="{url_of(path, lang)}">
  <meta property="og:image" content="{SITE}/assets/img/og-card.png">
  <meta property="og:image:width" content="1200">
  <meta property="og:image:height" content="630">
  <meta property="og:locale" content="{'el_GR' if lang == 'el' else 'en_GB'}">
  <meta name="twitter:card" content="summary_large_image">
  <link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'%3E%3Crect width='64' height='64' rx='14' fill='%231f5f5b'/%3E%3Ctext x='32' y='42' font-family='Georgia,serif' font-size='28' font-weight='700' text-anchor='middle' fill='%23fff'%3ESK%3C/text%3E%3C/svg%3E">
  <link rel="stylesheet" href="{p}assets/css/site.css">
{extra}</head>
<body>
"""


def lang_switch(lang, path):
    if lang == "en":
        return f'<div class="lang" aria-label="Language"><span aria-current="true">EN</span><a href="el/{path}" hreflang="el" lang="el">ΕΛ</a></div>'
    return f'<div class="lang" aria-label="Γλώσσα"><a href="../{path}" hreflang="en" lang="en">EN</a><span aria-current="true">ΕΛ</span></div>'


def profiles(lang):
    return f"""      <ul class="profiles" aria-label="{'Profiles' if lang == 'en' else 'Προφίλ'}">
        <li><a href="{SCHOLAR}" rel="me">{ICON['scholar']}Google Scholar</a></li>
        <li><a href="{SCOPUS}" rel="me">{ICON['scopus']}Scopus</a></li>
        <li><a href="{GITHUB}" rel="me">{ICON['github']}GitHub</a></li>
        <li><a href="{AUA}">{ICON['aua']}{t('aua_profile', lang)}</a></li>
      </ul>"""


def footer(lang):
    p = "../" if lang == "el" else ""
    return f"""  <footer>
    <div class="wrap">
      <span>© 2026 {t('name', lang)}</span>
      <a href="{p}tools/revenue-calculator.html">{t('tools', lang)}</a>
    </div>
  </footer>
</body>
</html>
"""


def sub_header(lang, path, h1):
    p = "../" if lang == "el" else ""
    return f"""  <header class="top">
    <div class="wrap">
      <div class="topbar">{lang_switch(lang, path)}</div>
      <p class="crumb"><a href="./">← {t('name', lang)}</a></p>
      <h1>{h1}</h1>
    </div>
  </header>
"""


def fmt_p(s, lang):
    return s.replace("{p}", "../" if lang == "el" else "")


# --------------------------------------------------------------------------------------------
# Home page
# --------------------------------------------------------------------------------------------

def person_ld():
    data = {
        "@context": "https://schema.org", "@type": "Person",
        "name": "Sotirios T. Karetsos", "alternateName": "Σωτήριος Καρέτσος",
        "jobTitle": "Assistant Professor", "url": SITE + "/",
        "image": SITE + "/assets/img/sotirios-karetsos.jpg",
        "worksFor": {"@type": "CollegeOrUniversity", "name": "Agricultural University of Athens"},
        "alumniOf": [{"@type": "CollegeOrUniversity", "name": "Agricultural University of Athens"},
                     {"@type": "CollegeOrUniversity", "name": "National Technical University of Athens"}],
        "knowsAbout": ["Blockchain traceability", "Agri-food supply chains", "Artificial intelligence in agriculture",
                       "Chatbots", "Mobile applications", "Digital marketing", "E-government", "Information systems"],
        "sameAs": [SCHOLAR, SCOPUS, GITHUB, AUA],
    }
    return '  <script type="application/ld+json">\n' + json.dumps(data, ensure_ascii=False, indent=2) + "\n  </script>\n"


def home(lang):
    p = "../" if lang == "el" else ""
    title = "Sotirios Karetsos · Agricultural University of Athens" if lang == "en" else "Σωτήριος Καρέτσος · Γεωπονικό Πανεπιστήμιο Αθηνών"
    desc = (t("role", lang) + ". " + t("pitch", lang))
    out = [head(lang, "index.html", title, desc, person_ld())]
    nav = "".join(f'<a href="#{a}">{b}</a>' for a, b in t("nav", lang))
    out.append(f"""  <header class="top">
    <div class="wrap">
      <div class="topbar">{lang_switch(lang, '')}</div>
      <div class="hero">
        <img class="avatar" src="{p}assets/img/sotirios-karetsos.jpg" width="480" height="480" alt="{t('photo_alt', lang)}">
        <div>
          <p class="eyebrow">{t('eyebrow', lang)}</p>
          <h1>{t('name', lang)}</h1>
          <p class="role">{t('role', lang)}</p>
          <p class="pitch">{t('pitch', lang)}</p>
{profiles(lang)}
        </div>
      </div>
      <nav class="jump" aria-label="{'Sections' if lang == 'en' else 'Ενότητες'}">{nav}</nav>
    </div>
  </header>

  <main class="wrap">
""")
    # News
    items = "\n".join(f'        <li><time>{n["date"][lang]}</time><div>{fmt_p(n[lang], lang)}</div></li>' for n in NEWS)
    out.append(f"""    <section aria-labelledby="news">
      <h2 id="news">{t('h_news', lang)}</h2>
      <ul class="news">
{items}
      </ul>
    </section>
""")
    # Research themes
    cards = []
    for th in THEMES:
        lis = "\n".join(f'            <li><span class="tag">{TAGS[k][lang]}</span><span>{fmt_p(v, lang)}</span></li>' for k, v in th["items"])
        cards.append(f"""        <article class="theme">
          <h3>{th['title'][lang]}</h3>
          <p>{th['desc'][lang]}</p>
          <ul>
{lis}
          </ul>
        </article>""")
    out.append(f"""    <section aria-labelledby="research">
      <h2 id="research">{t('h_research', lang)}</h2>
      <p class="lead">{t('research_lead', lang)}</p>
      <div class="themes">
{chr(10).join(cards)}
      </div>
    </section>
""")
    # Publications
    sel = "\n".join(f"        <li>{s}</li>" for s in SELECTED)
    out.append(f"""    <section aria-labelledby="publications">
      <h2 id="publications">{t('h_publications', lang)}</h2>
      <p class="lead">{t('pubs_lead', lang)}</p>
      <div class="pubs">
        <a href="{SCHOLAR}"><strong>Google Scholar</strong><b class="n">974 {t('citations', lang)}</b><span>h-index 12 · i10-index 19</span></a>
        <a href="{SCOPUS}"><strong>Scopus</strong><b class="n">410 {t('citations', lang)}</b><span>h-index 8 · Author ID 57204351053</span></a>
      </div>
      <p class="asof">{t('asof', lang)}</p>
      <h3 class="subhead">{t('selected', lang)}</h3>
      <ol class="selected" lang="en">
{sel}
      </ol>
      <a class="more" href="publications.html">{t('all_pubs', lang)}</a>
      <article class="book">
        <a class="cover" href="{BOOK}" aria-label="{t('book_page', lang)}">
          <span class="fallback" aria-hidden="true"><b>Modern Technological Improvement in Agriculture and Agribusiness</b><small>Sotirios Karetsos<br>Constantina Costopoulou<br>IGI Global</small></span>
          <img src="{p}assets/img/modern-technological-improvement-cover.jpg" alt="Cover of Modern Technological Improvement in Agriculture and Agribusiness" width="350" height="500" loading="lazy" onerror="this.remove()">
        </a>
        <div>
          <p class="meta">{t('book_kind', lang)}</p>
          <h3 lang="en">Modern Technological Improvement in Agriculture and Agribusiness</h3>
          <p>{t('book_desc', lang)}</p>
          <dl>
            <dt>{t('editors', lang)}</dt><dd>{t('editors_v', lang)}</dd>
            <dt>{t('publisher', lang)}</dt><dd>IGI Global Scientific Publishing, 2025</dd>
            <dt>ISBN</dt><dd>979-8-3693-8237-0 · 979-8-3693-8239-4 (e-book)</dd>
            <dt>DOI</dt><dd><a href="{doi('10.4018/979-8-3693-8237-0')}">10.4018/979-8-3693-8237-0</a></dd>
            <dt>{t('chapter', lang)}</dt><dd lang="en">M. Petropoulos, S. Karetsos, “GaiaMentor AI for Farmers: A Conversational Solution for Smarter Agriculture”, pp. 293–320</dd>
          </dl>
          <a href="{BOOK}">{t('book_page', lang)}</a>
        </div>
      </article>
    </section>
""")
    # Projects and software
    proj = "\n".join(f"            <li>{x}</li>" for x in PROJECTS[lang])
    soft = []
    for s in SOFTWARE:
        links = "".join(f'<a href="{u}">{t(k, lang)}</a>' for k, u in s["links"])
        soft.append(f"""        <article class="card">
          <p class="meta">{s['meta']}</p>
          <h3>{s['title']}</h3>
          <p>{s['desc'][lang]}</p>
          <div class="links">{links}</div>
        </article>""")
    out.append(f"""    <section aria-labelledby="projects">
      <h2 id="projects">{t('h_projects', lang)}</h2>
      <div class="cards">
        <article class="card">
          <h3>{t('h_selected_projects', lang)}</h3>
          <ul>
{proj}
          </ul>
        </article>
{chr(10).join(soft)}
      </div>
    </section>
""")
    # Teaching and students
    courses = "\n".join(f"            <li>{x}</li>" for x in COURSES[lang])
    sup = "\n".join(f"            <li>{x}</li>" for x in SUPERVISION[lang])
    topics, how = STUDENTS[lang]
    top = "\n".join(f"            <li>{x}</li>" for x in topics)
    out.append(f"""    <section aria-labelledby="teaching">
      <h2 id="teaching">{t('h_teaching', lang)}</h2>
      <div class="cards">
        <article class="card">
          <h3>{t('h_courses', lang)}</h3>
          <ul>
{courses}
          </ul>
        </article>
        <article class="card">
          <h3>{t('h_supervision', lang)}</h3>
          <ul>
{sup}
          </ul>
        </article>
        <article class="card">
          <h3>{t('h_students', lang)}</h3>
          <ul>
{top}
          </ul>
          <p style="margin-top:12px">{how}</p>
        </article>
      </div>
    </section>
""")
    # Experience and education
    exp = "\n".join(f'            <li><time>{d[lang]}</time><div><b>{h[lang]}</b><span>{s[lang]}</span></div></li>' for d, h, s in EXPERIENCE)
    edu = "\n".join(f'            <li><time>{d}</time><div><b>{h[lang]}</b><span>{s[lang]}</span></div></li>' for d, h, s in EDUCATION)
    serv = "\n".join(f"        <li>{x}</li>" for x in SERVICE[lang])
    out.append(f"""    <section aria-labelledby="experience">
      <h2 id="experience">{t('h_experience', lang)}</h2>
      <div class="split">
        <div>
          <h3>{t('h_exp', lang)}</h3>
          <ol class="tl">
{exp}
          </ol>
        </div>
        <div>
          <h3>{t('h_edu', lang)}</h3>
          <ol class="tl">
{edu}
          </ol>
        </div>
      </div>
      <h3 class="subhead">{t('h_service', lang)}</h3>
      <ul class="service">
{serv}
      </ul>
    </section>
""")
    # Posters (compact)
    th = []
    for po in POSTERS:
        key = lang if lang in po["title"] else po["lang"]
        title, tl = po["title"][key], key
        tw, thh = (800, round(800 * po["h"] / po["w"])) if po["thumb"] == "-800" else (900, round(900 * po["h"] / po["w"]))
        th.append(f"""        <a class="thumb" href="posters.html#{po['id']}">
          <span class="pic{' tall' if po.get('portrait') else ''}"><img src="{p}assets/img/{po['img']}{po['thumb']}.jpg" alt="" loading="lazy" width="{tw}" height="{thh}"></span>
          <span class="cap"><b lang="{tl}">{title}</b><small>{po['short'][lang]}</small></span>
        </a>""")
    out.append(f"""    <section aria-labelledby="posters">
      <h2 id="posters">{t('h_posters', lang)}</h2>
      <div class="thumbs">
{chr(10).join(th)}
      </div>
      <a class="more" href="posters.html">{t('posters_more', lang)}</a>
    </section>

    <section aria-labelledby="contact">
      <h2 id="contact">{t('h_contact', lang)}</h2>
      <p>{t('contact', lang)}</p>
    </section>
  </main>

""")
    out.append(footer(lang))
    return "".join(out)


# --------------------------------------------------------------------------------------------
# Posters page
# --------------------------------------------------------------------------------------------

def posters_page(lang):
    p = "../" if lang == "el" else ""
    h1 = t("h_posters", lang)
    title = f"{h1} · {t('name', lang)}"
    out = [head(lang, "posters.html", title, t("posters_lead", lang)), sub_header(lang, "posters.html", h1)]
    figs = []
    for po in POSTERS:
        main_lang = po["lang"]
        main_title = po["title"][main_lang]
        sub = ""
        if lang == "en" and po["lang"] == "el":
            sub = f'<p class="en">{po["title"]["en"]}</p>'
        venue = po.get("venue", {}).get(lang)
        venue_html = f'<p class="en">{venue}</p>' if venue else ""
        img = f"{p}assets/img/{po['img']}"
        thumb_w = 900 if po["thumb"] == "-900" else 800
        figs.append(f"""    <figure class="poster{' portrait' if po.get('portrait') else ''}" id="{po['id']}">
      <a class="img" href="{img}.jpg" aria-label="{t('open_full', lang)}">
        <img src="{img}{po['thumb']}.jpg" srcset="{img}{po['thumb']}.jpg {thumb_w}w, {img}.jpg {po['w']}w" sizes="(max-width: 1000px) 100vw, 940px" width="{po['w']}" height="{po['h']}" loading="lazy" alt="{E(po['alt'])}">
      </a>
      <figcaption>
        <h2 lang="{main_lang}">{main_title}</h2>
        {sub}{venue_html}
        <p class="authors">{po['authors'][lang]}</p>
        <p class="note">{po['note'][lang]} {po['funding'][lang]}</p>
        <div class="links"><a href="{img}.jpg">{t('full_image', lang)}</a><a href="{p}assets/docs/{po['img']}.pdf">PDF</a></div>
      </figcaption>
    </figure>""")
    out.append(f"""  <main class="wrap">
    <p class="lead" style="margin-top:24px">{t('posters_lead', lang)}</p>
{chr(10).join(figs)}
  </main>

""")
    out.append(footer(lang))
    return "".join(out)


# --------------------------------------------------------------------------------------------
# Publications page
# --------------------------------------------------------------------------------------------
OWN = re.compile(r"(S\.\s?T\.\s?Karetsos|S\.\s?Karetsos|Karetsos,\s?S\.|Σ\.\s?Θ\.\s?Καρέτσος|Σ\.\s?Καρέτσος)")
DOI = re.compile(r"(doi:\s*|https?://doi\.org/)(10\.[^\s,;]+?)(\.?)(?=\s|$)", re.I)


def render_pub(text):
    s = E(text)
    s = OWN.sub(r"<b>\1</b>", s)
    s = DOI.sub(lambda m: f'<a href="https://doi.org/{m.group(2)}">doi:{m.group(2)}</a>{m.group(3)}', s)
    return s


def pubs_page(lang):
    pubs = json.load(open(ROOT / "assets" / "data" / "publications.json", encoding="utf-8"))
    kind_order = {"journal": 0, "chapter": 1, "conference": 2}
    pubs.sort(key=lambda o: (-(o["year"] or 0), kind_order[o["type"]], -o["n"]))
    h1 = t("h_publications", lang)
    title = f"{h1} · {t('name', lang)}"
    out = [head(lang, "publications.html", title, t("pubs_page_lead", lang)), sub_header(lang, "publications.html", h1)]
    p = "../" if lang == "el" else ""
    groups = []
    years = sorted({o["year"] for o in pubs}, reverse=True)
    for y in years:
        lis = "\n".join(
            f'          <li data-type="{o["type"]}"><span class="kind">{t("k_" + o["type"], lang)}</span><span>{render_pub(o["text"])}</span></li>'
            for o in pubs if o["year"] == y)
        groups.append(f"""      <div data-year-group="{y}">
        <h2 class="year">{y}</h2>
        <ul class="plist">
{lis}
        </ul>
      </div>""")
    out.append(f"""  <main class="wrap">
    <p class="lead" style="margin-top:24px">{t('pubs_page_lead', lang)} {t('pubs_note', lang)}</p>
    <div class="filters" role="group" aria-label="{t('filter_label', lang)}">
      <button type="button" data-filter="all" aria-pressed="true">{t('f_all', lang)}</button>
      <button type="button" data-filter="journal" aria-pressed="false">{t('f_journal', lang)}</button>
      <button type="button" data-filter="chapter" aria-pressed="false">{t('f_chapter', lang)}</button>
      <button type="button" data-filter="conference" aria-pressed="false">{t('f_conference', lang)}</button>
      <input id="psearch" type="search" placeholder="{t('search', lang)}" aria-label="{t('search', lang)}">
    </div>
    <p id="pcount" class="count" aria-live="polite" data-template="{t('count_tpl', lang)}">{len(pubs)}</p>
    <div id="plist">
{chr(10).join(groups)}
    </div>
  </main>
  <script src="{p}assets/js/publications.js" defer></script>

""")
    out.append(footer(lang))
    return "".join(out)


# --------------------------------------------------------------------------------------------

def main():
    pages = {"index.html": home, "posters.html": posters_page, "publications.html": pubs_page}
    (ROOT / "el").mkdir(exist_ok=True)
    for name, fn in pages.items():
        (ROOT / name).write_text(fn("en"), encoding="utf-8")
        (ROOT / "el" / name).write_text(fn("el"), encoding="utf-8")
    urls = [f"{SITE}/", f"{SITE}/el/"] + [f"{SITE}/{n}" for n in ("posters.html", "publications.html")] \
        + [f"{SITE}/el/{n}" for n in ("posters.html", "publications.html")] + [f"{SITE}/tools/revenue-calculator.html"]
    (ROOT / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "".join(f"  <url><loc>{u}</loc></url>\n" for u in urls) + "</urlset>\n", encoding="utf-8")
    (ROOT / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {SITE}/sitemap.xml\n", encoding="utf-8")
    print("built:", ", ".join(list(pages) + ["el/…", "sitemap.xml", "robots.txt"]))


if __name__ == "__main__":
    main()
