
import requests
import json
import os
import re


supported_footprints = [ 
  "0201", "0402", "0603", "0805", "1206", 
  "SOT-23", "SOT-23-3", "SOT-23-5", "SOT-23-6", "SOT-23-8", 
  "SMD5032-2P", "SMD3225-4P",
  "SOIC-8"
]


meta_parts_text = "\n".join(open('meta_parts.kicad_sym').readlines()[1:-1])


resistor_tpl = """(
  symbol "{value} R {footprint}" (in_bom yes) (on_board yes) (extends "R {footprint}")
  (property "Reference" "R" (at -1.27 6.35 0) (effects (font (size 1.27 1.27)) hide))
  (property "Value" "{value}" (at -0.635 3.81 0) (effects (font (size 1.27 1.27))))
  (property "Footprint" "" (at -1.27 -6.35 0) (effects (font (size 1.27 1.27)) hide))
  (property "Datasheet" "{sheet}" (at -6.35 6.35 90) (effects (font (size 1.27 1.27)) hide))
  (property "LCSC" "{partnum}" (at -1.27 -1.905 0) (effects (font (size 1.27 1.27)) hide))
  (property "Stock" "{stock}" (at -1.27 -1.905 0) (effects (font (size 1.27 1.27)) {critical_stock}))
  (property "price" "{price}" (at -1.27 -1.905 0) (effects (font (size 1.27 1.27)) hide))
  (property "ki_keywords" "R res resistor" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))
  (property "ki_description" "{desc}" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))
  (property "ki_fp_filters" "R_*" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))
)"""


capacitor_tpl = """(
  symbol "{value} C {footprint}" (in_bom yes) (on_board yes) (extends "C {footprint}")
  (property "Reference" "C" (at -1.27 6.35 0) (effects (font (size 1.27 1.27)) hide))
  (property "Value" "{value}" (at -0.635 3.81 0) (effects (font (size 1.27 1.27))))
  (property "Footprint" "" (at -1.27 -6.35 0) (effects (font (size 1.27 1.27)) hide))
  (property "Datasheet" "{sheet}" (at -6.35 6.35 90) (effects (font (size 1.27 1.27)) hide))
  (property "LCSC" "{partnum}" (at -1.27 -1.905 0) (effects (font (size 1.27 1.27)) hide))
  (property "Stock" "{stock}" (at -1.27 -1.905 0) (effects (font (size 1.27 1.27)) {critical_stock}))
  (property "price" "{price}" (at -1.27 -1.905 0) (effects (font (size 1.27 1.27)) hide))
  (property "ki_keywords" "C capacitor" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))
  (property "ki_description" "{desc}" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))
  (property "ki_fp_filters" "R_*" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))
)"""


led_tpl = """
(symbol "{value} LED {footprint}" (pin_numbers hide) (pin_names (offset 1.016) hide) (in_bom yes) (on_board yes)
  (property "Reference" "D" (at 0 2.54 0) (effects (font (size 1.27 1.27))) )
  (property "Value" "{value}" (at 0 -2.54 0) (effects (font (size 1.27 1.27)) hide) )
  (property "Footprint" "{footprint_name}" (at -1.27 7.62 0) (effects (font (size 1.27 1.27)) hide) )
  (property "Datasheet" "{sheet}" (at 0 0 0) (effects (font (size 1.27 1.27)) hide) )
  (property "LCSC" "{partnum}" (at -1.905 4.445 0) (effects (font (size 1.27 1.27)) hide) )
  (property "Stock" "{stock}" (at -1.27 -1.905 0) (effects (font (size 1.27 1.27)) {critical_stock}))
  (property "price" "{price}" (at -1.27 -1.905 0) (effects (font (size 1.27 1.27)) hide))
  (property "ki_keywords" "LED diode" (at 0 0 0) (effects (font (size 1.27 1.27)) hide) )
  (property "ki_description" "{desc}" (at 0 0 0) (effects (font (size 1.27 1.27)) hide) )
  (property "ki_fp_filters" "LED* LED_SMD:*" (at 0 0 0) (effects (font (size 1.27 1.27)) hide) )
  (symbol "{value} LED {footprint}_0_1"
    (polyline (pts (xy -1.27 -1.27) (xy -1.27 1.27) ) (stroke (width 0.254) (type default)) (fill (type none) (color {color} 1)) )
    (polyline (pts (xy -3.048 -0.762) (xy -4.572 -2.286) (xy -3.81 -2.286) (xy -4.572 -2.286) (xy -4.572 -1.524) ) (stroke (width 0) (type default) (color {color} 1)) (fill (type none)) )
    (polyline (pts (xy -1.778 -0.762) (xy -3.302 -2.286) (xy -2.54 -2.286) (xy -3.302 -2.286) (xy -3.302 -1.524) ) (stroke (width 0) (type default) (color {color} 1)) (fill (type none)) )
  )
  (symbol "{value} LED {footprint}_1_1"
    (polyline (pts (xy 1.27 -1.27) (xy 1.27 1.27) (xy -1.27 0) (xy 1.27 -1.27) ) (stroke (width 0.254) (type default) ) (fill (type color) (color {color} 1))) 
  )
  (pin passive line (at -3.81 0 0) (length 2.54) (name "K" (effects (font (size 1.27 1.27)))) (number "1" (effects (font (size 1.27 1.27)))) )
  (pin passive line (at 3.81 0 180) (length 2.54) (name "A" (effects (font (size 1.27 1.27)))) (number "2" (effects (font (size 1.27 1.27)))) )
)"""


bjt_npn_tpl = """(
  symbol "{value}" (extends "NPN SOT-23")
  (property "Reference" "Q" (at 5.08 1.905 0) (effects (font (size 1.27 1.27)) (justify left)) )
  (property "Value" "{value}" (at 5.08 0 0) (effects (font (size 1.27 1.27)) (justify left) hide) )
  (property "Footprint" "" (at 5.08 -1.905 0) (effects (font (size 1.27 1.27) italic) (justify left) hide) )
  (property "Datasheet" "{sheet}" (at 0 0 0) (effects (font (size 1.27 1.27)) (justify left) hide) )
  (property "LCSC" "{partnum}" (at -1.905 4.445 0) (effects (font (size 1.27 1.27)) hide) )
  (property "Stock" "{stock}" (at -1.27 -1.905 0) (effects (font (size 1.27 1.27)) {critical_stock}))
  (property "price" "{price}" (at -1.27 -1.905 0) (effects (font (size 1.27 1.27)) hide))
  (property "ki_keywords" "npn transistor" (at 0 0 0) (effects (font (size 1.27 1.27)) hide) )
  (property "ki_description" "{desc}" (at 0 0 0) (effects (font (size 1.27 1.27)) hide) )
)"""


bjt_pnp_tpl = """(
  symbol "{value}" (extends "PNP SOT-23")
  (property "Reference" "Q" (at 5.08 1.905 0) (effects (font (size 1.27 1.27)) (justify left)) )
  (property "Value" "{value}" (at 5.08 0 0) (effects (font (size 1.27 1.27)) (justify left) hide) )
  (property "Footprint" "" (at 5.08 -1.905 0) (effects (font (size 1.27 1.27) italic) (justify left) hide) )
  (property "Datasheet" "{sheet}" (at 0 0 0) (effects (font (size 1.27 1.27)) (justify left) hide) )
  (property "LCSC" "{partnum}" (at -1.905 4.445 0) (effects (font (size 1.27 1.27)) hide) )
  (property "Stock" "{stock}" (at -1.27 -1.905 0) (effects (font (size 1.27 1.27)) {critical_stock}))
  (property "price" "{price}" (at -1.27 -1.905 0) (effects (font (size 1.27 1.27)) hide))
  (property "ki_keywords" "npn transistor" (at 0 0 0) (effects (font (size 1.27 1.27)) hide) )
  (property "ki_description" "{desc}" (at 0 0 0) (effects (font (size 1.27 1.27)) hide) )
)"""


crystal_2pin_tpl = """(
  symbol "{value}" (extends "Crystal")
  (property "Reference" "Y" (at 5.08 1.905 0) (effects (font (size 1.27 1.27)) (justify left)) )
  (property "Value" "{value}" (at 5.08 0 0) (effects (font (size 1.27 1.27)) (justify left) ) )
  (property "Footprint" "" (at 5.08 -1.905 0) (effects (font (size 1.27 1.27) italic) (justify left) hide) )
  (property "Datasheet" "{sheet}" (at 0 0 0) (effects (font (size 1.27 1.27)) (justify left) hide) )
  (property "LCSC" "{partnum}" (at -1.905 4.445 0) (effects (font (size 1.27 1.27)) hide) )
  (property "Stock" "{stock}" (at -1.27 -1.905 0) (effects (font (size 1.27 1.27)) {critical_stock}))
  (property "price" "{price}" (at -1.27 -1.905 0) (effects (font (size 1.27 1.27)) hide))
  (property "ki_keywords" "npn transistor" (at 0 0 0) (effects (font (size 1.27 1.27)) hide) )
  (property "ki_description" "{desc}" (at 0 0 0) (effects (font (size 1.27 1.27)) hide) )
)"""


crystal_4pin_tpl = """(
  symbol "{value}" (extends "Crystal_GND24")
  (property "Reference" "Y" (at 5.08 1.905 0) (effects (font (size 1.27 1.27)) (justify left)) )
  (property "Value" "{value}" (at 5.08 0 0) (effects (font (size 1.27 1.27)) (justify left) ) )
  (property "Footprint" "" (at 5.08 -1.905 0) (effects (font (size 1.27 1.27) italic) (justify left) hide) )
  (property "Datasheet" "{sheet}" (at 0 0 0) (effects (font (size 1.27 1.27)) (justify left) hide) )
  (property "LCSC" "{partnum}" (at -1.905 4.445 0) (effects (font (size 1.27 1.27)) hide) )
  (property "Stock" "{stock}" (at -1.27 -1.905 0) (effects (font (size 1.27 1.27)) {critical_stock}))
  (property "price" "{price}" (at -1.27 -1.905 0) (effects (font (size 1.27 1.27)) hide))
  (property "ki_keywords" "npn transistor" (at 0 0 0) (effects (font (size 1.27 1.27)) hide) )
  (property "ki_description" "{desc}" (at 0 0 0) (effects (font (size 1.27 1.27)) hide) )
)"""


def makereq(page, pagecount):
  ff = f"jlc_cache__{page}_{pagecount}.json"
  if os.path.exists(ff):
    print(ff)
    with open(ff) as f:
      j = json.loads(f.read())
      return j['data']['sortAndCountVoList'][0]['componentCount'], j['data']['componentPageInfo']['list']

  data = {
    "currentPage": page,
    "pageSize": pagecount,
    "keyword": None,
    "componentLibraryType": "base",
    "stockFlag": None,
    "stockSort": None,
    "firstSortName": "",
    "secondSortName": "",
    "componentBrandList": [],
    "componentSpecificationList": [],
    "componentAttributeList": [],
    "paramList": [],
    "startStockNumber": None,
    "endStockNumber": None,
    "firstSortId": 2,
    "secondSortId": None,
    "firstSortNameNew": "",
    "resetSearchComponent": False,
    "searchSource": "search",
    "firstSortNameList": []
  }
  headers = {'Content-type': 'application/json'}
  j = requests.post('https://jlcpcb.com/api/overseas-pcb-order/v1/shoppingCart/smtGood/selectSmtComponentList', data=json.dumps(data), headers=headers).json()
  with open(ff,"w") as f:
    f.write(json.dumps(j))
  return j['data']['sortAndCountVoList'][0]['componentCount'], j['data']['componentPageInfo']['list']


def get_parts():
    pagecount = 100
    page = 1
    parts = []
    seen_codes = set()
    while True:
      print(f"getting {page} {len(parts)}")
      count, pparts = makereq(page, pagecount)
      for part in pparts:
        if part['componentCode'] not in seen_codes:
          parts.append(part)
          seen_codes.add(part['componentCode'])
      page += 1
      if len(pparts) < pagecount:
        break
    return parts


part_stuff = {
    "Chip Resistor - Surface Mount": ('R', resistor_tpl),
    "Multilayer Ceramic Capacitors MLCC - SMD/SMT": ('C', capacitor_tpl),
    "Light Emitting Diodes (LED)": ('D', led_tpl),
    "Bipolar Transistors - BJT": ('Q', 'notarealtemplate'),
    "Crystals": ('Y', 'notarealtemplate'),
}


footprint_equivalents = {
  "LED_0805": "0805",
  "LED_0603": "0603",
}


def generate_part_sexps(parts):
    part_sexps = []

    for part in parts:
      component_type = part['componentTypeEn']
      if component_type not in part_stuff:
        continue
      symbol, tpl = part_stuff[component_type]

      spec = part['componentSpecificationEn']
      if spec in footprint_equivalents:
        spec = footprint_equivalents[spec]

      if spec not in supported_footprints:
        print(f"skipping {part['componentCode']} because {spec} not supported: {part['describe']}")
        continue

      color = None
      footprint_name = None

      if "Resistor" in component_type:
        value = part['erpComponentName'].split("Ω")[0].split(" ")[-1]
      elif "Capacitor" in component_type:
        value = re.match('([.0-9]+.?F ).*', part['erpComponentName']).group(1).replace("F ","")
      elif "LED" in component_type:
        colors = [ 'yellow', 'white', 'red', 'blue', 'green', 'emerald' ]
        value = "unknown"
        fpns = {
          "0201": "kpm-jlcpcb-basic:LED_0201_0603Metric",
          "0402": "kpm-jlcpcb-basic:LED_0402_1005Metric",
          "0603": "kpm-jlcpcb-basic:LED_0603_1608Metric",
          "0805": "kpm-jlcpcb-basic:LED_0805_2012Metric",
        }
        colorstrs = {
          "green": "123 255 125",
          "emerald": "123 255 125",
          "yellow": "255 255 161",
          "red": "255 115 94",
          "blue": "135 174 255",
          "white": "201 216 225",
        }
        for color in colors:
          if color in part['describe'].lower():
            value = color
        if value:
          footprint_name = fpns[spec]
          color = colorstrs[value]
      elif "BJT" in component_type:
        if "NPN" in part['describe']:
          value = f"NPN {part['componentModelEn']}"
          tpl = bjt_npn_tpl
        elif "PNP" in part['describe']:
          value = f"PNP {part['componentModelEn']}"
          tpl = bjt_pnp_tpl
        else:
          continue
      elif "Crystal" in component_type:
        value = part['erpComponentName'].split(" ")[0]
        if "-2P" in part['componentSpecificationEn']:
          value = f"{value} 2pin"
          tpl = crystal_2pin_tpl
        elif "-4P" in part['componentSpecificationEn']:
          value = f"{value} 4pin"
          tpl = crystal_4pin_tpl
        else:
          continue


      if "MHz" in value:
        print(value)
      fp = tpl.format(
        name=f"{value} R {spec}",
        footprint=f"{spec}",
        value=value,
        sheet=part['dataManualUrl'],
        partnum=part['componentCode'],
        desc=part['describe'],
        stock=part['stockCount'],
        price=part['componentPrices'][0]['productPrice'],
        critical_stock=("hide" if part['stockCount'] > 1000 else ""),
        footprint_name=footprint_name,
        color=color,
      )
      part_sexps.append(fp)
    return part_sexps


parts = get_parts()
with open('a.json', 'w') as f:
  f.write(json.dumps(parts))
part_sexps = generate_part_sexps(parts)

filedata = "(kicad_symbol_lib (version 20220914) (generator kicad_symbol_editor) " + meta_parts_text + "\n".join(part_sexps) + "\n)"
with open('symbols/kpm-jlcpcb-basic.kicad_sym', 'w') as f:
    f.write(filedata)

