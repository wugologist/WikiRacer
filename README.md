# WikiRacer
AI agent to play the Wikipedia Game

Final project for CS 4100 Foundations of Artificial Intelligence at Northeastern University

This is a project to find a series of Wikipedia pages linking one to another in as few page loads as possible (not necessarily the shortest path). It uses an A* search and a variety of different heuristics are being tested.

# Install
## Prerequisites
Depending on your machine, you may have to install some additional development packages so that the pip3 installation succeeds, such as `mysql-dev` and `python3-dev`.

## PIP3 Installation
```
pip3 install --user -r requirements.txt
```

## Updating Your Email
To use the Wikipedia API, you must update the file [`src/apis/WikipediaApi.py`](src/apis/WikipediaApi.py) to contain your email as the value for the user-agent (Search for the string "`your@email.here`").

## Setup on AWS
For testing purposes, we ran some of our tests on AWS EC2 instances. The following is a complete set of commands which will prepare an Amazon Linux EC2 instance to run WikiRacer:
```
sudo yum update
sudo yum install python3 python3-devel mysql-devel git gcc
git clone https://github.com/Emporophobe/WikiRacer.git
cd WikiRacer
sudo pip3 install -r requirements.txt
```

# Usage
```
python3 WikiRacer.py [-h] --heuristic {bfs,dfs,null,tfidf,wordnet,doc2vec}
                     [--greedy] [--quiet] [--no-console] [--no-file]
                     [--api {WikipediaApi,LocalApi,SqlApi}]
                     [--local-bz LOCAL_BZ] [--local-index LOCAL_INDEX]
                     start goal
```

## Local API
To use the Local API, you must download a `*-pages-articles-multistream.xml.bz2` file and a `*-pages-articles-index.txt` from the Wikimedia dump site and provide those files to the `--local-bz` and `--local-index` arguments.

## SQL API
Instructions for setting up a SQL API on your machine is listed under [`notes/creating-sql-db.md`](notes/creating-sql-db.md)