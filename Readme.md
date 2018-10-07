# CZ4031 Project 1
The SQL queries are executed on [PostgreSQL 10.0](https://www.postgresql.org/download/).  

Instructions:  
1. Import the project into Intellij Idea, and run `fun main()` from the IDE.  
2. Upon request, enter the location of the `dblp.xml` and the location of output files. The parser outputs three files: `publication.csv`, `author.csv`, `publication_author.csv`.  
3. Replace the paths in [`create_tables.sql`](./create_tables.sql) with the output paths chosen in the parser.
4. Execute the commands in [`create_tables.sql`](./create_tables.sql) in `psql` command line. (We have only tested on this)
5. The queries for part 2 is included in [`queries.sql`](./queries.sql) and tested on PgAdmin (PostgreSQL client that can run in browser). 
    * For PgAdmin users, connect to `cz4031` database, and for each query, the time taken to execute is in **Query History**. You don't need to execute the code shown below, which is only needed by `psql` users.  
    * For command line `psql` users,  you also need to execute these lines
      ```postgresql
      \connect cz4031
      SET CLIENT_ENCODING TO 'UTF8';
      \timing
      ```
      before the queries.
6. PostgreSQL controls size of cache via the variable `shared_buffers`. If you would like to change it, find `postgresql.conf` in the path of installation, and modify the value inside. 