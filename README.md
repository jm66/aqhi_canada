# Air Quality Health Index AQHI (aqhi_canada)

This package provides classes for accessing the Air Quality Health Index AQHI data published by Environment Canada.

```
from aqhi_canada.aqhi_data import AqhiData

aqhi = AqhiData(coordinates=(lat, long), language='english')
aqhi.conditions
{'aqhi': {'label': 'Air Quality Health Index', 'value': '2.1'}}

aqhi = AqhiData(coordinates=(lat, long), language='french')
aqhi.conditions
{'aqhi': {'label': 'Cote air santé', 'value': '2.1'}}
```