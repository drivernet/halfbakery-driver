# Halfbakery Driver

Usage, under `Python >= 3.5.3`, `pip install metadrive==1.4.28` (tested with `halfbakery-driver==0.1.5`).

```python
import metadrive
drive = metadrive.drives.get('halfbakery-driver')

from halfbakery_driver.api import Idea

ideas = Idea._filter(drive=drive)

for idea in ideas:
    if 'A slightly early farewell' in idea['title']:
        break

# print(idea)

idea._refresh()

print(idea)
```
