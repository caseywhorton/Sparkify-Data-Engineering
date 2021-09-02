<img src="images/weston-mackinnon-3pCRW_JRKM8-unsplash (1).jpg" width="1250" height="250">
Photo by <a href="https://unsplash.com/@betteratf8?utm_source=unsplash&utm_medium=referral&utm_content=creditCopyText">Weston MacKinnon</a> on <a href="https://unsplash.com/s/photos/sheet-music?utm_source=unsplash&utm_medium=referral&utm_content=creditCopyText">Unsplash</a>

# Sparkify Songplay Data ETL and Data Modeling

## Introduction

This project is intended to migrate **Sparkify** platform song and artist data to a postgres database hosted on an Amazon redshift cluster, create a descriptive set of records of **Sparkify** platform song plays, and a relational data model that allows for convenient ad-hoc analysis of data. This project extracts data from a S3 storage location to a staging area on Amazon Redshift, transforms and loads into a relational data model.

## Table of Contents
+ Installation
+ Usage
+ Configuration
+ Staging Tables
+ Database Design
+ ETL Process
+ Files
    + dwh.cfg
    + create_tables.py
    + etl.py
    + sql_queries.py

## Installation

**Python 3**

`pip install pyscopg2`

## Usage

Setup the configuration file (dwh.cfg)

From the command line, run these commands:

`$ python create_tables.py`

`$ python etl.py`

## Configuration

### Configuration Parameters

The _dwh.cfg_ file contains the parameters for the following areas:

+ Amazon Redshift Cluster
    + Database Host/Endpoint, Port and Name
    + Database username, password
+ IAM Role in Amazon Web Services
    + Amazon Resource Name (ARN) for Redshift role
+ S3 Bucket Data
    + Bucket names / file paths

Configuration parameters are used in the python modules.

### Redshift Cluster

A single node cluster with a single dc2 large node is being used. 

### IAM Role

You will need S3 read access to copy files from S3 to the staging tables. Refer to this link on setting up an IAM role on AWS: https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles_create_for-service.html.

The only permission the role needs is the AmazonS3ReadOnlyAccess. View this ARN: **arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess**, below is the policy in JSON format:
`
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "s3:Get*",
                "s3:List*"
            ],
            "Resource": "*"
        }
    ]
}
`

## Staging Tables

Two (2) staging tables are used for the data extracted from S3:

+ stg_events
    + Data from the S3 bucket using the LOG_DATA path
+ stg_songs
    + Data from the S3 bucket using the SONG_DATA path

### Staging Table Design

Staging Table: **stg_events**

Type | Column | Type
-----|--------|------
null | artist | varchar
null | auth | varchar
null | firstname | varchar
null | gender | varchar
null | iteminsession | bigint
null | lastname | varchar
null | length | decimal
null | level | varchar
null | location | varchar
null | method | varchar
null | page | varchar
null | registration | decimal
null | sessionid | int
null | song | varchar
null | status | int
null | ts | bigint
null | useragent | varchar
null | userid | int

Staging Table: **stg_songs**

Type | Column | Type
-----|--------|------
null | num_songs | int
null | artist_id | varchar
null | artist_latitude | decimal
null | artist_longitude | decimal
null | artist_name | varchar 
null | song_id | varchar
null | title | varchar
null | duration | decimal
null | year | int

## Database Design

The **Sparkify** database consists of 5 separate tables linked by primary and foreign keys. Below are descriptions of the tables and schema. 

Table: **songplay**

Contains data to show the songs listened to by **Sparkify** platform users. Also shows the time and location of when and where the user listened to the song.

Type | Column | Type
-----|--------|------
PK | songplay_id | int
FK | start_time | timestamp
FK | user_id | int
null | level | varchar
FK | song_id | varchar
FK | artist_id | varchar
null | session_id | varchar
null| location | varchar
null | user_agent | varchar

Table: **dim_user** 

Contains data on the Sparkify platform user.

Type | Column | Type
-----|--------|------
PK | user_id | int
null | first_name | varchar
null | last_name | varchar
null | gender | varchar
null | level | varchar

Table: **dim_song**

Contains song data.

Type | Column | Type
-----|--------|------
PK | song_id | varchar
null | title | varchar
FK | artist_id | varchar
null | year | int
null | duration | decimal
 
Table: **dim_artist**

Contains artist data.

Type | Column | Type
-----|--------|------
PK | artist_id | varchar
null | name | varchar
null | location | varchar
null | latitude | varchar
null | longitude | varchar

Table: **dim_time**

Contains timestamp data from song listens as well as other time related.

Type | Column | Type
-----|--------|------
PK | start_time | timestamp
null | hour | int
null | day | int
null | week | int
null | month | int
null | year | int
null | weekday | int

## ETL Process

1. Drop tables if they exist
    + Drop staging, fact, and dimension tables
2. Create tables if they do not exist
    + Create staging, fact, and dimension tables
3. Copy from S3 to staging tables
    + Copy files from LOG_DATA filepath to stg_events
    + Copy files from SONG_DATA filepath to stg_songs
4. Insert data from staging tables into fact and dimension tables
    + stg_events and stg_songs (join) **=>** find artist_id and song_id from artist and song tables **=>** insert artist, song, and songplay data into songplay table (fact table)
    + stg_events **=>** insert user data into dim_user
    + stg_songs **=>** insert song data into dim_song
    + stg_songs **=>** insert artist data into dim_artist
    + stg_events **=>** extract timestamp and time information from songplay, insert into dim_time

## Files

**dwh.cfg**

Configuration (config) file containing parameters needed for S3 bucket filepaths, AWS Redshift Cluster and IAM role.

**create_tables.py**

Python module that drops tables if they exist and creates them in the database using queries from _sql_queries_.

**etl.py**

Python module that moves songplay, song and artist data from the song_data and log_data folders and inserts data into the songplay table.

**sql_queries.py**

Python module that contains all SQL queries for table creation and inserts.
