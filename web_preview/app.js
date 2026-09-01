// Application State
let appData = {
  currentRole: 'client',
  currentUser: {
    name: 'خالد',
    phone: '0551234567',
    city: 'الرياض'
  },
  currentDriver: {
    name: 'أحمد السائق',
    phone: '0509876543',
    city: 'الرياض'
  },
  packageCount: 1,
  hasPhoto: false,
  currentSlideIndex: 0,
  autoSlideTimer: null,
  
  // البانرات الترويجية الحية
  banners: [
    {
      id: 1,
      title: 'شحنك يصل إليك',
      subtitle: 'بسرعة • أمان • موثوقية',
      badgeText: 'الأكثر طلباً ⭐',
      imageUrl: 'https://images.unsplash.com/photo-1586528116311-ad8dd3c8310d?w=800',
      buttonText: 'اطلب شحن الآن'
    },
    {
      id: 2,
      title: 'خصم 20% على الشحن السريع',
      subtitle: 'شحن آمن وفوري بين جميع المدن',
      badgeText: 'عرض محدود 🔥',
      imageUrl: 'https://images.unsplash.com/photo-1519003722824-194d4455a60c?w=800',
      buttonText: 'احصل على العرض'
    },
    {
      id: 3,
      title: 'خدمة التوصيل في نفس اليوم',
      subtitle: 'كباتن معتمدون بالقرب منك على مدار الساعة',
      badgeText: 'خدمة VIP ⚡',
      imageUrl: 'https://images.unsplash.com/photo-1601584115197-04ecc0da31d7?w=800',
      buttonText: 'شحن فوري وسريع'
    }
  ],

  orders: [
    {
      id: 'ORD-9821',
      clientName: 'خالد',
      clientPhone: '0551234567',
      city: 'الرياض',
      packageCount: 3,
      notes: 'الرجاء التعامل بحذر، توجد قطع قابلة للكسر',
      status: 'pending',
      driverName: null,
      driverPhone: null,
      failureReason: null,
      time: 'قبل 15 دقيقة'
    },
    {
      id: 'ORD-8714',
      clientName: 'سارة العتيبي',
      clientPhone: '0542233445',
      city: 'الرياض',
      packageCount: 1,
      notes: 'التسليم عند البوابة الرئيسية',
      status: 'accepted',
      driverName: 'أحمد السائق',
      driverPhone: '0509876543',
      failureReason: null,
      time: 'قبل ساعة'
    }
  ]
};

// Initialize
document.addEventListener('DOMContentLoaded', () => {
  renderCarousel();
  renderOrders();
  renderDriverOrders();
  renderAdmin();
  updateTime();
  setInterval(updateTime, 60000);
  startAutoSlide();
});

function updateTime() {
  const now = new Date();
  const hours = now.getHours().toString().padStart(2, '0');
  const minutes = now.getMinutes().toString().padStart(2, '0');
  const el = document.getElementById('liveTime');
  if (el) el.innerText = `${hours}:${minutes}`;
}

// ================= Carousel / Slider Functions =================
function renderCarousel() {
  const track = document.getElementById('carouselTrack');
  const dotsContainer = document.getElementById('carouselDots');
  if (!track || !dotsContainer) return;

  if (appData.banners.length === 0) {
    track.innerHTML = '<div style="padding:40px; text-align:center;">لا توجد بانرات</div>';
    dotsContainer.innerHTML = '';
    return;
  }

  // Generate Slides
  track.innerHTML = appData.banners.map((b, idx) => `
    <div class="carousel-slide" style="background-image: url('${b.imageUrl}')">
      <div class="slide-overlay"></div>
      
      <div class="slide-content-top">
        <span class="slide-badge">${b.badgeText || 'عرض خاص'}</span>
        <h2 class="slide-title">${b.title}</h2>
        <p class="slide-subtitle">${b.subtitle}</p>
      </div>

      <div class="slide-content-bottom">
        <button class="glowing-red-cta" onclick="openCreateOrderModal()">
          <span>${b.buttonText || 'اطلب شحن الآن'}</span>
          <div class="arrow-circle">
            <i data-lucide="arrow-left" class="w-4 h-4"></i>
          </div>
        </button>
      </div>
    </div>
  `).join('');

  // Generate Dots
  dotsContainer.innerHTML = appData.banners.map((_, idx) => `
    <div class="dot ${idx === appData.currentSlideIndex ? 'active' : ''}" onclick="goToSlide(${idx})"></div>
  `).join('');

  updateCarouselPosition();
  lucide.createIcons();
}

function updateCarouselPosition() {
  const track = document.getElementById('carouselTrack');
  if (track) {
    track.style.transform = `translateX(${appData.currentSlideIndex * 100}%)`;
  }
  document.querySelectorAll('.carousel-dots .dot').forEach((dot, idx) => {
    dot.classList.toggle('active', idx === appData.currentSlideIndex);
  });
}

function nextSlide() {
  if (appData.banners.length === 0) return;
  appData.currentSlideIndex = (appData.currentSlideIndex + 1) % appData.banners.length;
  updateCarouselPosition();
}

function prevSlide() {
  if (appData.banners.length === 0) return;
  appData.currentSlideIndex = (appData.currentSlideIndex - 1 + appData.banners.length) % appData.banners.length;
  updateCarouselPosition();
}

function goToSlide(idx) {
  appData.currentSlideIndex = idx;
  updateCarouselPosition();
}

function startAutoSlide() {
  clearInterval(appData.autoSlideTimer);
  appData.autoSlideTimer = setInterval(() => {
    nextSlide();
  }, 4500);
}

// ================= Tab Navigation =================
function switchToTab(tabId) {
  document.querySelectorAll('.view').forEach(v => v.classList.remove('active'));
  document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));

  if (tabId === 'home') {
    document.getElementById('homeView').classList.add('active');
    document.getElementById('navHome').classList.add('active');
    renderCarousel();
  } else if (tabId === 'orders') {
    document.getElementById('ordersView').classList.add('active');
    document.getElementById('navOrders').classList.add('active');
    renderOrders();
  } else if (tabId === 'driver') {
    document.getElementById('driverView').classList.add('active');
    document.getElementById('navDriver').classList.add('active');
    renderDriverOrders();
  } else if (tabId === 'admin') {
    document.getElementById('adminView').classList.add('active');
    document.getElementById('navAdmin').classList.add('active');
    renderAdmin();
  }
}

// Role Switcher
function toggleRoleModal() {
  document.getElementById('roleModal').classList.toggle('active');
}

function selectRole(role) {
  appData.currentRole = role;
  const roleNames = { client: 'العميل', driver: 'السائق', admin: 'لوحة الإدارة' };
  document.getElementById('currentRoleText').innerText = roleNames[role];
  toggleRoleModal();

  if (role === 'driver') switchToTab('driver');
  else if (role === 'admin') switchToTab('admin');
  else switchToTab('home');
}

// Banner Modal in Admin
function openAddBannerModal() {
  document.getElementById('addBannerModal').classList.add('active');
}

function closeAddBannerModal() {
  document.getElementById('addBannerModal').classList.remove('active');
}

function saveNewBanner() {
  const title = document.getElementById('newBannerTitle').value.trim();
  const sub = document.getElementById('newBannerSub').value.trim();
  const badge = document.getElementById('newBannerBadge').value.trim() || 'عرض خاص';
  const img = document.getElementById('newBannerImg').value.trim();
  const btn = document.getElementById('newBannerBtn').value.trim() || 'اطلب شحن الآن';

  if (!title || !img) {
    alert('الرجاء إدخال عنوان البانر ورابط الصورة');
    return;
  }

  const newBanner = {
    id: Date.now(),
    title: title,
    subtitle: sub,
    badgeText: badge,
    imageUrl: img,
    buttonText: btn
  };

  appData.banners.unshift(newBanner);
  appData.currentSlideIndex = 0;
  closeAddBannerModal();
  renderCarousel();
  renderAdmin();

  alert('تمت إضافة البانر بنجاح ونشره فورياً في الواجهة الرئيسية! 🎉');
}

function deleteBanner(bannerId) {
  if (confirm('هل أنت متأكد من حذف هذا البانر من التطبيق؟')) {
    appData.banners = appData.banners.filter(b => b.id !== bannerId);
    appData.currentSlideIndex = 0;
    renderCarousel();
    renderAdmin();
  }
}

// Create Order Modal
function openCreateOrderModal() {
  document.getElementById('orderModal').classList.add('active');
}

function closeCreateOrderModal() {
  document.getElementById('orderModal').classList.remove('active');
}

function changePackageCount(delta) {
  appData.packageCount = Math.max(1, appData.packageCount + delta);
  document.getElementById('packageCountVal').innerText = appData.packageCount;
}

function toggleMockPhoto() {
  appData.hasPhoto = !appData.hasPhoto;
  const box = document.getElementById('cameraBox');
  const text = document.getElementById('camText');
  if (appData.hasPhoto) {
    box.classList.add('uploaded');
    text.innerText = 'تم التقاط صورة الشحنة بنجاح 📷 (اضغط للتغيير)';
  } else {
    box.classList.remove('uploaded');
    text.innerText = 'اضغط هنا لتصوير الشحنة بالكاميرا 📷';
  }
}

function submitNewOrder() {
  const phone = document.getElementById('orderPhone').value.trim();
  const city = document.getElementById('orderCity').value;
  const notes = document.getElementById('orderNotes').value.trim() || 'لا توجد ملاحظات إضافية';

  if (!phone) {
    alert('الرجاء إدخال رقم جوال العميل');
    return;
  }

  const newOrder = {
    id: 'ORD-' + Math.floor(1000 + Math.random() * 9000),
    clientName: appData.currentUser.name,
    clientPhone: phone,
    city: city,
    packageCount: appData.packageCount,
    notes: notes,
    status: 'pending',
    driverName: null,
    driverPhone: null,
    failureReason: null,
    time: 'الآن'
  };

  appData.orders.unshift(newOrder);
  closeCreateOrderModal();

  appData.packageCount = 1;
  appData.hasPhoto = false;
  document.getElementById('packageCountVal').innerText = '1';
  document.getElementById('cameraBox').classList.remove('uploaded');
  document.getElementById('camText').innerText = 'اضغط هنا لتصوير الشحنة بالكاميرا 📷';
  document.getElementById('orderNotes').value = '';

  alert('تم إرسال طلب الشحن بنجاح! تم توجيهه فورياً إلى كباتن مدينة ' + city);
  switchToTab('orders');
}

function getStatusBadge(status) {
  switch(status) {
    case 'pending': return '<span class="status-badge pending">بانتظار سائق</span>';
    case 'accepted': return '<span class="status-badge accepted">تم القبول - السائق بالطريق</span>';
    case 'loaded': return '<span class="status-badge loaded">تم التحميل بنجاح ✅</span>';
    case 'failed': return '<span class="status-badge failed">تعذر الشحن ❌</span>';
    default: return '';
  }
}

function renderOrders() {
  const container = document.getElementById('clientOrdersContainer');
  const clientOrders = appData.orders.filter(o => o.clientPhone === appData.currentUser.phone);

  if (clientOrders.length === 0) {
    container.innerHTML = '<p style="text-align:center; color:var(--text-muted); padding:30px;">لا توجد شحنات حالية</p>';
    return;
  }

  container.innerHTML = clientOrders.map(order => `
    <div class="order-card">
      <div class="order-top">
        <span class="order-id">طلب #${order.id}</span>
        ${getStatusBadge(order.status)}
      </div>
      <div class="order-details-row">
        <span>المدينة: <strong>${order.city}</strong></span>
        <span>عدد القطع: <strong>${order.packageCount} قطعة</strong></span>
      </div>
      <div class="order-details-row">
        <span>الملاحظات: ${order.notes}</span>
        <span>${order.time}</span>
      </div>
      ${order.driverName ? `
        <div class="order-driver-box">
          <i data-lucide="truck" class="w-4 h-4"></i>
          <span>الكابتن: ${order.driverName} (${order.driverPhone})</span>
        </div>
      ` : ''}
      ${order.failureReason ? `
        <div class="order-fail-box">
          <span>سبب تعذر الشحن: ${order.failureReason}</span>
        </div>
      ` : ''}
    </div>
  `).join('');

  lucide.createIcons();
}

function renderDriverOrders() {
  const container = document.getElementById('driverOrdersContainer');
  const cityOrders = appData.orders.filter(o => o.city === appData.currentDriver.city);

  if (cityOrders.length === 0) {
    container.innerHTML = '<p style="text-align:center; color:var(--text-muted); padding:30px;">لا توجد طلبات في مدينتك حالياً</p>';
    return;
  }

  container.innerHTML = cityOrders.map(order => {
    let actionsHtml = '';
    if (order.status === 'pending') {
      actionsHtml = `
        <div class="driver-btn-row">
          <button class="btn-accept" onclick="driverAccept('${order.id}')">قبول الطلب ✅</button>
          <button class="btn-reject" onclick="driverReject('${order.id}')">رفض ❌</button>
        </div>
      `;
    } else if (order.status === 'accepted') {
      actionsHtml = `
        <div style="background:#ECFDF5; padding:10px; border-radius:12px; margin-top:10px;">
          <p style="font-size:11px; font-weight:700; color:#059669; text-align:center; margin-bottom:8px;">
            عند الوصول للعميل والاتفاق، اختر الإجراء:
          </p>
          <div class="driver-btn-row" style="margin-top:0;">
            <button class="btn-loaded" onclick="driverMarkLoaded('${order.id}')">تم التحميل ✅</button>
            <button class="btn-fail" onclick="driverMarkFailedPrompt('${order.id}')">تعذر الشحن ❌</button>
          </div>
        </div>
      `;
    }

    return `
      <div class="order-card">
        <div class="order-top">
          <span class="order-id">طلب #${order.id}</span>
          ${getStatusBadge(order.status)}
        </div>
        <div class="order-details-row">
          <span>العميل: <strong>${order.clientName}</strong></span>
          <span>الجوال: <strong>${order.clientPhone}</strong></span>
        </div>
        <div class="order-details-row">
          <span>عدد القطع: <strong>${order.packageCount} قطعة</strong></span>
          <span>المدينة: <strong>${order.city}</strong></span>
        </div>
        <div class="order-details-row">
          <span>الملاحظات: ${order.notes}</span>
        </div>
        ${order.failureReason ? `
          <div class="order-fail-box">
            <span>سبب التعذر: ${order.failureReason}</span>
          </div>
        ` : ''}
        ${actionsHtml}
      </div>
    `;
  }).join('');

  lucide.createIcons();
}

function driverAccept(orderId) {
  const order = appData.orders.find(o => o.id === orderId);
  if (order) {
    order.status = 'accepted';
    order.driverName = appData.currentDriver.name;
    order.driverPhone = appData.currentDriver.phone;
    renderDriverOrders();
    renderOrders();
    renderAdmin();
  }
}

function driverReject(orderId) {
  alert('تم رفض الطلب من قبل السائق');
}

function driverMarkLoaded(orderId) {
  const order = appData.orders.find(o => o.id === orderId);
  if (order) {
    order.status = 'loaded';
    renderDriverOrders();
    renderOrders();
    renderAdmin();
    alert('تم تسجيل تحميل الشحنة بنجاح! جاري التوصيل 🚚');
  }
}

function driverMarkFailedPrompt(orderId) {
  const reason = prompt('الرجاء إدخال سبب تعذر الشحن:', 'العميل لم يرد على الاتصال');
  if (reason) {
    const order = appData.orders.find(o => o.id === orderId);
    if (order) {
      order.status = 'failed';
      order.failureReason = reason;
      renderDriverOrders();
      renderOrders();
      renderAdmin();
      alert('تم تحديث حالة الطلب إلى (تعذر الشحن) وظهورها في لوحة التحكم');
    }
  }
}

function renderAdmin() {
  const total = appData.orders.length;
  const pending = appData.orders.filter(o => o.status === 'pending').length;
  const loaded = appData.orders.filter(o => o.status === 'loaded').length;
  const failed = appData.orders.filter(o => o.status === 'failed').length;

  document.getElementById('statTotal').innerText = total;
  document.getElementById('statPending').innerText = pending;
  document.getElementById('statLoaded').innerText = loaded;
  document.getElementById('statFailed').innerText = failed;

  // Render Admin Banners Manager
  const bannersContainer = document.getElementById('adminBannersList');
  if (bannersContainer) {
    bannersContainer.innerHTML = appData.banners.map(b => `
      <div class="admin-banner-row">
        <img src="${b.imageUrl}" class="admin-banner-thumb" onerror="this.src='https://images.unsplash.com/photo-1586528116311-ad8dd3c8310d?w=200'">
        <div class="admin-banner-meta">
          <strong>${b.title}</strong>
          <span>${b.subtitle} (${b.badgeText})</span>
        </div>
        <button class="btn-del-banner" onclick="deleteBanner(${b.id})">حذف 🗑️</button>
      </div>
    `).join('');
  }

  // Render Orders
  const container = document.getElementById('adminOrdersContainer');
  container.innerHTML = appData.orders.map(order => `
    <div class="order-card">
      <div class="order-top">
        <span class="order-id">#${order.id} - ${order.clientName}</span>
        ${getStatusBadge(order.status)}
      </div>
      <div class="order-details-row">
        <span>الجوال: ${order.clientPhone}</span>
        <span>المدينة: ${order.city} | القطع: ${order.packageCount}</span>
      </div>
      ${order.driverName ? `<div style="font-size:12px; color:#2563EB; font-weight:700;">السائق: ${order.driverName}</div>` : ''}
      ${order.failureReason ? `<div style="font-size:12px; color:#DC2626; font-weight:700;">التعذر: ${order.failureReason}</div>` : ''}
    </div>
  `).join('');

  lucide.createIcons();
}

function openNotifications() {
  alert('لديك 3 إشعارات جديدة بخصوص تحديثات شحناتك.');
}

function openTrackingModal() {
  switchToTab('orders');
}

function openSupportModal() {
  alert('فريق الدعم الفني متواجد لمساعدتك على مدار الساعة 24/7');
}
