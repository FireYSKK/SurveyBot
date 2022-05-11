import sqlite3

sqlite_connection = sqlite3.connect('surveys.db')
cursor = sqlite_connection.cursor()

cursor.execute("""CREATE TABLE IF NOT EXISTS users(
   userid INT PRIMARY KEY,
   firstname TEXT,
   lastname TEXT,
   username TEXT,
   age INT);
""")
sqlite_connection.commit()

cursor.execute("""CREATE TABLE IF NOT EXISTS tests(
   testid INT PRIMARY KEY,
   deadline TEXT);
""")
sqlite_connection.commit()

cursor.execute("""CREATE TABLE IF NOT EXISTS questions(
   questionid INT PRIMARY KEY,
   task TEXT,
   answer1 TEXT,
   answer2 TEXT,
   answer3 TEXT,
   answer4 TEXT,
   correct INT,
   testid INT,
   FOREIGN KEY(testid) REFERENCES tests(testid));
""")
sqlite_connection.commit()

cursor.execute("""CREATE TABLE IF NOT EXISTS results(
   resultid INT PRIMARY KEY,
   score INT,
   userid INT,
   testid INT,
   FOREIGN KEY(userid) REFERENCES users(userid),
   FOREIGN KEY(testid) REFERENCES tests(testid));
""")
sqlite_connection.commit()