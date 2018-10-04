USE cz4031;

DROP TABLE IF EXISTS publication_author;
DROP TABLE IF EXISTS raw_publication;
DROP TABLE IF EXISTS author;
DROP TABLE IF EXISTS raw_publication_author;

CREATE TABLE raw_publication (
    type VARCHAR(16) NOT NULL,
    pubkey VARCHAR(100) NOT NULL UNIQUE,
    title TEXT CHARACTER SET UTF8 NOT NULL,
    year INT NOT NULL,
    crossref VARCHAR(100) NULL,
    pubid INT AUTO_INCREMENT NOT NULL PRIMARY KEY
);

CREATE TABLE author (
    name VARCHAR(255) CHARACTER SET UTF8 NOT NULL UNIQUE,
    authorid INT AUTO_INCREMENT NOT NULL PRIMARY KEY
);

CREATE TABLE raw_publication_author (
    pubkey VARCHAR(100) NOT NULL,
    name VARCHAR(255) CHARACTER SET UTF8 NOT NULL,
    id INT AUTO_INCREMENT NOT NULL PRIMARY KEY
);

LOAD DATA LOCAL INFILE 'C:/Users/zpiao/Desktop/CZ4031/samples/publication_sample.csv'
INTO TABLE raw_publication
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS;

LOAD DATA LOCAL INFILE 'C:/Users/zpiao/Desktop/CZ4031/samples/author_sample.csv'
INTO TABLE author
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS;

LOAD DATA LOCAL INFILE 'C:/Users/zpiao/Desktop/CZ4031/samples/publication_author_sample.csv'
INTO TABLE raw_publication_author
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS;

DROP TABLE IF EXISTS publication;

CREATE TABLE publication (
    pubid INT AUTO_INCREMENT NOT NULL PRIMARY KEY,
    type VARCHAR(16) NOT NULL,
    pubkey VARCHAR(100) NOT NULL UNIQUE,
    title TEXT CHARACTER SET UTF8 NOT NULL,
    year INT NOT NULL,
    crossref INT NULL
);

INSERT INTO publication (type, pubkey, title, year, pubid)
SELECT raw_publication.type, raw_publication.pubkey, raw_publication.title, raw_publication.year, raw_publication.pubid
FROM raw_publication;

UPDATE publication,
    raw_publication AS pub,
    raw_publication AS crossrefpub
SET
    publication.crossref = crossrefpub.pubid
WHERE
    publication.pubid = pub.pubid
        AND pub.crossref IS NOT NULL
        AND pub.crossref = crossrefpub.pubkey;

ALTER TABLE publication ADD CONSTRAINT FK_crossref FOREIGN KEY (crossref) REFERENCES publication(pubid);

CREATE TABLE publication_author (
    pubid INT NULL,
    authorid INT NOT NULL,
    id INT AUTO_INCREMENT NOT NULL PRIMARY KEY
);

INSERT INTO publication_author (pubid, authorid)
SELECT pub.pubid, author.authorid
FROM raw_publication AS pub, author, raw_publication_author
WHERE pub.pubkey = raw_publication_author.pubkey AND author.name = raw_publication_author.name;

ALTER TABLE publication_author ADD CONSTRAINT FK_pubid FOREIGN KEY (pubid) REFERENCES publication(pubid);
ALTER TABLE publication_author ADD CONSTRAINT FK_authorid FOREIGN KEY (authorid) REFERENCES author(authorid);

DROP TABLE IF EXISTS raw_publication;
DROP TABLE IF EXISTS raw_publication_author;
