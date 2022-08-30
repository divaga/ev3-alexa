import json
import boto3
client = boto3.client('iot-data')


def lambda_handler(event, context):
    api_data = json.loads(event['body'])

    response = client.publish(
        topic = 'ev3/move',
        qos = 1,
        payload = json.dumps({"direction": api_data['direction_data'],  "duration": api_data['duration_data']})
    )
    return {
        "statusCode": 200,
        "body":"Success"
    }
