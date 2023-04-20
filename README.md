KPM JLCPCB Basic
================

A `kpm` package for the basic parts in the JLCPCB catalogue.

So far it supports:
- resistors
- capacitors

Wanted parts:
- diodes
- LEDs
- 


Installation
------------

Configure your `kpm.json` file to include this library as a dependency. eg:
```json
{
    "name": "your-project",
    "version": "0.0.1",
    "author": "Your Name",
    "homepage": "",
    "commands": {},
    "dependencies": {
        "kpm-jlcpcb-basic": "0.0.5",
    }
}
```

Then install the packages for your project:
```bash
$ kpm install .
```

Your symbols and footprints should be available in your parts menu!
