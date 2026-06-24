CREATE DATABASE IF NOT EXISTS tts_podcast
  DEFAULT CHARACTER SET utf8mb4
  DEFAULT COLLATE utf8mb4_unicode_ci;

USE tts_podcast;
SET NAMES utf8mb4;

CREATE TABLE IF NOT EXISTS users (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  username VARCHAR(50) NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  email VARCHAR(255) NULL,
  phone VARCHAR(20) NULL,
  avatar TEXT NULL,
  is_active BOOLEAN NOT NULL DEFAULT TRUE,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  UNIQUE KEY uk_user_username (username),
  UNIQUE KEY uk_user_email (email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS voices (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  voice_key VARCHAR(100) NOT NULL,
  display_name VARCHAR(50) NOT NULL,
  gender VARCHAR(20) NOT NULL,
  style VARCHAR(50) NULL,
  category VARCHAR(100) NULL,
  description VARCHAR(255) NULL,
  is_recommended BOOLEAN NOT NULL DEFAULT FALSE,
  is_active BOOLEAN NOT NULL DEFAULT TRUE,
  owner_id BIGINT UNSIGNED NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  UNIQUE KEY uk_voice_key (voice_key),
  KEY idx_voice_category (category),
  KEY idx_voice_recommended (is_recommended),
  KEY idx_voice_owner (owner_id),
  CONSTRAINT fk_voice_owner
    FOREIGN KEY (owner_id) REFERENCES users(id)
    ON DELETE CASCADE
    ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS voice_provider_profiles (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  voice_id BIGINT UNSIGNED NOT NULL,
  provider VARCHAR(50) NOT NULL,
  provider_voice_id VARCHAR(120) NOT NULL,
  locale VARCHAR(20) NULL,
  supports_wav BOOLEAN NOT NULL DEFAULT FALSE,
  supports_mp3 BOOLEAN NOT NULL DEFAULT TRUE,
  is_default BOOLEAN NOT NULL DEFAULT FALSE,
  is_active BOOLEAN NOT NULL DEFAULT TRUE,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  UNIQUE KEY uk_provider_voice (provider, provider_voice_id),
  KEY idx_voice_provider (voice_id, provider),
  CONSTRAINT fk_provider_voice
    FOREIGN KEY (voice_id) REFERENCES voices(id)
    ON DELETE RESTRICT
    ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS voice_preview_audios (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  voice_provider_profile_id BIGINT UNSIGNED NOT NULL,
  sample_text_hash CHAR(64) NOT NULL,
  sample_text VARCHAR(1000) NOT NULL,
  format VARCHAR(10) NOT NULL DEFAULT 'mp3',
  audio_path VARCHAR(500) NOT NULL,
  audio_url VARCHAR(500) NULL,
  duration_seconds DECIMAL(8,2) NULL,
  file_size_bytes BIGINT UNSIGNED NULL,
  status VARCHAR(20) NOT NULL DEFAULT 'ready',
  error_message VARCHAR(1000) NULL,
  generated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  UNIQUE KEY uk_preview_cache (
    voice_provider_profile_id,
    sample_text_hash,
    format
  ),
  KEY idx_preview_status (status),
  KEY idx_preview_generated_at (generated_at),
  CONSTRAINT fk_preview_provider_profile
    FOREIGN KEY (voice_provider_profile_id) REFERENCES voice_provider_profiles(id)
    ON DELETE RESTRICT
    ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS user_material_assets (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  owner_id BIGINT UNSIGNED NOT NULL,
  name VARCHAR(100) NOT NULL,
  description VARCHAR(500) NULL,
  asset_type VARCHAR(50) NOT NULL DEFAULT 'audio_dataset',
  source_format VARCHAR(20) NOT NULL DEFAULT 'audio',
  original_filename VARCHAR(255) NULL,
  storage_path VARCHAR(500) NULL,
  status VARCHAR(30) NOT NULL DEFAULT 'ready',
  metadata_json TEXT NULL,
  is_active BOOLEAN NOT NULL DEFAULT TRUE,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  KEY idx_material_asset_owner (owner_id, is_active),
  KEY idx_material_asset_status (status),
  CONSTRAINT fk_material_asset_owner
    FOREIGN KEY (owner_id) REFERENCES users(id)
    ON DELETE CASCADE
    ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS user_material_items (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  asset_id BIGINT UNSIGNED NOT NULL,
  filename VARCHAR(255) NOT NULL,
  media_type VARCHAR(50) NOT NULL DEFAULT 'audio',
  storage_path VARCHAR(500) NOT NULL,
  transcript TEXT NULL,
  duration_seconds DECIMAL(8,2) NULL,
  file_size_bytes BIGINT UNSIGNED NULL,
  status VARCHAR(30) NOT NULL DEFAULT 'ready',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  KEY idx_material_item_asset (asset_id),
  KEY idx_material_item_status (status),
  CONSTRAINT fk_material_item_asset
    FOREIGN KEY (asset_id) REFERENCES user_material_assets(id)
    ON DELETE CASCADE
    ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS voice_training_jobs (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  owner_id BIGINT UNSIGNED NOT NULL,
  material_asset_id BIGINT UNSIGNED NULL,
  result_model_artifact_id BIGINT UNSIGNED NULL,
  job_name VARCHAR(100) NOT NULL,
  provider VARCHAR(50) NOT NULL DEFAULT 'qwen3_tts',
  base_model VARCHAR(120) NOT NULL DEFAULT 'qwen3-tts-1.7b',
  status VARCHAR(30) NOT NULL DEFAULT 'queued',
  config_json TEXT NULL,
  error_message TEXT NULL,
  started_at DATETIME NULL,
  completed_at DATETIME NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  KEY idx_training_job_owner (owner_id),
  KEY idx_training_job_material (material_asset_id),
  KEY idx_training_job_result_model (result_model_artifact_id),
  KEY idx_training_job_status (status),
  CONSTRAINT fk_training_job_owner
    FOREIGN KEY (owner_id) REFERENCES users(id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT fk_training_job_material
    FOREIGN KEY (material_asset_id) REFERENCES user_material_assets(id)
    ON DELETE SET NULL
    ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS voice_model_artifacts (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  owner_id BIGINT UNSIGNED NULL,
  training_job_id BIGINT UNSIGNED NULL,
  display_name VARCHAR(100) NOT NULL,
  provider VARCHAR(50) NOT NULL DEFAULT 'qwen3_tts',
  model_version VARCHAR(120) NULL,
  artifact_path VARCHAR(500) NOT NULL,
  config_path VARCHAR(500) NULL,
  tokenizer_path VARCHAR(500) NULL,
  runtime_config_json TEXT NULL,
  status VARCHAR(30) NOT NULL DEFAULT 'ready',
  file_size_bytes BIGINT UNSIGNED NULL,
  is_active BOOLEAN NOT NULL DEFAULT TRUE,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  KEY idx_model_artifact_owner (owner_id, is_active),
  KEY idx_model_artifact_provider (provider),
  KEY idx_model_artifact_training_job (training_job_id),
  KEY idx_model_artifact_status (status),
  CONSTRAINT fk_model_artifact_owner
    FOREIGN KEY (owner_id) REFERENCES users(id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT fk_model_artifact_training_job
    FOREIGN KEY (training_job_id) REFERENCES voice_training_jobs(id)
    ON DELETE SET NULL
    ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

SET @sql = (
  SELECT IF(
    COUNT(*) = 0,
    'ALTER TABLE voice_provider_profiles ADD COLUMN provider_kind VARCHAR(50) NOT NULL DEFAULT ''external_tts'' AFTER provider_voice_id',
    'SELECT 1'
  )
  FROM information_schema.COLUMNS
  WHERE TABLE_SCHEMA = DATABASE()
    AND TABLE_NAME = 'voice_provider_profiles'
    AND COLUMN_NAME = 'provider_kind'
);
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;


SET @user_id_type = (
  SELECT COLUMN_TYPE
  FROM information_schema.COLUMNS
  WHERE TABLE_SCHEMA = DATABASE()
    AND TABLE_NAME = 'users'
    AND COLUMN_NAME = 'id'
);

SET @sql = (
  SELECT IF(
    IS_NULLABLE = 'NO',
    CONCAT('ALTER TABLE voice_model_artifacts MODIFY COLUMN owner_id ', @user_id_type, ' NULL'),
    'SELECT 1'
  )
  FROM information_schema.COLUMNS
  WHERE TABLE_SCHEMA = DATABASE()
    AND TABLE_NAME = 'voice_model_artifacts'
    AND COLUMN_NAME = 'owner_id'
);
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;
SET @model_artifact_id_type = (
  SELECT COLUMN_TYPE
  FROM information_schema.COLUMNS
  WHERE TABLE_SCHEMA = DATABASE()
    AND TABLE_NAME = 'voice_model_artifacts'
    AND COLUMN_NAME = 'id'
);

SET @provider_model_artifact_id_type = (
  SELECT COLUMN_TYPE
  FROM information_schema.COLUMNS
  WHERE TABLE_SCHEMA = DATABASE()
    AND TABLE_NAME = 'voice_provider_profiles'
    AND COLUMN_NAME = 'model_artifact_id'
);

SET @sql = (
  SELECT IF(
    @model_artifact_id_type IS NOT NULL
    AND @provider_model_artifact_id_type IS NOT NULL
    AND @model_artifact_id_type <> @provider_model_artifact_id_type,
    CONCAT('ALTER TABLE voice_provider_profiles MODIFY COLUMN model_artifact_id ', @model_artifact_id_type, ' NULL'),
    'SELECT 1'
  )
);
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

SET @sql = (
  SELECT IF(
    COUNT(*) = 0,
    'ALTER TABLE voice_provider_profiles ADD COLUMN model_artifact_id BIGINT UNSIGNED NULL AFTER provider_kind',
    'SELECT 1'
  )
  FROM information_schema.COLUMNS
  WHERE TABLE_SCHEMA = DATABASE()
    AND TABLE_NAME = 'voice_provider_profiles'
    AND COLUMN_NAME = 'model_artifact_id'
);
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

SET @sql = (
  SELECT IF(
    COUNT(*) = 0,
    'ALTER TABLE voice_provider_profiles ADD COLUMN runtime_config_json TEXT NULL AFTER model_artifact_id',
    'SELECT 1'
  )
  FROM information_schema.COLUMNS
  WHERE TABLE_SCHEMA = DATABASE()
    AND TABLE_NAME = 'voice_provider_profiles'
    AND COLUMN_NAME = 'runtime_config_json'
);
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

SET @sql = (
  SELECT IF(
    COUNT(*) = 0,
    'ALTER TABLE voice_provider_profiles ADD KEY idx_provider_model_artifact (model_artifact_id)',
    'SELECT 1'
  )
  FROM information_schema.STATISTICS
  WHERE TABLE_SCHEMA = DATABASE()
    AND TABLE_NAME = 'voice_provider_profiles'
    AND INDEX_NAME = 'idx_provider_model_artifact'
);
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

SET @sql = (
  SELECT IF(
    COUNT(*) = 0,
    'ALTER TABLE voice_provider_profiles ADD CONSTRAINT fk_provider_model_artifact FOREIGN KEY (model_artifact_id) REFERENCES voice_model_artifacts(id) ON DELETE SET NULL ON UPDATE CASCADE',
    'SELECT 1'
  )
  FROM information_schema.REFERENTIAL_CONSTRAINTS
  WHERE CONSTRAINT_SCHEMA = DATABASE()
    AND TABLE_NAME = 'voice_provider_profiles'
    AND CONSTRAINT_NAME = 'fk_provider_model_artifact'
);
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

INSERT INTO voices (
  voice_key,
  display_name,
  gender,
  style,
  category,
  description,
  is_recommended
) VALUES
  ('xiaoxiao', '晓晓', 'female', '温柔', '知识类', '温柔知性的女声，适合知识讲解、课程录制', TRUE),
  ('yunxi', '云希', 'male', '磁性', '故事类', '磁性的男声，适合故事叙述、播客节目', TRUE),
  ('xiaoyi', '晓伊', 'female', '活泼', '情感类', '活泼可爱的女声，适合轻松内容、情感表达', TRUE),
  ('yunjian', '云健', 'male', '活力', '播客类', '充满活力的男声，适合运动、户外类内容', TRUE),
  ('yunyang', '云扬', 'male', '阳光', '播客类', '阳光开朗的男声，适合轻松愉快的播客内容', FALSE),
  ('yunxia', '云夏', 'male', '沉稳', '知识类', '沉稳专业的男声，适合纪录片、教程配音', FALSE),
  ('liaoning-xiaobei', '东北小北', 'female', '方言', '播客类', '东北方言女声，适合搞笑、地域类内容', FALSE),
  ('shaanxi-xiaoni', '陕西小妮', 'female', '方言', '故事类', '陕西方言女声，适合方言类有声读物', FALSE)
ON DUPLICATE KEY UPDATE
  display_name = VALUES(display_name),
  gender = VALUES(gender),
  style = VALUES(style),
  category = VALUES(category),
  description = VALUES(description),
  is_recommended = VALUES(is_recommended),
  is_active = TRUE;

-- Mark voices that no longer exist in Edge-TTS as inactive.
-- These IDs were originally included but Microsoft has never published them.
UPDATE voices SET is_active = FALSE
WHERE voice_key IN (
  'xiaochen', 'xiaohan', 'yunfeng', 'xiaomeng', 'yunze',
  'hunan-xiaoxiao', 'xiaoyou', 'yunhao', 'xiaorui'
);

INSERT INTO voice_provider_profiles (
  voice_id,
  provider,
  provider_voice_id,
  locale,
  supports_wav,
  supports_mp3,
  is_default
)
SELECT id, 'edge_tts', edge_voice_id, 'zh-CN', FALSE, TRUE, TRUE
FROM (
  SELECT 'xiaoxiao' AS voice_key, 'zh-CN-XiaoxiaoNeural' AS edge_voice_id
  UNION ALL SELECT 'yunxi', 'zh-CN-YunxiNeural'
  UNION ALL SELECT 'xiaoyi', 'zh-CN-XiaoyiNeural'
  UNION ALL SELECT 'yunjian', 'zh-CN-YunjianNeural'
  UNION ALL SELECT 'yunyang', 'zh-CN-YunyangNeural'
  UNION ALL SELECT 'yunxia', 'zh-CN-YunxiaNeural'
  UNION ALL SELECT 'liaoning-xiaobei', 'zh-CN-liaoning-XiaobeiNeural'
  UNION ALL SELECT 'shaanxi-xiaoni', 'zh-CN-shaanxi-XiaoniNeural'
) AS seed
JOIN voices ON voices.voice_key = seed.voice_key
ON DUPLICATE KEY UPDATE
  voice_id = VALUES(voice_id),
  locale = VALUES(locale),
  supports_wav = VALUES(supports_wav),
  supports_mp3 = VALUES(supports_mp3),
  is_default = VALUES(is_default),
  is_active = TRUE;

-- Mark provider profiles for invalid voices as inactive as well.
UPDATE voice_provider_profiles
SET is_active = FALSE
WHERE provider_voice_id IN (
  'zh-CN-XiaochenNeural', 'zh-CN-XiaohanNeural', 'zh-CN-YunfengNeural',
  'zh-CN-XiaomengNeural', 'zh-CN-YunzeNeural', 'zh-CN-HunanXiaoxiaoNeural',
  'zh-CN-XiaoyouNeural', 'zh-CN-YunhaoNeural', 'zh-CN-XiaoruiNeural'
);
