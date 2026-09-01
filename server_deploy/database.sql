-- =========================================================
-- منظومة سودرا للشحن والتوصيل - SUDRA EXPRESS
-- سكربت قاعدة بيانات الإنتاج (MySQL Schema)
-- =========================================================

CREATE DATABASE IF NOT EXISTS `shipping_db` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE `shipping_db`;

-- 1. جدول المستخدمين (العملاء، السائقين، الإدارة)
CREATE TABLE IF NOT EXISTS `users` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `name` VARCHAR(100) NOT NULL,
    `phone` VARCHAR(20) NOT NULL UNIQUE,
    `email` VARCHAR(150) NULL UNIQUE,
    `password` VARCHAR(255) NOT NULL,
    `city` VARCHAR(50) NOT NULL DEFAULT 'الخرطوم',
    `vehicle_plate` VARCHAR(50) NULL,
    `role` ENUM('client', 'driver', 'admin') DEFAULT 'client',
    `is_active` TINYINT(1) DEFAULT 1,
    `avatar` VARCHAR(255) NULL,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX (`phone`),
    INDEX (`email`),
    INDEX (`role`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 2. جدول الشحنات والطلبات
CREATE TABLE IF NOT EXISTS `orders` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `order_code` VARCHAR(30) NOT NULL UNIQUE,
    `client_id` INT NULL,
    `client_name` VARCHAR(100) NOT NULL,
    `client_phone` VARCHAR(20) NOT NULL,
    `city` VARCHAR(50) NOT NULL DEFAULT 'الخرطوم',
    `pickup_city` VARCHAR(100) NULL,
    `pickup_address` VARCHAR(255) NULL,
    `delivery_city` VARCHAR(100) NULL,
    `delivery_address` VARCHAR(255) NULL,
    `package_count` INT NOT NULL DEFAULT 1,
    `image_path` VARCHAR(500) NULL,
    `notes` TEXT NULL,
    `status` ENUM('pending', 'accepted', 'loaded', 'failed', 'delivered') DEFAULT 'pending',
    `driver_name` VARCHAR(100) NULL,
    `driver_phone` VARCHAR(20) NULL,
    `collected_amount` DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    `failure_reason` TEXT NULL,
    `loaded_at` TIMESTAMP NULL,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX (`order_code`),
    INDEX (`client_phone`),
    INDEX (`status`),
    INDEX (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 3. جدول رموز التحقق عبر البريد الإلكتروني (Email OTPs)
CREATE TABLE IF NOT EXISTS `email_otps` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `email` VARCHAR(150) NOT NULL,
    `otp_code` VARCHAR(10) NOT NULL,
    `action_type` VARCHAR(50) DEFAULT 'register',
    `is_used` TINYINT(1) DEFAULT 0,
    `expires_at` DATETIME NOT NULL,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX (`email`),
    INDEX (`otp_code`),
    INDEX (`expires_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 4. جدول محاولات تسجيل الدخول وحماية Rate Limiting
CREATE TABLE IF NOT EXISTS `login_attempts` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `ip_address` VARCHAR(45) NOT NULL,
    `endpoint` VARCHAR(50) DEFAULT 'login',
    `attempt_time` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX (`ip_address`, `endpoint`, `attempt_time`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 5. جدول البانرات وسلايدر الصور الترويجي
CREATE TABLE IF NOT EXISTS `banners` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `title` VARCHAR(150) NOT NULL,
    `subtitle` VARCHAR(255) NOT NULL,
    `badge_text` VARCHAR(50) DEFAULT 'عرض خاص',
    `image_url` VARCHAR(500) NOT NULL,
    `button_text` VARCHAR(50) DEFAULT 'اطلب شحن الآن',
    `is_active` TINYINT(1) DEFAULT 1,
    `sort_order` INT DEFAULT 0,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- إدراج البانرات الترويجية الأولية
INSERT INTO `banners` (`id`, `title`, `subtitle`, `badge_text`, `image_url`, `button_text`, `is_active`) VALUES
(1, 'سودرا للشحن السريع', 'شحنك يصل إليك بسرعة وأمان وموثوقية', 'الأكثر طلباً ⭐', 'https://images.unsplash.com/photo-1586528116311-ad8dd3c8310d?w=800', 'اطلب شحن الآن', 1),
(2, 'تغطية شاملة لجميع المدن', 'شحن آمن وفوري مع متابعة حية للطلب', 'خدمة VIP ⚡', 'https://images.unsplash.com/photo-1519003722824-194d4455a60c?w=800', 'احصل على العرض', 1),
(3, 'كباتن معتمدون بالقرب منك', 'استلام فوري من الباب وتسليم للوجهة', 'سودرا إكسبريس', 'https://images.unsplash.com/photo-1601584115197-04ecc0da31d7?w=800', 'شحن فوري', 1)
ON DUPLICATE KEY UPDATE `title`=VALUES(`title`);

-- 6. جدول إعدادات النظام ومزود البريد (SMTP & Mail Provider Settings)
CREATE TABLE IF NOT EXISTS `system_settings` (
    `setting_key` VARCHAR(50) PRIMARY KEY,
    `setting_value` TEXT NULL,
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- إدراج الإعدادات الافتراضية للبريد
INSERT INTO `system_settings` (`setting_key`, `setting_value`) VALUES
('smtp_host', '127.0.0.1'),
('smtp_port', '25'),
('smtp_username', ''),
('smtp_password', ''),
('smtp_encryption', 'none'),
('sender_email', 'noreply@sudra.sa'),
('sender_name', 'سودرا للشحن والتوصيل')
ON DUPLICATE KEY UPDATE `setting_key`=`setting_key`;

