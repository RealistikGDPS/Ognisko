CREATE TABLE `users` (
  `id` int(11) NOT NULL,
  `username` varchar(20) NOT NULL,
  `email` varchar(255) NOT NULL,
  `password` char(60) NOT NULL,
  `message_privacy` tinyint(1) NOT NULL,
  `friend_privacy` tinyint(1) NOT NULL,
  `comment_privacy` tinyint(1) NOT NULL,
  `twitter_name` varchar(15) DEFAULT NULL,
  `youtube_name` int(25) DEFAULT NULL,
  `twitch_name` varchar(25) DEFAULT NULL,
  `register_ts` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `stars` int(10) UNSIGNED NOT NULL,
  `demons` smallint(5) UNSIGNED NOT NULL,
  `primary_colour` tinyint(3) UNSIGNED NOT NULL,
  `secondary_colour` tinyint(3) UNSIGNED NOT NULL,
  `display_type` tinyint(3) UNSIGNED NOT NULL,
  `icon` tinyint(3) UNSIGNED NOT NULL,
  `ship` tinyint(3) UNSIGNED NOT NULL,
  `ball` tinyint(3) UNSIGNED NOT NULL,
  `ufo` tinyint(3) UNSIGNED NOT NULL,
  `wave` tinyint(3) UNSIGNED NOT NULL,
  `robot` tinyint(3) UNSIGNED NOT NULL,
  `spider` tinyint(3) UNSIGNED NOT NULL,
  `explosion` tinyint(3) UNSIGNED NOT NULL,
  `glow` tinyint(1) NOT NULL,
  `creator_points` smallint(5) UNSIGNED NOT NULL,
  `coins` int(10) UNSIGNED NOT NULL,
  `user_coins` int(10) UNSIGNED NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

ALTER TABLE `users`
  ADD PRIMARY KEY (`id`),
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;
