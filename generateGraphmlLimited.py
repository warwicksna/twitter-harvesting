import sqlite3, json

conn = sqlite3.connect("./rettiwt.db")
curse = conn.cursor()
base = curse.execute("select uid, following, followers, targetinfo from gotcha")
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
for user in base:
    uid = user[0];
    following = json.loads(user[1])
    followers = json.loads(user[2])
    for toid in following:
        edgeID = str(uid)+"."+str(toid)
        if(edgeID not in dupedges and str(toid) in dupnodes):
            print "<edge  source=\""+str(uid)+"\" target=\""+str(toid)+"\"/>" #id=\"e"+edgeID+"\"
            dupedges.add(edgeID)
    for fromid in followers:
        edgeID = str(fromid)+"."+str(uid)
        if(edgeID not in dupedges and str(fromid) in dupnodes):
            print "<edge  source=\""+str(fromid)+"\" target=\""+str(uid)+"\"/>" #id=\"e"+edgeID+"\"
            dupedges.add(edgeID)
        
print "</graph>\n</graphml>";