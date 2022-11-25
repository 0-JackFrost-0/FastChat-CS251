CREATE TABLE READ(sender TEXT,receiver TEXT,message TEXT, type TEXT,time DATETIME,aes_key TEXT,grpname TEXT DEFAULT NULL);
CREATE TABLE UNREAD(sender TEXT,receiver TEXT,message TEXT, type TEXT,time DATETIME,aes_key TEXT,grpname TEXT DEFAULT NULL);
