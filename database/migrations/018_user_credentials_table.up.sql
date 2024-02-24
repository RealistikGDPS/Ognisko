CREATE TABLE `user_credentials` (
    `id` INT(11) NOT NULL AUTO_INCREMENT,
    `user_id` INT(11) NOT NULL,
    `version` TINYINT NOT NULL,
    `value` VARCHAR(128) NOT NULL,
    PRIMARY KEY (`id`)
) ENGINE=InnoDB;

-- Migrate user passwords to user_credentials table
INSERT INTO user_credentials (user_id, version, value) SELECT id, 1, password FROM users;
ALTER TABLE users DROP COLUMN password;
