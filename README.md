# Lego Mindstorm EV3 Robot controlled with Alexa

## Services Used

1. AWS Iot Core
2. Amazon API Gateway
3. AWS Lambda
4. Alexa Custom Skills

## Steps
1. Create AWS IoT Core Things, then download all the certificates and note down your IoT endpoint
2. Create AWS Lambda function and use the code provided in this repo
3. Create Amazon API Gateway as Lambda proxy, and use previously created Lambda function, note down your API Gateway endpoint URL
4. Deploy Alexa Custom Skill with the assets provided, change the API Gateway URL
6. Flash your EV3 with ev3dev
7. Change IoT Endpoint in ev3dev.py using your own IoT Endpoint
8. Copy ev3dev.py and all the certificates into your EV3 brick
9. Have fun!
