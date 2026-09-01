-- ====================================================================
-- SUDRA EXPRESS - Database Migration v3
-- 1. Multiple Order Images Support (order_images)
-- 2. Secure Password Reset System (password_resets)
-- ====================================================================

-- 1. إنشاء جدول الصور المتعددة للشحنات (order_images)
CREATE TABLE IF NOT EXISTS order_images (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL,
    image_path VARCHAR(500) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_order_id (order_id),
    CONSTRAINT fk_order_images_order FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 2. ترحيل روابط ومسارات الصور القديمة ذات الطول المناسب
INSERT INTO order_images (order_id, image_path, created_at)
SELECT o.id, o.image_path, o.created_at
FROM orders o
LEFT JOIN order_images oi ON oi.order_id = o.id
WHERE o.image_path IS NOT NULL 
  AND o.image_path != '' 
  AND LENGTH(o.image_path) <= 500
  AND oi.id IS NULL;

-- 3. إنشاء جدول استعادة كلمة المرور المشفر والآمن (password_resets)
CREATE TABLE IF NOT EXISTS password_resets (
    id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(255) NOT NULL,
    otp_hash VARCHAR(255) NOT NULL,
    reset_token_hash VARCHAR(255) DEFAULT NULL,
    attempts INT DEFAULT 0,
    is_used TINYINT(1) DEFAULT 0,
    expires_at DATETIME NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_email (email),
    INDEX idx_expires_at (expires_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
