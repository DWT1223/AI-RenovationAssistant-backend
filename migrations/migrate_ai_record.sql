-- 迁移脚本：为 ai_record 表添加渲染图相关字段并修改为 LONGTEXT
-- 执行前请先备份数据库！

USE decoration_ai;

-- 检查字段是否存在，如果不存在则添加
-- 添加 source_img 字段（如果不存在）
SET @column_exists = (
    SELECT COUNT(*)
    FROM INFORMATION_SCHEMA.COLUMNS
    WHERE TABLE_SCHEMA = 'decoration_ai'
    AND TABLE_NAME = 'ai_record'
    AND COLUMN_NAME = 'source_img'
);
SET @sql = IF(@column_exists = 0,
    'ALTER TABLE ai_record ADD COLUMN source_img LONGTEXT COMMENT "上传的户型图URL"',
    'SELECT "source_img already exists"');
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- 添加 prompt 字段
SET @column_exists = (
    SELECT COUNT(*)
    FROM INFORMATION_SCHEMA.COLUMNS
    WHERE TABLE_SCHEMA = 'decoration_ai'
    AND TABLE_NAME = 'ai_record'
    AND COLUMN_NAME = 'prompt'
);
SET @sql = IF(@column_exists = 0,
    'ALTER TABLE ai_record ADD COLUMN prompt LONGTEXT COMMENT "生成提示词"',
    'SELECT "prompt already exists"');
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- 添加 analysis_result 字段
SET @column_exists = (
    SELECT COUNT(*)
    FROM INFORMATION_SCHEMA.COLUMNS
    WHERE TABLE_SCHEMA = 'decoration_ai'
    AND TABLE_NAME = 'ai_record'
    AND COLUMN_NAME = 'analysis_result'
);
SET @sql = IF(@column_exists = 0,
    'ALTER TABLE ai_record ADD COLUMN analysis_result LONGTEXT COMMENT "AI分析结果"',
    'SELECT "analysis_result already exists"');
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- 添加 generated_img 字段
SET @column_exists = (
    SELECT COUNT(*)
    FROM INFORMATION_SCHEMA.COLUMNS
    WHERE TABLE_SCHEMA = 'decoration_ai'
    AND TABLE_NAME = 'ai_record'
    AND COLUMN_NAME = 'generated_img'
);
SET @sql = IF(@column_exists = 0,
    'ALTER TABLE ai_record ADD COLUMN generated_img LONGTEXT COMMENT "生成的图片URL"',
    'SELECT "generated_img already exists"');
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- 将现有字段修改为 LONGTEXT
ALTER TABLE ai_record MODIFY COLUMN source_img LONGTEXT COMMENT "上传的户型图URL";
ALTER TABLE ai_record MODIFY COLUMN prompt LONGTEXT COMMENT "生成提示词";
ALTER TABLE ai_record MODIFY COLUMN analysis_result LONGTEXT COMMENT "AI分析结果";
ALTER TABLE ai_record MODIFY COLUMN generated_img LONGTEXT COMMENT "生成的图片URL";

SELECT 'Migration completed successfully!' AS result;
