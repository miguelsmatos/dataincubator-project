from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from urllib.request import urlopen
import numpy as np

def parse_station(station):
    '''
    This function parses the web pages downloaded from wunderground.com
    into a flat CSV file for the station you provide it.

    Make sure to run the wunderground scraper first so you have the web
    pages downloaded.
    '''

    # Scrape between July 1, 2014 and July 1, 2015
    # You can change the dates here if you prefer to parse a different range
    current_date = datetime(year=2015, month=1, day=1)
    end_date = datetime(year=2017, month=1, day=1)

    with open('{}.csv'.format(station), 'w') as out_file:
        out_file.write('date,actual_mean_temp,actual_min_temp,actual_max_temp,'
                       'average_min_temp,average_max_temp,'
                       'record_min_temp,record_max_temp,'
                       'record_min_temp_year,record_max_temp_year,'
                       'actual_precipitation,average_precipitation,'
                       'record_precipitation,'
                       'actual_snow,'
                       'average_snow,'
                       'snow_depth,'
                       'sea_pressure,'
                       'wind_speed,'
                       'max_wind_speed,'
                       'max_gust_speed,'
                       'visibility\n')

        while current_date != end_date:
            print(current_date)
            try_again = False
            with open('{}/{}-{}-{}.html'.format(station,
                                                current_date.year,
                                                current_date.month,
                                                current_date.day)) as in_file:
                soup = BeautifulSoup(in_file.read(), 'html.parser')

                try:

                    weather_data = soup.find(id='historyTable').find_all('span', class_='wx-value')
                    weather_data_units = soup.find(id='historyTable').find_all('td')
                    actual_mean_temp = weather_data[0].text
                    actual_max_temp = weather_data[2].text
                    average_max_temp = weather_data[3].text
                    record_max_temp = weather_data[4].text
                    actual_min_temp = weather_data[5].text                
                    average_min_temp = weather_data[6].text
                    record_min_temp = weather_data[7].text
                    record_max_temp_year = weather_data_units[
                        9].text.split('(')[-1].strip(')')
                    record_min_temp_year = weather_data_units[
                        13].text.split('(')[-1].strip(')')
        

                    actual_precipitation = weather_data[9].text
                    if actual_precipitation == 'T':
                        actual_precipitation = '0.0'
                    average_precipitation = weather_data[10].text
                    record_precipitation = weather_data[11].text

                    actual_snow  = weather_data[12].text
                    if 'T' in actual_snow:
                        actual_snow = '0.0'
                    average_snow = weather_data[13].text
                    

                    for i,eachEntry in enumerate(weather_data_units[:-1]):
                        if 'Max Wind Speed' in eachEntry.text:
                            value = weather_data_units[i+1].text.split()[0]
                            if value.isdigit():
                                max_wind_speed = value
                            else:
                                print('No max windspeed data')
                                max_wind_speed = '0.0'
                        elif 'Wind Speed' in eachEntry.text:
                            value = weather_data_units[i+1].text.split()[0]
                            if value.isdigit():
                                wind_speed = value
                            else:
                                print('No windspeed data')
                                wind_speed = '0.0'
                        elif 'Max Gust Speed' in eachEntry.text:
                            value = weather_data_units[i+1].text.split()[0]
                            if value.isdigit():
                                max_gust_speed = value
                            else:
                                max_gust_speed = '0.0'
                        elif 'Visibility' in eachEntry.text:
                            value = weather_data_units[i+1].text.split()[0]
                            if value.isdigit():
                                visibility = value
                            else:
                                print('No visibility data, keeping %s value' % str(visibility))
                                pass
                        elif 'Sea Level Pressure' in eachEntry.text:
                            if weather_data_units[i+1].text.split():
                                value = weather_data_units[i+1].text.split()[0]
                                if value.isdigit():
                                    sea_pressure = value
                                else:
                                    print('No visibility data, keeping %s value' % str(visibility))
                                    pass
                                if float(sea_pressure) < 900. or float(sea_pressure)> 1200:
                                    raise IndexError('Abnormal sea pressure %s, check var order' % sea_pressure)
                        elif 'Snow Depth' in eachEntry.text:
                            value = weather_data_units[i+1].text.split()[0]
                            if value[0].isdigit():
                                snow_depth = value
                            elif 'T' in value:
                                snow_depth = '0.0'
                            else:
                                snow_depth = '0.0'
                                print('No snow depth data:',weather_data_units[i+1].text.rstrip('\r\n') )

                except ValueError as e:
                    print(e)
                    for i,j in enumerate(weather_data):
                        print('%d: %s' % (i,str(j.text)))
                    for i,j in enumerate(weather_data_units):
                        print('%d: %s' % (i,str(j.text)))
                    exit()
                if False:
                    for i,j in enumerate(weather_data):
                        print('%d: %s' % (i,str(j.text)))
                    for i,j in enumerate(weather_data_units):
                        print('%d: %s' % (i,str(j.text)))

                # Verify that the parsed data is valid
                if (record_max_temp_year == '-1' or record_min_temp_year == '-1' or
                        int(record_max_temp) < max(int(actual_max_temp), int(average_max_temp)) or
                        int(record_min_temp) > min(int(actual_min_temp), int(average_min_temp)) or
                        float(actual_precipitation) > float(record_precipitation) or
                        float(average_precipitation) > float(record_precipitation)):
                    pass#raise Exception

                out_file.write('{}-{}-{},'.format(current_date.year, current_date.month, current_date.day))
                out_file.write(','.join([actual_mean_temp, actual_min_temp, actual_max_temp,
                                            average_min_temp, average_max_temp,
                                            record_min_temp, record_max_temp,
                                            record_min_temp_year, record_max_temp_year,
                                            actual_precipitation, average_precipitation,
                                            record_precipitation,
                                            actual_snow,average_snow,snow_depth,
                                            sea_pressure,
                                            wind_speed,max_wind_speed,max_gust_speed,visibility]))
                out_file.write('\n')
                current_date += timedelta(days=1)
            # If the web page needs to be downloaded again, re-download it from
            # wunderground.com

            # If the parser gets stuck on a certain date, you may need to investigate
            # the page to find out what is going on. Sometimes data is missing, in
            # which case the parser will get stuck. You can manually put in the data
            # yourself in that case, or just tell the parser to skip this day.
            if try_again:
                print('Error with date {}'.format(current_date))

                lookup_URL = 'http://www.wunderground.com/history/airport/{}/{}/{}/{}/DailyHistory.html'
                formatted_lookup_URL = lookup_URL.format(station,
                                                         current_date.year,
                                                         current_date.month,
                                                         current_date.day)
                html = urlopen(formatted_lookup_URL).read().decode('utf-8')

                out_file_name = '{}/{}-{}-{}.html'.format(station,
                                                          current_date.year,
                                                          current_date.month,
                                                          current_date.day)

                with open(out_file_name, 'w') as out_file:
                    out_file.write(html)


# Parse the stations used in this article
for station in ['KNYC']:
    parse_station(station)
