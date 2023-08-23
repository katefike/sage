-- Save file using ctrl+K S
\connect sage
SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = ON;
SELECT pg_catalog.set_config('search_path', '', FALSE);
SET check_function_bodies = FALSE;
SET xmloption = CONTENT;
SET client_min_messages = warning;
SET row_security = OFF;
SET TIME ZONE 'UTC';
CREATE TABLE IF NOT EXISTS public.emails(
    id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    uid INT NOT NULL,
    batch_time TIMESTAMPTZ NOT NULL,
    forwarded_date DATE NOT NULL,
    from_ TEXT NOT NULL,
    origin TEXT NOT NULL,
    subject TEXT NOT NULL,
    html bool NOT NULL,
    body TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS public.banks(
    id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    NAME TEXT NOT NULL,
    account TEXT,
    -- TODO: Replace with enum (liquid, debt, investment)
    TYPE TEXT NOT NULL
);
INSERT INTO public.banks (NAME, account, TYPE)
VALUES ('Huntington', 'savings', 'liquid'),
    ('Huntington', 'checking', 'liquid');
INSERT INTO public.banks (NAME, TYPE)
VALUES ('Chase', 'credit'),
    ('Discover', 'credit');
CREATE TABLE IF NOT EXISTS public.entity_tags(
    id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    NAME TEXT NOT NULL,
    recurring BOOLEAN NOT NULL
);
CREATE TABLE IF NOT EXISTS public.entities(
    id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    NAME TEXT NOT NULL,
    payer BOOL NOT NULL
);
CREATE TABLE IF NOT EXISTS public.entity_tag_mapping(
    id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    entity_id INT NOT NULL,
    entity_tag_id INT NOT NULL,
    FOREIGN KEY (entity_id) REFERENCES public.entities(id),
    FOREIGN KEY (entity_tag_id) REFERENCES public.entity_tags(id)
);
CREATE TABLE IF NOT EXISTS public.transactions(
    id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    email_id INT NOT NULL, 
    date DATE NOT NULL,
    -- TODO: Replace with enum (withdrawal, deposit, transfer withdrawal, transfer deposit)
    TYPE TEXT NOT NULL,
    bank_id INTEGER NOT NULL,
    amount NUMERIC NOT NULL,
    entity_id INT NOT NULL,
    FOREIGN KEY (email_id) REFERENCES public.emails(id),
    FOREIGN KEY (bank_id) REFERENCES public.banks(id),
    FOREIGN KEY (entity_id) REFERENCES public.entities(id)
);

CREATE TABLE IF NOT EXISTS public.transaction_tags(
    id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    NAME TEXT NOT NULL,
    recurring BOOLEAN NOT NULL
);
CREATE TABLE IF NOT EXISTS public.transaction_tag_mapping(
    id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    transaction_id INT NOT NULL,
    transaction_tag_id INT NOT NULL,
    FOREIGN KEY (transaction_id) REFERENCES public.transactions(id),
    FOREIGN KEY (transaction_tag_id) REFERENCES public.transaction_tags(id)
);
