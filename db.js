import Database from 'better-sqlite3';

const db = new Database('blog.db');

// Создаем таблицу
db.exec(`
  CREATE TABLE IF NOT EXISTS posts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    content TEXT NOT NULL
  )
`);

export default db;