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
    manually_forwarded BOOLEAN NOT NULL,
    from_ TEXT NOT NULL,
    subject TEXT NOT NULL,
    html bool NOT NULL,
    body TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS public.banks(
    id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name TEXT NOT NULL,
    account TEXT,
    type TEXT NOT NULL,
    email_addresses TEXT[] NOT NULL,
    date_opened DATE,
    date_closed DATE
);
INSERT INTO public.banks (name, account, type, email_addresses, date_opened, date_closed)
VALUES 
    ('Huntington', 'SAVE', 'liquid', ARRAY['HuntingtonAlerts@email.huntington.com', 'HuntingtonOnline@email.huntington.com'], '2024-01-01', '2024-12-31'),
    ('Huntington', 'CHECK', 'liquid', ARRAY['HuntingtonAlerts@email.huntington.com', 'HuntingtonOnline@email.huntington.com'], '2024-01-01', '2024-12-31'),
    ('Huntington', 'CK9706', 'liquid', ARRAY['HuntingtonAlerts@email.huntington.com', 'HuntingtonOnline@email.huntington.com'], '2024-01-01', '2024-12-31'),
    ('Discover', 'student', 'credit', ARRAY['discover@services.discover.com'], '2024-01-01', '2024-12-31'),
    ('Discover', 'miles', 'credit', ARRAY['discover@services.discover.com'], '2024-01-01', '2024-12-31'),
    ('Discover', 'savings', 'liquid', ARRAY['discover@services.discover.com'], '2024-01-01', '2024-12-31');
INSERT INTO public.banks (name, type, email_addresses, date_opened, date_closed)
VALUES ('Chase', 'credit', ARRAY['no.reply.alerts@chase.com'], '2024-01-01', '2024-12-31');
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
CREATE TABLE IF NOT EXISTS public.txns(
    id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    email_id INT NOT NULL,
    date DATE NOT NULL,
    -- TODO: Replace with enum (withdrawal, deposit, transfer withdrawal, transfer deposit)
    TYPE TEXT NOT NULL,
    bank_id INTEGER NOT NULL,
    amount NUMERIC NOT NULL,
    balance NUMERIC,
    entity_id INT,
    identical_txn_id INT,
    FOREIGN KEY (email_id) REFERENCES public.emails(id),
    FOREIGN KEY (bank_id) REFERENCES public.banks(id),
    FOREIGN KEY (entity_id) REFERENCES public.entities(id),
    FOREIGN KEY (identical_txn_id) REFERENCES public.txns(id)
);
CREATE TABLE IF NOT EXISTS public.txn_tags(
    id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    NAME TEXT NOT NULL,
    recurring BOOLEAN NOT NULL
);
CREATE TABLE IF NOT EXISTS public.txn_tag_mapping(
    id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    txn_id INT NOT NULL,
    txn_tag_id INT NOT NULL,
    FOREIGN KEY (txn_id) REFERENCES public.txns(id),
    FOREIGN KEY (txn_tag_id) REFERENCES public.txn_tags(id)
);