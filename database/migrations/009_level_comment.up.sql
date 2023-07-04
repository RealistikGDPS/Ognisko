CREATE TABLE `level_comments` (
    `id` INT(11) NOT NULL AUTO_INCREMENT,
    `user_id` INT(11) NOT NULL,
    `level_id` INT(11) NOT NULL,
    `content` VARCHAR(256) NOT NULL,
    `likes` INT(11) NOT NULL,
    `post_ts` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `deleted` TINYINT(1) NOT NULL DEFAULT '0',
    PRIMARY KEY (`id`)
) ENGINE = InnoDB;

ALTER TABLE `level_comments` ADD INDEX(`user_id`);
ALTER TABLE `level_comments` ADD INDEX(`level_id`);
