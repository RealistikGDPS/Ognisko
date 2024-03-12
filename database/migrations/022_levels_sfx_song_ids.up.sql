ALTER TABLE `levels` 
    ADD COLUMN `sfx_ids` JSON AFTER `update_ts`,
    ADD COLUMN `song_ids` JSON AFTER `update_ts`;

UPDATE `levels` SET `song_ids` = JSON_ARRAY(song_id), `sfx_ids` = JSON_ARRAY();
