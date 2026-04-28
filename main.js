import express from 'express';
import http from 'http';
import { Server } from 'socket.io';

const app = express();
const server = http.createServer(app);
const io = new Server(server);

app.use(express.static('public'));

let players = {}; 
let score = { left: 0, right: 0 };
let ball = { x: 300, y: 200, dx: 4, dy: 4, color: '#fff', size: 10 };
let powerUp = { x: 300, y: 200, active: true };

function resetBall() {
    ball = {
        x: 300, y: 200,
        dx: (Math.random() > 0.5 ? 5 : -5),
        dy: (Math.random() * 6 - 3),
        color: '#fff',
        size: 10
    };
}
// Выше функция resetBall, ниже io.on('connection')
setInterval(() => {
    // 1. Движение мяча
    ball.x += ball.dx;
    ball.y += ball.dy;

    // 2. Отскок от стен
    if (ball.y <= 0 || ball.y >= 400) ball.dy *= -1;

    // Продолжаем писать в setInterval 
    // 3. Столкновение с ракетками
    Object.values(players).forEach(p => {
        const isLeft = p.side === 'left' && ball.x < 30 && ball.x > 10;
        const isRight = p.side === 'right' && ball.x > 570 && ball.x < 590;
        
        if ((isLeft || isRight) && ball.y > p.y && ball.y < p.y + 80) {
            ball.dx *= -1.1; // Ускорение
            ball.color = p.color; // Красим мяч
            ball.size = 25; // Раздуваем мяч
        }
    });

    // Продолжаем писать в setInterval 
    // Плавное уменьшение мяча до нормы
    if (ball.size > 10) ball.size -= 0.5;

    // 4. Проверка бонуса (Золотой пиксель)
    if (powerUp.active && Math.abs(ball.x - powerUp.x) < 20 && Math.abs(ball.y - powerUp.y) < 20) {
        ball.size = 60; // Мяч становится гигантским
        powerUp.active = false;
        setTimeout(() => {
            powerUp.x = Math.random() * 400 + 100;
            powerUp.y = Math.random() * 300 + 50;
            powerUp.active = true;
        }, 7000);
    }

    // Продолжаем писать в setInterval 
    // 5. Голы
    if (ball.x < 0) { score.right++; resetBall(); }
    else if (ball.x > 600) { score.left++; resetBall(); }

    io.emit('state', { players, ball, score, powerUp });
}, 1000 / 60);

io.on('connection', (socket) => {
    let side = 'left'; // По умолчанию хотим зайти за левых
    // Проверяем: есть ли уже кто-то, у кого side равен 'left'?
    const leftIsTaken = Object.values(players).find(p => p.side === 'left');
    if (leftIsTaken) {
        side = 'right'; // Если лево занято, прыгаем в правую команду
    }

    // Продолжаем в том же io.on('connection', (socket) => {})
    players[socket.id] = { 
        side, 
        y: 160, 
        color: `hsl(${Math.random() * 360}, 80%, 60%)` 
    };

    socket.on('move', (y) => {
        if (players[socket.id]) players[socket.id].y = y;
    });

    socket.on('disconnect', () => delete players[socket.id]);
});

server.listen(3000, () => console.log('Server fly on http://localhost:3000'));
