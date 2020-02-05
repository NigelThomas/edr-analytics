import random
import time
import argparse
import csv

parser = argparse.ArgumentParser()
parser.add_argument("-c","--subscriber_count", type=int, default=1000, help="number of subscribers to be created")
parser.add_argument("-o","--output_time", type=int, default=10000, help="number of seconds of calls")
parser.add_argument("-r","--call_rate", type=int, default=10, help="max number of calls per second")
parser.add_argument("-u","--upgrade_prob", type=int, default=5, help="integer pct probability of upgrade")

parser.add_argument( "-k", "--trickle", default=True, action='store_true', help="Trickle one second of data each second")
parser.add_argument( "-n", "--no_trickle", default=False, dest='trickle', action='store_false', help="No trickling - emit data immediately")

parser.add_argument('-t', '--tac_file', default='./test/tac.csv', help='input: TAC database for generating random TACs')
parser.add_argument('-T', '--tac_count', default=0, help='Number of distinct TACs')
parser.add_argument('-s', '--subscriber_file', default='./subscribers.csv', help='output: initial list of generated subscribers')
parser.add_argument('-e', '--edr_file', default='./calldata.csv', help='output: generated file of EDRs')

args = parser.parse_args()


# TAC|Marketing Name|Manufacturer (or) Applicant|Bands|5G Bands|LPWAN|Radio Interface|Brand Name|Model Name|Operating System|NFC|Bluetooth|WLAN|Device Type|Removable UICC|Removable EUICC|NonRemovable UICC|NonRemovable EUICC|Simslot|Imeiquantitysupport

tacs = []
tac_descs = []
tac=0

with open(args.tac_file, "r") as tf:
    tfreader = csv.DictReader(tf, delimiter='|')

    for row in tfreader:
        tac_desc = {'code':row['TAC'],'model':row['Model Name'],'band':row['Bands']}
        tac_descs.append(tac_desc)
        tacs.append(tac)

        tac += 1
        if args.tac_count > 0 and tac >= args.tac_count:
            break

    tf.close()

# just number the subscribers
# treat subscriber number as msisdn
subscribers = [i for i in range(args.subscriber_count)]

subscriber_tacs = []
subscriber_tacnos = []
subscriber_imeis = []

# Generate the initial list of subscribers and IMEIs

sf = open(args.subscriber_file,"w")


sf.write("msisdn|imei|band\n")

for sub in range(len(subscribers)):
    tac = random.randrange(len(tacs))
    subscriber_tacs.append(tac)
    subscriber_tacnos.append(1)
    imei = "%s-%05d-%04d" % (tac_descs[subscriber_tacs[sub]]['code'], sub , subscriber_tacnos[sub])
    subscriber_imeis.append(imei)
    tac_desc = tac_descs[tac]
    band = tac_desc['band']

    # has the subscriber previously been given the promotion
    promoted = random.choice(['Y','N'])


    sf.write("%010d|%s|%s|%s\n"% (sub, imei, band, promoted))

sf.close



# Now generate calls for random TACs every second

startsecs = time.time()

# Generate data for this many "seconds"

ef = open(args.edr_file,"w")

ef.write("calltime|msisdn|imei|band|upg_imei\n")

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

        ef.write("%010d|%010d|%s|%s|%d\n"% (calltime+startsecs, sub, imei, band, upgrade_imei))
    
   
    # If we want to trickle the data:
    if args.trickle:
        # keep pushing data out
        ef.flush()
        time.sleep(1)

ef.close()

