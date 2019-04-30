# FarmOSMQTT

A python script for integrating LoRaWAN providers with the [Sensor](https://farmos.org/guide/assets/sensors/) asset of [FarmOS](https://www.farmos.org).

## What does it do?

This script runs on the same server as your FarmOS installation.  

It connects to the MQTT service provided by your LoRaWAN supplier, and converts the messages into data that can be used in FarmOS to see a near real-time view of the environment that you are responsible for managing.

## Which services can I use it with?

At the moment (2019-04-30), it can be used with an installation of [LoRaServer](https://www.loraserver.io), which is the platform upon which Mockingbird Consulting can offer LoRaWAN services.

In future, we plan to add support for [The Things Network](https://www.thethingsnetwork.org) and [LoRIOT](https://www.loriot.io), and you can keep track of how we're doing on that front by following our issue tracker.

## How do I install it?

Due to design constraints within FarmOS, this script needs to be installed on the same server as the FarmOS Database.

If you want to use multiple providers you'll need to run multiple copies of the script, and you *must* use python 3.6 or above.

Installing is best done into a Virtual Environment and run as a dedicated user as follows:

```bash
useradd -m farmosmqtt
su - farmosmqtt
git clone https://github.com/mockingbirdconsulting/FarmOSMQTT.git
cd FarmOSMQTT
virtualenv -p /usr/bin/python3 .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Once you have run the above, copy `config.example.yml` to `config.yml` and update the appropriate settings for your environment.

Now switch back to the root user and run the following from the directory into which you have cloned this repository:

```bash
mkdir /etc/farmosmqtt/
cp config.yml /etc/farmosmqtt/config.yml
cp farmosmqtt.service /etc/systemd/system/farmosmqtt.service # Update the file if you have used a different username/location for this repository.
cp farmosmqtt /usr/local/bin
systemctl daemon-reload
systemctl start farmosmqtt
systemctl status farmosmqtt
```

If all goes well, you should see that the service is running.

## How do I see my data in FarmOS?

The script assumes that the sensor name is the same in both your LoRaWAN provider and FarmOS.

First of all, configure your sensor on your LoRa Provider's console/dashboard and make sure that data is reaching their platform.

Follow the instructions at [Sensor](https://farmos.org/guide/assets/sensors/) to create a new "Listener" Sensor with the *exact* same name as the name you have given it in your LoRa provider. 

**Failure to name the sensor the same in both locations will result in data not being collected in FarmOS.**

Wait for your sensor to send the data in to your LoRa provider, then refresh the sensor page in FarmOS.  Your metrics should be displayed in FarmOS.

## What if I don't have a LoRaWAN provider?

Drop us an email: [info@mockingbirdconsulting.co.uk](mailto:info@mockingbirdconsulting.co.uk) and we can help you decide which provider is right for you, and which sensors are most appropriate for your environment.

## Copyright Notice

All copy marks and trademarks within this document remain the property of their respective owners.  Using this software *does not* grant *any* kind of license to you, the user, to use or replicate these marks in any way, shape, or form.
