CREATE DATABASE cz4031 ENCODING 'UTF8';

\connect cz4031;

UPDATE CLIENT_ENCODING TO 'UTF8';

DROP TABLE IF EXISTS publication_author;
DROP TABLE IF EXISTS raw_publication;
DROP TABLE IF EXISTS raw_author;
DROP TABLE IF EXISTS author;
DROP TABLE IF EXISTS raw_publication_author;
DROP TABLE IF EXISTS publication;

CREATE TABLE raw_publication (
    type VARCHAR(16) NOT NULL,
    pubkey VARCHAR(100) NOT NULL,
    title TEXT NOT NULL,
    year INT NULL,
    crossref VARCHAR(100) NULL
);

CREATE TABLE raw_author (name VARCHAR(255) NOT NULL);

CREATE TABLE raw_publication_author (
    pubkey VARCHAR(100) NOT NULL,
    name VARCHAR(255) NOT NULL
);

CREATE TABLE author (
    name VARCHAR(255) NOT NULL,
    authorid SERIAL PRIMARY KEY
);

CREATE TABLE publication (
    pubid SERIAL PRIMARY KEY,
    type VARCHAR(16) NOT NULL,
    pubkey VARCHAR(100) NOT NULL,
    title TEXT NOT NULL,
    year INT NOT NULL,
    crossref INT NULL
);

CREATE TABLE publication_author (
    pubid INT NOT NULL,
    authorid INT NOT NULL,
    id SERIAL PRIMARY KEY
);

\copy raw_publication (type, pubkey, title, year, crossref) FROM 'C:/Users/zpiao/Desktop/CZ4031/data/publication.csv' DELIMITER ',' CSV HEADER;

\copy raw_author (name) FROM 'C:/Users/zpiao/Desktop/CZ4031/data/author.csv' DELIMITER ',' CSV HEADER;

\copy raw_publication_author (pubkey, name) FROM 'C:/Users/zpiao/Desktop/CZ4031/data/publication_author.csv' DELIMITER ',' CSV HEADER;

UPDATE raw_publication UPDATE crossref = NULL WHERE crossref = 'NULL';

INSERT INTO author (name)
SELECT DISTINCT ON (name) name FROM raw_author;

INSERT INTO publication (type, pubkey, title, year)
SELECT DISTINCT ON (pubkey) A.type, A.pubkey, A.title, A.year FROM raw_publication AS A;

UPDATE publication
UPDATE crossref = B.pubid
FROM publication AS B, raw_publication AS C
WHERE publication.pubkey = C.pubkey AND C.crossref = B.pubkey;

INSERT INTO publication_author (pubid, authorid)
SELECT A.pubid, B.authorid
FROM publication AS A, author AS B, (SELECT DISTINCT pubkey, name
  FROM raw_publication_author) AS C
WHERE A.pubkey = C.pubkey AND B.name = C.name;

ALTER TABLE publication ADD CONSTRAINT UC_pubkey UNIQUE (pubkey);
ALTER TABLE publication ADD CONSTRAINT FK_crossref FOREIGN KEY (crossref) REFERENCES publication(pubid);

ALTER TABLE author ADD CONSTRAINT UC_name UNIQUE (name);

ALTER TABLE publication_author ADD CONSTRAINT FK_pubid FOREIGN KEY (pubid) REFERENCES publication(pubid);
ALTER TABLE publication_author ADD CONSTRAINT FK_authorid FOREIGN KEY (authorid) REFERENCES author(authorid);
ALTER TABLE publication_author ADD CONSTRAINT UC_pubid_authorid UNIQUE (pubid, authorid);

DROP TABLE IF EXISTS raw_publication;
DROP TABLE IF EXISTS raw_author;
DROP TABLE IF EXISTS raw_publication_author;
