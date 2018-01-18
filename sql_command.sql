CREATE TABLE users (
  id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
  user_name  TEXT NOT NULL,
  passw TEXT NOT NULL

)

commit;

INSERT INTO 'users' ('user_name' , 'passw') VALUES ('volodymyr', '1q2w3e4r5t')
commit;

select * from users