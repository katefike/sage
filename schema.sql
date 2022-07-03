CREATE TABLE IF NOT EXISTS banks(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    NAME TEXT NOT NULL,
    account TEXT NOT NULL,
    TYPE TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS entities(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    NAME TEXT NOT NULL,
    tag_id INT NOT NULL,
    FOREIGN KEY (tag_id) REFERENCES tags(id)
);
CREATE TABLE IF NOT EXISTS entity_tag_mapping(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    entity_id INT NOT NULL,
    tag_id INT NOT NULL,
    FOREIGN KEY (entity_id) REFERENCES entityies(id),
    FOREIGN KEY (tag_id) REFERENCES tags(id)
);
CREATE TABLE IF NOT EXISTS transactions(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    bank_id INTEGER NOT NULL,
    cents INT NOT NULL,
    date TEXT NOT NULL,
    descr TEXT NOT NULL,
    entity_id INT,
    FOREIGN KEY (bank_id) REFERENCES banks (id),
    FOREIGN KEY (entity_id) REFERENCES entities (id)
);
CREATE TABLE IF NOT EXISTS transaction_tag_mapping(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    transaction_id INT NOT NULL,
    tag_id INT NOT NULL,
    FOREIGN KEY (transaction_id) REFERENCES transactions (id),
    FOREIGN KEY (tag_id) REFERENCES tags(id)
);
CREATE TABLE IF NOT EXISTS tags(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    NAME TEXT NOT NULL,
    recurring BOOLEAN NOT NULL
);