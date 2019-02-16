import halfbakery

def test_session():
    s = halfbakery._login()

def test_harvest():
    for item in halfbakery._harvest():
        print(item)
