\connect cz4031
SET CLIENT_ENCODING TO 'UTF8';

CREATE INDEX ID_year ON publication (year);
CREATE INDEX ID_lower_title ON publication (LOWER(title));
CREATE INDEX ID_crossref ON publication (crossref);

CREATE INDEX ID_pubid ON publication_author (pubid);
CREATE INDEX ID_authorid ON publication_author (authorid);

-- Speed ups for each query
-- Without index, With index, shared_buffers=1GB
-- 17.245, 17.095, 17.289
-- 1.367, 1.656, 1.643
-- 21.545, 0.090, 0.124
-- 1.507, 0.084, 0.064
-- 20.078, 1.048, 1.184
-- 6.419, 4.731, 3.612
-- 9.744, 6.403, 5.943
-- 9.013, 7.197, 8.754
-- 25.232, 23.905, 23.997
-- 5.717, 3.324, 2.873
-- 2.712, 1.197, 0.961
-- 36.279, 35.058, 32.799
-- 31.468, 0.564, 0.427
-- 6.935, 2.956, 1.310
