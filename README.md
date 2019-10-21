# securitasdirect
New Python command_line tool to interact with Securitas Direct (AKA Verisure Spain), based on mobile API (thanks to https://github.com/Cebeerre/VerisureAPIClient great Cebeerre work...)

1. Download "[securitas.py](https://github.com/segalion/securitasdirect/raw/master/securitas.py)" script file (as raw)
2. install proper requirements:
`pip3 install requests xml2dict`
3. make it executable 
`chmod +x securitas.py`
4. run with 
`securitas.py username password [ACTION]`
to see all actions:
`securitas.py username password ?` 


##TODO:
- Create a Home Assistant component
- Photo (CAMERA) request







##OLD VERSION:
There are an old bash script command_line tool based on web API (works but its very slow).

1. Download securitas script file
2. make it executable (chmod +x securitas)
3. edit and change NICK and PASSWD (nano securitas)
4. try execute (./securitas)
5. Call it from your favorite Home Automation tool (note that inputs and outputs has been changed to be compatible with Home Assistant Alarm Component)

You can use it to automate wherever you want:
- When nobody on home > securitas armed_away 
- When all in home > securitas armed_home
- When someone enter home > securitas disarmed

EXAMPLES:

>./securitas armed_away

{"last_triggered": "10-10-2018 11:08 ", "state": "armed_away", "changed_by": "VERISURE WEB" }

>./securitas disarmed

{"last_triggered": "10-10-2018 11:09 ", "state": "disarmed", "changed_by": "VERISURE WEB" }

>./securitas log

10-10-2018 11:09 ;Desconectado;"";;VERISURE WEB

10-10-2018 11:08 ;Conectado;"";;VERISURE WEB

10-10-2018 09:19 ;Cerrar;"";Yo;

10-10-2018 00:26 ;Comprobacion de estado;"";;ANDROID

09-10-2018 23:53 ;Armado día;"";;VERISURE WEB

03-10-2018 23:12 ;Sabotaje/manipulación;1;;

02-10-2018 18:59 ;Petición de foto;Home Puerta Garaje;;ANDROID

01-10-2018 14:47 ;Alarma;Home Puerta Garaje;;

28-09-2018 14:32 ;Error procesando conexión de alarma;"";;VERISURE WEB

26-09-2018 07:20 ;Comprobacion de estado;"";;VERISURE WEB


REQUIREMENTS:
- bash, grep, awk, head (most linux distribution has all this included)
- curl (maybe you need make "sudo apt-get install curl")
- internet connection
Its supposed to run on Android with TERMUX, so you can easyly make an automation like:
- When connect to mywifi > securitas disarmed
- When disconnect from mywifi > securitas armed_away

NOTES:

This project has no relation with Securitas Direct / Verisure company (unofficial).
Has been tested in Spain. Similar webs has been found in 
- France: https://customers.securitasdirect.fr/
- Italy: https://customers.verisure.it/
- UK: https://customers.verisure.co.uk/
- Portugal: https://customers.securitasdirect.pt/
- Brasil: https://customers.verisure.com.br/
- Netherland:
- Chile:
- Perú:
So change country and traslate could be needed. Please report ISSUEs about it. Thanks.


LICENCE:
Code is under MIT licence.
