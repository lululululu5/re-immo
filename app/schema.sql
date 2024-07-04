DROP TABLE IF EXISTS user;

CREATE TABLE user (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT UNIQUE NOT NULL,
  hashed_password TEXT NOT NULL,
  email TEXT UNIQUE NOT NULL,
  type TEXT NOT NULL
)

