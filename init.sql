

USE decoration_ai;

-- 用户表
CREATE TABLE IF NOT EXISTS `user` (
    `id` BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '用户ID',
    `openid` VARCHAR(64) NOT NULL UNIQUE COMMENT '微信openid',
    `nickname` VARCHAR(64) DEFAULT '' COMMENT '昵称',
    `avatar` VARCHAR(255) DEFAULT '' COMMENT '头像URL',
    `phone` VARCHAR(20) DEFAULT NULL COMMENT '手机号',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX `idx_openid` (`openid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户表';

-- 装修笔记表
CREATE TABLE IF NOT EXISTS `note` (
    `id` BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '笔记ID',
    `user_id` BIGINT NOT NULL COMMENT '用户ID',
    `title` VARCHAR(128) NOT NULL COMMENT '标题',
    `content` TEXT COMMENT '正文内容',
    `images` TEXT COMMENT '图片URL列表JSON',
    `category` VARCHAR(32) DEFAULT NULL COMMENT '分类',
    `stage` VARCHAR(32) DEFAULT NULL COMMENT '装修阶段',
    `is_public` TINYINT NOT NULL DEFAULT 0 COMMENT '是否公开：0私密/1公开',
    `status` TINYINT NOT NULL DEFAULT 0 COMMENT '状态：0草稿/1已发布',
    `like_count` INT NOT NULL DEFAULT 0 COMMENT '点赞数',
    `favorite_count` INT NOT NULL DEFAULT 0 COMMENT '收藏数',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX `idx_user_id` (`user_id`),
    INDEX `idx_is_public` (`is_public`),
    FOREIGN KEY (`user_id`) REFERENCES `user`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='装修笔记表';

-- 账单表
CREATE TABLE IF NOT EXISTS `bill` (
    `id` BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '账单ID',
    `user_id` BIGINT NOT NULL COMMENT '用户ID',
    `category` VARCHAR(32) NOT NULL COMMENT '消费分类',
    `amount` DECIMAL(12,2) NOT NULL DEFAULT 0 COMMENT '金额',
    `bill_date` DATE NOT NULL COMMENT '消费日期',
    `remark` VARCHAR(255) DEFAULT NULL COMMENT '备注',
    `voucher` VARCHAR(255) DEFAULT NULL COMMENT '凭证照片URL',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX `idx_user_id` (`user_id`),
    INDEX `idx_category` (`category`),
    INDEX `idx_bill_date` (`bill_date`),
    FOREIGN KEY (`user_id`) REFERENCES `user`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='账单表';

-- 预算表
CREATE TABLE IF NOT EXISTS `budget` (
    `id` BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '预算ID',
    `user_id` BIGINT NOT NULL UNIQUE COMMENT '用户ID',
    `total_budget` DECIMAL(12,2) NOT NULL DEFAULT 0 COMMENT '总预算',
    `items` TEXT COMMENT '分项预算JSON',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    FOREIGN KEY (`user_id`) REFERENCES `user`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='预算表';

-- 户型图表
CREATE TABLE IF NOT EXISTS `house_img` (
    `id` BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '户型图ID',
    `user_id` BIGINT NOT NULL COMMENT '用户ID',
    `img_url` VARCHAR(255) NOT NULL COMMENT '图片URL',
    `img_type` VARCHAR(32) DEFAULT NULL COMMENT '分类',
    `title` VARCHAR(128) DEFAULT NULL COMMENT '名称',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX `idx_user_id` (`user_id`),
    FOREIGN KEY (`user_id`) REFERENCES `user`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='户型图表';

-- 装修风格表
CREATE TABLE IF NOT EXISTS `style` (
    `id` BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '风格ID',
    `name` VARCHAR(32) NOT NULL UNIQUE COMMENT '风格名称',
    `cover` VARCHAR(255) DEFAULT NULL COMMENT '封面图URL',
    `description` TEXT COMMENT '风格介绍',
    `color_scheme` TEXT COMMENT '配色方案',
    `material` TEXT COMMENT '主材搭配要点',
    `suitable` TEXT COMMENT '适配户型',
    `pros` TEXT COMMENT '优点',
    `cons` TEXT COMMENT '缺点',
    `sort` INT NOT NULL DEFAULT 0 COMMENT '排序',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='装修风格表';

-- 收藏表
CREATE TABLE IF NOT EXISTS `collect` (
    `id` BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '收藏ID',
    `user_id` BIGINT NOT NULL COMMENT '用户ID',
    `target_type` VARCHAR(16) NOT NULL COMMENT '收藏对象类型：note/style',
    `target_id` BIGINT NOT NULL COMMENT '收藏对象ID',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '收藏时间',
    INDEX `idx_user_id` (`user_id`),
    INDEX `idx_target` (`target_type`, `target_id`),
    UNIQUE KEY `uk_user_target` (`user_id`, `target_type`, `target_id`),
    FOREIGN KEY (`user_id`) REFERENCES `user`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='收藏表';

-- AI生成记录表
CREATE TABLE IF NOT EXISTS `ai_record` (
    `id` BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '记录ID',
    `user_id` BIGINT NOT NULL COMMENT '用户ID',
    `type` VARCHAR(16) NOT NULL COMMENT '类型：plan/render',
    `source_img` LONGTEXT COMMENT '上传的户型图URL',
    `prompt` LONGTEXT COMMENT '生成提示词',
    `analysis_result` LONGTEXT COMMENT 'AI分析结果',
    `generated_img` LONGTEXT COMMENT '生成的图片URL',
    `params` TEXT COMMENT '生成参数JSON',
    `result` TEXT COMMENT '生成结果',
    `status` TINYINT NOT NULL DEFAULT 0 COMMENT '状态：0生成中/1成功/2失败',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX `idx_user_id` (`user_id`),
    FOREIGN KEY (`user_id`) REFERENCES `user`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='AI生成记录表';

-- 插入初始装修风格数据
INSERT INTO `style` (`name`, `description`, `color_scheme`, `material`, `suitable`, `pros`, `cons`, `sort`) VALUES
('现代简约', '以简洁、功能性为核心的设计风格', '黑白灰为主，搭配亮色点缀', '玻璃、金属、瓷砖', '适合各种户型', '简洁大方、易于清洁、显空间大', '可能缺乏温馨感', 1),
('奶油风', '温馨柔和的暖色调设计', '米白、奶咖、淡黄为主', '布艺、木质、藤编', '适合小户型、刚需房', '温馨舒适、治愈感强', '不耐脏、难打理', 2),
('轻奢', '低调奢华的品质感设计', '金色、灰色、米白为主', '大理石、金属、丝绒', '适合大户型、改善型住房', '品质感强、档次高', '造价较高', 3),
('原木风', '自然原始的木质元素设计', '木色、米白、绿色为主', '实木、竹子、棉麻', '适合各种户型', '自然温馨、环保健康', '需要定期保养', 4),
('北欧风', '简洁实用的斯堪的纳维亚设计', '白墙、木地板、彩色点缀', '木材、玻璃、塑料', '适合小户型', '简洁明亮、性价比高', '不够个性化', 5),
('日式', '简约淡雅的东方美学设计', '原木、白墙、素色', '木材、纸质、棉麻', '适合小户型', '简约禅意、收纳强', '色彩单一', 6),
('美式', '自由随性的美洲风格设计', '深木色、复古色、蓝色', '实木、皮质、壁纸', '适合大户型、别墅', '大气舒适、历史感', '占用空间大', 7),
('极简', '极度精简的装饰设计', '黑白灰为主', '金属、玻璃、混凝土', '适合各种户型', '干净利落、易于维护', '可能显得冷清', 8),
('新中式', '传统与现代融合的东方设计', '黑白灰、朱红、金色', '实木、陶瓷、水墨画', '适合大户型', '文化底蕴强、有格调', '造价较高', 9),
('ins风', '年轻时尚的网络流行风格', '粉色、白色、灰色为主', '金属、玻璃、绿植', '适合小户型', '颜值高、易出片', '不够实用', 10);
