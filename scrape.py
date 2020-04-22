import calendar
import json
import re

from selenium.webdriver import Firefox
from selenium.webdriver.firefox.options import Options


def main():
    options = Options()
    options.add_argument('-headless')
    driver = Firefox(executable_path='/usr/bin/geckodriver', options=options)
    output_json = {}
    for animal in ['Bugs', 'Fish']:
        output_json[animal] = {}
        for hemisphere in ['Northern', 'Southern']:
            url = f'https://animalcrossing.fandom.com/wiki/{animal}_(New_Horizons)#{hemisphere}%20Hemisphere'
            driver.get(url)
            print(f'processing: {url}')
            table = driver.find_element_by_css_selector('table.sortable tbody')
            output_json[animal][hemisphere] = clean_table(table, animal)

    with open('out.json', 'w+') as fp:
        json.dump(output_json, fp, indent=2, sort_keys=True)
    
    driver.close()

def clean_table(table, animal):
    json = {}
    for row in table.find_elements_by_tag_name('tr'):
        elements = row.find_elements_by_tag_name('td')
        if animal == 'Fish':
            name, image, price, location, shadow_size, time = elements[:6]
            months = elements[6:]
        else:
            name, image, price, location, time = elements[:5]
            months = elements[5:]
        times = parse_time(time.text.strip())
        month_array = get_months(months)
        json[name.text] = {
            'price': price.text,
            'location': location.text,
            'time_string': time.text,
            'times': times,
            'months': month_array,
        }
        try:
            json[name.text]['shadow_size'] = shadow_size.text
        except:
            pass
    return json


def parse_time(time_string):
    if time_string == 'All day':
        return [0000, 0000]
    if '&' in time_string:
        time_strings = time_string.split('&')
        return parse_time(time_strings[0].strip()) + parse_time(time_strings[1].strip())
    match = re.match(r'(\d+) ([AP]M) - (\d+) ([AP]M)', time_string)
    ret = []
    for i in range(1, len(match.groups()), 2):
        if match.group(i + 1) == 'AM':
            ret.append(int(match.group(i)))
        else:
            ret.append(int(match.group(i)) + 12)
    return ret


def get_months(months):
    month_array = []
    for i in range(len(months)):
        if months[i].text.strip() != '-':
            month_array.append(calendar.month_abbr[i + 1])
    return month_array


if __name__ == '__main__':
    main()