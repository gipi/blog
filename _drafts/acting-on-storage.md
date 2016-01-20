---
layout: post
comments: true
title: ""
---

```python
from django.core.files.storage import default_storage
from PIL import Image

def act_on_media_file(instance):

    f = default_storage.open(file_path, 'r')
    image = Image.open(f)
```
