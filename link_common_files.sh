#!/bin/bash
# you need run this, when git clone
# create common file hard links
ln -i common/settings.py redis2bq/www/common/settings.py
ln -i common/utils.py redis2bq/www/common/utils.py

ln -i common/settings.py oceanus/www/common/settings.py
ln -i common/utils.py oceanus/www/common/utils.py

ln -i common/settings.py sub2revelation/www/common/settings.py
ln -i common/utils.py sub2revelation/www/common/utils.py

ln -i common/settings.py table-manager/www/common/settings.py
ln -i common/utils.py table-manager/www/common/utils.py
