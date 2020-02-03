import random
import time
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-s","--subscriber_count", type=int, default=1000, help="number of subscribers to be created")
parser.add_argument("-t","--output_time", type=int, default=1000, help="number of seconds of calls")
parser.add_argument("-r","--call_rate", type=int, default=10, help="max number of calls per second")
parser.add_argument("-u","--upgrade_prob", type=int, default=5, help="integer pct probability of upgrade")

parser.add_argument( "-k", "--trickle", default=False, action='store_true', help="Trickle one second of data each second?")

args = parser.parse_args()


# just number the subscribers
# treat subscriber number as msisdn
subscribers = [i for i in range(args.subscriber_count)]

tacs = [i for i in range(3)]

tac_descs = [{'code':'01233900','model':'iPhone 4', 'band':'3G'}
            ,{'code':'35357505','model':'Samsung GALAXY S3 GT-I9305','band':'LTE'}
            ,{'code':'35549706','model':'Motorola Moto G','band':'3G'}]

subscriber_tacs = []
subscriber_tacnos = []
subscriber_imeis = []

for sub in range(len(subscribers)):
    subscriber_tacs.append(random.randrange(len(tacs)))
    subscriber_tacnos.append(1)
    imei = "%s-%05d-%04d" % (tac_descs[subscriber_tacs[sub]]['code'], sub , subscriber_tacnos[sub])
    subscriber_imeis.append(imei)

# Initial status

#print subscribers
#print tacs
#print tac_descs
#print subscriber_tacs

#for sub in range(len(subscribers)):
#    print "Subscriber:"+str(sub) + ", Tac#:"+ str(subscriber_tacs[sub])+ ", Tac:" + str(tac_descs[subscriber_tacs[sub]])


# Now generate calls for random TACs every second

startsecs = time.time()

# Generate data for this many "seconds"

print "calltime,msisdn, imei,band,upg_imei\n"

for calltime in range(args.output_time):

    # Generate up to this many calls per second

    for counter in range(random.randint(1,args.call_rate)):
        # choose a random subscriber
        sub = random.randrange(len(subscribers))

        # randomly decide if the subscriber has updated his phone since the last call, with provided percentage probability
        r = random.randint(0,100)
        upgrade_imei = (r <= args.upgrade_prob)
        

        if upgrade_imei:
            subscriber_tacnos[sub] += 1
            tac = random.randrange(len(tacs))
            subscriber_tacs[sub] = tac
            imei = "%s-%05d-%04d" % (tac_descs[subscriber_tacs[sub]]['code'], sub , subscriber_tacnos[sub])
            subscriber_imeis[sub] = imei
        else:
            tac = subscriber_tacs[sub]
            imei = subscriber_imeis[sub]
        
        tac_desc = tac_descs[tac]
        band = tac_desc['band']

        print "%010d,%010d,%s,%s,%d"% (calltime+startsecs, sub, imei, band, upgrade_imei)
    
    # If we want to trickle the data:
    if args.trickle:
        time.sleep(1)



