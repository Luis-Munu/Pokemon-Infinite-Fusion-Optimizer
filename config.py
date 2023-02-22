from json import loads

profiles = loads(open("data/profiles.json", 'r').read())
settings = loads(open("settings.json", 'r').read())
type_info = loads(open("data/type_info.json", 'r').read())