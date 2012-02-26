import sqlite3, json

conn = sqlite3.connect('./rettiwt.db')
curse = conn.cursor()
base = curse.execute("select uid, following, followers from gotcha")
dup = set([])
nodes = ""
edges = ""
edgeID = ""
for user in base:
    uid = user[0];
    following = json.loads(user[1])
    followers = json.loads(user[2])
    nodes += "<node id='n"+uid+"'/>\n"
    for toid in following:
        edgeID = str(uid)+"."+str(toid)
        if(edgeID not in dup):
            edges += "<edge id='e"+edgeID+"' source='"+str(uid)+"' target='"+str(toid)+"'/>\n"
            dup.add(edgeID)
    for fromid in followers:
        edgeID = str(fromid)+"."+str(uid)
        if(edgeID not in dup):
            edges += "<edge id='e"+edgeID+"' source='"+str(fromid)+"' target='"+str(uid)+"'/>\n"
            dup.add(edgeID)
        
graphml = "<graphml edgedefault='undirected'>\n<graph>\n" + nodes + edges + "</graph>\n</graphml>";
print graphml