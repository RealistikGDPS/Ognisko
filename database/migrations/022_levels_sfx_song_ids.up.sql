ALTER TABLE `levels`
    ADD COLUMN `sfx_ids` JSON AFTER `update_ts`,
    ADD COLUMN `song_ids` JSON AFTER `update_ts`;

UPDATE `levels` SET
    `song_ids` = CASE WHEN `custom_song_id` IS NULL THEN JSON_ARRAY() ELSE JSON_ARRAY(`custom_song_id`) END,
    `sfx_ids` = JSON_ARRAY();
