# Table of Contents
1. [Problem](README.md#problem)
2. [Approach](README.md#approach)
3. [Tech Stack](README.md#tech-stack)
4. [Dependencies](README.md#dependencies)
5. [Run](README.md#run)
6. [Schedule daily preprocessing](README.md#schedule-daily-preprocessing)

# Problem

Your cloud storage allows a user to upload contents. The problem, however, is that you charge by the MB used/month and the user wants to minimize cost.

Two files could be named differently, but may contain identical content. Because many users store millions of files, it's practically impossible for them to manually weed out duplicate contents.

Wouldn't it be great if the user can be prompted with a message - at the time of the upload - that a file of the same content already exists?

Some of the challenges to consider include the following:

* The new content will be compared against millions of existing contents.
	* Upload the file to the cloud storage if the content is unique.
	* If a duplicate exists, let the user know and cancel the upload.
* The latency for the scan must be short; the user shouldn't need to wait for more than a few seconds.

# Approach

1. When the user submits a new file, calculate its checksum.
2. Compare the value of the checksum against existing values in the database.
3. If no match is found, then upload the file to S3 bucket.

> In this prototype, the above approach has been simplified:
>
> 1. The user submits a file. Calculate checksum (using [SparkMD5](https://github.com/satazor/js-spark-md5)).
> 2. This invokes API gateway and the lambda function will check the value in DynamoDB.
> 3. The user will get a response of whether or not the content exists.
>
> More feature may be added in the future.

### Preprocessing

The database containing millions of checksum values have already been made using a [batch ETL process](https://github.com/for-loop/duplicate-detector).

The data, however, is stored in PostgreSQL, a relational database. I wonder how the latency compares to NoSQL.

So as a preprocessing step, the data was moved from Postgres to DynamoDB.

# Tech Stack

<img src='images/tech-stack.jpg' />

# Dependencies

### Preprocessing

* Authentication for PostgreSQL. Create the following environmental variables in `.bashrc`:

	```bash
	export POSTGRES_USER=xxxx
	export POSTGRES_PASSWORD=xxxx
	export POSTGRES_HOST=x.x.x.x
	export POSTGRES_PORT=xxxx
	export POSTGRES_DATABASE=xxx
	```

* [boto3](https://github.com/boto/boto3)
* [psycopg2](https://pypi.org/project/psycopg2/)

### Backend

* Environment variables for Lambda function.

	```
	DYNAMODB_TABLE:xxxx
	DYNAMODB_KEY:xxxx
	```

### Frontend

* URL for the API Gateway. Edit `src/frontend/config.js`

# Run

### Preprocessing

1. Move the data from Postgres to DynamoDB.

    > Make sure you will have enough write capacity units on DynamoDB.

    ```bash
    python etl_postgres2dynamodb.py <postgres table name> <postgres column name> \
			    	<dynamodb table name> <dynamodb partition key> \
		    		[--region <region name>]
    ```

    > To schedule this ETL process with Apache Airflow, see [below](README.md#schedule-daily-preprocessing)

# Schedule daily preprocessing

0. Install dependencies

    * I installed [Anaconda on Ubuntu 18.04](https://www.anaconda.com/products/individual#linux).
    * In addition, `setproctitle` was required.

    ```bash
    conda install setproctitle
    ```

1. Create a path for Airflow as an environment variable

    > * Also export arguments to `etl_postgres2dynamodb.py`
    > * Add the line below to `.bashrc`, then do `source .bashrc`

    ```bash
    export AIRFLOW_HOME=~/airflow
    export ETL_HOME=~/content-uploader/src
    export ETL_FROM_TABLE='<postgres table name>'
    export ETL_FROM_COLUMN='<postgres column name>'
    export ETL_TO_TABLE='<dynamodb table name>'
    export ETL_TO_KEY='<dynamodb partition key>'
    export ETL_REGION='<region name>'
    ```

2. Install Apache Airflow ([Quick start](https://airflow.apache.org/docs/stable/start.html))

    ```bash
    pip install apache-airflow
    ```

3. Initialize database

    ```bash
    airflow initdb
    ```

4. Start web server (new shell)

    ```bash
    airflow webserver --port 8080
    ```

5. Make `dags/` directory

    ```bash
    cd $AIRFLOW_HOME
    mkdir -p dags
    ```

6. Copy `airflow_etl.py` to this directory

    ```bash
    cp dags/airflow_etl.py $AIRFLOW_HOME/dags/
    ```

7. Test

    > Enter today's date

    ```bash
    cd $AIRFLOW_HOME/dags/
    airflow test airflow_etl_v01 etl_postgres2dynamodb <YYYY-MM-DD>
    ```

8. Start scheduler (new shell)

    ```bash
    airflow scheduler
    ```

8. Turn on `airflow_etl_v01` on the web server

    > The ETL process will run once a day.
