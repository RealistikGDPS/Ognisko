CREATE TABLE `messages` (
    `id` int(11) NOT NULL AUTO_INCREMENT,
    `sender_user_id` int(11) NOT NULL,
    `recipient_user_id` int(11) NOT NULL,
    `subject` varchar(35),
    `content` varchar(200),
    `post_ts` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `seen_ts` TIMESTAMP NULL DEFAULT NULL,
    `sender_deleted` TINYINT(1) NOT NULL DEFAULT '0',
    `recipient_deleted` TINYINT(1) NOT NULL DEFAULT '0',
    `deleted` TINYINT(1) NOT NULL DEFAULT '0',
    PRIMARY KEY (`id`)
) ENGINE = InnoDB;
ALTER TABLE `messages` ADD INDEX(`sender_user_id`);
ALTER TABLE `messages` ADD INDEX(`recipient_user_id`);
