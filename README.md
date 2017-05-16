# AlexaBus
This is an alexa skill that provides bus times using publically available GTFS data. It is meant to run on
AWS lambda.

## Setup
### General
This skill requires a postgres database with postgis installed. To populate the database one can use the 
provided provisioning code. The provisioning code requires an API key for [TransitFeeds](http://transitfeeds.com/). This code relies on the submodule `pygtfsdb`. To create a deploy bundle for 
lambda you can use the provided shell script.

### Config.py
In order to properly run the lambda function, you must setup a `config.py` file inside the `AlexaBus` directory.
This file should look something like this:

```
TRANSIT_FEED_API_KEY = "transit feed key"
DB_USER = "dbuser"
DB_PASSWORD = "dbpassword"
DB_NAME = "dbname"
DB_PORT = "5432"
DB_ENDPOINT = "dbendpoint"
GOOGLE_API_KEY = "google api key"
```