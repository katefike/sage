--
-- PostgreSQL database dump
--

-- Dumped from database version 14.4 (Debian 14.4-1.pgdg110+1)
-- Dumped by pg_dump version 14.18 (Ubuntu 14.18-0ubuntu0.22.04.1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: banks; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.banks (
    id integer NOT NULL,
    name text NOT NULL,
    account text,
    type text NOT NULL
);


ALTER TABLE public.banks OWNER TO admin;

--
-- Name: banks_id_seq; Type: SEQUENCE; Schema: public; Owner: admin
--

ALTER TABLE public.banks ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.banks_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: emails; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.emails (
    id integer NOT NULL,
    uid integer NOT NULL,
    batch_time timestamp with time zone NOT NULL,
    forwarded_date date NOT NULL,
    from_ text NOT NULL,
    origin text NOT NULL,
    subject text NOT NULL,
    html boolean NOT NULL,
    body text NOT NULL
);


ALTER TABLE public.emails OWNER TO admin;

--
-- Name: emails_id_seq; Type: SEQUENCE; Schema: public; Owner: admin
--

ALTER TABLE public.emails ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.emails_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: entities; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.entities (
    id integer NOT NULL,
    name text NOT NULL,
    payer boolean NOT NULL
);


ALTER TABLE public.entities OWNER TO admin;

--
-- Name: entities_id_seq; Type: SEQUENCE; Schema: public; Owner: admin
--

ALTER TABLE public.entities ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.entities_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: entity_tag_mapping; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.entity_tag_mapping (
    id integer NOT NULL,
    entity_id integer NOT NULL,
    entity_tag_id integer NOT NULL
);


ALTER TABLE public.entity_tag_mapping OWNER TO admin;

--
-- Name: entity_tag_mapping_id_seq; Type: SEQUENCE; Schema: public; Owner: admin
--

ALTER TABLE public.entity_tag_mapping ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.entity_tag_mapping_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: entity_tags; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.entity_tags (
    id integer NOT NULL,
    name text NOT NULL,
    recurring boolean NOT NULL
);


ALTER TABLE public.entity_tags OWNER TO admin;

--
-- Name: entity_tags_id_seq; Type: SEQUENCE; Schema: public; Owner: admin
--

ALTER TABLE public.entity_tags ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.entity_tags_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: transaction_tag_mapping; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.transaction_tag_mapping (
    id integer NOT NULL,
    transaction_id integer NOT NULL,
    transaction_tag_id integer NOT NULL
);


ALTER TABLE public.transaction_tag_mapping OWNER TO admin;

--
-- Name: transaction_tag_mapping_id_seq; Type: SEQUENCE; Schema: public; Owner: admin
--

ALTER TABLE public.transaction_tag_mapping ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.transaction_tag_mapping_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: transaction_tags; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.transaction_tags (
    id integer NOT NULL,
    name text NOT NULL,
    recurring boolean NOT NULL
);


ALTER TABLE public.transaction_tags OWNER TO admin;

--
-- Name: transaction_tags_id_seq; Type: SEQUENCE; Schema: public; Owner: admin
--

ALTER TABLE public.transaction_tags ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.transaction_tags_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: transactions; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.transactions (
    id integer NOT NULL,
    email_id integer NOT NULL,
    date date NOT NULL,
    type text NOT NULL,
    bank_id integer NOT NULL,
    amount numeric NOT NULL,
    entity_id integer
);


ALTER TABLE public.transactions OWNER TO admin;

--
-- Name: transactions_id_seq; Type: SEQUENCE; Schema: public; Owner: admin
--

ALTER TABLE public.transactions ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.transactions_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: banks banks_pkey; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.banks
    ADD CONSTRAINT banks_pkey PRIMARY KEY (id);


--
-- Name: emails emails_pkey; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.emails
    ADD CONSTRAINT emails_pkey PRIMARY KEY (id);


--
-- Name: entities entities_pkey; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.entities
    ADD CONSTRAINT entities_pkey PRIMARY KEY (id);


--
-- Name: entity_tag_mapping entity_tag_mapping_pkey; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.entity_tag_mapping
    ADD CONSTRAINT entity_tag_mapping_pkey PRIMARY KEY (id);


--
-- Name: entity_tags entity_tags_pkey; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.entity_tags
    ADD CONSTRAINT entity_tags_pkey PRIMARY KEY (id);


--
-- Name: transaction_tag_mapping transaction_tag_mapping_pkey; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.transaction_tag_mapping
    ADD CONSTRAINT transaction_tag_mapping_pkey PRIMARY KEY (id);


--
-- Name: transaction_tags transaction_tags_pkey; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.transaction_tags
    ADD CONSTRAINT transaction_tags_pkey PRIMARY KEY (id);


--
-- Name: transactions transactions_pkey; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.transactions
    ADD CONSTRAINT transactions_pkey PRIMARY KEY (id);


--
-- Name: entity_tag_mapping entity_tag_mapping_entity_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.entity_tag_mapping
    ADD CONSTRAINT entity_tag_mapping_entity_id_fkey FOREIGN KEY (entity_id) REFERENCES public.entities(id);


--
-- Name: entity_tag_mapping entity_tag_mapping_entity_tag_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.entity_tag_mapping
    ADD CONSTRAINT entity_tag_mapping_entity_tag_id_fkey FOREIGN KEY (entity_tag_id) REFERENCES public.entity_tags(id);


--
-- Name: transaction_tag_mapping transaction_tag_mapping_transaction_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.transaction_tag_mapping
    ADD CONSTRAINT transaction_tag_mapping_transaction_id_fkey FOREIGN KEY (transaction_id) REFERENCES public.transactions(id);


--
-- Name: transaction_tag_mapping transaction_tag_mapping_transaction_tag_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.transaction_tag_mapping
    ADD CONSTRAINT transaction_tag_mapping_transaction_tag_id_fkey FOREIGN KEY (transaction_tag_id) REFERENCES public.transaction_tags(id);


--
-- Name: transactions transactions_bank_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.transactions
    ADD CONSTRAINT transactions_bank_id_fkey FOREIGN KEY (bank_id) REFERENCES public.banks(id);


--
-- Name: transactions transactions_email_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.transactions
    ADD CONSTRAINT transactions_email_id_fkey FOREIGN KEY (email_id) REFERENCES public.emails(id);


--
-- Name: transactions transactions_entity_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.transactions
    ADD CONSTRAINT transactions_entity_id_fkey FOREIGN KEY (entity_id) REFERENCES public.entities(id);


--
-- Name: SCHEMA public; Type: ACL; Schema: -; Owner: admin
--

GRANT USAGE ON SCHEMA public TO grafanareader;


--
-- Name: TABLE banks; Type: ACL; Schema: public; Owner: admin
--

GRANT INSERT ON TABLE public.banks TO etl;


--
-- Name: TABLE emails; Type: ACL; Schema: public; Owner: admin
--

GRANT INSERT ON TABLE public.emails TO etl;


--
-- Name: TABLE entities; Type: ACL; Schema: public; Owner: admin
--

GRANT INSERT ON TABLE public.entities TO etl;


--
-- Name: TABLE entity_tag_mapping; Type: ACL; Schema: public; Owner: admin
--

GRANT INSERT ON TABLE public.entity_tag_mapping TO etl;


--
-- Name: TABLE entity_tags; Type: ACL; Schema: public; Owner: admin
--

GRANT INSERT ON TABLE public.entity_tags TO etl;


--
-- Name: TABLE transaction_tag_mapping; Type: ACL; Schema: public; Owner: admin
--

GRANT INSERT ON TABLE public.transaction_tag_mapping TO etl;


--
-- Name: TABLE transaction_tags; Type: ACL; Schema: public; Owner: admin
--

GRANT INSERT ON TABLE public.transaction_tags TO etl;


--
-- Name: TABLE transactions; Type: ACL; Schema: public; Owner: admin
--

GRANT INSERT ON TABLE public.transactions TO etl;


--
-- Name: DEFAULT PRIVILEGES FOR TABLES; Type: DEFAULT ACL; Schema: public; Owner: admin
--

ALTER DEFAULT PRIVILEGES FOR ROLE admin IN SCHEMA public GRANT INSERT ON TABLES  TO etl;
ALTER DEFAULT PRIVILEGES FOR ROLE admin IN SCHEMA public GRANT SELECT ON TABLES  TO grafanareader;


--
-- PostgreSQL database dump complete
--

