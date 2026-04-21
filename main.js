import express from 'express';
import db from './db.js';
import { fileURLToPath } from 'url';
import path from 'path';
import { json } from 'stream/consumers';

const app = express();
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// --- НАСТРОЙКИ ---
app.use(express.json()); // Для API (JSON)

// --- РОУТЫ ДЛЯ БРАУЗЕРА (HTML) ---

// Главная страница: рендерим index.ejs и передаем туда посты
app.get('/', (req, res) => {
    const id = req.query.id //
    const posts = db.prepare('SELECT * FROM posts ORDER BY id DESC').all();
    res.json(posts)
});

// Создание поста через HTML-форму
app.post('/web/add', (req, res) => {
    const { title, content } = req.body;
    if (title && content) {
        const data = async() => { db.prepare('INSERT INTO posts (title, content) VALUES (?, ?)').run(title, content); }
        await data()
    }

});

// --- REST API (JSON) ---

app.get('/api/posts', (req, res) => {
    const posts = db.prepare('SELECT * FROM posts').all();
    res.json(posts);
});

// --- ЗАПУСК ---
const PORT = 4000;
app.listen(PORT, () => {
    console.log(`
    🚀 Сервер запущен!
    🏠 Главная страница (HTML): http://localhost:${PORT}/
    📊 Список постов (JSON API): http://localhost:${PORT}/api/posts
    `);
});