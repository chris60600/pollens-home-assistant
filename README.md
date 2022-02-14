[![Downloads for latest release](https://img.shields.io/github/downloads/chris60600/pollens-home-assistant/latest/total)](https://github.com/hacs/integration/releases/latest)
[![](https://img.shields.io/github/issues/chris60600/pollens-home-assistant)](https://github.com/chris60600/pollens-home-assistant/issues)
[![]https://img.shields.io/github/manifest-json/v/chris60600/pollens-home-assistant?filename=custom_components%2Fpollens%2Fmanifest.json]
# Pollens home assistant

This module show pollen concentration inside [Homeassistant](https://home-assistant.io):

Datas provided by 'Réseau National de Surveillance Aérobiologique' (R.N.S.A.)
https://pollens.fr

it's inspired by papoo work at [papo-o/home-assistant-config/integrations/](https://github.com/papo-o/home-assistant-config/blob/master/integrations/pollens.yaml).
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
The pollens integration is **now available in the Integration Menu**
1. Select your county
2. Untick the option to have numeric states or submit to stay with literal states
3. Select all the pollens you want to have in sensors

You can also configure option to change default scan interval (3 hours)

Old Pollens platform configuration **must be removed** from `configuration.yaml` file

This will create one sensor ~~and severals attributes~~ :
* sensor.pollens_*dept*
  * attribution: Data from Reseau National de Surveillance Aerobiologique 
  * departement: *dept*
  * *pollen* : *concentration*

Sensors with particular Pollens like : 
Tilleul, Ambroisies, Olivier, Plantain, Noisetier, Aulne, Armoise, Châtaignier, Urticacées, Oseille, Graminées, Chêne, Platane, Bouleau, Charme, Peuplier, Frêne, Saule, Cyprès, Cupressacées.
All sensors are named sensor.pollens_*dept*_*pollen-name*
