// The version-pinned Kuma Socket.IO API is used only on loopback.
const { io } = require('/app/node_modules/socket.io-client');
const fs = require('fs');
const config = JSON.parse(fs.readFileSync(0, 'utf8'));
const socket = io('http://127.0.0.1:13001', { transports: ['websocket'], reconnection: false });
const timeout = setTimeout(() => { console.error('Kuma configuration timed out'); process.exit(1); }, 60000);
let monitors = {};
socket.on('monitorList', value => { monitors = value; });
function call(event, ...args) {
    return new Promise((resolve, reject) => socket.timeout(15000).emit(event, ...args, (error, result) => {
        if (error) reject(error); else resolve(result);
    }));
}
function checked(result) {
    if (!result.ok) throw new Error(result.msg || 'Kuma API request failed');
    return result;
}
socket.on('connect', async () => {
    try {
        let changed = false;
        const setup = await call('setup', 'admin', config.password);
        if (setup.ok) changed = true;
        checked(await call('login', { username: 'admin', password: config.password }));
        const ids = [];
        for (const desired of config.monitors) {
            const existing = Object.values(monitors).find(m => m.name === desired.name);
            if (existing) { ids.push(existing.id); continue; }
            const result = checked(await call('add', {
                type: 'http', name: desired.name, url: desired.url,
                method: 'GET', interval: 60, retryInterval: 60, maxretries: 2,
                timeout: 15, active: 1, accepted_statuscodes: ['200-299'],
                notificationIDList: {}, ignoreTls: false, upsideDown: false,
                maxredirects: 5, conditions: [], expiryNotification: false,
            }));
            ids.push(result.monitorID);
            changed = true;
        }
        let status = await call('getStatusPage', 'portfolio');
        if (!status.ok) {
            checked(await call('addStatusPage', 'Mikrus DevOps / Service status', 'portfolio'));
            status = checked(await call('getStatusPage', 'portfolio'));
            checked(await call('saveStatusPage', 'portfolio', {
                ...status.config, slug: 'portfolio', title: 'Mikrus DevOps / Service status',
                description: 'Automated monitoring on a 2 GB VPS. Checks run every 60 seconds.',
                theme: 'dark', published: true, showTags: false,
                showPoweredBy: true, analyticsType: null, domainNameList: [],
                footerText: 'Provisioned with Ansible', customCSS: '',
            }, '', [{name: 'Platform services', weight: 1, monitorList: ids.map(id => ({id}))}]));
            changed = true;
        }
        console.log(JSON.stringify({changed, monitors: ids.length}));
        clearTimeout(timeout); socket.disconnect();
    } catch (error) { console.error(error.message); process.exit(1); }
});
socket.on('connect_error', error => { console.error(error.message); process.exit(1); });
