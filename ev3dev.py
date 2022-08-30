import time as t
import json
import time
import AWSIoTPythonSDK.MQTTLib as AWSIoTPyMQTT
from ev3dev2.motor import MoveTank, MediumMotor,OUTPUT_A, OUTPUT_B,OUTPUT_C
from ev3dev2.sensor.lego import ColorSensor
from ev3dev2.sound import Sound

spkr = Sound()

def moveRobot(direction,duration):
    tank_pair = MoveTank(OUTPUT_A, OUTPUT_B)
    if (direction.lower() =='forward'):
        tank_pair.on_for_seconds(30, 30, duration)
    if (direction.lower() =='backward'):
        tank_pair.on_for_seconds(-30, -30, duration)
    if (direction.lower() =='left'):
        tank_pair.on_for_seconds(30, 15, duration)
    if (direction.lower() =='right'):
        tank_pair.on_for_seconds(15, 30, duration)

def giveSouvenir():
    current_area = checkArea()
    print("Current color = " + current_area)
    # This guy need to landed in red area
    if (current_area == 'red'):
        print("Dropping Souvenir...")
        time.sleep(0.5)
        clamp = MediumMotor(OUTPUT_C)
        clamp.on_for_rotations(50,2)
        clamp.on_for_rotations(50,-2)


def checkArea():
    cl = ColorSensor()
    cl.mode='COL-COLOR'
    colors=('unknown','black','blue','green','yellow','red','white','brown')
    return colors[cl.value()]


# Define ENDPOINT, CLIENT_ID, PATH_TO_CERTIFICATE, PATH_TO_PRIVATE_KEY, PATH_TO_AMAZON_ROOT_CA_1, MESSAGE, TOPIC, and RANGE
ENDPOINT = "<your-iot-endpoint-here>.iot.us-east-1.amazonaws.com"
CLIENT_ID = "ev3"
PATH_TO_CERTIFICATE = "certificates/ev3.cert.pem"
PATH_TO_PRIVATE_KEY = "certificates/ev3.private.key"
PATH_TO_AMAZON_ROOT_CA_1 = "certificates/root-CA.crt"


myAWSIoTMQTTClient = AWSIoTPyMQTT.AWSIoTMQTTClient(CLIENT_ID)
myAWSIoTMQTTClient.configureEndpoint(ENDPOINT, 8883)
myAWSIoTMQTTClient.configureCredentials(PATH_TO_AMAZON_ROOT_CA_1, PATH_TO_PRIVATE_KEY, PATH_TO_CERTIFICATE)

myAWSIoTMQTTClient.connect()

# Define what happens when messages are received
def callback_function(client, userdata, message):
    print("Received a new message:\n{0}".format(message.payload))
    print("from topic:\n{0}".format(message.topic))
    my_json = message.payload.decode('utf8').replace("'", '"')
    msg = json.loads(my_json)
    direction = msg['direction']
    duration = int(msg['duration'])
    moveRobot(direction,duration)
    giveSouvenir()

# Subscribe
myAWSIoTMQTTClient.subscribe("ev3/move", 1, callback_function)

# Wait for messages to arrive
print("Listening to topic...")
# Introduce yourself:
spkr.speak('Hello, I am ready')
counter = 0
while True:
    time.sleep(1)
myAWSIoTMQTTClient.disconnect()