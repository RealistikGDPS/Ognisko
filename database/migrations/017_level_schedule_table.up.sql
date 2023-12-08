CREATE TABLE `level_schedule` (
  `id` INT(11) NOT NULL AUTO_INCREMENT,
  `type` TINYINT NOT NULL,
  `level_id` INT(11) NOT NULL,
  `start_time` TIMESTAMP NOT NULL,
  `end_time` TIMESTAMP NOT NULL,
  `scheduled_by_id` INT(11),
  PRIMARY KEY (`id`)
) ENGINE=InnoDB;
