
import requests
import json
import os
import re


supported_footprints = [ "0201", "0402", "0603", "0805" ]


meta_parts_text = "\n".join(open('meta_parts.kicad_sym').readlines()[1:-1])


resistor_tpl = """(
  symbol "{value} R {footprint}" (in_bom yes) (on_board yes) (extends "R {footprint}")
  (property "Reference" "R" (at -1.27 6.35 0) (effects (font (size 1.27 1.27)) hide))
  (property "Value" "{value}" (at -0.635 3.81 0) (effects (font (size 1.27 1.27))))
  (property "Footprint" "" (at -1.27 -6.35 0) (effects (font (size 1.27 1.27)) hide))
  (property "Datasheet" "{sheet}" (at -6.35 6.35 90) (effects (font (size 1.27 1.27)) hide))
  (property "LCSC" "{partnum}" (at -1.27 -1.905 0) (effects (font (size 1.27 1.27)) hide))
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
  (property "ki_keywords" "C capacitor" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))
  (property "ki_description" "{desc}" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))
  (property "ki_fp_filters" "R_*" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))
)"""


part_templates = {
    "Resistors": resistor_tpl,
    "Capacitors": capacitor_tpl,
}


def makereq(page, pagecount, section):
  ff = f"jlc_cache_{section}_{page}_{pagecount}.json"
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
    "firstSortName": section,
    "secondSortName": "",
    "componentBrandList": [],
    "componentSpecificationList": [],
    "componentAttributeList": [],
    "paramList": [],
    "startStockNumber": None,
    "endStockNumber": None,
    "firstSortId": 2,
    "secondSortId": None,
    "firstSortNameNew": "Resistors",
    "resetSearchComponent": False,
    "searchSource": "search",
    "firstSortNameList": []
  }
  headers = {'Content-type': 'application/json'}
  j = requests.post('https://jlcpcb.com/api/overseas-pcb-order/v1/shoppingCart/smtGood/selectSmtComponentList', data=json.dumps(data), headers=headers).json()
  with open(ff,"w") as f:
    f.write(json.dumps(j))
  return j['data']['sortAndCountVoList'][0]['componentCount'], j['data']['componentPageInfo']['list']


def get_parts(section):
    pagecount = 100
    page = 1
    parts = []
    while True:
      print(f"getting {page} {len(parts)}")
      count, pparts = makereq(page, pagecount, section)
      parts += pparts
      page += 1
      if len(pparts) < pagecount:
        break
    return parts


def generate_part_sexps(parts, section):
    part_sexps = []

    for part in parts:
      if section == 'Resistors':
        value = re.match('([.0-9]+.?Ω).*', part['erpComponentName']).group(1).replace("Ω","")
      elif section == 'Capacitors':
        value = re.match('([.0-9]+.?F ).*', part['erpComponentName']).group(1).replace("F ","")

      spec = part['componentSpecificationEn']
      code = part['componentCode']
      name = part['componentName']
      sheet = part['dataManualUrl']
      ctype = part['componentTypeEn']

      if spec not in supported_footprints:
        print(f"skipping {code} because {spec} not supported: {name}")
        continue

      fp = part_templates[section].format(
        name=f"{value} R {spec}",
        footprint=f"{spec}",
        value=value,
        sheet=sheet,
        partnum=code,
        desc=name,
      )
      part_sexps.append(fp)
    return part_sexps


sections = [ 'Resistors', 'Capacitors' ]
part_sexps = []
for section in sections:
    parts = get_parts(section)
    part_sexps += generate_part_sexps(parts, section)


filedata = "(kicad_symbol_lib (version 20220914) (generator kicad_symbol_editor) " + meta_parts_text + "\n".join(part_sexps) + "\n)"
with open('symbols/kpm-jlcpcb-basic.kicad_sym', 'w') as f:
    f.write(filedata)

