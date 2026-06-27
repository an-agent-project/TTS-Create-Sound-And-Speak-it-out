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
  avatar MEDIUMTEXT NULL,
  is_active BOOLEAN NOT NULL DEFAULT TRUE,
  role VARCHAR(20) NOT NULL DEFAULT 'user',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  UNIQUE KEY uk_user_username (username),
  UNIQUE KEY uk_user_email (email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
-- Development default admin account.
-- Username: admin
-- Password: Admin@123456
-- Change this password after first login in non-local environments.
INSERT INTO users (
  username,
  password_hash,
  email,
  role,
  is_active
) VALUES (
  'admin',
  '$2b$12$mtsTFkXD6Ru1o9Dd1HPbl.9BTapzSjG9/j9P4i/upHmyWKrXPFaUS',
  'admin@example.local',
  'admin',
  TRUE
)
ON DUPLICATE KEY UPDATE
  role = 'admin',
  is_active = TRUE,
  email = VALUES(email);

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
  role VARCHAR(20) NOT NULL DEFAULT 'user',
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
  role VARCHAR(20) NOT NULL DEFAULT 'user',
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

CREATE TABLE IF NOT EXISTS materials (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  material_key VARCHAR(100) NOT NULL,
  filename VARCHAR(255) NOT NULL,
  title VARCHAR(100) NOT NULL,
  category VARCHAR(50) NOT NULL DEFAULT 'bgm',
  format VARCHAR(10) NOT NULL,
  duration_seconds INT NOT NULL DEFAULT 0,
  file_size_bytes BIGINT UNSIGNED NOT NULL DEFAULT 0,
  uploader VARCHAR(100) NOT NULL DEFAULT '系统素材',
  audio_path VARCHAR(500) NOT NULL,
  audio_url VARCHAR(500) NOT NULL,
  license VARCHAR(100) NULL,
  source_url VARCHAR(500) NULL,
  is_active BOOLEAN NOT NULL DEFAULT TRUE,
  role VARCHAR(20) NOT NULL DEFAULT 'user',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  UNIQUE KEY uk_material_key (material_key),
  KEY idx_material_category (category)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


CREATE TABLE IF NOT EXISTS material_reports (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  material_id BIGINT UNSIGNED NOT NULL,
  reporter_id BIGINT UNSIGNED NOT NULL,
  reason_category VARCHAR(50) NOT NULL,
  reason_detail VARCHAR(500) NULL,
  status VARCHAR(20) NOT NULL DEFAULT 'pending',
  reviewed_by BIGINT UNSIGNED NULL,
  review_note VARCHAR(500) NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  KEY idx_report_material (material_id),
  KEY idx_report_status (status),
  KEY idx_report_reporter (reporter_id),
  UNIQUE KEY uk_active_report (material_id, reporter_id, status),
  CONSTRAINT fk_report_material
    FOREIGN KEY (material_id) REFERENCES materials(id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT fk_report_reporter
    FOREIGN KEY (reporter_id) REFERENCES users(id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT fk_report_reviewer
    FOREIGN KEY (reviewed_by) REFERENCES users(id)
    ON DELETE SET NULL
    ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


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


INSERT INTO voices (
  voice_key,
  display_name,
  gender,
  style,
  category,
  description,
  is_recommended
) VALUES
  ('bailian-qwen-cherry', '芊悦', 'female', '阳光', '知识类', '阳光积极、亲切自然的百炼 Qwen-TTS 女声。', TRUE),
  ('bailian-qwen-serena', '苏瑶', 'female', '温柔', '情感类', '温柔细腻的百炼 Qwen-TTS 女声。', TRUE),
  ('bailian-qwen-ethan', '晨煦', 'male', '温暖', '播客类', '阳光温暖的百炼 Qwen-TTS 男声。', TRUE),
  ('bailian-qwen-chelsie', '千雪', 'female', '二次元', '故事类', '二次元风格的百炼 Qwen-TTS 女性音色。', FALSE),
  ('bailian-qwen-moon', '月白', 'male', '率性', '播客类', '率性帅气的百炼 Qwen-TTS 男声。', FALSE),
  ('bailian-qwen-maia', '四月', 'female', '知性', '知识类', '知性温柔的百炼 Qwen-TTS 女声。', TRUE),
  ('bailian-qwen-kai', '凯', 'male', '低沉', '故事类', '低沉舒适的百炼 Qwen-TTS 男声。', FALSE),
  ('bailian-qwen-neil', '阿闻', 'male', '新闻', '知识类', '新闻主持风格的百炼 Qwen-TTS 男声。', FALSE)
ON DUPLICATE KEY UPDATE
  display_name = VALUES(display_name),
  gender = VALUES(gender),
  style = VALUES(style),
  category = VALUES(category),
  description = VALUES(description),
  is_recommended = VALUES(is_recommended),
  is_active = TRUE,
  owner_id = NULL;

INSERT INTO voice_provider_profiles (
  voice_id,
  provider,
  provider_voice_id,
  locale,
  supports_wav,
  supports_mp3,
  is_default
)
SELECT voices.id, 'bailian_tts', seed.provider_voice_id, 'zh-CN', FALSE, TRUE, TRUE
FROM (
  SELECT 'bailian-qwen-cherry' AS voice_key, 'bailian:qwen3-tts-flash:Cherry' AS provider_voice_id
  UNION ALL SELECT 'bailian-qwen-serena', 'bailian:qwen3-tts-flash:Serena'
  UNION ALL SELECT 'bailian-qwen-ethan', 'bailian:qwen3-tts-flash:Ethan'
  UNION ALL SELECT 'bailian-qwen-chelsie', 'bailian:qwen3-tts-flash:Chelsie'
  UNION ALL SELECT 'bailian-qwen-moon', 'bailian:qwen3-tts-flash:Moon'
  UNION ALL SELECT 'bailian-qwen-maia', 'bailian:qwen3-tts-flash:Maia'
  UNION ALL SELECT 'bailian-qwen-kai', 'bailian:qwen3-tts-flash:Kai'
  UNION ALL SELECT 'bailian-qwen-neil', 'bailian:qwen3-tts-flash:Neil'
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
