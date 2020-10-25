# Halfbakery Driver

Usage, under `Python >= 3.5.3`, `pip install metadrive==1.4.28` (tested with `halfbakery-driver==0.1.5`).

Some examples:

## Get the ideas of a particular Halfbakery user:

```python
import metadrive
from halfbakery_driver.api import Idea, User

def get_ideas(username):

    drive = metadrive.drives.get('halfbakery-driver')
    Idea.drive = drive
    User.drive = drive

    user = User({'-': f'https://www.halfbakery.com/user/{username}'})
    user._refresh()

    ideas = []

    for i, item in enumerate(user['ideas']):
        print(i, item.get('-'))
        idea = Idea(item)
        idea._refresh()
        ideas.append(idea)

    return ideas

user_ideas = get_ideas('MaxwellBuchanan')
```

## Iterate over all ideas in Halfbakery:

```python
import metadrive
from halfbakery_driver.api import Idea
drive = metadrive.drives.get('halfbakery-driver')

for idea in Idea._filter(drive=drive):
    if 'A slightly early farewell' in idea['title']:
        break

# Get the details of a particular idea.
idea._refresh()
```
