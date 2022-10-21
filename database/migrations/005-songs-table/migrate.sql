CREATE TABLE `songs` (
    `id` INT(11) NOT NULL AUTO_INCREMENT,
    `name` VARCHAR(32) NOT NULL,
    `author_id` INT(11) NOT NULL,
    `author` VARCHAR(32) NOT NULL,
    `author_youtube` VARCHAR(25) NOT NULL,
    `size` FLOAT NOT NULL,
    `download_url` VARCHAR(256) NOT NULL,
    `source` TINYINT(2) NOT NULL,
    `blocked` TINYINT(1) NOT NULL,
    PRIMARY KEY (`id`)
) ENGINE = InnoDB;
