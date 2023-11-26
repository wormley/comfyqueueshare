import requests
import json
import sys
import os
import time
import random

delay=10
long_delay =delay*6

dorandom=0
if ( sys.argv[1] == "random" ):
    dorandom=1
    sys.argv.pop(1) 

# Primary queue is first argument
pri = sys.argv[1]
# Secondary queues follow
sec = sys.argv[2:]


skip={}
while(1):
    moved=0
    try:
        # check to see if there's any pending items
        pri_info = requests.get(pri+"/prompt").json()
        queue_remaining=pri_info['exec_info']['queue_remaining']
        if (queue_remaining <2 ):
            time.sleep(delay)
            continue
        print(time.asctime()+": Found "+str(queue_remaining)+" items in queue, checking for available secondaries")
    except Exception as error: 
        print("Exception on primary: ", error)
        print("Delaying before reattempt")
        time.sleep(long_delay)
        continue

    # walk the list of secondary queues, look for any that are
    # empty and have no running jobs
    for i in sec:
        try:
            if (i in skip):
               skip[i]=skip[i]-1
               if (skip[i] <= 0 ):
                  del skip[i]
               else:
                  continue
            info = requests.get(i+"/prompt").json()
            if (info['exec_info']['queue_remaining'] != 0 ):
                continue
        except:
            print("Error while checking: "+i)
            print("Possible node outage")
            skip[i]=3
            continue
        queue = requests.get(i+"/queue").json()
        if (len(queue['queue_running']) > 0 ):
            continue
        print("Secondary: "+i+" has queue space, attempting to move prompt")
        # now, attempt to grab a primary item
        pri_queue = requests.get(pri+"/queue").json()
        if (len(pri_queue['queue_pending']) == 0 ):
            # Take a break, nothing to pass on, let the outer loop... well... loop
            break
        if (dorandom):
            our_item = random.choice(pri_queue['queue_pending'])
        else:
            our_item = pri_queue['queue_pending'][0]
        pri_uuid = our_item[1]
        # attempt to delete
        d = requests.post(pri+"/queue", json={"delete": [pri_uuid]})
        print(d.text)
        # sadly, that doesn't return a useful status code, so we check the queue again
        # if it's been moved to running then we lost the race
        time.sleep(2)
        pri_queue = requests.get(pri+"/queue").json()
        if (pri_queue['queue_running'][0][1] == pri_uuid):
            # too slow
            continue
        # finally, send the item to the designated secondary
        new_req = requests.post(i+"/prompt", json={"prompt":our_item[2] })
        print("sent prompt: "+(new_req.text))
        moved=1
    if (moved == 0 ):
        # all queues full, take a little nap
        #print("No objects moved, queues likely full")
        time.sleep(delay)
