import argparse
import boto3
import os
import sqlalchemy
import pandas as pd


def postgres_url():
    '''
    Return url to access the Postgres db
    '''
    return 'postgresql://{}:{}@{}:{}/{}'.format(os.environ['POSTGRES_USER'], os.environ['POSTGRES_PASSWORD'], os.environ['POSTGRES_HOST_PUBLIC'], os.environ['POSTGRES_PORT'], os.environ['POSTGRES_DATABASE'])


def etl(from_table, from_column, to_table, to_partition_key, region):
    '''
    Load data from Postgres into DynamoDB
    '''
    engine = sqlalchemy.create_engine(postgres_url())

    ser = pd.read_sql_query('SELECT {} FROM {}'.format(from_column, from_table), con = engine)
    
    dynamodb = boto3.resource('dynamodb', region_name=region)

    table = dynamodb.Table(to_table)
    
    for item in ser[from_column]:
        table.put_item(
            Item={to_partition_key: item}
        )


def main():
    parser = argparse.ArgumentParser(description = "Batch ETL from Postgres to DynamoDB")
    
    parser.add_argument("from_table", type = str, nargs = 1,
                        metavar = "postgres_table", default = None,
                        help = "Name of the Postgres table.")

    parser.add_argument("from_column", type = str, nargs = 1,
                        metavar = "postgres_column", default = None,
                        help = "Name of the column in Postgres table.")
    
    parser.add_argument("to_table", type = str, nargs = 1,
                        metavar = "dynamodb_table", default = None,
                        help = "Name of the DynamoDB table.")

    parser.add_argument("to_partition_key", type = str, nargs = 1,
                        metavar = "dynamodb_partition_key", default = None,
                        help = "Name of the partition key in DynamoDB table.")

    parser.add_argument("-r", "--region", type = str, nargs = 1,
                        metavar = "region_name", default = ["us-west-2"],
                        help = "Name of the region where the DynamoDB is located. \
                                The default is 'us-west-2'.")
    
    args = parser.parse_args()
    
    from_table = args.from_table[0]
    from_column = args.from_column[0]
    to_table = args.to_table[0]
    to_partition_key = args.to_partition_key[0]
    if args.region != None: region_name = args.region[0]

    etl(from_table, from_column, to_table, to_partition_key, region_name)


if __name__ == "__main__":
    main()
