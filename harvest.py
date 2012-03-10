import os, base64, time, urllib, hashlib, hmac, urllib2, re, json, sqlite3, sys

class twitterError(Exception):
    def __init__(self, desc, code):
        self.value = desc
        self.code = code
        
    def __str__(self):
        return repr(self.value)

def api(url, args):
    base = "https://api.twitter.com/1/"
    url = base + url
    consumer_key = "D9UDOREUonmfuA67RFJ0A"
    consumer_secret = "bk1bI1U4tM8XTBkz3bFciM6pWW5tygdNsOESNSk" #shouldn't really be public
    access_token = "490379139-ksKju3iLmWfd66JTdZWnqFEE7qSR1ueAKllO6QOn"
    access_secret = "uL2iAXr7EOUgkXgQMxHx1smocuGisByVldhm0GMGCI" #shouldn't really be public
    signature_method = "HMAC-SHA1"
    oauth_version = "1.0"
    digest_maker = hmac.new(urllib.quote(consumer_secret)+'&'+urllib.quote(access_secret), '', hashlib.sha1)
    nonce = base64.b16encode(os.urandom(16))
    timestamp = time.time()
    HTTP_method = "GET"
    paramstring = ""

    params =  {
            "oauth_consumer_key":consumer_key,
            "oauth_nonce":nonce,
            "oauth_signature_method":signature_method,
            "oauth_timestamp":timestamp,
            "oauth_token":access_token,
            "oauth_version":oauth_version
        }
    params = dict(args.items() + params.items())
        
    for k, v in params.iteritems():
        params[k] = urllib.quote(str(v))
        
    for key in sorted(params):
        paramstring +=key + "=" + params[key] + '&'
        
    paramstring = paramstring[:-1]
    output = HTTP_method+'&'+urllib.quote(url, '')+'&'+urllib.quote(paramstring, '');
    digest_maker.update(output)
    signature = base64.encodestring(digest_maker.digest())[:-1]

    finalString = "OAuth oauth_consumer_key=\""+consumer_key+"\", \
oauth_nonce=\""+urllib.quote(nonce)+"\", \
oauth_signature=\""+urllib.quote(signature)+"\", \
oauth_signature_method=\""+signature_method+"\", \
oauth_timestamp=\""+str(timestamp)+"\", \
oauth_token=\""+access_token+"\", \
oauth_version=\""+oauth_version+"\""
    url+="?"
    for k, v in args.iteritems():
        url += urllib.quote(k)+"="+urllib.quote(v)+"&"
    url = url[:-1]
    headers = {'Authorization' : finalString}
    fails = 0
    while(fails < 20):
        try:
            req = urllib2.Request(url, None, headers)
            response = urllib2.urlopen(req)
            the_page = response.read()
            break
        except urllib2.HTTPError as error:
            if(error.code == 401 or error.code == 404):
                raise twitterError('Protected/deleted user', 1)
            elif(error.code == 502 or error.code == 503 or error.code == 500):
                fails +=1
                print "Bad gateway on attempt "+str(fails)+""
                if(fails >= 5):
                    print 'Too many 50X errors, taking a nap'
                    time.sleep(pow(2, (fails)))
                continue
            elif(error.code == 400):
                status = api("account/rate_limit_status.json", {})["reset_time_in_seconds"]-time.time()
                print "Rate limit hit. Sleeping for "+str(status)+" seconds"
                time.sleep(status)
                continue
            else:
                print url
                raise
    return json.loads(the_page)

def fetchUsers(url, args):
    cursor = "-1"
    followers = []
    while(cursor != "0"):
        try:
            data = api(url, args)
        except twitterError:
            break
        followers = followers + data['ids']
        cursor = data['next_cursor_str']
        args["cursor"] = cursor
    return followers
    
def fetchTweets(url, args):
    page = 1
    tweets = []
    data = ["z"]
    while(data != []):
        try:
            data = api(url, args)
        except twitterError:
            break
        tweets = tweets + data
        page+=1
        args["page"]=str(page)
    return tweets
        
        

maxSize = 50000
conn = sqlite3.connect('./rettiwt.db')
curse = conn.cursor()
try:
    print curse.execute("select done from state").fetchone()[0]
    done = set(json.loads(curse.execute("select done from state").fetchone()[0]))
    queue = json.loads(curse.execute("select queue from state").fetchone()[0])
except sqlite3.OperationalError:
    curse.execute("create table gotcha (uid text, targetinfo text, following text, followers text, tweets text)") #a smarter db design might help
    curse.execute("create table state (done text, queue text)")
    curse.execute("insert into state values ('', '')")
    target = sys.argv[1]
    target = api("users/lookup.json",{"screen_name":target})[0]["id"]
    done = set([])
    queue = [target]

while(True):
    fails = 0
    target = queue.pop(0)
    done.add(target)
    try:
        targetinfo = api("users/lookup.json",{"user_id":str(target)})
        followers = set(fetchUsers("followers/ids.json", {"user_id":str(target)})) #gets all followers
        following = set(fetchUsers("friends/ids.json", {"user_id":str(target)})) #gets all following
    except twitterError:
        print "Skipping protected user"
        continue
    tweets = fetchTweets("statuses/user_timeline.json", {"count":"200","trim_user":"true", "user_id":str(target), "include_rts":"true"}) #randomly drops a few tweets
    if(len(queue) < maxSize):
        queue += (list((following & followers)-done-set(queue)))
        queue += (list((following ^ followers)-done-set(queue)))
    while (fails < 15):
        try:
            curse.execute('insert into gotcha values (?, ?, ?, ?, ?)', (json.dumps(target), json.dumps(targetinfo), json.dumps(list(following)), json.dumps(list(followers)), json.dumps(tweets)))
            curse.execute('update state set done=?, queue=?', (json.dumps(list(done)), json.dumps(queue)))
            conn.commit()
            break
        except sqlite3.OperationalError:
            fails+=1
            print 'Database write error #'+str(fails)+', taking a nap'
            time.sleep(pow(2, (fails)))
    print len(done)





#print fetchTweets("statuses/retweeted_by_user.json", {"count":"100", "trim_user":"true", "screen_name":target}) #gets 100 retweets, unknown cap
   



