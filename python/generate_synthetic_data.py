"""
Synthetic data generator for the WBS Online Bookstore database.

Produces all nine tables and writes them to bookstore_synth_final.xlsx
(one sheet per table).
"""


# ----------------------------------------------------------------------
# Imports
import random
import string
from datetime import date, timedelta, datetime
import pandas as pd

# ----------------------------------------------------------------------
# Config
# Global configuration constants: random seed, record counts, and output filename.
# ----------------------------------------------------------------------
SEED = 42
random.seed(SEED)
TODAY       = date.today()
N_CUSTOMERS = 800
N_GENRES    = 15
N_BOOKS     = 1200
N_AUTHORS   = 700
N_ORDERS    = 3000
OUT_XLSX    = "bookstore_synth_final.xlsx"

# ----------------------------------------------------------------------
# Helpers
# Utility functions for date generation, email creation, postcode generation, ISBN validation, and monetary rounding.
# ----------------------------------------------------------------------
def random_date(start: date, end: date) -> date:
    if start >= end:
        return start
    return start + timedelta(days=random.randint(0, (end - start).days))

def weighted_choice(items, weights):
    return random.choices(items, weights=weights, k=1)[0]

REAL_DOMAINS   = ["gmail.com","outlook.com","hotmail.com","yahoo.co.uk","icloud.com","btinternet.com","sky.com"]
DOMAIN_WEIGHTS = [0.35, 0.25, 0.15, 0.10, 0.07, 0.05, 0.03]

def unique_email(first, last, used):
    base   = "".join(ch for ch in f"{first}.{last}".lower() if ch.isalnum() or ch == ".")
    domain = weighted_choice(REAL_DOMAINS, DOMAIN_WEIGHTS)
    while True:
        email = f"{base}{random.randint(1,9999)}@{domain}"
        if email not in used:
            used.add(email)
            return email
# FIX 1: return as string to preserve leading zero
def uk_phone() -> str:
    return "07" + "".join(random.choice(string.digits) for _ in range(9))
def uk_postcode():
    FL = "ABCDEFGHIJKLMNOPRSTUWYZ"
    SL = "ABCDEFGHJKMNPRSTUVWXY"
    IL = "ABDEFGHJLNPQRSTUWXYZ"
    D  = lambda: str(random.randint(0, 9))
    L  = lambda s: random.choice(s)
    pat = random.choice(["A9","A99","AA9","AA99","A9A","AA9A"])
    if   pat == "A9":   out = f"{L(FL)}{D()}"
    elif pat == "A99":  out = f"{L(FL)}{random.randint(1,9)}{D()}"
    elif pat == "AA9":  out = f"{L(FL)}{L(SL)}{D()}"
    elif pat == "AA99": out = f"{L(FL)}{L(SL)}{random.randint(1,9)}{D()}"
    elif pat == "A9A":  out = f"{L(FL)}{D()}{L(SL)}"
    else:               out = f"{L(FL)}{L(SL)}{D()}{L(SL)}"
    return f"{out} {D()}{L(IL)}{L(IL)}"
def eu_postcode():
    return "".join(random.choice(string.digits) for _ in range(5))

def street_address():
    streets = ["High Street","Station Road","Main Street","Park Road","Church Lane",
               "Victoria Road","Green Lane","Castle Street","Mill Road","Queen Street",
               "King Street","Bridge Road"]
    return f"{random.randint(1, 299)} {random.choice(streets)}"
def isbn13_unique(used):
    while True:
        isbn = random.choice(["978","979"]) + "".join(random.choice(string.digits) for _ in range(10))
        if isbn not in used:
            used.add(isbn)
            return isbn
def money(x):
    return round(float(x), 2)

# ----------------------------------------------------------------------
# Title catalogs
# Word banks and template functions used to generate realistic book titles by genre.
# ----------------------------------------------------------------------
FIC_ADJ    = ["Lost","Broken","Hidden","Stolen","Forgotten","Ancient","Dark","Silver",
              "Golden","Crimson","Iron","Hollow","Silent","Burning","Frozen"]
FIC_NOUNS  = ["Shadow","River","Crown","Garden","Storm","Labyrinth","Whisper","Mirror",
              "Ember","Voyage","Throne","Relic","Flame","Tide","Veil","Clock","Gate",
              "Key","Mask","Cipher"]
FIC_PLACES = ["London","Edinburgh","York","Oxford","Bristol","Glasgow","Bath","Cambridge",
              "Canterbury","Whitby","Dover","Chester","Salisbury","Durham","Exeter"]
FIC_TWISTS = ["Secrets","Lies","Silence","Ashes","Echoes","Night","Winter","Gold",
              "Thorns","Dust","Blood","Smoke","Mist","Ice","Ruin"]
FIC_CHARS  = ["The Widow","The Heir","The Scholar","The Stranger","The Captain",
              "The Clockmaker","The Cartographer","The Surgeon","The Spy","The Exile"]
SERIES_NAMES = [
    "The Ravenscroft Files","London Shadows","The Northsea Chronicles",
    "Cambridge Mysteries","Ironwood Saga","The Glass Atlas","Arcadia Station",
    "The Alderwood Archives","The Kensington Papers","The Midnight Codex",
    "Chronicles of the Pale Coast","The Ashford Trilogy"
]
NF_TOPICS = {
    "Business":    ["Strategy","Leadership","Negotiation","Startups","Productivity",
                    "Finance","Marketing","Innovation","Entrepreneurship","Operations",
                    "Sales","Branding"],
    "Technology":  ["Data Science","Machine Learning","Cybersecurity","Cloud Computing",
                    "Python","Artificial Intelligence","Blockchain","UX Design",
                    "Software Engineering","Network Security","DevOps","Quantum Computing"],
    "Self-Help":   ["Habits","Mindset","Focus","Confidence","Wellbeing","Resilience",
                    "Motivation","Creativity","Decision-Making","Emotional Intelligence",
                    "Time Management","Stress Management"],
    "Biography":   ["A Life","My Story","Memoir","Letters","Reflections","Portrait",
                    "A Journey","Untold","In My Own Words","The Making Of"],
    "Non-Fiction": ["Climate Change","The Human Brain","Lost Civilisations","The Ocean",
                    "Space Exploration","The History of Money","Language","Evolution",
                    "The Power of Maps","Artificial Intelligence","Democracy","The Silk Road",
                    "Pandemics","The Philosophy of Time","Memory","Colour","Sound",
                    "Mathematics","The Rise of Cities","Food and Culture"],
}
NF_SUBTITLES = [
    "A World History","The Untold Story","A New Perspective","Science and Society",
    "Past, Present and Future","What the Evidence Shows","A Complete Guide",
    "Rethinking Everything We Know","An Illustrated History","The Hidden Truth",
    "Facts, Myths and Meaning","From the Beginning","A Human Story",
]
NF_SUBTITLE_FORMATS = [
    "A Practical Guide","The Definitive Handbook","Methods and Applications",
    "Tools, Tactics, and Templates","Lessons from the Real World",
    "A Beginner's Introduction","The Essential Reference","Theory and Practice",
    "Principles and Frameworks","A Step-by-Step Approach",
]
CHILDREN_ADJ      = ["Little","Brave","Clever","Tiny","Mighty","Curious","Sleepy",
                      "Grumpy","Happy","Wild","Magic","Lost","Friendly","Sneaky","Gentle"]
CHILDREN_CHARS    = ["Fox","Bear","Rabbit","Dragon","Owl","Cat","Mouse","Tiger",
                     "Penguin","Elephant","Lion","Frog","Hedgehog","Badger","Wolf"]
CHILDREN_SETTINGS = ["Midnight Moon","Enchanted Forest","Whispering Wood","Secret Garden",
                      "Faraway Mountain","Crystal Cave","Starlit Sea","Hidden Valley",
                      "Magical Library","Rainbow Meadow","Forgotten Island","Cobblestone Town"]
CHILDREN_PLOTS    = ["and the Missing Treasure","and the Stolen Star","and the Great Adventure",
                     "and the Mysterious Map","and the Lost Friend","Goes to School",
                     "Saves the Day","and the Magic Door","Finds a Home","and the Big Storm",
                     "and the Colour Thief","Makes a Wish"]
HISTORICAL_SETTINGS = ["Tudor","Victorian","Elizabethan","Medieval","Georgian","Edwardian",
                        "Regency","Roman","Byzantine","Renaissance","Viking","Saxon"]
HISTORICAL_THEMES   = ["Court","Conquest","Betrayal","Exile","Alliance","Revolution",
                        "Inheritance","Plague","Discovery","Uprising","Conspiracy","Legacy"]
# FIX 2: Expanded Poetry — hardcoded pool + 3 template patterns
POETRY_POOL = [
    "Lines for a Quiet Winter","Saltwater and Streetlights","Small Bright Things",
    "Letters to the Sea","The Grammar of Leaves","Everything Ordinary","Night Bus",
    "The Patience of Rivers","After the Rain","Stitched in Starlight","Loose Stones",
    "The Long Way Round","Half Light","Common Ground","What the Garden Knows",
    "Still Life with Silence","Threshold","The Weight of Feathers","Speaking in Tides",
    "Unfinished Maps","The Space Between Words","Borrowed Light","Fragments","Wren Song",
    "Ink and Bone","The North Road","Foxglove Hours","Mornings Without You",
    "The Arithmetic of Loss","Field Notes","Harbour Light","Verb","Low Tide","Signals",
    "Margins","Weather Systems","Interior","Dusk Chorus","Landfall","The Quiet Hours",
    "Silverline","Gravel and Grace","Overgrown","Coastline","Depths","The Heron's Flight",
    "Open Water","Late Light","Undergrowth","Shore Leave",
]
POETRY_ADJ    = ["Still","Soft","Quiet","Dark","Pale","Thin","Cold","Warm","Small",
                 "Slow","Deep","Wild","Raw","Bare","Brief"]
POETRY_NOUNS  = ["Hours","Roads","Fields","Rooms","Light","Rain","Smoke","Stone",
                 "Tide","Glass","Salt","Dust","Wire","Thread","Moss","Grain","Water"]
POETRY_TITLES_USED = set()
def poetry_title_unique() -> str:
    # Try pool first
    remaining = [t for t in POETRY_POOL if t not in POETRY_TITLES_USED]
    if remaining:
        chosen = random.choice(remaining)
        POETRY_TITLES_USED.add(chosen)
        return chosen
    # Fall back to templates
    for _ in range(200):
        t = random.randint(1, 3)
        if   t == 1: title = f"{random.choice(POETRY_ADJ)} {random.choice(POETRY_NOUNS)}"
        elif t == 2: title = f"The {random.choice(POETRY_ADJ)} {random.choice(POETRY_NOUNS)}"
        else:        title = f"{random.choice(POETRY_NOUNS)} and {random.choice(POETRY_NOUNS)}"
        if title not in POETRY_TITLES_USED:
            POETRY_TITLES_USED.add(title)
            return title
    return f"Poem Collection {random.randint(100,999)}"

def book_title_catalog(genre_name: str) -> str:
    in_series = random.random() < 0.28
    if genre_name == "Fiction":
        t = random.randint(1, 5)
        if   t == 1: title = f"The {random.choice(FIC_ADJ)} {random.choice(FIC_NOUNS)}"
        elif t == 2: title = f"{random.choice(FIC_TWISTS)} at {random.choice(FIC_PLACES)}"
        elif t == 3: title = f"The {random.choice(FIC_NOUNS)} of {random.choice(FIC_PLACES)}"
        elif t == 4: title = f"{random.choice(FIC_CHARS)} of {random.choice(FIC_PLACES)}"
        else:        title = f"{random.choice(FIC_TWISTS)} and {random.choice(FIC_NOUNS)}"
        if in_series: title += f" ({random.choice(SERIES_NAMES)} #{random.randint(1,8)})"
        return title
    if genre_name == "Fantasy":
        t = random.randint(1, 4)
        if   t == 1: title = f"The {random.choice(FIC_ADJ)} {random.choice(FIC_NOUNS)}"
        elif t == 2: title = f"{random.choice(FIC_ADJ)} {random.choice(FIC_NOUNS)} of {random.choice(FIC_PLACES)}"
        elif t == 3: title = f"The {random.choice(FIC_NOUNS)} and the {random.choice(FIC_NOUNS)}"
        else:        title = f"Realm of {random.choice(FIC_TWISTS)}"
        if in_series: title += f" ({random.choice(SERIES_NAMES)} #{random.randint(1,8)})"
        return title
    if genre_name == "Science Fiction":
        sf_prefixes = ["Station","Project","Protocol","Signal","Sector","Unit","Grid",
                       "Archive","Module","Terminal"]
        sf_words    = ["Zero","Horizon","Parallax","Nexus","Cascade","Threshold","Rift",
                       "Echo","Vector","Omega","Alpha","Delta","Nova","Apex","Zenith"]
        t = random.randint(1, 4)
        if   t == 1: title = f"{random.choice(sf_prefixes)} {random.choice(sf_words)}"
        elif t == 2: title = f"The {random.choice(sf_words)} {random.choice(['Initiative','Protocol','Directive','Sequence','Paradox'])}"
        elif t == 3: title = f"Beyond {random.choice(sf_words)}"
        else:        title = f"{random.choice(sf_words)}: {random.choice(['Year One','The Final Run','Dark Matter','Last Signal','First Contact'])}"
        if in_series: title += f" ({random.choice(SERIES_NAMES)} #{random.randint(1,8)})"
        return title

    if genre_name == "Mystery":
        crimes = ["Murder","Disappearance","Theft","Death","Secret","Forgery","Poisoning"]
        t = random.randint(1, 4)
        if   t == 1: title = f"The {random.choice(FIC_PLACES)} {random.choice(crimes)}"
        elif t == 2: title = f"A {random.choice(crimes)} in {random.choice(FIC_PLACES)}"
        elif t == 3: title = f"The {random.choice(FIC_ADJ)} {random.choice(['Case','Clue','Witness','Suspect','Confession'])}"
        else:        title = f"Death at {random.choice(FIC_PLACES)}"
        if in_series: title += f" ({random.choice(SERIES_NAMES)} #{random.randint(1,8)})"
        return title
    if genre_name == "Thriller":
        t = random.randint(1, 4)
        if   t == 1: title = f"The {random.choice(FIC_ADJ)} {random.choice(['Protocol','Directive','Asset','Extraction','Gambit','Betrayal'])}"
        elif t == 2: title = f"{random.choice(FIC_TWISTS)} {random.choice(['Zone','Network','Code','List','File','Signal'])}"
        elif t == 3: title = f"The {random.choice(FIC_PLACES)} {random.choice(['Conspiracy','Incident','Affair','Operation'])}"
        else:        title = f"Run from {random.choice(FIC_TWISTS)}"
        if in_series: title += f" ({random.choice(SERIES_NAMES)} #{random.randint(1,8)})"
        return title
    if genre_name == "Romance":
        rom_adj   = ["Sweet","Tender","Unexpected","Reluctant","Eternal","Stolen",
                     "Second","Last","Brave","Wild"]
        rom_nouns = ["Love","Heart","Promise","Kiss","Beginning","Chance","Summer",
                     "Return","Wedding","Proposal"]
        t = random.randint(1, 3)
        if   t == 1: title = f"{random.choice(rom_adj)} {random.choice(rom_nouns)}"
        elif t == 2: title = f"A {random.choice(rom_adj)} {random.choice(rom_nouns)} in {random.choice(FIC_PLACES)}"
        else:        title = f"The {random.choice(rom_adj)} {random.choice(rom_nouns)}"
        return title
    if genre_name == "Historical":
        t = random.randint(1, 4)
        if   t == 1: title = f"The {random.choice(HISTORICAL_SETTINGS)} {random.choice(HISTORICAL_THEMES)}"
        elif t == 2: title = f"{random.choice(FIC_TWISTS)} in the {random.choice(HISTORICAL_SETTINGS)} Age"
        elif t == 3: title = f"The {random.choice(FIC_ADJ)} {random.choice(['Queen','King','Knight','Lady','Duke','Merchant','Soldier','Monk'])}"
        else:        title = f"A {random.choice(HISTORICAL_SETTINGS)} {random.choice(['Tale','Chronicle','Story','Account','Record'])}"
        if in_series: title += f" ({random.choice(SERIES_NAMES)} #{random.randint(1,8)})"
        return title
    if genre_name == "Young Adult":
        ya_adj   = ["Neon","Electric","Ordinary","Infinite","Almost","Broken","Wild",
                    "Midnight","Last","First"]
        ya_nouns = ["Stars","Hearts","Worlds","Nights","Roads","Voices","Choices",
                    "Wars","Lies","Truths","Dreams","Fears"]
        t = random.randint(1, 3)
        if   t == 1: title = f"The {random.choice(ya_adj)} {random.choice(ya_nouns)}"
        elif t == 2: title = f"{random.choice(ya_adj)} {random.choice(ya_nouns)}"
        else:        title = f"All the {random.choice(ya_adj)} {random.choice(ya_nouns)}"
        if in_series: title += f" ({random.choice(SERIES_NAMES)} #{random.randint(1,8)})"
        return title
    if genre_name == "Non-Fiction":
        return f"{random.choice(NF_TOPICS['Non-Fiction'])}: {random.choice(NF_SUBTITLES)}"
    if genre_name in ("Business", "Technology", "Self-Help"):
        return f"{random.choice(NF_TOPICS[genre_name])}: {random.choice(NF_SUBTITLE_FORMATS)}"
    if genre_name == "Biography":
        BIO_FIRST = ["Winston","Margaret","Charles","Diana","Nelson","Florence","Alan",
                     "Marie","Nikola","Ada","Stephen","Frida","Pablo","Leonardo","Coco",
                     "Oscar","Virginia","Simone","George","Elizabeth"]
        BIO_LAST  = ["Churchill","Thatcher","Darwin","Curie","Mandela","Nightingale",
                     "Turing","Shelley","Tesla","Lovelace","Hawking","Kahlo","Picasso",
                     "da Vinci","Chanel","Wilde","Woolf","de Beauvoir","Orwell","Blackwell"]
        return f"{random.choice(BIO_FIRST)} {random.choice(BIO_LAST)}: {random.choice(NF_TOPICS['Biography'])}"
    if genre_name == "Children":
        t = random.randint(1, 3)
        if   t == 1: return f"The {random.choice(CHILDREN_ADJ)} {random.choice(CHILDREN_CHARS)} and the {random.choice(CHILDREN_SETTINGS)}"
        elif t == 2: return f"{random.choice(CHILDREN_ADJ)} {random.choice(CHILDREN_CHARS)} {random.choice(CHILDREN_PLOTS)}"
        else:        return f"The {random.choice(CHILDREN_CHARS)} Who {random.choice(['Found a Star','Lost the Moon','Stole the Sun','Saved the Forest','Learned to Fly','Became a Knight','Baked a Rainbow','Moved Mountains'])}"
    if genre_name == "Poetry":
        return poetry_title_unique()  # FIX 2
    # fallback
    return f"{random.choice(NF_TOPICS['Self-Help'])}: {random.choice(NF_SUBTITLE_FORMATS)}"

# ----------------------------------------------------------------------
# Author name pool (unique)
# First and last name pools used to generate unique author names.
# ----------------------------------------------------------------------
AUTHOR_FIRST = [
    "James","William","Henry","Oliver","Thomas","George","Arthur","Edward","Samuel","Daniel",
    "Charlotte","Amelia","Olivia","Isla","Emily","Sophia","Grace","Eleanor","Alice","Harriet",
    "Noah","Leo","Theodore","Lucas","Benjamin","Michael","David","Joseph","Matthew","Nathan",
    "Aisha","Zara","Hana","Mei","Sofia","Elena","Anya","Maya","Nina","Leila",
    "Robert","Charles","Richard","Andrew","Patrick","Jonathan","Sebastian","Alexander","Frederick","Edmund",
    "Catherine","Margaret","Elizabeth","Victoria","Beatrice","Rosalind","Penelope","Josephine","Dorothy","Agnes",
    "Ethan","Liam","Mason","Caleb","Aaron","Dylan","Ryan","Connor","Evan","Owen",
    "Priya","Fatima","Yuki","Layla","Ingrid","Astrid","Sienna","Naomi","Chloe","Isabel",
]
AUTHOR_LAST = [
    "Bennett","Harrington","Whitaker","Montgomery","Chamberlain","Lancaster","Sinclair","Ashford","Kensington","Pembroke",
    "Caldwell","Fairchild","Blackwood","Rutherford","Hawthorne","Sterling","Waverley","Marlowe","Everett","Holloway",
    "Patel","Khan","Ahmed","Singh","Nakamura","Rossi","Dubois","Müller","Jansen","Nowak",
    "Fletcher","Thornton","Hammond","Whitfield","Langford","Ellsworth","Dunmore","Ashby","Clifton","Weston",
    "Pearce","Sutton","Cromwell","Dalton","Holbrook","Mercer","Tanner","Oswald","Pemberton","Carrington",
    "Nakagawa","Yamamoto","Eriksson","Lindqvist","Kowalski","Ferreira","Moreau","Schneider","Okonkwo","Adeyemi",
    "Fitzgerald","Gallagher","Maguire","Donnelly","Brennan","Sullivan","O'Brien","McCarthy","Byrne","Hennessy",
    "Castellano","Ricci","Greco","Esposito","Conti","Ferrari","Marchetti","Lombardi","Barbieri","Santoro",
]
def author_name_unique(used: set) -> str:
    for _ in range(10000):
        first = random.choice(AUTHOR_FIRST)
        last  = random.choice(AUTHOR_LAST)
        name  = f"{first} {random.choice(string.ascii_uppercase)}. {last}" if random.random() < 0.20 else f"{first} {last}"
        if name not in used:
            used.add(name)
            return name
    name = f"{first} {last} {random.randint(2,9)}"
    used.add(name)
    return name

# ----------------------------------------------------------------------
# Customer reference data
# Name pools, city lists, country distributions, and payment/shipping vocabulary used for customer and order generation.
# ----------------------------------------------------------------------
FIRST_NAMES = [
    "Oliver","George","Harry","Jack","Jacob","Noah","Charlie","Thomas","Oscar",
    "Olivia","Amelia","Isla","Ava","Mia","Isabella","Sophia","Grace","Lily","Freya",
    "James","William","Henry","Leo","Alfie","Theodore","Arthur","Lucas","Archie","Ethan",
    "Emily","Ella","Jessica","Poppy","Sienna","Daisy","Phoebe","Evie","Ruby","Chloe",
    "Mohammed","Aisha","Priya","Ravi","Fatima","Yusuf","Layla","Omar","Zara","Tariq",
]
LAST_NAMES = [
    "Smith","Jones","Taylor","Brown","Williams","Wilson","Johnson","Davies","Patel","Wright",
    "Walker","White","Roberts","Green","Hall","Thomas","Clarke","Jackson","Wood","Thompson",
    "Hughes","Edwards","Collins","Reed","Morgan","Cooper","Bailey","Harris","Martin","Khan",
    "Ahmed","Ali","Shah","Begum","Hussain","Malik","Chowdhury","Islam","Miah","Uddin",
]
UK_CITIES  = ["London","Birmingham","Manchester","Leeds","Liverpool","Bristol","Glasgow",
              "Edinburgh","Cardiff","Sheffield","Leicester","Nottingham","Southampton",
              "Portsmouth","Newcastle"]
EU_CITIES  = {
    "Ireland":       ["Dublin","Cork","Galway","Limerick"],
    "France":        ["Paris","Lyon","Marseille","Bordeaux","Toulouse"],
    "Germany":       ["Berlin","Munich","Hamburg","Frankfurt","Cologne"],
    "Netherlands":   ["Amsterdam","Rotterdam","Utrecht","The Hague"],
    "Spain":         ["Madrid","Barcelona","Valencia","Seville"],
    "Italy":         ["Milan","Rome","Turin","Florence","Naples"],
    "Belgium":       ["Brussels","Antwerp","Ghent","Bruges"],
    "Sweden":        ["Stockholm","Gothenburg","Malmö","Uppsala"],
    "United States": ["New York","Boston","Chicago","Los Angeles","Seattle"],
    "Canada":        ["Toronto","Vancouver","Montreal","Calgary"],
    "Australia":     ["Sydney","Melbourne","Brisbane","Perth"],
}
COUNTRIES       = ["United Kingdom","Ireland","France","Germany","Netherlands","Spain",
                   "Italy","Belgium","Sweden","United States","Canada","Australia"]
COUNTRY_WEIGHTS = [0.88,0.03,0.02,0.02,0.01,0.01,0.01,0.005,0.005,0.01,0.005,0.005]
GENRES          = ["Fiction","Non-Fiction","Fantasy","Science Fiction","Mystery","Thriller",
                   "Romance","Historical","Biography","Self-Help","Business","Technology",
                   "Children","Young Adult","Poetry"]
PAY_METHODS     = ["Card","PayPal","Apple Pay","Google Pay"]
SHIP_UK         = ["Standard","Express","Next-Day"]
SHIP_EU         = ["International Standard","International Express"]

# ----------------------------------------------------------------------
# Seasonal order date generator
# Weighted date sampler that applies growth over time and seasonal spikes in November and December.
# ----------------------------------------------------------------------
def generate_order_dates(n: int, start: date, end: date) -> list:
    months = []
    d = date(start.year, start.month, 1)
    end_m = date(end.year, end.month, 1)
    while d <= end_m:
        months.append(d)
        d = date(d.year + (d.month == 12), (d.month % 12) + 1, 1)
    total   = len(months)
    weights = []
    for i, m in enumerate(months):
        base  = 0.5 + 1.5 * (i / max(total - 1, 1))
        spike = 1.8 if m.month == 12 else (1.2 if m.month == 11 else 1.0)
        weights.append(base * spike)
    chosen = random.choices(months, weights=weights, k=n)
    result = []
    for m in chosen:
        next_m   = date(m.year + (m.month == 12), (m.month % 12) + 1, 1)
        last_day = next_m - timedelta(days=1)
        result.append(random_date(m, min(last_day, end)))
    return result

# ----------------------------------------------------------------------
# Generate tables
# Main data generation loop. Produces all nine tables: genre, customer, author, book, book_author, orders, order_item, payment, and shipping_details.
# ----------------------------------------------------------------------
df_genre = pd.DataFrame([{"genre_id": i+1, "genre_name": GENRES[i]} for i in range(N_GENRES)])
# Customer
used_emails = set()
customers   = []
for cid in range(1, N_CUSTOMERS + 1):
    first   = random.choice(FIRST_NAMES)
    last    = random.choice(LAST_NAMES)
    country = weighted_choice(COUNTRIES, COUNTRY_WEIGHTS)
    join_dt = random_date(date(2022, 1, 1), TODAY - timedelta(days=1))
    customers.append({
        "customer_id": cid,
        "email":       unique_email(first, last, used_emails),
        "first_name":  first,
        "last_name":   last,
        "phone":       uk_phone() if country == "United Kingdom" else None,
        "join_date":   join_dt.isoformat(),
        "country":     country,
    })
df_customer = pd.DataFrame(customers)
# Author
used_author_names = set()
df_author = pd.DataFrame([
    {"author_id": aid, "author_name": author_name_unique(used_author_names)}
    for aid in range(1, N_AUTHORS + 1)
])
# Book
used_isbn = set()
genre_map = dict(zip(df_genre["genre_id"], df_genre["genre_name"]))
books = []
for bid in range(1, N_BOOKS + 1):
    genre_id = random.randint(1, N_GENRES)
    books.append({
        "book_id":        bid,
        "isbn":           isbn13_unique(used_isbn),
        "genre_id":       genre_id,
        "title":          book_title_catalog(genre_map[genre_id]),
        "publish_year":   random.randint(1995, TODAY.year),
        "list_price":     money(random.uniform(4.99, 39.99)),
        "stock_quantity": int(max(0, round(random.gauss(80, 60)))),
    })
df_book = pd.DataFrame(books)
# Book_Author
ba_pairs, ba_rows = set(), []
for bid in range(1, N_BOOKS + 1):
    k = random.choices([1, 2, 3], weights=[0.75, 0.20, 0.05], k=1)[0]
    for aid in random.sample(range(1, N_AUTHORS + 1), k=k):
        if (bid, aid) not in ba_pairs:
            ba_pairs.add((bid, aid))
            ba_rows.append({"book_id": bid, "author_id": aid})
df_book_author = pd.DataFrame(ba_rows)
# Orders / Items / Payments / Shipping
book_price      = dict(zip(df_book["book_id"], df_book["list_price"]))
ORDER_STATUS    = ["Pending","Paid","Shipped","Delivered","Cancelled","Returned"]
ORDER_W         = [0.04, 0.07, 0.10, 0.74, 0.03, 0.02]
all_order_dates = generate_order_dates(N_ORDERS, date(2022, 1, 1), TODAY)
orders, order_items, payments, shippings = [], [], [], []
pay_id = ship_id = 1
for oid in range(1, N_ORDERS + 1):
    cust         = df_customer.sample(1, random_state=random.randint(0, 10**9)).iloc[0]
    cid          = int(cust["customer_id"])
    cust_country = cust["country"]
    join_dt      = datetime.strptime(cust["join_date"], "%Y-%m-%d").date()
    order_dt     = max(all_order_dates[oid - 1], join_dt)
    status       = weighted_choice(ORDER_STATUS, ORDER_W)
    # Items
    n_lines     = random.choices([1,2,3,4,5], weights=[0.35,0.30,0.18,0.10,0.07], k=1)[0]
    items_total = 0.0
    for b in random.sample(range(1, N_BOOKS + 1), k=n_lines):
        qty        = random.choices([1,2,3], weights=[0.80,0.17,0.03], k=1)[0]
        unit_price = money(book_price[b] * random.uniform(0.70, 1.00))
        items_total += unit_price * qty
        order_items.append({"order_id": oid, "book_id": b, "quantity": qty, "unit_price": unit_price})
    # Shipping cost
    if cust_country == "United Kingdom":
        ship_method = weighted_choice(SHIP_UK, [0.70, 0.20, 0.10])
        base_ship   = {"Standard": 2.99, "Express": 5.99, "Next-Day": 7.99}[ship_method]
        free_thresh = 30.0
    else:
        ship_method = weighted_choice(SHIP_EU, [0.75, 0.25])
        base_ship   = {"International Standard": 6.99, "International Express": 12.99}[ship_method]
        free_thresh = 60.0
    ship_cost    = money(0.0 if items_total >= free_thresh else base_ship)
    total_amount = money(items_total + ship_cost)
    # Payment
    pay_method = weighted_choice(PAY_METHODS, [0.70, 0.15, 0.08, 0.07])
    if status in ("Paid", "Shipped", "Delivered"):
        pay_status = "Success"
        pay_dt     = random_date(order_dt, min(TODAY, order_dt + timedelta(days=2)))
    elif status == "Pending":
        pay_status = weighted_choice(["Pending","Failed"], [0.85, 0.15])
        pay_dt     = order_dt
    elif status == "Cancelled":
        pay_status = weighted_choice(["Failed","Pending","Refunded"], [0.60, 0.25, 0.15])
        pay_dt     = random_date(order_dt, min(TODAY, order_dt + timedelta(days=3)))
    else:  # Returned
        pay_status = "Refunded"
        pay_dt     = random_date(order_dt, min(TODAY, order_dt + timedelta(days=10)))
    payments.append({"payment_id": pay_id, "order_id": oid,
                     "payment_date": pay_dt.isoformat(), "payment_method": pay_method,
                     "amount": total_amount, "payment_status": pay_status})
    pay_id += 1
    # Shipping record
    if cust_country == "United Kingdom":
        city, postal = random.choice(UK_CITIES), uk_postcode()
    else:
        key    = cust_country if cust_country in EU_CITIES else "Ireland"
        city   = random.choice(EU_CITIES.get(key, ["Paris"]))
        postal = eu_postcode()
    shipped_dt = delivery_dt = None
    if status == "Delivered":
        ship_status = "Delivered"
        shipped_dt  = random_date(pay_dt, min(TODAY, pay_dt + timedelta(days=2)))
        max_d       = 5 if cust_country == "United Kingdom" else 10
        delivery_dt = random_date(shipped_dt + timedelta(days=1), min(TODAY, shipped_dt + timedelta(days=max_d)))
    elif status == "Shipped":
        ship_status = "Shipped"
        shipped_dt  = random_date(pay_dt, min(TODAY, pay_dt + timedelta(days=2)))
    elif status in ("Paid", "Pending"):
        ship_status = "Not Shipped"
    elif status == "Cancelled":
        ship_status = "Cancelled"
    else:  # Returned
        ship_status = "Returned"
        shipped_dt  = random_date(pay_dt, min(TODAY, pay_dt + timedelta(days=2)))
        max_d       = 5 if cust_country == "United Kingdom" else 10
        delivery_dt = random_date(shipped_dt + timedelta(days=1), min(TODAY, shipped_dt + timedelta(days=max_d)))
    shippings.append({
        "shipping_id": ship_id, "order_id": oid,
        "recipient_name":   f"{cust['first_name']} {cust['last_name']}",
        "shipping_address": street_address(),
        "city": city, "postal_code": postal, "country": cust_country,
        "shipping_method": ship_method, "shipping_cost": ship_cost,
        "shipped_date":   shipped_dt.isoformat()  if shipped_dt  else None,
        "delivery_date":  delivery_dt.isoformat() if delivery_dt else None,
        "shipping_status": ship_status,
    })
    ship_id += 1
    orders.append({"order_id": oid, "customer_id": cid, "order_date": order_dt.isoformat(),
                   "order_status": status, "total_amount": total_amount})
df_order      = pd.DataFrame(orders)
df_order_item = pd.DataFrame(order_items)
df_payment    = pd.DataFrame(payments)
df_shipping   = pd.DataFrame(shippings)

# ----------------------------------------------------------------------
# Sanity checks
# Built-in validation checks run after generation. Verifies date sequences, financial consistency, uniqueness constraints, and status logic.
# ----------------------------------------------------------------------
errors = []
tmp = df_order.merge(df_customer[["customer_id","join_date"]], on="customer_id")
if (pd.to_datetime(tmp["order_date"]) < pd.to_datetime(tmp["join_date"])).any():
    errors.append("Orders before join_date")
oi_sum = df_order_item.assign(line=df_order_item.quantity * df_order_item.unit_price).groupby("order_id")["line"].sum().reset_index()
chk    = df_order.merge(oi_sum, on="order_id").merge(df_shipping[["order_id","shipping_cost"]], on="order_id")
chk["calc"] = (chk["line"] + chk["shipping_cost"]).round(2)
if (chk["calc"] != chk["total_amount"].round(2)).any():
    errors.append("total_amount mismatch")
pc = df_payment.merge(df_order[["order_id","total_amount"]], on="order_id")
if (pc["amount"].round(2) != pc["total_amount"].round(2)).any():
    errors.append("Payment.amount mismatch")
sp = df_shipping[df_shipping["shipped_date"].notna()].merge(df_payment[["order_id","payment_date"]], on="order_id")
if (pd.to_datetime(sp["shipped_date"]) < pd.to_datetime(sp["payment_date"])).any():
    errors.append("Shipped before payment")
op = df_order.merge(df_payment[["order_id","payment_status"]], on="order_id")
if op[op["order_status"].isin(["Paid","Shipped","Delivered"]) & (op["payment_status"] != "Success")].shape[0]:
    errors.append("Non-Success payment on completed order")
if df_customer["email"].duplicated().any():     errors.append("Duplicate emails")
if df_book["isbn"].duplicated().any():          errors.append("Duplicate ISBNs")
if df_author["author_name"].duplicated().any(): errors.append("Duplicate author names")
if errors:
    print("FAILED:", errors)
else:
    print("All sanity checks passed!")
# Quick stats
print(f"Unique book titles : {df_book['title'].nunique()} / {len(df_book)}")
print(f"Duplicate authors  : {df_author['author_name'].duplicated().sum()}")
print(f"Phone sample (str) : {df_customer[df_customer['country']=='United Kingdom']['phone'].head(3).tolist()}")
df_order["order_date"] = pd.to_datetime(df_order["order_date"])
by_ym = df_order.groupby(df_order["order_date"].dt.to_period("M")).size()
print("December spike:")
for yr in [2023, 2024, 2025]:
    dec = by_ym.get(pd.Period(f"{yr}-12"), 0)
    avg = sum(by_ym.get(pd.Period(f"{yr}-{m:02d}"), 0) for m in range(1,12)) / 11
    print(f"  {yr}: Dec={dec}, avg_other={avg:.0f}, spike={dec/avg:.2f}x")

# ----------------------------------------------------------------------
# Export
# Writes all tables to a single Excel workbook. A post-processing step restores UK phone numbers as text strings to preserve leading zeros.
# ----------------------------------------------------------------------
with pd.ExcelWriter(OUT_XLSX, engine="openpyxl") as writer:
    df_customer.to_excel(   writer, sheet_name="Customer",         index=False)
    df_genre.to_excel(      writer, sheet_name="Genre",            index=False)
    df_book.to_excel(       writer, sheet_name="Book",             index=False)
    df_author.to_excel(     writer, sheet_name="Author",           index=False)
    df_book_author.to_excel(writer, sheet_name="Book_Author",      index=False)
    df_order.to_excel(      writer, sheet_name="Order",            index=False)
    df_order_item.to_excel( writer, sheet_name="Order_Item",       index=False)
    df_payment.to_excel(    writer, sheet_name="Payment",          index=False)
    df_shipping.to_excel(   writer, sheet_name="Shipping_Details", index=False)

# FIX 1: patch phone column back to string with leading zero
# pandas writes phone as float (7181960013.0), so we reopen and fix each cell
import openpyxl
phone_col_idx = df_customer.columns.get_loc("phone") + 1  # 1-indexed for openpyxl
wb = openpyxl.load_workbook(OUT_XLSX)
ws = wb["Customer"]
for row in ws.iter_rows(min_row=2, min_col=phone_col_idx, max_col=phone_col_idx):
    for cell in row:
        if cell.value is not None:
            cell.value = "0" + str(int(cell.value))  # restore leading zero
wb.save(OUT_XLSX)

print(f"\nSaved → {OUT_XLSX}")
