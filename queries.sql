\connect cz4031
SET CLIENT_ENCODING TO 'UTF8';
\timing

-- 1
SELECT type, COUNT(*)
FROM publication
WHERE year BETWEEN 2000 AND 2017
GROUP BY type;

-- 2
SELECT DISTINCT (REGEXP_MATCHES(A.pubkey, '.*/(.*)/.*', 'g'))[1]
FROM publication AS A
WHERE A.type = 'proceedings'
AND A.pubid IN (
    SELECT B.crossref
    FROM publication AS B
    WHERE B.crossref IS NOT NULL
    GROUP BY B.crossref
    HAVING COUNT(*) > 200
)
AND LOWER(A.title) LIKE '%july%';

-- 3a
SELECT A.pubid, A.type, A.pubkey, A.title, A.year, A.crossref
FROM publication AS A, author AS B, publication_author AS C
WHERE B.name = 'Aditya G. Parameswaran'
AND A.year = 2015
AND B.authorid = C.authorid
AND C.pubid = A.pubid;

-- 3b
SELECT A.pubid, A.type, A.pubkey, A.title, A.year, A.crossref
FROM publication AS A, author AS B, publication_author AS C, publication AS D
WHERE B.name = 'Aditya G. Parameswaran'
AND D.pubkey LIKE '%sigmod%'
AND D.year = 2015
AND B.authorid = C.authorid
AND C.pubid = A.pubid
AND A.crossref = D.pubid;

-- 3c
SELECT name
FROM author
WHERE authorid IN (
    SELECT A.authorid
    FROM publication_author AS A, publication AS B, publication AS C
    WHERE C.year = 2015
    AND C.pubkey LIKE '%sigmod%'
    AND C.pubid = B.crossref
    AND B.pubid = A.pubid
    GROUP BY A.authorid
    HAVING COUNT(A.pubid) >= 2
);

-- 4a
SELECT name
FROM author
WHERE authorid IN (
    (
        SELECT A.authorid
        FROM publication_author AS A, publication AS B, publication AS C
        WHERE C.pubkey LIKE '%vldb%'
        AND C.pubid = B.crossref
        AND B.pubid = A.pubid
        GROUP BY A.authorid
        HAVING COUNT(A.pubid) >= 10
    ) INTERSECT (
        SELECT D.authorid
        FROM publication_author AS D, publication AS E, publication AS F
        WHERE F.pubkey LIKE '%sigmod%'
        AND F.pubid = E.crossref
        AND E.pubid = D.pubid
        GROUP BY D.authorid
        HAVING COUNT(D.pubid) >= 10
    )
);

-- 4b
SELECT name
FROM author
WHERE authorid IN (
    (
        SELECT A.authorid
        FROM publication_author AS A, publication AS B, publication AS C
        WHERE C.pubkey LIKE '%vldb%'
        AND C.pubid = B.crossref
        AND B.pubid = A.pubid
        GROUP BY A.authorid
        HAVING COUNT(A.pubid) >= 15
    ) INTERSECT (
        SELECT D.authorid
        FROM publication_author AS D
        WHERE NOT EXISTS(
            SELECT E.pubid
            FROM publication AS E, publication AS F
            WHERE F.pubkey LIKE '%kdd%'
            AND F.pubid = E.crossref
            AND E.pubid = D.pubid
        )
    )
);

-- 5
SELECT (B.year / 10) AS decades, COUNT(A.pubid)
FROM publication AS A, publication AS B
WHERE B.year BETWEEN 1970 AND 2019
AND A.crossref = B.pubid
GROUP BY B.year / 10;

-- 6
SELECT A.name
FROM author AS A,
	publication_author AS B,
	publication_author AS C,
	author AS D,
	publication AS E,
	publication AS F
WHERE LOWER(E.title) LIKE '%data%'
AND (E.pubkey LIKE '%conf%' OR E.pubkey LIKE '%journals%')
AND E.pubid = F.crossref
AND F.pubid = B.pubid
AND A.authorid != D.authorid
AND A.authorid = B.authorid
AND C.authorid = D.authorid
AND B.pubid = C.pubid
GROUP BY A.authorid
ORDER BY COUNT(DISTINCT D.authorid) DESC
LIMIT 1;

-- 7
SELECT A.name
FROM author AS A, publication_author AS B, publication AS C, publication AS D
WHERE LOWER(D.title) LIKE '%data%'
AND (D.pubkey LIKE '%conf%' OR D.pubkey LIKE '%journals%')
AND D.year BETWEEN 2014 AND 2018
AND D.pubid = C.crossref
AND C.pubid = B.pubid
AND B.authorid = A.authorid
GROUP BY A.authorid
ORDER BY COUNT(B.pubid) DESC
LIMIT 10;

-- 8
SELECT DISTINCT (REGEXP_MATCHES(A.pubkey, '.*/(.*)/.*', 'g'))[1]
FROM publication AS A, publication AS B
WHERE A.type = 'proceedings'
AND LOWER(A.title) LIKE '%june%'
AND A.pubid = B.crossref
GROUP BY A.pubid
HAVING COUNT(B.pubid) > 100;

-- 9a
SELECT A.name
FROM author AS A, (
	SELECT DISTINCT C.authorid, D.year
	FROM publication_author AS C, publication AS D
	WHERE C.pubid = D.pubid
	AND D.year BETWEEN 1989 AND 2018
) AS B
WHERE A.name ~ '.* H\w*( \d+)?$'
AND A.authorid = B.authorid
GROUP BY A.authorid
HAVING COUNT(B.year) = 30;

-- 9b
SELECT C.name, COUNT(D.pubid)
FROM author AS C, publication_author AS D, (
	SELECT DISTINCT A.authorid
	FROM publication_author AS A, publication AS B
	WHERE A.pubid = B.pubid
	AND B.year = (SELECT MIN(year) FROM publication)
) AS E
WHERE C.authorid = D.authorid
AND C.authorid = E.authorid
GROUP BY C.authorid;

-- 10
-- Find the top 10 authors who have most publications in KDDs. Report their names and the number of publication in KDD authored by them.
SELECT A.name, COUNT(B.pubid)
FROM author AS A, publication_author AS B, publication AS C, publication AS D
WHERE D.pubkey LIKE '%kdd%'
AND D.pubid = C.crossref
AND C.pubid = B.pubid
AND B.authorid = A.authorid
GROUP BY A.authorid
ORDER BY COUNT(B.pubid) DESC
LIMIT 10;
