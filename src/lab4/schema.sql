-- Схема предметної області «Музичний інструмент»
DROP TABLE IF EXISTS musician_instruments, musicians, instruments, manufacturers, categories;

CREATE TABLE categories (
    id          serial PRIMARY KEY,
    name        varchar(50)  NOT NULL UNIQUE,
    description text
);

CREATE TABLE manufacturers (
    id       serial PRIMARY KEY,
    name     varchar(100) NOT NULL UNIQUE,
    country  varchar(60)  NOT NULL,
    email    varchar(120) NOT NULL,
    website  varchar(200)
);

-- instruments: N:1 -> categories, N:1 -> manufacturers (з боку категорії/виробника це 1:N)
CREATE TABLE instruments (
    id              serial PRIMARY KEY,
    serial_number   varchar(16)   NOT NULL UNIQUE,
    name            varchar(120)  NOT NULL,
    category_id     integer       NOT NULL REFERENCES categories(id)    ON DELETE RESTRICT,
    manufacturer_id integer       NOT NULL REFERENCES manufacturers(id) ON DELETE RESTRICT,
    price           numeric(10,2) NOT NULL CHECK (price >= 0),
    year_made       integer       NOT NULL CHECK (year_made BETWEEN 1600 AND 2100)
);

CREATE TABLE musicians (
    id        serial PRIMARY KEY,
    full_name varchar(120) NOT NULL,
    email     varchar(120) NOT NULL UNIQUE,
    phone     varchar(13)  NOT NULL
);

-- N:M musicians <-> instruments
CREATE TABLE musician_instruments (
    musician_id   integer NOT NULL REFERENCES musicians(id)   ON DELETE CASCADE,
    instrument_id integer NOT NULL REFERENCES instruments(id) ON DELETE CASCADE,
    since_year    integer,
    PRIMARY KEY (musician_id, instrument_id)
);
