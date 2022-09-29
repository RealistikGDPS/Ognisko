CREATE TABLE `user_likes` (
    `id` INT(11) NOT NULL AUTO_INCREMENT,
    `target_type` TINYINT(1) NOT NULL,
    `target_id` INT(11) NOT NULL,
    `user_id` INT(11) NOT NULL,
    `value` tinyint(1) NOT NULL
    PRIMARY KEY (`id`)
) ENGINE = InnoDB;

ALTER TABLE `user_likes` ADD INDEX(`user_id`);
