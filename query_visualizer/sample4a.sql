SELECT name, age, type
FROM author, publication, conference
WHERE authorid IN (
    (
        SELECT A.authorid, A.something, B.this
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