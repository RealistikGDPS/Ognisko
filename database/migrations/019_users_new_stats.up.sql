ALTER TABLE `users`
    ADD COLUMN `moons` int(10) UNSIGNED NOT NULL DEFAULT 0 AFTER `demons`,
    ADD COLUMN `swing_copter` tinyint(3) UNSIGNED NOT NULL DEFAULT 0 AFTER `spider`,
    ADD COLUMN `jetpack` tinyint(3) UNSIGNED NOT NULL DEFAULT 0 AFTER `swing_copter`,
    ADD COLUMN `glow_colour` tinyint(3) UNSIGNED NOT NULL DEFAULT 0 AFTER `secondary_colour`;
