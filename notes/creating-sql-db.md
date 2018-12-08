# Creating the SQL Database

Recreating the SQL database for wikipedia based on the data dump was not trivial. Here are some quick instructions that might be helpful for anyone else trying to do the same in the future.

### My Setup

I was running this on a Debian machine: `Linux entei 4.9.0-7-amd64 #1 SMP Debian 4.9.110-3+deb9u2 (2018-08-13) x86_64 GNU/Linux`

### Install MySQL Server

```
sudo apt-get install mysql-server
mysql_secure_installation
sudo systemctl stop mysql
```

### Clone MWDumper
```
git clone https://gerrit.wikimedia.org/r/mediawiki/tools/mwdumper
cd mwdumper/
sudo apt install maven
mvn package -DskipTests
```
The `-DskipTests` is because for some reason maven couldn't run the tests for mwdumper, and would refuse to build the jar until the tests passed. This flag bypasses those tests.

### Download wikipedia dump
You'll want a database dump named similar to: `enwiki-20181120-pages-articles-multistream.xml.bz2`. That's the specific dump that I was using, but feel free to try a different one. For some reason the October dump from this year didn't work (it only imported some of the pages), but the November one did.

### Configure mysql to allow passwordless logins
This is temporary and only while you're importing the dump. Out of an abundance of caution, you should consider making sure that your server isn't accessible from the internet while doing this process.

You can enable passwordless logins by either having mysql use local user auth, or by creating a `~/.mysql.cnf` file with the following contents:
```
[client]
user=root
password=PASSWORD
```

### Import the mediawiki schema
You want to find the `tables.sql` file for the current media wiki. You can find it here: https://phabricator.wikimedia.org/source/mediawiki/browse/master/maintenance/tables.sql.

Also, if that ends up giving you problems, the table schema from commit `88fa7822340eb13e3499a746ae355b9760a326b7` is (probably) the one that I used with success: https://phabricator.wikimedia.org/source/mediawiki/browse/master/maintenance/tables.sql;88fa7822340eb13e3499a746ae355b9760a326b7

Log into mysql as root and run the command `CREATE DATABASE wiki`, then `USE wiki`, and then `SOURCE tables.sql`.


### Import the data (This step will take many hours!!)
Note: You probably want to run this in a screen or tmux.

Basically, you want a command like this:

`bunzip2 -c /hdd/WikiRacer/data/enwiki-20181020-pages-articles-multistream.xml.bz2 | java -jar mwdumper-1.25.jar --format=sql:1.25 | mysql wiki`

That last `wiki` is the database name you chose, so if you chose a different name while making the schema, adjust appropriately.

### Re-secure your mysql instance
Undo whatever you had to do in order to make the script run without prompting for a password.