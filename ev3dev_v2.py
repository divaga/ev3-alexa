import json
import time
import datetime
import AWSIoTPythonSDK.MQTTLib as AWSIoTPyMQTT
from ev3dev2.motor import MoveTank, MediumMotor,OUTPUT_A, OUTPUT_B,OUTPUT_D
from ev3dev2.sensor.lego import ColorSensor
from ev3dev2.sensor.lego import TouchSensor
from ev3dev2.led import Leds
import uuid


def moveRobot(direction,duration):
    print("Moving Robot...")
    if (direction.lower() =='forward'):
        tank_pair.on_for_seconds(30, 30, duration,block=False)
    if (direction.lower() =='backward'):
        tank_pair.on_for_seconds(-30, -30, duration,block=False)
    if (direction.lower() =='left'):
        tank_pair.on_for_seconds(30, 15, duration,block=False)
    if (direction.lower() =='right'):
        tank_pair.on_for_seconds(15, 30, duration,block=False)
    time.sleep(duration)

def giveSouvenir():
    global label
    current_area = checkArea()
    print("Current color = " + current_area)
    #get current time
    curr_time = datetime.datetime.now().strftime("%d-%b-%Y %H:%M:%S")
    #submit score
    print("Publishing Score Topic....")
    publish_topic(current_area,curr_time)
    # This guy need to landed in red area
    if (current_area == 'green'):
        print("Dropping Souvenir...")
        clamp = MediumMotor(OUTPUT_D)
        clamp.on_for_rotations(60,2)
        clamp.on_for_rotations(60,-2)
        label = ''


def checkArea():
    cl = ColorSensor()
    cl.mode='COL-COLOR'
    colors=('unknown','black','blue','green','yellow','red','white','brown')
    return colors[cl.value()]

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


# Define ENDPOINT, CLIENT_ID, PATH_TO_CERTIFICATE, PATH_TO_PRIVATE_KEY, PATH_TO_AMAZON_ROOT_CA_1, MESSAGE, TOPIC, and RANGE
ENDPOINT = "<your-endpoint-here>.amazonaws.com"
CLIENT_ID = "ev3"
PATH_TO_CERTIFICATE = "certificates/ev3.cert.pem"
PATH_TO_PRIVATE_KEY = "certificates/ev3.private.key"
PATH_TO_AMAZON_ROOT_CA_1 = "certificates/root-CA.crt"


myAWSIoTMQTTClient = AWSIoTPyMQTT.AWSIoTMQTTClient(CLIENT_ID)
myAWSIoTMQTTClient.configureEndpoint(ENDPOINT, 8883)
myAWSIoTMQTTClient.configureCredentials(PATH_TO_AMAZON_ROOT_CA_1, PATH_TO_PRIVATE_KEY, PATH_TO_CERTIFICATE)
myAWSIoTMQTTClient.configureConnectDisconnectTimeout(10)  # 10 sec
myAWSIoTMQTTClient.configureMQTTOperationTimeout(5)  # 5 sec
ts = TouchSensor()
leds = Leds()
tank_pair = MoveTank(OUTPUT_A, OUTPUT_B)
label = ''

def publish_topic(area,currtime):
    global label
    message = {"id": label, "color" : area,"finish_time": currtime} 
    myAWSIoTMQTTClient.publishAsync("ev3/score", json.dumps(message), 1) 
    print("Published: '" + json.dumps(message) + "' to the topic: " + "'ev3/score'")


def connect_subscribe():
    # Connect & Subscribe
    print("CONNECTING...")
    leds.set_color("LEFT", "RED")
    leds.set_color("RIGHT", "RED")
    myAWSIoTMQTTClient.connect()
    myAWSIoTMQTTClient.subscribe("ev3/move", 1, callback_function)
    print("SUCCESS RECONNECT !!!")
    leds.set_color("LEFT", "GREEN")
    leds.set_color("RIGHT", "GREEN")

def resetRobot():
    global label
    print("Stopping Motor...")
    tank_pair.on_for_seconds(0,0,0)
    curr_time = datetime.datetime.now().strftime("%d-%b-%Y %H:%M:%S")
    label = uuid.uuid4().hex
    print("New ID= " + label)
    msg = {"id": label, "name" : "","color":"","start_time":curr_time,"finish_time" : ""} 
    myAWSIoTMQTTClient.disconnect()
    connect_subscribe()
    myAWSIoTMQTTClient.publish("ev3/score", json.dumps(msg), 1) 
    print("Published: '" + json.dumps(msg) + "' to the topic: " + "'ev3/score'")



# connect for the first time
connect_subscribe()

# Wait for messages to arrive
print("EV3 Initialized, Listening to topic...")

counter = 0
while True:
    time.sleep(1)
    counter = counter + 1
    if ((counter % 500) == 0):
        # reconnect to prevent time out
        myAWSIoTMQTTClient.disconnect()
        connect_subscribe()
    if ts.is_pressed:
        resetRobot()
myAWSIoTMQTTClient.disconnect()
