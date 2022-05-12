import sqlite3

sqlite_connection = sqlite3.connect('surveys.db')
cursor = sqlite_connection.cursor()

cursor.execute("""CREATE TABLE IF NOT EXISTS users(
   userid INT PRIMARY KEY,
   telegramid INT,
   firstname TEXT,
   lastname TEXT,
   age INT);
""")
sqlite_connection.commit()

cursor.execute("""CREATE TABLE IF NOT EXISTS surveys(
   surveyid INT PRIMARY KEY,
   startdate TEXT,
   enddate TEXT);
""")
sqlite_connection.commit()

cursor.execute("""CREATE TABLE IF NOT EXISTS questions(
   questionid INT PRIMARY KEY,
   task TEXT,
   answer1 TEXT,
   answer2 TEXT,
   answer3 TEXT,
   answer4 TEXT,
   testid INT,
   FOREIGN KEY(testid) REFERENCES tests(testid));
""")
sqlite_connection.commit()

cursor.execute("""CREATE TABLE IF NOT EXISTS results(
   resultid INT PRIMARY KEY,
   datecompleted TEXT,
   userid INT,
   testid INT,
   FOREIGN KEY(userid) REFERENCES users(userid),
   FOREIGN KEY(testid) REFERENCES tests(testid));
""")
sqlite_connection.commit()

cursor.execute("""CREATE TABLE IF NOT EXISTS answers(
   answerid INT PRIMARY KEY,
   questionid INT,
   userid INT,
   option INT,
   FOREIGN KEY(questionid) REFERENCES questions(questionid),
   FOREIGN KEY(userid) REFERENCES users(userid));
""")
sqlite_connection.commit()
