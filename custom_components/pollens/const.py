"""Constants for the Pollens integration."""

DOMAIN = "pollens"
ATTRIBUTION = "Data from Reseau National de Surveillance Aerobiologique "
CONF_VERSION = 2
COORDINATOR = "coordinator"
UNDO_LISTENER = "undo_listener"

CONF_COUNTRYCODE = "county"
CONF_SCAN_INTERVAL = "scan_interval"
CONF_SCANINTERVAL = "scaninterval"
CONF_POLLENSLIST = "pollens_list"
CONF_LITERAL = "literal_states"

ATTR_TILLEUL = "tilleul"
ATTR_AMBROISIES = "ambroisies"
ATTR_OLIVIER = "olivier"
ATTR_PLANTAIN = "plantain"
ATTR_NOISETIER = "noisetier"
ATTR_AULNE = "aulne"
ATTR_ARMOISE = "armoise"
ATTR_CHATAIGNIER = "chataignier"
ATTR_URTICACEES = "urticacees"
ATTR_OSEILLE = "oseille"
ATTR_GRAMINEES = "graminees"
ATTR_CHENE = "chene"
ATTR_PLATANE = "platane"
ATTR_BOULEAU = "bouleau"
ATTR_CHARME = "charme"
ATTR_PEUPLIER = "peuplier"
ATTR_FRENE = "frene"
ATTR_SAULE = "saule"
ATTR_CYPRES = "cypres"
ATTR_CUPRESSASEES = "cupressacees"
ATTR_LITERAL_STATE = "literal_state"
ATTR_POLLEN_NAME = "pollen_name"

ICON_FLOWER = "mdi:flower"
ICON_TREE = "mdi:tree"
ICON_GRASS = "mdi:grass"
KEY_TO_ATTR = {
    "tilleul": [ATTR_TILLEUL, ICON_TREE],
    "ambroisies": [ATTR_AMBROISIES, ICON_GRASS],
    "olivier": [ATTR_OLIVIER, ICON_TREE],
    "plantain": [ATTR_PLANTAIN, ICON_GRASS],
    "noisetier": [ATTR_NOISETIER, ICON_TREE],
    "aulne": [ATTR_AULNE, ICON_TREE],
    "armoise": [ATTR_ARMOISE, ICON_GRASS],
    "châtaignier": [ATTR_CHATAIGNIER, ICON_TREE],
    "urticacées": [ATTR_URTICACEES, ICON_GRASS],
    "oseille": [ATTR_OSEILLE, ICON_GRASS],
    "graminées": [ATTR_GRAMINEES, ICON_GRASS],
    "chêne": [ATTR_CHENE, ICON_TREE],
    "platane": [ATTR_PLATANE, ICON_TREE],
    "bouleau": [ATTR_BOULEAU, ICON_TREE],
    "charme": [ATTR_CHARME, ICON_TREE],
    "peuplier": [ATTR_PEUPLIER, ICON_TREE],
    "frêne": [ATTR_FRENE, ICON_TREE],
    "saule": [ATTR_SAULE, ICON_TREE],
    "cyprès": [ATTR_CYPRES, ICON_TREE],
    "cupressacées": [ATTR_CUPRESSASEES, ICON_GRASS],
}

ATTR_COUNTY_NAME = "departement"
ATTR_URL = "url"

LIST_RISK = ["nul", "faible", "moyen", "élevé"]
