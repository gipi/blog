---
layout: post
comments: true
title: "Django and stuffs around storages"
---

```python
from django.core.files.storage import default_storage
from PIL import Image

def act_on_media_file(instance):

    f = default_storage.open(file_path, 'r')
    image = Image.open(f)
```

## Testing

```python
import boto
from moto import mock_s3

class S3MotoMixin(object):
    def setupMoto(self):
        '''Call this to initialize the bicket'''
        conn = boto.connect_s3()
        # We need to create the bucket since this is all in Moto's 'virtual' AWS account
        conn.create_bucket(settings.AWS_STORAGE_BUCKET_NAME)


@mock_s3
@override_settings(
    MEDIA_ROOT=tempfile.mkdtemp(),
    AWS_ACCESS_KEY_ID='bau',
    AWS_SECRET_ACCESS_KEY='miao',
    AWS_STORAGE_BUCKET_NAME='bucket',
    AWS_CLOUDFRONT_DOMAIN='foobar',
    AWS_CLOUDFRONT_DISTRIBUTION_ID='kebba',
)
class MyAwesomeS3Tests(TestCase, S3MotoMixin):
    def setUp(self):
        self.setupMoto()

        # do your things
```
