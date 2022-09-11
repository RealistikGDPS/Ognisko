UPDATE comments SET `comment` = FROM_BASE64(`comment`);
UPDATE acccomments SET `comment` = FROM_BASE64(`comment`);
UPDATE messages SET `body` = FROM_BASE64(`body`), `subject` = FROM_BASE64(`subject`);
