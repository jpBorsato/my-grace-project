COTEXT_DATE_FORMAT = {
    0: ("\S.\d.", lambda s: s),
    1: ("Y", lambda s: s),
    2: ("F \d\e Y", lambda s: s),
    3: ("j \d\e F \d\e Y", str.lower)
}
