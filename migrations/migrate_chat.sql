-- 迁移脚本：创建 AI 问答对话相关表（chat_session、chat_message）
-- 执行前请先备份数据库！
-- 幂等：重复执行不会出错

USE decoration_ai;

-- ============================================================
-- 1. 创建 chat_session 会话表
-- ============================================================
SET @table_exists = (
    SELECT COUNT(*)
    FROM INFORMATION_SCHEMA.TABLES
    WHERE TABLE_SCHEMA = 'decoration_ai'
      AND TABLE_NAME = 'chat_session'
);
SET @sql = IF(@table_exists = 0, '
    CREATE TABLE chat_session (
        id BIGINT NOT NULL COMMENT "会话ID" AUTO_INCREMENT,
        user_id BIGINT NOT NULL COMMENT "所属用户ID",
        title VARCHAR(255) NOT NULL DEFAULT "新对话" COMMENT "会话标题",
        created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT "创建时间",
        updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT "更新时间",
        PRIMARY KEY (id),
        KEY idx_chat_session_user_id (user_id),
        KEY idx_chat_session_updated_at (updated_at),
        CONSTRAINT fk_chat_session_user FOREIGN KEY (user_id)
            REFERENCES user (id) ON DELETE CASCADE
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT="AI问答会话表"
', 'SELECT "chat_session table already exists"');
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- ============================================================
-- 2. 创建 chat_message 消息表
-- ============================================================
SET @table_exists = (
    SELECT COUNT(*)
    FROM INFORMATION_SCHEMA.TABLES
    WHERE TABLE_SCHEMA = 'decoration_ai'
      AND TABLE_NAME = 'chat_message'
);
SET @sql = IF(@table_exists = 0, '
    CREATE TABLE chat_message (
        id BIGINT NOT NULL COMMENT "消息ID" AUTO_INCREMENT,
        session_id BIGINT NOT NULL COMMENT "所属会话ID",
        user_id BIGINT NOT NULL COMMENT "用户ID（冗余字段，便于按用户过滤）",
        `role` VARCHAR(16) NOT NULL COMMENT "角色：user 用户 / assistant AI",
        content LONGTEXT NOT NULL COMMENT "消息内容",
        created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT "创建时间",
        PRIMARY KEY (id),
        KEY idx_chat_msg_session_created (session_id, created_at),
        KEY idx_chat_msg_user (user_id),
        CONSTRAINT fk_chat_msg_session FOREIGN KEY (session_id)
            REFERENCES chat_session (id) ON DELETE CASCADE,
        CONSTRAINT fk_chat_msg_user FOREIGN KEY (user_id)
            REFERENCES user (id) ON DELETE CASCADE
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT="AI问答消息表"
', 'SELECT "chat_message table already exists"');
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- ============================================================
-- 3. 验证：列出已创建的 chat 相关表
-- ============================================================
SELECT TABLE_NAME, TABLE_COMMENT
FROM information_schema.TABLES
WHERE TABLE_SCHEMA = 'decoration_ai'
  AND TABLE_NAME IN ('chat_session', 'chat_message')
ORDER BY TABLE_NAME;

-- ============================================================
-- 4. 验证：列出 chat 表的所有字段
-- ============================================================
SELECT TABLE_NAME, COLUMN_NAME, COLUMN_TYPE, IS_NULLABLE, COLUMN_DEFAULT, COLUMN_COMMENT
FROM information_schema.COLUMNS
WHERE TABLE_SCHEMA = 'decoration_ai'
  AND TABLE_NAME IN ('chat_session', 'chat_message')
ORDER BY TABLE_NAME, ORDINAL_POSITION;

-- ============================================================
-- 5. 验证：列出 chat 表的外键约束
-- ============================================================
SELECT
    kcu.TABLE_NAME,
    kcu.CONSTRAINT_NAME,
    kcu.COLUMN_NAME,
    kcu.REFERENCED_TABLE_NAME,
    kcu.REFERENCED_COLUMN_NAME,
    rc.DELETE_RULE
FROM information_schema.KEY_COLUMN_USAGE kcu
JOIN information_schema.REFERENTIAL_CONSTRAINTS rc
    ON kcu.CONSTRAINT_SCHEMA = rc.CONSTRAINT_SCHEMA
   AND kcu.CONSTRAINT_NAME = rc.CONSTRAINT_NAME
WHERE kcu.CONSTRAINT_SCHEMA = 'decoration_ai'
  AND kcu.TABLE_NAME IN ('chat_session', 'chat_message')
  AND kcu.REFERENCED_TABLE_NAME IS NOT NULL
ORDER BY kcu.TABLE_NAME, kcu.CONSTRAINT_NAME;

SELECT 'Chat migration completed successfully!' AS result;