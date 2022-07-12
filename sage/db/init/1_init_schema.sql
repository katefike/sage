\connect sage
SET
    statement_timeout = 0;
SET
    lock_timeout = 0;
SET
    idle_in_transaction_session_timeout = 0;
SET
    client_encoding = 'UTF8';
SET
    standard_conforming_strings = ON;
SELECT
    pg_catalog.set_config('search_path', '', FALSE);
SET
    check_function_bodies = FALSE;
SET
    xmloption = CONTENT;
SET
    client_min_messages = warning;
SET
    row_security = OFF;
CREATE TABLE IF NOT EXISTS public.banks(
    id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    NAME TEXT NOT NULL,
    account TEXT,
    TYPE TEXT NOT NULL
);
INSERT INTO
    public.banks (NAME, account, TYPE)
VALUES
    ('Huntington', 'savings', 'liquid'),
    ('Huntington', 'checking', 'liquid');
INSERT INTO
    public.banks (NAME, TYPE)
VALUES
    ('Chase', 'credit'),
    ('Discover', 'credit');
CREATE TABLE IF NOT EXISTS public.tags(
    id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    NAME TEXT NOT NULL,
    recurring BOOLEAN NOT NULL
);
CREATE TABLE IF NOT EXISTS public.entities(
    id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    NAME TEXT NOT NULL,
    tag_id INT NOT NULL,
    FOREIGN KEY (tag_id) REFERENCES public.tags(id)
);
CREATE TABLE IF NOT EXISTS public.entity_tag_mapping(
    id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    entity_id INT NOT NULL,
    tag_id INT NOT NULL,
    FOREIGN KEY (entity_id) REFERENCES public.entities(id),
    FOREIGN KEY (tag_id) REFERENCES public.tags(id)
);
CREATE TABLE IF NOT EXISTS public.transactions(
    id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    gmail_id TEXT NOT NULL,
    bank_id INTEGER NOT NULL,
    cents INT NOT NULL,
    date TEXT NOT NULL,
    descr TEXT NOT NULL,
    entity_id INT,
    FOREIGN KEY (bank_id) REFERENCES public.banks (id),
    FOREIGN KEY (entity_id) REFERENCES public.entities (id)
);
CREATE TABLE IF NOT EXISTS public.transaction_tag_mapping(
    id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    transaction_id INT NOT NULL,
    tag_id INT NOT NULL,
    FOREIGN KEY (transaction_id) REFERENCES public.transactions (id),
    FOREIGN KEY (tag_id) REFERENCES public.tags(id)
);