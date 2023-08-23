DROP TABLE IF EXISTS users;
 
/* no need for primary keys because rowid exist in sqlite3 */ 

CREATE TABLE IF NOT EXISTS users (
    user_id VARCHAR(255) NULL UNIQUE,
    reminder BOOLEAN DEFAULT 0,
    reminder_settings VARCHAR(255) NULL
);

DROP TABLE IF EXISTS events;
 
CREATE TABLE IF NOT EXISTS events (
    event_id VARCHAR(255)  NULL UNIQUE,
    event_url VARCHAR(255)  NULL UNIQUE,
    event_title VARCHAR(255) NULL,
    time_start VARCHAR(255) NULL,
    time_finish VARCHAR(255) NULL,
    channel_id VARCHAR(255) NULL UNIQUE,
    channel_name VARCHAR(255) NULL UNIQUE,
    ended_status BOOLEAN DEFAULT 0,
    ctf_password VARCHAR(255) NULL,
    archived BOOLEAN DEFAULT 0

); 

DROP TABLE IF EXISTS join_requests;

CREATE TABLE IF NOT EXISTS join_requests (
    user_id VARCHAR(255) NULL,
    event_id VARCHAR(255) NULL,
    join_state BOOLEAN DEFAULT 0
);