CREATE TABLE `daily_chests` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `user_id` INT NOT NULL,
  `type` TINYINT NOT NULL,
  `mana` SMALLINT NOT NULL,
  `diamonds` INT NOT NULL,
  `fire_shards` INT NOT NULL,
  `ice_shards` INT NOT NULL,
  `poison_shards` INT NOT NULL,
  `shadow_shards` INT NOT NULL,
  `lava_shards` INT NOT NULL,
  `demon_keys` INT NOT NULL,
  `claimed_ts` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE = InnoDB;

ALTER TABLE `daily_chests` ADD INDEX(`user_id`);
ALTER TABLE `daily_chests` ADD INDEX(`type`);
