# edr-analytics

This application is a demonstration of using SQLstream sliding window analytics to monitor changes to IMEI for a given subscriber.

## Producing test data
Data is generated in a CSV format by `test/generate_data.py`. To get help:
```
  python generate_data.py -h
```

### Trickling data

We can trickle data using the `-k` option. The data can either be trickled into a (single) file - no support for file rotation as yet -
or it can be pushed into Kafka using kafkacat.

This should all be a handled in the container startup.

## Docker image

For now we use the generic `streamlab-git-dev` docker image; that is based on sqlstream/development and already has `kafkacat` included. 

## Starting the project

Start the project by running `./edr_dev.sh`. This will start an instance of `streamlab-git-dev` with a container name of `edr_dev`.

The application will be  written as a StreamLab project `edr-analytics.slab`.

# Pipelines

## Pipeline 1 - Ingestion and analytics

### Pipeline overview
* Reads from `edrs_in`
* Joins to `tacs` - database of TACs with fields including `Model Name`, `Bands` etc
* Joins to `subscribers` - list of subscriber MSISDNs with latest `imei`, and a flag indicating if the LTE promotion has already been received

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
* Reads from `annotated_edrs`
### Pipeline Steps
1. Over a sliding window of rows since startup, compute `COUNT("promotion_applies") AS "promotions_today",  COUNT("msisdn") AS "records_today"
2. Accept rows where `"promotions_apply" = 'Y'`


