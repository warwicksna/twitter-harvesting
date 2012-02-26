import sqlite3, json, time, base64

conn = sqlite3.connect("./rettiwt.db")
curse = conn.cursor()
base = curse.execute("select uid, tweets from gotcha")
tid = 0;
for user in base:
    uid = json.loads(user[0])
    for tweet in json.loads(user[1]):
        if(tweet["in_reply_to_user_id"]):
            tid+=1
            timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.strptime(tweet['created_at'],'%a %b %d %H:%M:%S +0000 %Y'))
            data = base64.b64encode(tweet["text"].encode('utf-8'))
            print "INSERT INTO `MessageProperties` VALUES("+str(tid)+", '"+data+"', '"+timestamp+"', 1, NULL);" #data MUST be escaped
            print "INSERT INTO `MessageReceive` VALUES("+str(tid)+", "+str(tweet["in_reply_to_user_id"])+");"
            print "INSERT INTO `MessageSend` VALUES("+str(tid)+", "+str(uid)+");"
            print

