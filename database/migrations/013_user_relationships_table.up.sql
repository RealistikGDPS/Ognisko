CREATE TABLE `user_relationships` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `relationship_type` int(2) NOT NULL,
  `user1_id` int(11) NOT NULL,
  `user2_id` int(11) NOT NULL,
  `post_ts` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `seen_ts` TIMESTAMP NULL DEFAULT NULL,
  `deleted` TINYINT(1) NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB;

ALTER TABLE `user_relationships` ADD INDEX(`user1_id`);
ALTER TABLE `user_relationships` ADD INDEX(`user2_id`);
