# KumoRailT Project

New version of kumoRail, the back-end software for kumoRail WeChat public account.

We aims to provide more convenience for passengers, with schedule & status history & EMU type and so on.

It is based on Python tornado and Mariadb.

## Users' Guide

1. Send Train Number to the account directly, you will get the basic info.

2. Send Train Number and one of the arrival station, you will get the arrival history.

## Developers' Guide 

### Install & Run

Run deploy.sh and follow the steps to deploy the code. (Under construction)

### About the Code

The code contains 4 parts:
1. Database interface.
    1. There are 9 database models divided into 6 parts. 
    2. The dbmaria2 module contains the base class of database interface and provides generic functions
       for upper modules to access to the database.
    3. The staInfo module defines the table that holds data of stations.
    4. The depot module holds depots' names. 
       "Seq" means sequence, all trains in an operation cycle.
    5. Train table contains the actual number & operation number & train class of a train.
       Train Code is a 12-bytes string used by the online ticket system to label the train uniquely.
    6. Arrival table contains each station in a train's schedule.
    7. The "actArr" & "subArr" table is used to record actual arrival time of trains.
    
2. Server progress and Message handler.
    1. We are using Python tornado frame to handle base web requests. They are in server.py.
    2. "Parse" module in parse/ will handle the message passed by server.py
       and classify them, then call "hlsearch" module to execute the query and generate an answer.
    3. The format and encrypt module is provided by WeChat.
    
3. Data Collecter.
    1. They are called "hook". There are 4 hooks here.
    
4. Other Tools.
    (Under Construction)
  
### EMU Sequence getter

   (Under Construction) 
    