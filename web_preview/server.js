const http = require('http');
const fs = require('fs');
const path = require('path');

const PORT = 3005;
const PUBLIC_DIR = path.join(__dirname);
const DB_FILE = path.join(__dirname, 'data.json');

const MIME_TYPES = {
  '.html': 'text/html; charset=utf-8',
  '.css': 'text/css; charset=utf-8',
  '.js': 'text/javascript; charset=utf-8',
  '.json': 'application/json; charset=utf-8',
  '.png': 'image/png',
  '.jpg': 'image/jpeg',
  '.svg': 'image/svg+xml'
};

function readDb() {
  try {
    const raw = fs.readFileSync(DB_FILE, 'utf8');
    return JSON.parse(raw);
  } catch (e) {
    return { users: [], orders: [], drivers: [], clients: [], banners: [] };
  }
}

function writeDb(data) {
  try {
    fs.writeFileSync(DB_FILE, JSON.stringify(data, null, 2), 'utf8');
  } catch (e) {
    console.error('Error writing DB:', e);
  }
}

function parseBody(req) {
  return new Promise((resolve) => {
    let body = '';
    req.on('data', chunk => { body += chunk.toString(); });
    req.on('end', () => {
      try {
        resolve(body ? JSON.parse(body) : {});
      } catch (e) {
        resolve({});
      }
    });
  });
}

function sendJson(res, data, status = 200) {
  res.writeHead(status, {
    'Content-Type': 'application/json; charset=utf-8',
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET, POST, PUT, PATCH, DELETE, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type'
  });
  res.end(JSON.stringify(data));
}

const server = http.createServer(async (req, res) => {
  // CORS Preflight
  if (req.method === 'OPTIONS') {
    res.writeHead(204, {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, POST, PUT, PATCH, DELETE, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type'
    });
    return res.end();
  }

  const url = new URL(req.url, `http://localhost:${PORT}`);
  const pathname = url.pathname;

  // ================= REST API ENDPOINTS =================
  if (pathname.startsWith('/api/')) {
    const db = readDb();

    // 0. AUTHENTICATION (STRICT VALIDATION)
    if (pathname === '/api/auth/login' && req.method === 'POST') {
      const body = await parseBody(req);
      const phone = (body.phone || body.phone_or_email || '').trim();
      const password = (body.password || '').trim();

      if (!phone || !password) {
        return sendJson(res, { success: false, message: 'الرجاء إدخال رقم الجوال وكلمة المرور' }, 400);
      }

      const user = (db.users || []).find(u => (u.phone === phone || u.email === phone) && u.password === password);
      if (!user) {
        return sendJson(res, { 
          success: false, 
          message: 'بيانات الدخول غير صحيحة! رقم الجوال أو كلمة المرور غير مسجلة في النظام.' 
        }, 401);
      }

      return sendJson(res, {
        success: true,
        message: 'تم تسجيل الدخول بنجاح',
        user: { id: user.id, name: user.name, phone: user.phone, city: user.city || 'الخرطوم', role: user.role }
      });
    }

    if (pathname === '/api/auth/admin-login' && req.method === 'POST') {
      const body = await parseBody(req);
      const email = (body.email || '').trim().toLowerCase();
      const password = (body.password || '').trim();

      if (!email || !password) {
        return sendJson(res, { success: false, message: 'الرجاء إدخال البريد الإلكتروني وكلمة المرور' }, 400);
      }

      const admin = (db.users || []).find(u => u.role === 'admin' && (u.email && u.email.toLowerCase() === email) && u.password === password);
      if (!admin) {
        return sendJson(res, { 
          success: false, 
          message: 'بيانات المشرف غير صحيحة! البريد الإلكتروني أو كلمة المرور خاطئة أو ليس لديك صلاحية مدير.' 
        }, 401);
      }

      return sendJson(res, {
        success: true,
        message: 'تم تسجيل دخول المشرف بنجاح',
        admin: { id: admin.id, name: admin.name, email: admin.email, role: 'admin' }
      });
    }

    // 1. ORDERS API
    if (pathname === '/api/orders') {
      if (req.method === 'GET') {
        const city = url.searchParams.get('city');
        const phone = url.searchParams.get('phone');
        let filtered = db.orders;
        if (city) filtered = filtered.filter(o => o.city.toLowerCase().includes(city.toLowerCase()));
        if (phone) filtered = filtered.filter(o => o.phone === phone);
        return sendJson(res, { success: true, data: filtered });
      }

      if (req.method === 'POST') {
        const body = await parseBody(req);
        const newOrder = {
          id: 'SUD-' + Math.floor(1000 + Math.random() * 9000),
          client: body.client || 'عميل جديد',
          phone: body.phone || '0912345678',
          city: body.city || 'الخرطوم',
          count: Number(body.count) || 1,
          driver: '-',
          notes: body.notes || 'لا توجد ملاحظات',
          status: 'pending',
          createdAt: new Date().toISOString()
        };
        db.orders.unshift(newOrder);
        writeDb(db);
        return sendJson(res, { success: true, data: newOrder }, 201);
      }
    }

    // UPDATE ORDER
    if (pathname.startsWith('/api/orders/') && (req.method === 'PATCH' || req.method === 'POST')) {
      const id = pathname.replace('/api/orders/', '');
      const body = await parseBody(req);
      const idx = db.orders.findIndex(o => o.id === id);
      if (idx !== -1) {
        db.orders[idx] = { ...db.orders[idx], ...body };
        writeDb(db);
        return sendJson(res, { success: true, data: db.orders[idx] });
      }
      return sendJson(res, { success: false, message: 'Order not found' }, 404);
    }

    // 2. DRIVERS API
    if (pathname === '/api/drivers') {
      if (req.method === 'GET') {
        return sendJson(res, { success: true, data: db.drivers });
      }
      if (req.method === 'POST') {
        const body = await parseBody(req);
        const newDriver = {
          id: Date.now(),
          name: body.name || 'مندوب جديد',
          phone: body.phone || '',
          city: body.city || 'الخرطوم',
          plate: body.plate || 'خ 1234',
          active: false,
          createdAt: new Date().toISOString()
        };
        db.drivers.unshift(newDriver);
        
        // Also register in users table
        if (!db.users) db.users = [];
        db.users.push({
          id: newDriver.id,
          name: newDriver.name,
          phone: newDriver.phone,
          password: body.password || '123456',
          city: newDriver.city,
          role: 'driver'
        });

        writeDb(db);
        return sendJson(res, { success: true, data: newDriver }, 201);
      }
    }

    // TOGGLE / UPDATE DRIVER
    if (pathname.startsWith('/api/drivers/') && (req.method === 'PATCH' || req.method === 'POST')) {
      const id = Number(pathname.replace('/api/drivers/', ''));
      const body = await parseBody(req);
      const idx = db.drivers.findIndex(d => d.id === id);
      if (idx !== -1) {
        db.drivers[idx] = { ...db.drivers[idx], ...body };
        writeDb(db);
        return sendJson(res, { success: true, data: db.drivers[idx] });
      }
      return sendJson(res, { success: false, message: 'Driver not found' }, 404);
    }

    // DELETE DRIVER
    if (pathname.startsWith('/api/drivers/') && req.method === 'DELETE') {
      const id = Number(pathname.replace('/api/drivers/', ''));
      db.drivers = db.drivers.filter(d => d.id !== id);
      if (db.users) db.users = db.users.filter(u => u.id !== id);
      writeDb(db);
      return sendJson(res, { success: true });
    }

    // 3. CLIENTS API
    if (pathname === '/api/clients') {
      if (req.method === 'GET') {
        return sendJson(res, { success: true, data: db.clients });
      }
      if (req.method === 'POST') {
        const body = await parseBody(req);
        const newClient = {
          id: Date.now(),
          name: body.name || 'عميل جديد',
          phone: body.phone || '',
          city: body.city || 'الخرطوم',
          active: true,
          createdAt: new Date().toISOString()
        };
        db.clients.unshift(newClient);

        // Also register in users table
        if (!db.users) db.users = [];
        db.users.push({
          id: newClient.id,
          name: newClient.name,
          phone: newClient.phone,
          password: body.password || '123456',
          city: newClient.city,
          role: 'client'
        });

        writeDb(db);
        return sendJson(res, { success: true, data: newClient }, 201);
      }
    }

    if (pathname.startsWith('/api/clients/') && req.method === 'DELETE') {
      const id = Number(pathname.replace('/api/clients/', ''));
      db.clients = db.clients.filter(c => c.id !== id);
      if (db.users) db.users = db.users.filter(u => u.id !== id);
      writeDb(db);
      return sendJson(res, { success: true });
    }

    // 4. BANNERS API
    if (pathname === '/api/banners') {
      if (req.method === 'GET') {
        return sendJson(res, { success: true, data: db.banners });
      }
      if (req.method === 'POST') {
        const body = await parseBody(req);
        const newBanner = {
          id: Date.now(),
          title: body.title || 'عرض جديد',
          subtitle: body.subtitle || '',
          badge: body.badge || 'SUDAPOST ⭐',
          img: body.img || 'images/banner1.jpg',
          btn: body.btn || 'اطلب شحن الآن'
        };
        db.banners.unshift(newBanner);
        writeDb(db);
        return sendJson(res, { success: true, data: newBanner }, 201);
      }
    }

    if (pathname.startsWith('/api/banners/') && req.method === 'DELETE') {
      const id = Number(pathname.replace('/api/banners/', ''));
      db.banners = db.banners.filter(b => b.id !== id);
      writeDb(db);
      return sendJson(res, { success: true });
    }

    return sendJson(res, { error: 'Not Found' }, 404);
  }

  // ================= STATIC FILES SERVER =================
  let reqPath = pathname;
  if (reqPath === '/') reqPath = '/index.html';

  const filePath = path.join(PUBLIC_DIR, reqPath);
  const ext = path.extname(filePath).toLowerCase();
  const contentType = MIME_TYPES[ext] || 'application/octet-stream';

  fs.readFile(filePath, (err, content) => {
    if (err) {
      if (err.code === 'ENOENT') {
        res.writeHead(404, { 'Content-Type': 'text/plain; charset=utf-8' });
        res.end('404 Not Found');
      } else {
        res.writeHead(500);
        res.end('Server Error: ' + err.code);
      }
    } else {
      res.writeHead(200, { 'Content-Type': contentType });
      res.end(content);
    }
  });
});

server.listen(PORT, '0.0.0.0', () => {
  console.log(`Live Real-time Server running at http://0.0.0.0:${PORT}/`);
});
