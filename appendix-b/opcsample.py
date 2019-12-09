import OpenOPC
import threading
import time
import paho.mqtt.publish as publish
import paho.mqtt.client as mqtt

def pubService():

	items = ['[OPC_Sample]Program:MainProgram.OUTPUT1',
			'[OPC_Sample]Program:MainProgram.OUTPUT2',
			'[OPC_Sample]Program:MainProgram.INPUT']
	while True:
		try:
			opc = OpenOPC.client()
			opc.connect('RSLinx OPC Server')
			opcData = opc.read(items)
		except:
			print "pubService OPC exception"
		else:
			msgs=[]
			for i in opcData:
				msgs.append(("opcsample/get/"+i[0]+"/", i[1], 0, False));
			try:
				publish.multiple(msgs, hostname="***.eercan.com", auth={'username':"***",'password':"***"})
			except:
				print "pubService MQTT exception, sleeping 5 sec"
				time.sleep(5)
			time.sleep(1)
			opc.close()



def subService():
	try:
		opc = OpenOPC.client()
		opc.connect('RSLinx OPC Server')
	except:
		print "subService OPC Connect exception"
	def on_connect(client, userdata, flags, rc):
		print("MQTT Connected with result code "+str(rc))
		client.subscribe("opcsample/set/#")

	def on_message(client, userdata, msg):
		topicParse=msg.topic.split("/")
		opc.write( (topicParse[-2:][0], msg.payload) )
		print "set: "+topicParse[-2:][0]+": "+msg.payload

	client = mqtt.Client()
	client.on_connect = on_connect
	client.on_message = on_message

	try:
		client.username_pw_set("***","***")
		client.connect("***.eercan.com", 1883, 60)
	except:
		print "subService MQTT Connect exception"
	client.loop_forever()
	opc.close()

threading.Thread(name='pubService', target=pubService).start()
threading.Thread(name='subService', target=subService).start()
