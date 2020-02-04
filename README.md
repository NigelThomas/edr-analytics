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





