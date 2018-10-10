# securitasdirect
Bash script command_line tool to interact with Securitas Direct (AKA Verisure Spain).

1. Download "securitas" script file
2. make it executable (chmod +x securitas)
3. edit and change NICK and PASSWD (nano securitas)
4. try execute (./securitas)
5. Call it from your favorite Home Automation tool (note tha inputs and outputs has been changed to be compatible with Home Assistant Alarm Component)

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
- bash, grep, awk, head
- curl (maybe you need make "sudo apt-get install curl")
- internet connection
(most linux distribution has all this included).


NOTES:
This project has no relation with Securitas Direct / Verisure (unofficial).

TODO:
- Photo requests
- Enable/disable keys and remotes
- yaml code to create a Home Assistant component

LICENCE:
Code is under MIT licence.
