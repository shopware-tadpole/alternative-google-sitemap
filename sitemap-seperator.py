from lxml import etree
import argparse
import os
import gzip
from datetime import datetime
from pprint import pprint

def new_sub_sitemap_element():
    return etree.Element("urlset", xmlns="http://www.sitemaps.org/schemas/sitemap/0.9")

def save_sub_sitemap(filename, xml_root_el, pretty_print=False, compress=True):
    tree_new = etree.ElementTree(xml_root_el)
    # pretty_print = True only for debug
    if compress:
        with gzip.open(filename, "wb") as f:
            f.write(b'<?xml version="1.0" encoding="UTF-8"?>\n')
            f.write(etree.tostring(tree_new, pretty_print=pretty_print))
    else:
        tree_new.write(filename, encoding='UTF-8', pretty_print=pretty_print, doctype='<?xml version="1.0" encoding="UTF-8"?>')


arg_parser = argparse.ArgumentParser(description='')
arg_parser.add_argument('--input-dir', type=str, help='Path to original shopware sitemap')
arg_parser.add_argument('--output-dir', type=str, help='Path where the seperated sitemap should be stored. Output dir has to be accessible from outside via the the shop url, defined via "frontend_url"')
arg_parser.add_argument('--frontend-url', type=str, help='Url to seperated sitemap')
arg_parser.add_argument('--entry-limit', type=int, default=1000, help='Maximum entries per file. Default: 1000')
arg_parser.add_argument('--compress', action='store_true', help='Compress sitemap with gzip if set')
arg_parser.add_argument('--debug', action='store_true', help='Addional output and pretty prints the sitemap to make it human readable')

args = arg_parser.parse_args()
input_dir = args.input_dir
output_dir = args.output_dir
frontend_url = args.frontend_url
entry_limit = args.entry_limit
compress = args.compress
DEBUG_MODE = args.debug
if input_dir.endswith('/'):
    input_dir = input_dir[:-1]
if output_dir.endswith('/'):
    output_dir = output_dir[:-1]
if frontend_url.endswith('/'):
    frontend_url = frontend_url[:-1]

if DEBUG_MODE:
    print("Debug mode on")

if DEBUG_MODE:
    print("Options:")
    print("input-dir: " + input_dir)
    print("output-dir: " + output_dir)
    print("frontend-url: " + frontend_url)
    print("entry-limit: " + str(entry_limit))
    print("Compress: " + str(compress))

# Create output dir if not exists
os.makedirs(output_dir, exist_ok=True)
if output_dir == "" or output_dir == "":
    print("Invalid output dir: '" + output_dir + "'")

# Delete old Sitemap files within the output dir if exists
for file in os.listdir(output_dir):
    if file.endswith(".xml") or file.endswith(".xml.gz"):
        file_path = os.path.join(output_dir, file)
        os.remove(file_path)

# Store data abouzt new created sitemap files here
sitemap_files_new = []
# Cunt of entries in current xml file
cur_entry_cnt = 0
# Store new created (sepereated) xml data in new root el
xml_root_el_new = None

# Handle all xml and gz files in given input dir and seperate the xml entries in multiple seperated files (not recursive for sub dirs) 
for file in os.listdir(input_dir):
    file_path = input_dir + "/" + file
    
    input = None
    # Unpack before using if .gz
    if file.endswith('.xml.gz'):
        input = gzip.open(file_path, 'r')
    elif file.endswith('.xml'):
        input = file_path
    # Skip if no valid file format
    else:
        print("WARNING: File '" + file_path + "' is not valid. Skip File.")
        continue
    
    # Do not strip the cdata and use recover, so also bad formed xml is parsed (and can be saved later without the invalid chars)
    xml_parser_orig = etree.XMLParser(recover=True, strip_cdata=False)
    xml_tree_orig = etree.parse(input, xml_parser_orig)
    
    # Read the xml file
    xml_root_el_orig = xml_tree_orig.getroot()
    
    # Iterate over all url elements of origial xml file
    for xml_url_el_orig in xml_root_el_orig.iter("{http://www.sitemaps.org/schemas/sitemap/0.9}url"):
        # New sitemap xml file
        if cur_entry_cnt == 0:
            xml_root_el_new = new_sub_sitemap_element()
            file_num = len(sitemap_files_new) + 1
            sitemap_name = "sitemap-" + str(file_num) + ".xml"
            if compress:
                sitemap_name = "sitemap-" + str(file_num) + ".xml.gz"
            sitemap_server_path = os.path.join(output_dir, sitemap_name)
            sitemap_files_new.append({'path': sitemap_server_path, 'name': sitemap_name})
        
        # Get original data
        loc_entries = xml_url_el_orig.findall('{http://www.sitemaps.org/schemas/sitemap/0.9}loc')
        if (len(loc_entries) < 1):
            print("Url Entry has no entry 'loc'. Skip entry.")
            continue
        loc = loc_entries[0].text
        
        lastmod_entries = xml_url_el_orig.findall('{http://www.sitemaps.org/schemas/sitemap/0.9}lastmod')
        if (len(lastmod_entries) < 1):
            print("Url Entry has no entry 'lastmod'. Skip entry.")
            continue
        lastmod = lastmod_entries[0].text

        changefreq_entries = xml_url_el_orig.findall('{http://www.sitemaps.org/schemas/sitemap/0.9}changefreq')
        if (len(changefreq_entries) < 1):
            print("Url Entry has no entry 'changefreq'. Skip entry.")
            continue
        changefreq = changefreq_entries[0].text

        priority_entries = xml_url_el_orig.findall('{http://www.sitemaps.org/schemas/sitemap/0.9}priority')
        if (len(priority_entries) < 1):
            print("Url Entry has no entry 'priority'. Skip entry.")
            continue
        priority = priority_entries[0].text

        # Create new data
        cur_entry_cnt += 1
        xml_url_el_new = etree.SubElement(xml_root_el_new, "url")

        etree.SubElement(xml_url_el_new, "loc").text = loc
        etree.SubElement(xml_url_el_new, "lastmod").text = lastmod
        etree.SubElement(xml_url_el_new, "changefreq").text = changefreq
        etree.SubElement(xml_url_el_new, "priority").text = priority

        if cur_entry_cnt >= entry_limit:
            cur_entry_cnt = 0
            save_sub_sitemap(sitemap_files_new[-1]['path'], xml_root_el_new, DEBUG_MODE, compress)

# Save xml file when not filed fully
if cur_entry_cnt < entry_limit:
    save_sub_sitemap(sitemap_files_new[-1]['path'], xml_root_el_new, DEBUG_MODE, compress)

# Create main Sitemap
xml_root_el_main = etree.Element("sitemapindex", xmlns="http://www.sitemaps.org/schemas/sitemap/0.9")
for sitemap_data in sitemap_files_new:
    sitemap_name = sitemap_data['name']
    sitemap_path = sitemap_data['path']

    # Get last modification time of created sitemap file and format it
    last_modified = os.stat(sitemap_path).st_mtime
    last_modified_formatted = datetime.fromtimestamp(last_modified).strftime("%Y-%m-%d")
    #pprint(last_modified_formatted)
    xml_sitemap_el = etree.SubElement(xml_root_el_main, "sitemap")
    etree.SubElement(xml_sitemap_el, "loc").text = frontend_url + "/" + sitemap_name
    etree.SubElement(xml_sitemap_el, "lastmod").text = last_modified_formatted
    # pprint(datetime.utcnow().strftime("%d/%m/%Y %H:%M:%S %z"))
xml_main_tree = etree.ElementTree(xml_root_el_main)
xml_main_tree.write(os.path.join(output_dir, "sitemap.xml"), encoding="UTF-8", pretty_print=True, doctype='<?xml version="1.0" encoding="UTF-8"?>')