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