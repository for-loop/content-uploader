import os
import boto3
from boto3.dynamodb.conditions import Key, Attr

dynamodb = boto3.resource('dynamodb', region_name = os.environ['AWS_REGION'])
table = dynamodb.Table(os.environ['DYNAMODB_TABLE'])

def lambda_handler(event, context):
    
    content = event['content']
    
    response = table.query(
        KeyConditionExpression=Key(os.environ['DYNAMODB_KEY']).eq(content)
    )
    
    return {
        'exists': response['Count']
    }

