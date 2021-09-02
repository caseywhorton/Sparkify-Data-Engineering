import configparser

# CONFIG
config = configparser.ConfigParser()
config.read('dwh.cfg')

# DROP TABLES

staging_events_table_drop = "DROP TABLE IF EXISTS stg_events"
staging_songs_table_drop = "DROP TABLE IF EXISTS stg_songs"
songplay_table_drop = "DROP TABLE IF EXISTS songplay"
user_table_drop = "DROP TABLE IF EXISTS dim_user"
song_table_drop = "DROP TABLE IF EXISTS dim_song"
artist_table_drop = "DROP TABLE IF EXISTS dim_artist"
time_table_drop = "DROP TABLE IF EXISTS dim_time"

# CREATE TABLES

# S3 to Redshift staging table for log data
staging_events_table_create= ("""
CREATE TABLE IF NOT EXISTS stg_events
(
    artist varchar NULL,
    auth varchar NULL,
    firstname varchar NULL,
    gender varchar NULL,
    iteminsession bigint NULL,
    lastname varchar NULL,
    length decimal NULL,
    level varchar NULL,
    location varchar NULL,
    method varchar NULL,
    page varchar NULL,
    registration decimal NULL,
    sessionid int NULL,
    song varchar NULL,
    status int NULL,
    ts bigint NULL,
    useragent varchar NULL,
    userid int NULL
)
""")

# S3 to Redshift staging table for song data JSON files
staging_songs_table_create = ("""
CREATE TABLE IF NOT EXISTS stg_songs
(
    num_songs int NULL,
    artist_id varchar NULL,
    artist_latitude decimal NULL,
    artist_longitude decimal NULL,
    artist_name varchar NULL, 
    song_id varchar NOT NULL,
    title varchar NULL,
    duration decimal NULL,
    year int NULL
)
""")

# Create table for songplay information (fact table)
songplay_table_create = ("""
CREATE TABLE IF NOT EXISTS songplay 
    (
    songplay_id int NOT NULL GENERATED ALWAYS AS IDENTITY,
    start_time varchar NULL,
    user_id varchar NOT NULL,
    level varchar NULL,
    song_id varchar NOT NULL,
    artist_id varchar NOT NULL,
    session_id varchar NOT NULL,
    location varchar NULL,
    user_agent varchar NULL
    )
""")

# Create table for user information in the log data (dimension table)
user_table_create = ("""
CREATE TABLE IF NOT EXISTS dim_user
    (
    user_id int NOT NULL PRIMARY KEY,
    first_name varchar NULL,
    last_name varchar NULL,
    gender varchar NULL,
    level varchar NULL
    )
""")

# Create table for songs in the song data (dimension table)
song_table_create = ("""
CREATE TABLE IF NOT EXISTS dim_song
    (
    song_id varchar NOT NULL PRIMARY KEY,
    title varchar NULL,
    artist_id varchar NOT NULL,
    year int NULL,
    duration decimal NULL
    )
""")

# Create table for artists in the song data (dimension table)
artist_table_create = ("""
CREATE TABLE IF NOT EXISTS dim_artist
    (
    artist_id varchar NOT NULL PRIMARY KEY,
    name varchar NULL,
    location varchar NULL,
    lattitude decimal NULL,
    longitude decimal NULL
    )
""")

# Create table for start times and date information from log data (dimension table)
time_table_create = ("""
CREATE TABLE IF NOT EXISTS dim_time
    (
    start_time varchar NOT NULL PRIMARY KEY,
    hour int NOT NULL,
    day int NOT NULL,
    week int NOT NULL,
    month int NOT NULL,
    year int NOT NULL,
    weekday int NOT NULL
    )
""")

# STAGING TABLES

# Copy log data to the stg_events table
staging_events_copy = ("""
copy stg_events
    from 's3://udacity-dend/log_data'
credentials 'aws_iam_role={}' 
compupdate on
format as json 'auto ignorecase'
region 'us-west-2';
""").format(config['IAM_ROLE']['ARN'])

# Copy song data to the stg_songs table
staging_songs_copy = ("""
copy stg_songs from 's3://udacity-dend/song_data' 
credentials 'aws_iam_role={}'  
compupdate on
format as json 'auto ignorecase'
region 'us-west-2';
""").format(config['IAM_ROLE']['ARN'])

# FINAL TABLES

# Insert songplay information into songplay table (fact table)
songplay_table_insert = ("""
INSERT INTO songplay
    (
    start_time,
    user_id,
    level,
    song_id,
    artist_id,
    session_id,
    location,
    user_agent
    )
SELECT 
    e.ts,
    e.userid,
    e.level,
    s.song_id,
    s.artist_id,
    e.sessionid,
    e.location,
    e.useragent
FROM stg_events as e
JOIN stg_songs as s
ON e.artist = s.artist_name
AND e.song = s.title
""")

# Insert user information into the dim_user table (dimension table)
user_table_insert = ("""
INSERT INTO dim_user
SELECT
    DISTINCT userid,
    firstname,
    lastname,
    gender,
    level
FROM stg_events
where userid is not null
""")

# Insert user information into the dim_song table (dimension table)
song_table_insert = ("""
INSERT INTO dim_song
SELECT
    DISTINCT song_id,
    title,
    artist_id,
    year,
    duration
FROM stg_songs
""")

# Insert user information into the dim_artist table (dimension table)
artist_table_insert = ("""
INSERT INTO dim_artist
SELECT
    DISTINCT s.artist_id,
    s.artist_name,
    e.location,
    s.artist_latitude,
    s.artist_longitude
FROM stg_songs as s
JOIN stg_events as e
ON s.artist_name = e.artist
""")

# Insert user information into the dim_time table (dimension table)
time_table_insert = ("""
INSERT INTO dim_time
SELECT
    ts,
    EXTRACT(HOUR from (TIMESTAMP 'epoch' + (ts/1000)*INTERVAL '1 second')),
    EXTRACT(DAY from (TIMESTAMP 'epoch' + (ts/1000)*INTERVAL '1 second')),
    EXTRACT(WEEK from (TIMESTAMP 'epoch' + (ts/1000)*INTERVAL '1 second')),
    EXTRACT(MONTH from (TIMESTAMP 'epoch' + (ts/1000)*INTERVAL '1 second')),
    EXTRACT(YEAR FROM (TIMESTAMP 'epoch' + (ts/1000)*INTERVAL '1 second')),
    EXTRACT(DOW from (TIMESTAMP 'epoch' + (ts/1000) * INTERVAL '1 second'))
from stg_events
""")

# QUERY LISTS

# list of query names to create teables if they do not exist
create_table_queries = [staging_events_table_create, staging_songs_table_create, songplay_table_create, user_table_create, song_table_create, artist_table_create, time_table_create]

# list of query names to drop tables if they exist
drop_table_queries = [staging_events_table_drop, staging_songs_table_drop, songplay_table_drop, user_table_drop, song_table_drop, artist_table_drop, time_table_drop]

# list of copy statements for moving data from S3 to Redshift
copy_table_queries = [staging_events_copy, staging_songs_copy]

# list of query names that insert rows into tables in schema
insert_table_queries = [songplay_table_insert, user_table_insert, song_table_insert, artist_table_insert, time_table_insert]