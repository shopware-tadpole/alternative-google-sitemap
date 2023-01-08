# Tiny Google Sitemap for Shopware
A script that splits Shopware's standard Google sitemap into many small digists for better readability. 

## How to use
The script must be called separately for each sales channel. The script can be called as cronjob. It is recommended to call the script after the original Sitemap was created by Shopware. The script is tested under python 3.10, but should also be compatible with other python versions >= 3.6.

### Note:
The script needs the Google Sitemap created by Shopware. It will then, based on the original sitemap, split and optimize the data.  
After the script was running successfully the sitemap is accessible under: {frontend-url}/sitemap.xml

### Options:
```
--input-dir DIR
    Path to original shopware sitemap
--output-dir DIR
    Path where the seperated sitemap should be stored.
    Output dir has to be accessible from outside via the the shop url, defined via "frontend_url"
--frontend-url URL
    Url to seperated sitemap
--entry-limit LIMIT
    Maximum entries per file. Default: 1000
--compress
    Compress sitemap with gzip if set
--debug
    Addional output and pretty prints the sitemap to make it human readable
```

### Example call:
```
python3 sitemap-seperator.py \
--input-dir "/path/to/shopware/public/sitemap/salesChannel-f48daa3eebeaf68ef62c8adb3f8e345a-e29a4d0aa55fe2ebb5fe2ece7ce3e20b/" \
--output-dir "/path/to/shopware/public/sitemap-tiny/de/" \
--frontend-url "https://your-shop.de/sitemap-tiny/de/"
```
In this example the sitemap index is available under https://your-shop.de/sitemap-tiny/de/sitemap.xml

### Attention:
The Script deletes all old .xml and .xml.gz in defined output-dir before creating the new sitemap files. So make sure you specify the correct directory.

## ToDo:
Add option to make entry parameter "priority" optional, so sitemap is even smaller.