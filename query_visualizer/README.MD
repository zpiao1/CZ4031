## Query Visualizer
#### A CZ4031 Project

Query Visualizer is a tool designed to visualize the correlation of query tokens and the corresponding Query Execution Plan (QEP) components. It also supports automatic parsing and building of QEP tree from a QEP JSON object. It provides an interactive user interface that allows users to analyze detailed information of individual stages of the execution plan.
 
The tool is fully written in Python 3. The GUI component is built using Python’s Tkinter library. PostgreSQL version 10 is supported and tested, with no guarantee that other versions will also work properly with the tool.

### Usage
Make sure you have python 3 installed.

Clone the repo and install required libraries:

`pip install -r requirements.txt`

Start the GUI by running `gui.py`:

`python gui.py`

Paste the query and QEP JSON to the respective field and click Enter.

Here you go!

### How to obtain QEP JSON
The suggested way for obtaining a legal QEP JSON from PostgreSQL is to add EXPLAIN (ANALYZE, VERBOSE, FORMAT JSON) as the first line of the query, and paste the generated JSON to the tool.