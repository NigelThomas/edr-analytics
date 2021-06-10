import random
import time
import argparse
import csv
import math

parser = argparse.ArgumentParser()
parser.add_argument("-c","--subscriber_count", type=int, default=10000, help="number of subscribers to be created")
parser.add_argument("-o","--output_time", type=int, default=10000, help="number of seconds of calls")
parser.add_argument("-r","--call_rate", type=int, default=1000, help="max number of calls per minute")
parser.add_argument("-u","--upgrade_prob", type=int, default=5, help="integer pct probability of upgrade")
parser.add_argument("-m","--output_minutes", type=int, default=200, help="minutes of data")

parser.add_argument( "-k", "--trickle", default=True, action='store_true', help="Trickle one second of data each second")
parser.add_argument( "-n", "--no_trickle", default=False, dest='trickle', action='store_false', help="No trickling - emit data immediately")

parser.add_argument('-t', '--tac_file', default='./test/tac.csv', help='input: TAC database for generating random TACs')
parser.add_argument('-T', '--tac_count', default=0, help='Number of distinct TACs')
parser.add_argument('-s', '--subscriber_file', default='./subscribers.csv', help='output: initial list of generated subscribers')
parser.add_argument('-e', '--edr_file', default='./calldata.csv', help='output: generated file of EDRs')

parser.add_argument("-g","--gridsize", type=int, default=5, help="size of grid")
parser.add_argument("-a","--active_prob", type=int, default=10, help="integer pct probability of activity")
parser.add_argument("-w","--walk_prob", type=int, default=20, help="integer pct probability of movement")
parser.add_argument("-x","--base_longitude", type=float, default=-0.157, help="Longitude bottom left")
parser.add_argument("-y","--base_latitude", type=float, default=51.523, help="Latitude bottom left")

args = parser.parse_args()


# TAC|Marketing Name|Manufacturer (or) Applicant|Bands|5G Bands|LPWAN|Radio Interface|Brand Name|Model Name|Operating System|NFC|Bluetooth|WLAN|Device Type|Removable UICC|Removable EUICC|NonRemovable UICC|NonRemovable EUICC|Simslot|Imeiquantitysupport

tacs = []
tac_descs = []
tac = 0

with open(args.tac_file, "r") as tf:
    tfreader = csv.DictReader(tf, delimiter='|')

    for row in tfreader:
        tac_desc = {'code':row['TAC'],'model':row['Model Name'],'band':row['Bands']}
        tac_descs.append(tac_desc)
        tacs.append(row['TAC'])

        tac += 1
        if args.tac_count > 0 and tac >= args.tac_count:
            break

    tf.close()

print("tac file read")

# just number the subscribers
# treat subscriber number as msisdn
subscribers = [i for i in range(args.subscriber_count)]
subscriber_recs = []

#subscriber_tacs = []
#subscriber_tacnos = []
#subscriber_imeis = []

# Generate the initial list of subscribers and IMEIs

sf = open(args.subscriber_file,"w")

# number of subdivisions x,y in each grid square to display subscribers
subsize = math.ceil(math.sqrt(args.subscriber_count))
# bottom left of display (London West End)
baseLat = args.base_latitude
baseLon = args.base_longitude
# size of grid squares
gridDeltaLon = 0.006
gridDeltaLat = 0.004
# size of sub-cells within each grid cell
subDeltaLon = gridDeltaLon/subsize
subDeltaLat = gridDeltaLat/subsize


sf.write("msisdn|imei|promoted\n")

for s in range(len(subscribers)):
    tac = tacs[random.randrange(len(tacs))]
    #subscriber_tacs.append(tac)
    #subscriber_tacnos.append(1)
    imei = "%s-%05d-%04d" % (tac, s , 1)
    #subscriber_imeis.append(imei)
    #tac_desc = tac_descs[tac]
    #band = tac_desc['band']
    promoted = random.choice(['Y','N'])
    sub={ "no": s
           , "tac": tac
           , "tacno": 1
           , "imei": imei
           , 'x': random.randint(0,args.gridsize - 1) \
           , 'y': random.randint(0,args.gridsize - 1) 
           , 'sx': (s % subsize) * subDeltaLon
           , 'sy': int(s / subsize) * subDeltaLat
           , 'promoted': promoted

    }
    subscriber_recs.append(sub)
    # has the subscriber previously been given the promotion


    #sf.write("%010d|%s|%s|%s\n"% (sub, imei, band, promoted))
    sf.write("%010d|%s|%s\n"% (s, imei, promoted))

sf.close
print("subscriber file written, starting calldata")


# Now generate calls for random TACs every second

startsecs = time.time()
startmillis = startsecs * 1000

# Generate data for this many "seconds"

ef = open(args.edr_file,"w")

#ef.write("calltime|msisdn|imei|band|upg_imei\n")
ef.write("calltime|msisdn|imei|lat|lon\n")


# Generate up to this many calls per second
color = 0

for m in range(0,args.output_minutes):
#for counter in range(random.randint(1,args.call_rate)):
    # change colour each minute
    color = (color + 1) % 10
    recno = 0
    prior_seconds = 0
    minutes_millis = m * 60000

    # choose a random subscriber

    for s in subscribers:
        sub = subscriber_recs[s]

        # randomly decide if the subscriber has updated his phone since the last call, with provided percentage probability
        r = random.randint(0,100)
        upgrade_imei = (r <= args.upgrade_prob)

        if upgrade_imei:
            sub['tacno'] += 1
            tac = tacs[random.randrange(len(tacs))]
            sub['tac']  = tac
            imei = "%s-%05d-%04d" % (tac, s , sub['tacno'])
            sub['imei'] = imei
        else:
            tac = sub['tac']
            imei = sub['imei']
        
        #tac_desc = tac_descs[tac]
        #band = tac_desc['band']

        if (random.randint(0,99) < args.walk_prob):
            # 2 directional random work zero or +/- one step each
            # So there is a 1/9 chance of not moving even when a move is selected
            sub['x'] = (sub['x'] + random.randint(0,2) - 1) % args.gridsize;
            sub['y'] = (sub['y'] + random.randint(0,2) - 1) % args.gridsize;

            # ef.write("%010d|%010d|%s|%s|%d\n"% (calltime+startsecs, sub, imei, band, upgrade_imei))

        milliseconds = (60000*recno)/args.call_rate
        seconds = milliseconds / 1000

        # is the subscriber active? 
        if (random.randint(0,99) < args.active_prob):
            # write out the record and current location
            # TODO add trailing fields
            lat = baseLat + sub['y'] * gridDeltaLat + sub['sy']
            lon = baseLon + sub['x'] * gridDeltaLon + sub['sx']
            ef.write("%010d|%010d|%s|%f|%f\n"% (startmillis+minutes_millis+milliseconds, s, imei, lat,lon))
            recno += 1

            if seconds > prior_seconds:
                ef.flush()
                time.sleep(seconds - prior_seconds)
                prior_seconds = seconds

        if recno > args.call_rate:
            break
    
   
    # If we want to trickle the data:
    if args.trickle:
        # keep pushing data out
        ef.flush()
        time.sleep(1)

ef.close()

