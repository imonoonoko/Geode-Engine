// Mineflayer Bot for Geode-Engine AI
// ヘッドレス・バックグラウンド動作対応

const mineflayer = require('mineflayer');
const { pathfinder, Movements, goals } = require('mineflayer-pathfinder');
const mineflayerViewer = require('prismarine-viewer').mineflayer; // Phase 15.6: Geode Vision

// HTTP API Server for Python communication
const http = require('http');

let bot = null;
let currentState = {
    connected: false,
    position: { x: 0, y: 64, z: 0 },
    health: 20,
    food: 20,
    inventory: [],
    nearbyEntities: [],
    lastAction: null,
    reward: 0
};

// Command queue from Python
let commandQueue = [];

function createBot(options) {
    const defaultOptions = {
        host: 'localhost',
        port: 25565,
        username: 'GeodeAI',
        version: '1.20.4'
    };

    const config = { ...defaultOptions, ...options };

    console.log(`🤖 Creating bot: ${config.username}@${config.host}:${config.port}`);

    if (bot) {
        bot.end();
        bot = null;
    }

    bot = mineflayer.createBot(config);
    bot.loadPlugin(pathfinder);

    bot.on('login', () => {
        console.log('✅ Bot logged in');
        currentState.connected = true;
    });

    bot.on('spawn', () => {
        console.log('✅ Bot spawned in world!');
        currentState.connected = true;
        updateState();

        // Phase 15.6: Geode Vision (WebViewer)
        try {
            mineflayerViewer(bot, { port: 3007, firstPerson: true });
            console.log('👀 Geode Vision Online! Open http://localhost:3007 to see what Geode sees.');
        } catch (err) {
            // Already running or port busy is common
            console.log(`⚠️ Viewer log: ${err.message}`);
        }
    });

    // Phase 11.3: Learning Feedbacks
    bot.on('health', () => {
        if (bot.health < currentState.health) {
            // Damage taken
            currentState.events.push({ type: 'damage', amount: currentState.health - bot.health });
        }
        currentState.health = bot.health;
        currentState.food = bot.food;
    });

    bot.on('entityDead', (entity) => {
        // 自分が直近で敵対していた、かつ近くのMobなら「倒した」と推定
        // 簡易実装: 半径5m以内の敵性Mobが死んだら WIN とみなす
        if (entity.type === 'mob' && bot.entity && entity.position.distanceTo(bot.entity.position) < 5.0) {
            currentState.events.push({ type: 'kill', mob: entity.name });
        }
    });

    bot.on('move', () => {
        updateState();
    });

    bot.on('error', (err) => {
        console.error('❌ Bot error:', err);
        currentState.events.push({ type: 'error', message: err.message });
    });

    bot.on('kicked', (reason) => {
        console.log('⚠️ Bot kicked:', reason);
        currentState.connected = false;
        currentState.events.push({ type: 'kicked', reason: reason });
    });

    bot.on('end', () => {
        console.log('🔌 Bot disconnected');
        currentState.connected = false;
        currentState.events.push({ type: 'disconnected' });
    });

    return bot;
}

function updateState() {
    if (!bot || !bot.entity) return;

    currentState.position = {
        x: bot.entity.position.x,
        y: bot.entity.position.y,
        z: bot.entity.position.z,
        yaw: bot.entity.yaw,
        pitch: bot.entity.pitch
    };

    // Update nearby entities
    currentState.nearbyEntities = Object.values(bot.entities)
        .filter(e => e.type === 'mob' || e.type === 'player')
        .slice(0, 10)
        .map(e => ({
            type: e.type,
            name: e.name,
            position: e.position
        }));

    // Phase 10.1: Raycasting (Vision)
    // 視線の先にあるブロックを取得 (最大5ブロック)
    const cursorBlock = bot.blockAtCursor(5);
    currentState.cursor = cursorBlock ? {
        name: cursorBlock.name,
        type: cursorBlock.type,
        position: cursorBlock.position,
        displayName: cursorBlock.displayName
    } : null;

    if (cursorBlock && Math.random() < 0.05) {
        console.log(`[Vision] Looking at: ${cursorBlock.name} (${cursorBlock.position})`);
    }

    // Phase 10.2: Peripheral Vision (周辺視野)
    // 半径5ブロック以内の「興味深いブロック」をスキャン
    // (空気、石、土などを除外して軽量化)
    const nearbyBlocks = bot.findBlocks({
        matching: (block) => {
            return block &&
                block.name !== 'air' &&
                block.name !== 'stone' &&
                block.name !== 'dirt' &&
                block.name !== 'grass_block' &&
                block.name !== 'water' &&
                block.type !== 0; // 0 is air
        },
        maxDistance: 5,
        count: 10 // 最大10個まで
    });

    // 座標情報だけ送る（名前はPython側で解決するか、ここで名前解決するか）
    // bot.findBlocksは座標(Vec3)の配列を返す
    currentState.nearby = nearbyBlocks.map(pos => {
        const b = bot.blockAt(pos);
        return {
            name: b.name,
            position: pos
        };
    });

    // Status flags
    currentState.isDigging = !!bot.targetDigBlock;
    currentState.isPlacing = !!currentState.isPlacing; // Persist or reset handled in executeAction

    // Phase 11.3: Perception (Mobs)
    // 一番近いMobを探す (半径15以内)
    const mobFilter = e => e.type === 'mob' && e.position.distanceTo(bot.entity.position) < 15;
    const nearestMob = bot.nearestEntity(mobFilter);
    if (nearestMob) {
        currentState.nearestMob = {
            id: nearestMob.id,
            name: nearestMob.name, // e.g. "zombie"
            position: nearestMob.position,
            distance: nearestMob.position.distanceTo(bot.entity.position),
            isEnemy: ['zombie', 'skeleton', 'spider', 'creeper', 'enderman'].includes(nearestMob.name)
        };
    } else {
        currentState.nearestMob = null;
    }
}

function executeAction(action) {
    if (!bot) return { success: false, error: 'Bot not ready' };

    currentState.lastAction = action;
    currentState.isPlacing = false; // Reset placing flag (simplified)

    try {
        switch (action.type) {
            case 'MOVE_FORWARD':
                bot.setControlState('forward', true);
                if (bot.entity.isCollidedHorizontally && bot.entity.onGround) {
                    bot.setControlState('jump', true);
                }
                setTimeout(() => {
                    bot.setControlState('forward', false);
                    bot.setControlState('jump', false);
                }, action.duration || 500);
                break;
            case 'MOVE_BACK':
                bot.setControlState('back', true);
                setTimeout(() => bot.setControlState('back', false), action.duration || 500);
                break;
            case 'TURN_LEFT':
                bot.look(bot.entity.yaw + 0.5, bot.entity.pitch);
                break;
            case 'TURN_RIGHT':
                bot.look(bot.entity.yaw - 0.5, bot.entity.pitch);
                break;
            case 'JUMP':
                bot.setControlState('jump', true);
                setTimeout(() => bot.setControlState('jump', false), 100);
                break;
            case 'ATTACK':
                const nearestMob = bot.nearestEntity(e => e.type === 'mob');
                if (nearestMob) bot.attack(nearestMob);
                break;
            case 'DIG':
                // Phase 11.1: Digging
                // 非同期で実行し、Stateで進行状況を監視する
                const target = bot.blockAtCursor(5);
                if (target && target.name !== 'air' && target.name !== 'bedrock') {
                    bot.dig(target).catch(err => {
                        console.log(`[DigError] ${err.message}`);
                    });
                    return { success: true, status: 'started_digging', target: target.name };
                }
                return { success: false, error: 'No target to dig' };
            case 'PLACE':
                // Phase 11.2: Placing
                const placeTarget = bot.blockAtCursor(5);
                if (placeTarget && placeTarget.name !== 'air') {
                    // 持っているアイテムがあるか確認 (簡易実装: 手持ちを使用)
                    // TODO: インベントリからブロックを探して装備するロジック
                    const heldItem = bot.inventory.slots[bot.getEquipmentDestSlot('hand')];
                    if (!heldItem) {
                        return { success: false, error: 'No item in hand' };
                    }

                    // 上面(0,1,0)に置く
                    bot.placeBlock(placeTarget, new Vec3(0, 1, 0)).catch(err => {
                        console.log(`[PlaceError] ${err.message}`);
                    });
                    return { success: true, status: 'placed_block', target: placeTarget.name };
                }
                return { success: false, error: 'No target to place on' };
            case 'STOP':
                bot.stopDigging(); // 掘削キャンセル
                ['forward', 'back', 'left', 'right', 'jump', 'sprint'].forEach(
                    ctrl => bot.setControlState(ctrl, false)
                );
                break;
            default:
                return { success: false, error: 'Unknown action' };
        }
        return { success: true };
    } catch (err) {
        return { success: false, error: err.message };
    }
}

// HTTP API Server
const server = http.createServer((req, res) => {
    res.setHeader('Content-Type', 'application/json');
    res.setHeader('Access-Control-Allow-Origin', '*');

    let body = '';
    req.on('data', chunk => body += chunk);
    req.on('end', () => {
        const url = req.url;

        if (url === '/state') {
            // GET state
            // Phase 11.3: Drain events
            const responsePayload = { ...currentState };
            // Deep copy items if needed, but array of simple objects is fine

            // Clear events safely
            responsePayload.events = [...(currentState.events || [])];
            currentState.events = [];

            res.end(JSON.stringify(responsePayload));
        } else if (url === '/action' && req.method === 'POST') {
            // POST action
            try {
                const action = JSON.parse(body);
                const result = executeAction(action);
                res.end(JSON.stringify(result));
            } catch (e) {
                res.end(JSON.stringify({ success: false, error: e.message }));
            }
        } else if (url === '/connect' && req.method === 'POST') {
            // POST connect
            try {
                const options = JSON.parse(body);
                createBot(options);
                res.end(JSON.stringify({ success: true }));
            } catch (e) {
                res.end(JSON.stringify({ success: false, error: e.message }));
            }
        } else if (url === '/disconnect') {
            if (bot) {
                bot.quit();
                bot = null;
            }
            res.end(JSON.stringify({ success: true }));
        } else {
            res.end(JSON.stringify({ error: 'Unknown endpoint' }));
        }
    });
});

const PORT = process.env.BOT_PORT || 3001;
server.listen(PORT, () => {
    console.log(`🚀 Mineflayer API Server running on http://localhost:${PORT}`);
    console.log('   Endpoints:');
    console.log('   - GET  /state     : Get current bot state');
    console.log('   - POST /action    : Execute action');
    console.log('   - POST /connect   : Connect to server');
    console.log('   - GET  /disconnect: Disconnect bot');
});

// Auto-connect if environment variable is set
if (process.env.MC_HOST) {
    createBot({
        host: process.env.MC_HOST,
        port: process.env.MC_PORT || 25565,
        username: process.env.MC_USERNAME || 'GeodeAI'
    });
}
