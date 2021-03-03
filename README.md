# Pollens home assistant

This module show pollen concentration inside [Homeassistant](https://home-assistant.io):

Datas provided by 'Réseau National de Surveillance Aérobiologique' (R.N.S.A.)
https://pollens.fr

it's inspired by pappo work at [papo-o/home-assistant-config/integrations/](https://github.com/papo-o/home-assistant-config/blob/master/integrations/pollens.yaml).
and dzvents script [pon.fr](https://pon.fr/dzvents-alerte-pollens/)


## Install

### HACS (recommended)

You can install this custom component using [HACS](https://hacs.xyz/) by adding a custom repository.

### Manual install

1. Using the tool of choice open the directory (folder) for your HA configuration (where you find `configuration.yaml`).
2. If you do not have a `custom_components` directory (folder) there, you need to create it.
3. In the `custom_components` directory (folder) create a new folder called `pollens`.
4. Download _all_ the files from the `custom_components/pollens/` directory (folder) in this repository.
5. Place the files you downloaded in the new directory (folder) you created.
6. Restart Home Assistant

## Configuration

Add this to your `configuration.yaml`:

```yaml
sensor:
  - platform: pollens
    location: "60"
    timeout: 60
```
Name|Required|Description|Default
--|--|--|--
`location`|yes|Department number|
`timeout`|no|Timeour for web site response| 

This will create one sensor and severals attributes :
* sensor.pollens_*dept*
  * attribution: Data from Reseau National de Surveillance Aerobiologique 
  * departement: *dept*
  * *pollen* : *concentration*

Pollens are : 
Tilleul, Ambroisies, Olivier, Plantain, Noisetier, Aulne, Armoise, Châtaignier, Urticacées, Oseille, Graminées, Chêne, Platane, Bouleau, Charme, Peuplier, Frêne, Saule, Cyprès.
