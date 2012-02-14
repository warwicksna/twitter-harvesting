import os, base64, time, urllib, hashlib, hmac, urllib2, re, json

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
    nonce = base64.urlsafe_b64encode(os.urandom(32))
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
    output = HTTP_method+'&'+urllib.quote(url)+'&'+urllib.quote(paramstring);
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
    while(fails < 5):
        try:
            req = urllib2.Request(url, None, headers)
            response = urllib2.urlopen(req)
            the_page = response.read()
            break
        except urllib2.HTTPError as error:
            if(error.code == 401):
                raise twitterError('Protected user', 1)
            elif(error.code == 502):
                fails +=1
                print "Bad gateway on attempt "+str(fails)+""
                continue
            elif(error.code == 400):
                print "Rate limit hit. Time for a nap."
                time.sleep(json.loads(api("account/rate_limit_status.json", {}))["reset_time_in_seconds"])
                continue
            else:
                print url
                raise
    return the_page

def fetchUsers(url, args):
    cursor = "-1"
    followers = []
    while(cursor != "0"):
        try:
            data = json.loads(api(url, args))
            followers = followers + data['ids']
        except twitterError:
            print "Skipping protected user"
            break
        cursor = data['next_cursor_str']
        args["cursor"] = cursor
    return followers
    
def fetchTweets(url, args):
    page = 1
    tweets = []
    data = ["z"]
    while(data != []):
        time.sleep(5)
        data = json.loads(api(url, args))
        tweets = tweets + data
        page+=1
        args["page"]=str(page)
    return tweets
        
        
#TODO return json instead of string from api()
#save data&state to tables

#use calls from https://dev.twitter.com/docs/api

print api("account/rate_limit_status.json", {}) #the hourly limit is 150?. It should be 350.

target = "uaf"  #how appropriate
target = json.loads(api("users/lookup.json",{"screen_name":target}))[0]["id"]
done = set([])
queue = [target]

while(True):
    target = queue.pop(0)
    done.add(target)
    followers = set(fetchUsers("followers/ids.json", {"user_id":str(target)})) #gets all followers
    following = set(fetchUsers("friends/ids.json", {"user_id":str(target)})) #gets all following
   #    save their tweets
   
    queue += (list((following & followers)-done))
    queue += (list((following ^ followers)-done))
    print done
    print len(queue)





#print fetchTweets("statuses/user_timeline.json", {"count":"200","trim_user":"true", "screen_name":target}) #randomly drops a few tweets
#print fetchTweets("statuses/retweeted_by_user.json", {"count":"100", "trim_user":"true", "screen_name":target}) #gets 100 retweets, unknown cap



