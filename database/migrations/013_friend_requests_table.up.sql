CREATE TABLE `friend_requests` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `sender_user_id` int(11) NOT NULL,
  `recipient_user_id` int(11) NOT NULL,
  `message` varchar(140) NOT NULL,
  `post_ts` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `seen_ts` TIMESTAMP NULL DEFAULT NULL,
  `deleted` TINYINT(1) NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB;

ALTER TABLE `friend_requests` ADD INDEX(`sender_user_id`);
ALTER TABLE `friend_requests` ADD INDEX(`recipient_user_id`);
