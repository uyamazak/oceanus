#!/bin/bash
# you need run this, when git clone
# create common file hard links
ln common/settings.py redis2bq/www/common/settings.py
ln common/utils.py redis2bq/www/common/utils.py

ln common/settings.py oceanus/www/common/settings.py
ln common/utils.py oceanus/www/common/utils.py
