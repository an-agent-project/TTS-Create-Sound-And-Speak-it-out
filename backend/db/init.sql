CREATE DATABASE IF NOT EXISTS tts_podcast
  DEFAULT CHARACTER SET utf8mb4
  DEFAULT COLLATE utf8mb4_unicode_ci;

USE tts_podcast;

CREATE TABLE IF NOT EXISTS voices (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  voice_key VARCHAR(100) NOT NULL,
  display_name VARCHAR(50) NOT NULL,
  gender VARCHAR(20) NOT NULL,
  style VARCHAR(50) NULL,
  category VARCHAR(50) NULL,
  description VARCHAR(255) NULL,
  is_recommended BOOLEAN NOT NULL DEFAULT FALSE,
  is_active BOOLEAN NOT NULL DEFAULT TRUE,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  UNIQUE KEY uk_voice_key (voice_key),
  KEY idx_voice_category (category),
  KEY idx_voice_recommended (is_recommended)
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
  ('xiaochen', '晓辰', 'female', '沉稳', '知识类', '沉稳大气的女声，适合正式场合配音', FALSE),
  ('yunyang', '云扬', 'male', '阳光', '播客类', '阳光开朗的男声，适合轻松愉快的播客内容', FALSE),
  ('xiaohan', '晓涵', 'female', '甜美', '情感类', '甜美清新的女声，适合朗读、有声书', FALSE),
  ('yunfeng', '云枫', 'male', '沉稳', '知识类', '沉稳专业的男声，适合纪录片、教程配音', FALSE),
  ('xiaomeng', '晓梦', 'female', '亲切', '播客类', '亲切自然的女声，适合日常聊天类播客', FALSE),
  ('yunze', '云泽', 'male', '温和', '故事类', '温和有磁性的男声，适合睡前故事朗读', FALSE),
  ('hunan-xiaoxiao', '湖南晓晓', 'female', '方言', '故事类', '湖南方言女声，适合方言类有声内容', FALSE),
  ('liaoning-xiaobei', '东北小北', 'female', '方言', '播客类', '东北方言女声，适合搞笑、地域类内容', FALSE),
  ('shaanxi-xiaoni', '陕西小妮', 'female', '方言', '故事类', '陕西方言女声，适合方言类有声读物', FALSE),
  ('xiaoyou', '晓悠', 'child', '童真', '故事类', '稚嫩童声，适合儿童故事、绘本朗读', FALSE),
  ('yunhao', '云浩', 'male', '激情', '播客类', '充满激情的男声，适合体育、赛事类解说', FALSE),
  ('xiaorui', '晓蕊', 'female', '知性', '知识类', '知性优雅的女声，适合人文社科类内容', FALSE)
ON DUPLICATE KEY UPDATE
  display_name = VALUES(display_name),
  gender = VALUES(gender),
  style = VALUES(style),
  category = VALUES(category),
  description = VALUES(description),
  is_recommended = VALUES(is_recommended),
  is_active = TRUE;

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
  UNION ALL SELECT 'xiaochen', 'zh-CN-XiaochenNeural'
  UNION ALL SELECT 'yunyang', 'zh-CN-YunyangNeural'
  UNION ALL SELECT 'xiaohan', 'zh-CN-XiaohanNeural'
  UNION ALL SELECT 'yunfeng', 'zh-CN-YunfengNeural'
  UNION ALL SELECT 'xiaomeng', 'zh-CN-XiaomengNeural'
  UNION ALL SELECT 'yunze', 'zh-CN-YunzeNeural'
  UNION ALL SELECT 'hunan-xiaoxiao', 'zh-CN-HunanXiaoxiaoNeural'
  UNION ALL SELECT 'liaoning-xiaobei', 'zh-CN-liaoning-XiaobeiNeural'
  UNION ALL SELECT 'shaanxi-xiaoni', 'zh-CN-shaanxi-XiaoniNeural'
  UNION ALL SELECT 'xiaoyou', 'zh-CN-XiaoyouNeural'
  UNION ALL SELECT 'yunhao', 'zh-CN-YunhaoNeural'
  UNION ALL SELECT 'xiaorui', 'zh-CN-XiaoruiNeural'
) AS seed
JOIN voices ON voices.voice_key = seed.voice_key
ON DUPLICATE KEY UPDATE
  voice_id = VALUES(voice_id),
  locale = VALUES(locale),
  supports_wav = VALUES(supports_wav),
  supports_mp3 = VALUES(supports_mp3),
  is_default = VALUES(is_default),
  is_active = TRUE;
