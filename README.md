# securitasdirect


New Home Assistant custom component to interact with Securitas Direct (AKA Verisure EU), based on mobile API (thanks to https://github.com/Cebeerre/VerisureAPIClient great Cebeerre work...)

1. Download [securitasdirect zip project](https://github.com/segalion/securitasdirect/archive/master.zip)
2. unzip and just copy 'custom_components' folder inside Home Assistant config folder
3. configure your configuration.yaml with proper securitas_direct/verisure parameters (as [example_config.yaml](https://github.com/segalion/securitasdirect/blob/master/custom_components/securitas_direct/example_config.yaml) 
3. restar HA and search for unused entities


You can use the python command_line tool to interact with Securitas Direct (Verisure EU), withot any Home Assistant...

1. Download "[securitas.py](https://github.com/segalion/securitasdirect/raw/master/custom_components/securitas_direct/securitas.py)" script file
2. install proper requirements:
`pip3 install requests xml2dict`
3. make it executable 
`chmod +x securitas.py`
4. run with 
`securitas.py username password [ACTION] [COUNTRY_CODE]`

( to see all actions:
`securitas.py username password ?` )


## TODO:
- Create a Home Assistant component
- Photo (CAMERA) request

## NOTES:

This project has no relationship with Securitas Direct / Verisure company (unofficial).
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

## LICENCE:
Code is under MIT licence.
 
  
   
There are an old cli bash version to interact with web access 
