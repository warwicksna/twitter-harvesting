#delete from gotcha where uid=127567007;  << way to break everything
import sqlite3, json, sys

conn = sqlite3.connect("./rettiwt.db")
curse = conn.cursor()
base = curse.execute("select uid, following, followers, targetinfo from gotcha limit 3000")
dupedges = set([])
dupnodes = set([])
nodes = ""
edges = ""
edgeID = ""
print "<graphml edgedefault=\"directed\">\n<key id=\"name\" for=\"edge\" attr.name=\"name\" attr.type=\"string\"/>\n<graph edgedefault=\"directed\">"
for user in base:
    uid = user[0];
    name = json.loads(user[3])[0]["screen_name"]
    print "<node id=\""+uid+"\"><data key=\"name\">"+name+"</data></node>"
    dupnodes.add(str(uid))
#print dupnodes
base = curse.execute("select uid, following, followers, targetinfo from gotcha")
i=0
for user in base:
    i+=1
    if(i%1000 == 0):
        sys.stderr.write(str(i)+"\n")
    uid = user[0];
    following = json.loads(user[1])
    followers = json.loads(user[2])
    for toid in following:
        edgeID = str(uid)+"."+str(toid)
        if(edgeID not in dupedges and str(toid) in dupnodes and str(uid) in dupnodes):
            print "<edge  source=\""+str(uid)+"\" target=\""+str(toid)+"\"/>" #id=\"e"+edgeID+"\"
            dupedges.add(edgeID)
    for fromid in followers:
        edgeID = str(fromid)+"."+str(uid)
        if(edgeID not in dupedges and str(fromid) in dupnodes and str(uid) in dupnodes):
            print "<edge  source=\""+str(fromid)+"\" target=\""+str(uid)+"\"/>" #id=\"e"+edgeID+"\"
            dupedges.add(edgeID)
        
base = curse.execute("select uid, tweets, followers, following from gotcha limit 3000")
i=0
for user in base:
    i+=1
    if(i%100 == 0):
        sys.stderr.write(str(i)+"\n")
    uid = json.loads(user[0])
    for tweet in json.loads(user[1]):
        if("retweeted_status" in tweet):
            toid = tweet["retweeted_status"]["user"]["id"]
        else:
            toid = tweet["in_reply_to_user_id"]
        if(toid):
            edgeID = str(uid)+"."+str(toid)
            if(edgeID not in dupedges and str(toid) in dupnodes and str(uid) in dupnodes): #assumes direction is irrelevant; (check user[2] only otherwise)
                print "<edge source=\""+str(uid)+"\" target=\""+str(toid)+"\"/>"
                dupedges.add(edgeID)

print "</graph>\n</graphml>";