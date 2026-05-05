import * as PIXI from 'pixi.js'

(async () => {
    const app = new PIXI.Application();

    await app.init({ 
        background: '#050505', 
        resizeTo: window,
        antialias: true 
    });
    document.body.appendChild(app.canvas);

    const world = new PIXI.Container();
    const ui = new PIXI.Container();
    app.stage.addChild(world, ui);

    // --- СОСТОЯНИЕ ИГРЫ ---
    let isGameOver = false;
    let score = 0;
    let lastShotTime = 0;
    const shootInterval = 200;
    const enemies = [];
    const bullets = [];
    const keys = {};

    window.addEventListener('keydown', e => keys[e.code] = true);
    window.addEventListener('keyup', e => keys[e.code] = false);
    
    let isMouseDown = false;
    window.addEventListener('mousedown', () => isMouseDown = true);
    window.addEventListener('mouseup', () => isMouseDown = false);

    // --- ОБЪЕКТЫ ---

    const player = new PIXI.Graphics()
        .circle(0, 0, 15)
        .fill(0x00ffcc)
        .stroke({ width: 2, color: 0xffffff });
    
    player.x = app.screen.width / 2;
    player.y = app.screen.height / 2;
    player.speed = 4;
    world.addChild(player);

    const scoreText = new PIXI.Text({
        text: 'Kills: 0',
        style: { fill: '#ffffff', fontSize: 24, fontFamily: 'Arial' }
    });
    scoreText.x = 20; scoreText.y = 20;
    ui.addChild(scoreText);

    // Экран смерти (по умолчанию скрыт)
    const gameOverContainer = new PIXI.Container();
    const overlay = new PIXI.Graphics()
        .rect(0, 0, app.screen.width, app.screen.height)
        .fill({ color: 0x000000, alpha: 0.7 });
    
    const deadText = new PIXI.Text({
        text: 'ВЫ ПОГИБЛИ\nНажмите F5 для рестарта',
        style: { fill: '#ff0000', fontSize: 48, fontWeight: 'bold', align: 'center' }
    });
    deadText.anchor.set(0.5);
    deadText.x = app.screen.width / 2;
    deadText.y = app.screen.height / 2;

    gameOverContainer.addChild(overlay, deadText);
    gameOverContainer.visible = false;
    ui.addChild(gameOverContainer);

    // --- ЛОГИКА ---

    function spawnEnemy() {
        if (isGameOver) return;
        const enemy = new PIXI.Graphics().poly([-12, 12, 12, 12, 0, -18]).fill(0xff4444);
        const angle = Math.random() * Math.PI * 2;
        enemy.x = player.x + Math.cos(angle) * 800;
        enemy.y = player.y + Math.sin(angle) * 800;
        world.addChild(enemy);
        enemies.push(enemy);
    }

    function shoot(targetX, targetY) {
        const bullet = new PIXI.Graphics().circle(0, 0, 5).fill(0xffff00);
        bullet.x = player.x;
        bullet.y = player.y;
        
        const dx = targetX - world.x - player.x;
        const dy = targetY - world.y - player.y;
        const angle = Math.atan2(dy, dx);
        
        bullet.vx = Math.cos(angle) * 15;
        bullet.vy = Math.sin(angle) * 15;
        
        world.addChild(bullet);
        bullets.push(bullet);
    }

    setInterval(spawnEnemy, 800);

    // --- ГЛАВНЫЙ ЦИКЛ ---
    app.ticker.add((ticker) => {
        if (isGameOver) return; // Останавливаем всё, если проиграли

        const dt = ticker.deltaTime;
        const now = Date.now();

        // 1. Движение игрока
        let vx = 0; let vy = 0;
        if (keys['KeyW']) vy -= 1;
        if (keys['KeyS']) vy += 1;
        if (keys['KeyA']) vx -= 1;
        if (keys['KeyD']) vx += 1;

        if (vx !== 0 || vy !== 0) {
            const length = Math.sqrt(vx * vx + vy * vy);
            player.x += (vx / length) * player.speed * dt;
            player.y += (vy / length) * player.speed * dt;
        }

        // 2. Стрельба
        if (isMouseDown && now - lastShotTime > shootInterval) {
            const mousePos = app.renderer.events.pointer;
            shoot(mousePos.x, mousePos.y);
            lastShotTime = now;
        }

        // 3. Камера
        world.x = app.screen.width / 2 - player.x;
        world.y = app.screen.height / 2 - player.y;

        // 4. Пули и коллизии с врагами
        for (let i = bullets.length - 1; i >= 0; i--) {
            const b = bullets[i];
            b.x += b.vx * dt;
            b.y += b.vy * dt;

            for (let j = enemies.length - 1; j >= 0; j--) {
                const en = enemies[j];
                if (Math.hypot(en.x - b.x, en.y - b.y) < 25) {
                    world.removeChild(en, b);
                    enemies.splice(j, 1);
                    bullets.splice(i, 1);
                    score++;
                    scoreText.text = `Kills: ${score}`;
                    break;
                }
            }
        }

        // 5. Враги: движение и проверка смерти игрока
        enemies.forEach(en => {
            const angle = Math.atan2(player.y - en.y, player.x - en.x);
            en.x += Math.cos(angle) * 2 * dt;
            en.y += Math.sin(angle) * 2 * dt;
            en.rotation = angle + Math.PI / 2;

            // ПРОВЕРКА СМЕРТИ: если враг коснулся игрока
            const distToPlayer = Math.hypot(en.x - player.x, en.y - player.y);
            if (distToPlayer < 25) {
                isGameOver = true;
                gameOverContainer.visible = true;
            }
        });
    });
})();
