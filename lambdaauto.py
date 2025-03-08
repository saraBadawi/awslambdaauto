import json
import boto3
from decimal import Decimal

# Initialize DynamoDB client
dynamodb = boto3.resource('dynamodb')
table_name = 'CounterTable'
table = dynamodb.Table(table_name)

# Helper function to convert Decimal to Python types
def decimal_to_standard(obj):
    if isinstance(obj, Decimal):
        return int(obj) if obj % 1 == 0 else float(obj)
    if isinstance(obj, list):
        return [decimal_to_standard(item) for item in obj]
    if isinstance(obj, dict):
        return {key: decimal_to_standard(value) for key, value in obj.items()}
    return obj

# CORS Headers
response_headers = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type'
}

def lambda_handler(event, context):
    try:
        http_method = event.get('requestContext', {}).get('http', {}).get('method')
        # Get the counterId from pathParameters or default to "counter"
        counter_id = event.get('pathParameters', {}).get('counterId', 'counter')

        if http_method == 'GET' and counter_id:
            response = table.update_item(
                Key={'counterId': counter_id},
                UpdateExpression="ADD #count :inc",
                ExpressionAttributeNames={'#count': 'count'},
                ExpressionAttributeValues={':inc': 1},
                ReturnValues="UPDATED_NEW"
            )
            attributes = decimal_to_standard(response.get('Attributes'))
            return {
                'statusCode': 200,
                'headers': response_headers,
                'body': json.dumps(attributes)
            }
        else:
            return {
                'statusCode': 400,
                'headers': response_headers,
                'body': json.dumps({'error': 'Unsupported HTTP method or missing counterId'})
            }
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': response_headers,
            'body': json.dumps({'error': str(e)})
        }

