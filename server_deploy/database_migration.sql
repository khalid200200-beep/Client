-- =========================================================
-- سكربت الترقية الآمنة لقاعدة البيانات القائمة (Migration Script)
-- يضمن إضافة الأعمدة والجداول الجديدة دون فقدان أي بيانات
-- =========================================================

USE `shipping_db`;

-- 1. ترقية جدول المستخدمين users
SET @dbname = DATABASE();
SET @tablename = "users";
SET @columnname = "email";
SET @preparedStatement = (SELECT IF(
  (
    SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
    WHERE
      (table_name = @tablename)
      AND (table_schema = @dbname)
      AND (column_name = @columnname)
  ) > 0,
  "SELECT 1",
  "ALTER TABLE users ADD COLUMN `email` VARCHAR(150) NULL UNIQUE AFTER `phone`;"
));
PREPARE alterIfNotExists FROM @preparedStatement;
EXECUTE alterIfNotExists;
DEALLOCATE PREPARE alterIfNotExists;

-- 2. ترقية جدول الطلبات orders (collected_amount)
SET @tablename = "orders";
SET @columnname = "collected_amount";
SET @preparedStatement = (SELECT IF(
  (
    SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
    WHERE
      (table_name = @tablename)
      AND (table_schema = @dbname)
      AND (column_name = @columnname)
  ) > 0,
  "SELECT 1",
  "ALTER TABLE orders ADD COLUMN `collected_amount` DECIMAL(10,2) NOT NULL DEFAULT 0.00 AFTER `driver_phone`;"
));
PREPARE alterIfNotExists FROM @preparedStatement;
EXECUTE alterIfNotExists;
DEALLOCATE PREPARE alterIfNotExists;

-- 3. ترقية جدول الطلبات orders (pickup_city, delivery_city)
SET @columnname = "pickup_city";
SET @preparedStatement = (SELECT IF(
  (
    SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
    WHERE
      (table_name = @tablename)
      AND (table_schema = @dbname)
      AND (column_name = @columnname)
  ) > 0,
  "SELECT 1",
  "ALTER TABLE orders ADD COLUMN `pickup_city` VARCHAR(100) NULL AFTER `city`;"
));
PREPARE alterIfNotExists FROM @preparedStatement;
EXECUTE alterIfNotExists;
DEALLOCATE PREPARE alterIfNotExists;

SET @columnname = "delivery_city";
SET @preparedStatement = (SELECT IF(
  (
    SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
    WHERE
      (table_name = @tablename)
      AND (table_schema = @dbname)
      AND (column_name = @columnname)
  ) > 0,
  "SELECT 1",
  "ALTER TABLE orders ADD COLUMN `delivery_city` VARCHAR(100) NULL AFTER `pickup_address`;"
));
PREPARE alterIfNotExists FROM @preparedStatement;
EXECUTE alterIfNotExists;
DEALLOCATE PREPARE alterIfNotExists;

-- 4. إنشاء جدول رموز OTP إن لم يكن موجوداً
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

-- 5. إنشاء جدول محاولات الدخول login_attempts
CREATE TABLE IF NOT EXISTS `login_attempts` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `ip_address` VARCHAR(45) NOT NULL,
    `endpoint` VARCHAR(50) DEFAULT 'login',
    `attempt_time` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX (`ip_address`, `endpoint`, `attempt_time`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 6. إنشاء جدول البانرات banners
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

-- 7. إنشاء جدول إعدادات النظام ومزود البريد system_settings
CREATE TABLE IF NOT EXISTS `system_settings` (
    `setting_key` VARCHAR(50) PRIMARY KEY,
    `setting_value` TEXT NULL,
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT INTO `system_settings` (`setting_key`, `setting_value`) VALUES
('smtp_host', '127.0.0.1'),
('smtp_port', '25'),
('smtp_username', ''),
('smtp_password', ''),
('smtp_encryption', 'none'),
('sender_email', 'noreply@sudra.sa'),
('sender_name', 'سودرا للشحن والتوصيل')
ON DUPLICATE KEY UPDATE `setting_key`=`setting_key`;

