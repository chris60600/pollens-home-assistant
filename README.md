# Pollens home assistant

This module show pollen concentration inside home assistant:
Datas provided by 'Réseau National de Surveillance Aérobiologique' (R.N.S.A.)
https://pollens.fr

It is based on pappo work at [papo-o/home-assistant-config/integrations/](https://github.com/papo-o/home-assistant-config/blob/master/integrations/pollens.yaml).
and dzvents script [pon.fr](https://pon.fr/dzvents-alerte-pollens/)


## Install

### HACS (recommended)

You can install this custom component using [HACS](https://hacs.xyz/) by adding a custom repository.

### Manual install

Copy this repository inside `config/custom_components/pollens`.

## Configuration

Add this to your `configuration.yaml`:

```yaml
sensor:
  - platform: pollens
    location: "60"
    timeout: 60
```

This will create one sensor and severals attributes :
* sensor.pollens_*dept*
  * attribution: Data from Reseau National de Surveillance Aerobiologique 
  * departement: *dept*
  * *pollen* : *concentration*

Pollens are : 
Tilleul, Ambroisies, Olivier, Plantain, Noisetier, Aulne, Armoise, Châtaignier, Urticacées, Oseille, Graminées, Chêne, Platane, Bouleau, Charme, Peuplier, Frêne, Saule, Cyprès.
