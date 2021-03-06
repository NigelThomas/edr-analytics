# edr-analytics

This application is a demonstration of using SQLstream sliding window analytics to monitor changes to IMEI for a given subscriber.

This project depends on two related projects:

* https://github.com/NigelThomas/streamlab-git - builds development and test docker images
* https://github.com/NigelThomas/sqlstream-docker-utils - utilities for managing and starting StreamLab projects using docker 

## Starting the project

Ensure that you either `docker pull sqlstream/streamlab-git-dev` or build your own local image using `develop_image/dockerbuild.sh` from the `streamlab-git` project.

Start the container by running `./edr_dev.sh`. This will start an instance of `streamlab-git-dev` with a container name of `edr_dev`. Test data is generated directly on the container (see below).

The StreamLab application will be  written as a StreamLab project `edr.slab`.

# Test Source Data
These data are generated by the `test/generate_data.py` module (see below) which is automatically started when the container is started.

## TAC data `tacs`

A database of around 172k real-world TACs and associated information.

|TAC|Marketing Name|Manufacturer (or) Applicant|Bands|5G Bands|LPWAN|Radio Interface|Brand Name|Model Name|Operating System|NFC|Bluetooth|WLAN|Device Type|Removable UICC|Removable EUICC|NonRemovable UICC|NonRemovable EUICC|Simslot|Imeiquantitysupport| 
|----|----|----|----|----|----|----|----|----|----|----|----|----|----|----|----|----|----|----|----|
|00100100|G410|Mitsubishi|GSM 1800,GSM 900|Not Known|Not Known|NONE|Not Known|G410|Not Known|Not Known|Not Known|Not Known|Handheld|Not Known|Not Known|Not Known|Not Known|Not Known|Not Known|
|00100200|A53|Siemens|GSM 1900,GSM850 (GSM800)|Not Known|Not Known|NONE|Not Known|A53|Not Known|Not Known|Not Known|Not Known|Handheld|Not Known|Not Known|Not Known|Not Known|Not Known|Not Known|
|00100300|TBD (AAB-1880030-BV)|Sony Ericsson|GSM 1900,GSM850 (GSM800)|Not Known|Not Known|NONE|Not Known|TBD (AAB-1880030-BV)|Not Known|Not Known|Not Known|Not Known|Handheld|Not Known|Not Known|Not Known|Not Known|Not Known|Not Known|
|00100400|RM-669|Nokia|GSM 1900,GSM850 (GSM800)|Not Known|Not Known|NONE|Not Known|RM-669|Not Known|Not Known|Not Known|Not Known|Handheld|Not Known|Not Known|Not Known|Not Known|Not Known|Not Known|
|35297609|Apple iPhone 8 Plus (A1897)|Apple Inc|CDMA2000,LTE FDD BAND 1,LTE FDD BAND 2,LTE FDD BAND 3,LTE FDD BAND 4,LTE FDD BAND 5,LTE FDD BAND 7,LTE FDD BAND 8,LTE FDD BAND 12,LTE FDD BAND 13,LTE FDD BAND 17,LTE FDD BAND 18,LTE FDD BAND 19,LTE FDD BAND 20,LTE FDD BAND 24,LTE FDD BAND 25,LTE FDD BAND 26,LTE FDD BAND 27,LTE FDD BAND 28,LTE TDD BAND 38,LTE TDD BAND 39,LTE TDD BAND 40,LTE TDD BAND 41,GSM850 (GSM800),GSM 900,GSM 1800,GSM 1900,WCDMA FDD Band 1,WCDMA FDD Band 2,WCDMA FDD Band 4,WCDMA FDD Band 5,WCDMA FDD Band 8|Not Known|Not Known|CDMA|Apple|iPhone 8 Plus (A1897)|iOS|Y|Y|Y|Smartphone|1 UICC|0 eUICC|0 UICC|0 eUICC|1|1|

LTE-capable handsets are identified by including the word 'LTE' in the `Bands` field.

## Subscriber data `subscribers`

Initial state of all subscribers

msisdn|imei|band|promoted
---|---|---|---
0000000000|35882704-00000-0001|GSM 1900,GSM850 (GSM800)|N
0000000001|86669803-00001-0001|CDMA2000,LTE FDD BAND 1,LTE FDD BAND 3,LTE FDD BAND 4,LTE FDD BAND 5,LTE FDD BAND 7,LTE FDD BAND 8,LTE TDD BAND 34,LTE TDD BAND 38,LTE TDD BAND 39,LTE TDD BAND 40,LTE TDD BAND 41,GSM850 (GSM800),GSM 900,GSM 1800,GSM 1900,WCDMA FDD Band 1,WCDMA FDD Band 2,WCDMA FDD Band 5,WCDMA FDD Band 8,WCDMA TDD Band A|N
0000000002|01143200-00002-0001|GSM 1800,GSM 1900,GSM850 (GSM800)|N
0000000003|35304308-00003-0001|LTE FDD BAND 17,LTE FDD BAND 2,LTE FDD BAND 4,LTE FDD BAND 5,LTE FDD BAND 7,GSM 1900,GSM850 (GSM800)|Y

The `promoted` field indicates that the subscriber has already received the upgrade promotion in the past.

## EDR data stream

EDR records are generated (by default at ~ 5/sec for 3 hours)

calltime|msisdn|imei|band|upg_imei
--------|------|----|----|---
1580994307|0000000004|35450103-00004-0001|GSM 1800,GSM 900|0
1580994308|0000000021|35212501-00021-0001|GSM 1800,GSM 1900,GSM 900|0
1580994309|0000000034|86307002-00034-0001|GSM 1800,GSM 900,802.11a,Bluetooth,FM87.5MHZ-108MHZ,WCDMA TDD Band A|0
1580994310|0000000000|35882704-00000-0001|GSM 1900,GSM850 (GSM800)|0

The fields `band` and `upg_imei` are not used in the SQLstream processing (they are there as a cross-check, to show the test data generator's state).

# Pipelines

## Pipeline 1 - Ingestion and analytics

### Pipeline overview
* Reads from `edrs_in`
* Joins to `tacs` - database of TACs with fields including `Model Name`, `Bands` etc
* Joins to `subscribers` - list of subscriber MSISDNs with latest `imei`, and a flag indicating if the LTE promotion has already been received
* Determines whether the TAC has been changed, if so is it upgraded to LTE, and if so has it been upgraded before.

### Pipeline Steps

1. Convert `calltime` as Unix seconds to a SQL timestamp.
1. Extract text from `imei` into `tac`, starting at 1 for 8 characters
   * Ready to join to the `tacs` table
1. Perform an inner join to `tacs` on `tac` = `TAC`
1. Drop columns `5G Bands,LPWAN,Radio Interface,NFX,Bluetooth,WLAN,Device Type,Removable UICC,NonRemovable UICC,NonRemovable EUICC,Simslot,Imeiquantitysupport,band,upg_imei`
   * These are mainly columns we don't need from `tacs`
   * we could have excluded them from the source definition
   * we also drop `band` and `upg_imei` which are in the generated test data but wouldn't be expected in a real dataset
1. New column `is_lte` = `(CASE WHEN (POSITION('LTE' in "Bands") > 0 THEN 'Y' ELSE 'N' END)`
   * Flag that the current TAC supports at least one LTE band
1. Perform a left join to `subacribers` on `msisdn`
   * Pick up the subscribers table, as at startup time
   * In a long running system we would use a stream instead, containing the latest value for each subscriber (maybe receiving daily updates)
1. Rename `t_imei,band,promoted` to `sub_imei,sub_band,sub_promoted`
   * This is just to highlight that these are the fields we use from the `subscribers` file
1. New column `is_sub_lte` = `(CASE WHEN (POSITION('LTE' in "sub_band") > 0 THEN 'Y' ELSE 'N' END)`
   * this tells us whether the subscriber was using an LTE phone at startup time
1. Sliding rows window compute `NTH_VALUE("is_lte",2) FROM LAST OVER (PARTITION BY "mdisdn" ROWS UNBOUNDED PRECEDING) AS "was_lte"`
   * was the subscriber using an LTE phone the last time we got an EDR?
1. New column `new_lte` = `(CASE WHEN "is_lte" = 'Y' and coalesce("was_lte","is_sub_lte") = 'N' THEN 'Y' ELSE null END)`
   * Is this a change from non-LTE to LTE?
1. Sliding rows window compute `COUNT("new_lte") FROM LAST OVER (PARTITION BY "mdisdn" ROWS UNBOUNDED PRECEDING) AS "lte_upgrade_count"`
   * How many times have we seen a switch from non-LTE to LTE today (for this client
1. New column `promotion_applies` = `(CASE WHEN "lte_upgrade_count" = 1 and "sub_promoted" = 'N' THEN 'Y' ELSE null END)`
   * The subscriber has upgraded to LTE
   * This is the first upgrade today (since startup)
   * And according to `subscribers.promoted` he has never previously received the promotion
1. Route to stream `annotated_edrs`
   * To provide an input for subsequent pipelines

## Pipeline 2 - Reporting
### Pipeline Overview
* Reads from `annotated_edrs` (the output of pipeline 2)
* Filters out all EDRs except those showing a qualified upgrade

### Pipeline Steps
1. Over a sliding window of rows since startup, compute `COUNT("promotion_applies") AS "promotions_today",  COUNT("msisdn") AS "records_today"
2. Accept rows where `"promotions_apply" = 'Y'`

# Test Data Generation
Data is generated in a CSV format by `test/generate_data.py`. To get help:
```
python test/generate_data.py -h
usage: generate_data.py [-h] [-c SUBSCRIBER_COUNT] [-o OUTPUT_TIME]
                        [-r CALL_RATE] [-u UPGRADE_PROB] [-k] [-n]
                        [-t TAC_FILE] [-T TAC_COUNT] [-s SUBSCRIBER_FILE]
                        [-e EDR_FILE]

optional arguments:
  -h, --help            show this help message and exit
  -c SUBSCRIBER_COUNT, --subscriber_count SUBSCRIBER_COUNT
                        number of subscribers to be created
  -o OUTPUT_TIME, --output_time OUTPUT_TIME
                        number of seconds of calls
  -r CALL_RATE, --call_rate CALL_RATE
                        max number of calls per second
  -u UPGRADE_PROB, --upgrade_prob UPGRADE_PROB
                        integer pct probability of upgrade
  -k, --trickle         Trickle one second of data each second
  -n, --no_trickle      No trickling - emit data immediately
  -t TAC_FILE, --tac_file TAC_FILE
                        input: TAC database for generating random TACs
  -T TAC_COUNT, --tac_count TAC_COUNT
                        Number of distinct TACs
  -s SUBSCRIBER_FILE, --subscriber_file SUBSCRIBER_FILE
                        output: initial list of generated subscribers
  -e EDR_FILE, --edr_file EDR_FILE
                        output: generated file of EDRs
```


