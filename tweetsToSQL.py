import sqlite3, json, time, base64

conn = sqlite3.connect("./rettiwt.db")
curse = conn.cursor()
base = curse.execute("select uid, tweets, followers, following from gotcha")
tid = 0;
for user in base:
    uid = json.loads(user[0])
    for tweet in json.loads(user[1]):
        followers = json.loads(user[2])
        following = json.loads(user[3])
        
        if("retweeted_status" in tweet):
            toid = tweet["retweeted_status"]["user"]["id"]
        else:
            toid = tweet["in_reply_to_user_id"]
            
        if(toid):
            tid+=1
            if(toid not in followers and toid not in following): #assumes direction is irrelevant; (check user[2] only otherwise)
                print "INSERT INTO `Connected` VALUES("+str(tid)+", "+str(toid)+", 1, 0);"
            
            timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.strptime(tweet['created_at'],'%a %b %d %H:%M:%S +0000 %Y'))
            data = base64.b64encode(tweet["text"].encode('utf-8'))
            print "INSERT INTO `MessageProperties` VALUES("+str(tid)+", '"+data+"', '"+timestamp+"', 1, NULL);" #data MUST be escaped
            print "INSERT INTO `MessageReceive` VALUES("+str(tid)+", "+str(toid)+");"
            print "INSERT INTO `MessageSend` VALUES("+str(tid)+", "+str(uid)+");"
            print
                

