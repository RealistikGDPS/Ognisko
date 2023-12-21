ALTER TABLE users ADD COLUMN password VARCHAR(20) NOT NULL AFTER email;
UPDATE users SET password = (SELECT value FROM user_credentials WHERE user_id = users.id AND version = 1);
DROP TABLE user_credentials;
