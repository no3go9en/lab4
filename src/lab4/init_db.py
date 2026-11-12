"""Ініціалізація БД безпосередньо з Python: створення таблиць + тестові дані (50+ записів).

Запуск: uv run lab4-init-db
"""

import random
from importlib.resources import files

import psycopg

from lab4.storage import DSN

CATEGORIES = [
    ("Струнні щипкові", "Гітари, бас-гітари, укулеле, бандури"),
    ("Струнні смичкові", "Скрипки, альти, віолончелі, контрабаси"),
    ("Клавішні", "Фортепіано, синтезатори, цифрові піаніно"),
    ("Ударні", "Барабанні установки, малі барабани, кахони"),
    ("Мідні духові", "Труби, тромбони, валторни"),
    ("Дерев'яні духові", "Флейти, кларнети, саксофони, сопілки"),
    ("Електронні", "Драм-машини, грувбокси, MIDI-контролери"),
    ("Народні", "Бандури, трембіти, цимбали, кобзи"),
]

MANUFACTURERS = [
    ("Yamaha", "Японія", "info@yamaha.com", "https://yamaha.com"),
    ("Fender", "США", "support@fender.com", "https://fender.com"),
    ("Gibson", "США", "service@gibson.com", "https://gibson.com"),
    ("Roland", "Японія", "contact@roland.com", "https://roland.com"),
    ("Steinway & Sons", "Німеччина", "info@steinway.com", "https://steinway.com"),
    ("Pearl", "Японія", "info@pearldrum.com", "https://pearldrum.com"),
    ("Bach", "США", "info@bachbrass.com", "https://bachbrass.com"),
    ("Buffet Crampon", "Франція", "contact@buffet-crampon.com", "https://buffet-crampon.com"),
    ("Korg", "Японія", "info@korg.com", "https://korg.com"),
    ("Трембіта Майстер", "Україна", "hello@trembita.ua", None),
]

# (назва, категорія 1-8, виробник 1-10, префікс серійника, базова ціна)
MODELS = [
    ("Stratocaster", 1, 2, "FND", 1500),
    ("Telecaster", 1, 2, "FND", 1300),
    ("Precision Bass", 1, 2, "FND", 1400),
    ("Les Paul Standard", 1, 3, "GIB", 2800),
    ("SG Standard", 1, 3, "GIB", 1900),
    ("Hummingbird", 1, 3, "GIB", 3500),
    ("Pacifica 112V", 1, 1, "YMH", 330),
    ("FG800", 1, 1, "YMH", 230),
    ("Silent Violin SV-250", 2, 1, "YMH", 2200),
    ("V5 Violin", 2, 1, "YMH", 650),
    ("Cello VC5S", 2, 1, "YMH", 1700),
    ("Model D Concert Grand", 3, 5, "STW", 180000),
    ("Model B", 3, 5, "STW", 120000),
    ("U1 Upright", 3, 1, "YMH", 9000),
    ("Clavinova CLP-745", 3, 1, "YMH", 2700),
    ("FP-30X", 3, 4, "ROL", 700),
    ("Fantom 8", 3, 4, "ROL", 4300),
    ("Kronos 2", 3, 9, "KRG", 3900),
    ("Minilogue XD", 7, 9, "KRG", 650),
    ("TR-8S", 7, 4, "ROL", 700),
    ("MC-707", 7, 4, "ROL", 1100),
    ("Volca Beats", 7, 9, "KRG", 160),
    ("Export EXX", 4, 6, "PRL", 800),
    ("Masters Maple", 4, 6, "PRL", 3200),
    ("TD-27KV", 4, 4, "ROL", 3000),
    ("Stage Custom", 4, 1, "YMH", 750),
    ("Stradivarius 180S37", 5, 7, "BCH", 3400),
    ("TR300H2", 5, 7, "BCH", 900),
    ("YSL-354 Trombone", 5, 1, "YMH", 1200),
    ("YHR-567 Horn", 5, 1, "YMH", 4600),
    ("R13 Clarinet", 6, 8, "BCR", 3800),
    ("E11 Clarinet", 6, 8, "BCR", 1400),
    ("YAS-280 Sax", 6, 1, "YMH", 1500),
    ("YFL-222 Flute", 6, 1, "YMH", 600),
    ("Сопілка класична", 6, 10, "TRM", 40),
    ("Трембіта гуцульська", 8, 10, "TRM", 900),
    ("Бандура Чернігівська", 8, 10, "TRM", 2500),
    ("Цимбали концертні", 8, 10, "TRM", 1800),
    ("Кобза", 8, 10, "TRM", 1200),
    ("Укулеле GL1", 1, 1, "YMH", 120),
]

MUSICIANS = [
    "Олена Коваленко",
    "Андрій Шевчук",
    "Ірина Мельник",
    "Тарас Бондаренко",
    "Марія Ткаченко",
    "Олег Кравчук",
    "Софія Литвин",
    "Дмитро Савчук",
    "Наталія Гнатюк",
    "Богдан Руденко",
    "Юлія Павленко",
    "Максим Іваненко",
    "Оксана Мороз",
    "Василь Гуцуляк",
    "Катерина Остапенко",
]
OPERATOR_CODES = [50, 63, 66, 67, 68, 73, 93, 95, 97, 99]
TRANSLIT = str.maketrans(
    {
        "а": "a",
        "б": "b",
        "в": "v",
        "г": "h",
        "ґ": "g",
        "д": "d",
        "е": "e",
        "є": "ie",
        "ж": "zh",
        "з": "z",
        "и": "y",
        "і": "i",
        "ї": "i",
        "й": "i",
        "к": "k",
        "л": "l",
        "м": "m",
        "н": "n",
        "о": "o",
        "п": "p",
        "р": "r",
        "с": "s",
        "т": "t",
        "у": "u",
        "ф": "f",
        "х": "kh",
        "ц": "ts",
        "ч": "ch",
        "ш": "sh",
        "щ": "shch",
        "ь": "",
        "ю": "iu",
        "я": "ia",
        " ": ".",
    }
)


def init_db(dsn: str = DSN) -> dict[str, int]:
    rnd = random.Random(8)  # noqa: S311 — детерміновані тестові дані, не криптографія
    schema = (files("lab4") / "schema.sql").read_text(encoding="utf-8")

    with psycopg.connect(dsn) as conn, conn.cursor() as cur:
        cur.execute(schema.encode())

        cur.executemany("INSERT INTO categories (name, description) VALUES (%s, %s)", CATEGORIES)
        cur.executemany(
            "INSERT INTO manufacturers (name, country, email, website) VALUES (%s, %s, %s, %s)",
            MANUFACTURERS,
        )
        cur.executemany(
            "INSERT INTO instruments"
            " (serial_number, name, category_id, manufacturer_id, price, year_made)"
            " VALUES (%s, %s, %s, %s, %s, %s)",
            [
                (
                    f"{pfx}-{100000 + i * 7919}",
                    name,
                    cat,
                    man,
                    round(price * rnd.uniform(0.9, 1.15), 2),
                    rnd.randint(1965, 2025),
                )
                for i, (name, cat, man, pfx, price) in enumerate(MODELS, start=1)
            ],
        )
        cur.executemany(
            "INSERT INTO musicians (full_name, email, phone) VALUES (%s, %s, %s)",
            [
                (
                    n,
                    f"{n.lower().translate(TRANSLIT)}@music.ua",
                    f"+380{rnd.choice(OPERATOR_CODES)}{rnd.randint(0, 9_999_999):07d}",
                )
                for n in MUSICIANS
            ],
        )
        links = {
            (m, i)
            for m in range(1, len(MUSICIANS) + 1)
            for i in rnd.sample(range(1, len(MODELS) + 1), rnd.randint(1, 4))
        }
        cur.executemany(
            "INSERT INTO musician_instruments (musician_id, instrument_id, since_year)"
            " VALUES (%s, %s, %s)",
            [(m, i, rnd.randint(2005, 2025)) for m, i in sorted(links)],
        )

        counts = {}
        for table in (
            "categories",
            "manufacturers",
            "instruments",
            "musicians",
            "musician_instruments",
        ):
            row = cur.execute(f"SELECT count(*) FROM {table}".encode()).fetchone()  # noqa: S608
            counts[table] = row[0] if row else 0
    return counts  # commit — автоматично при виході з with


def main() -> None:
    counts = init_db()
    for table, n in counts.items():
        print(f"{table:<22} {n:>4}")
    print(f"{'РАЗОМ':<22} {sum(counts.values()):>4}")


if __name__ == "__main__":
    main()
