ALTER TABLE `users`
    MODIFY COLUMN `glow_colour` tinyint(3) UNSIGNED NOT NULL DEFAULT 0 AFTER `secondary_colour`;
