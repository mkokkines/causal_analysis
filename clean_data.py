import os
import os.path
import csv
import ast
import datetime
import argparse
import dowhy

def convert_single_date_string_to_datetime_object(datestring):
    first_dash_index = datestring.find('-')
    second_dash_index = datestring.rfind('-')
    year = int(datestring[0:first_dash_index])
    month = int(datestring[first_dash_index + 1:second_dash_index])
    day = int(datestring[second_dash_index + 1:])
    return datetime.datetime(year, month, day)


def convert_date_strings_to_datetime_objects(weather_data):
    # Converting the date strings to datetime objects will allow us to
    # perform checks on the date without continually re-parsing the string.
    # The date strings are structured as YYYY-MM-DD.
    for single_day_weather in weather_data['daily_weather_data']:
        datestring = single_day_weather['date']
        single_day_weather['date'] = datetime_object


def process_single_day_weather_data(single_day_weather_data, need_to_clean_data=True):
    if need_to_clean_data:
        # Each row in the csv should have seven fields
        # If it does not, we cannot process it properly.
        if len(single_day_weather_data) != 7:
            return None

        # The fields at indexes 1, 2, and 3 (ref_evapotranspiration, min_temperature,
        # and max_temperature) are essential. If any of these values are missing,
        # simply return None
        for i in range(1, 4):
            if single_day_weather_data[i] == 'M' or single_day_weather_data[i] == ' M':
                return None

    # The essential fields are not missing!
    # Add the weather data to a dictionary and return said dictionary
    processed_single_day_weather_data = {}
    processed_single_day_weather_data['date'] = single_day_weather_data[0]
    processed_single_day_weather_data['ref_evapotranspiration'] = float(single_day_weather_data[1])
    processed_single_day_weather_data['min_temperature'] = float(single_day_weather_data[2])
    processed_single_day_weather_data['max_temperature'] = float(single_day_weather_data[3])

    # It is possible that the remaining fields have missing values.
    # If the values are present, we should convert them to floating point numbers
    # If they are missing, keep the 'M' string
    if single_day_weather_data[4] != 'M' and single_day_weather_data[4] != ' M':
        processed_single_day_weather_data['snow_depth'] = float(single_day_weather_data[4])
    else:
        processed_single_day_weather_data['snow_depth'] = 'M'

    if single_day_weather_data[5] != 'M' and single_day_weather_data[5] != ' M':
        processed_single_day_weather_data['snow_fall'] = float(single_day_weather_data[5])
    else:
        processed_single_day_weather_data['snow_fall'] = 'M'

    if single_day_weather_data[6] != 'M' and single_day_weather_data[6] != ' M':
        processed_single_day_weather_data['precipitation'] = float(single_day_weather_data[6])
    else:
        processed_single_day_weather_data['precipitation'] = 'M'

    return processed_single_day_weather_data


def load_dict_from_csv_file(file_path, need_to_clean_data=True):
    # The cleaned weather data dictionary will include all the metadata
    # and weather data from the given input file
    cleaned_weather_data = {}
    cleaned_weather_data['daily_weather_data'] = []

    with open(file_path) as weather_file:
        weather_file_reader = csv.reader(weather_file, delimiter=',')

        # The files are structured as follows:
        # 1) The first nine lines of the file contain metadata. We parse the metadata
        # using if statements below.
        # 2) The next two lines are blank. No parsing occurs when we arrive at these lines.
        # 3) The next line contains the column names. This line likewise is not parsed.
        # 4) The remaining lines contain weather data, which is processsed using a helper
        # function.
        line_count = 0
        for row in weather_file_reader:
            if line_count > 12:
                processed_single_day_weather_data = process_single_day_weather_data(
                    row, need_to_clean_data=need_to_clean_data
                )
                if processed_single_day_weather_data is not None:
                    cleaned_weather_data['daily_weather_data'].append(processed_single_day_weather_data)
            elif line_count == 0:
                cleaned_weather_data['station_name'] = row[1]
            elif line_count == 1:
                cleaned_weather_data['country'] = row[1]
            elif line_count == 2:
                cleaned_weather_data['state'] = row[1]
            elif line_count == 3:
                cleaned_weather_data['station_id'] = row[1]
            elif line_count == 4:
                cleaned_weather_data['network'] = row[1]
            elif line_count == 5:
                try:
                    cleaned_weather_data['longitude'] = float(row[1])
                except:
                    cleaned_weather_data['longitude'] = row[1]
            elif line_count == 6:
                try:
                    cleaned_weather_data['latitude'] = float(row[1])
                except:
                    cleaned_weather_data['latitude'] = row[1]
            elif line_count == 7:
                try:
                    cleaned_weather_data['elevation'] = float(row[1])
                except:
                    cleaned_weather_data['elevation'] = row[1]
            elif line_count == 8:
                try:
                    cleaned_weather_data['start_date'] = row[1]
                except:
                    cleaned_weather_data['start_date'] = "Unknown"
                try:
                    cleaned_weather_data['end_date'] = row[3]
                except:
                    cleaned_weather_data['end_date'] = "Unknown"

            line_count += 1

    return cleaned_weather_data


def write_metadata_to_csv(weather_data_writer, cleaned_weather_data):
    weather_data_writer.writerow(['Station Name:', cleaned_weather_data['station_name']])
    weather_data_writer.writerow(['Country:', cleaned_weather_data['country']])
    weather_data_writer.writerow(['State:', cleaned_weather_data['state']])
    weather_data_writer.writerow(['Station ID:', cleaned_weather_data['station_id']])
    weather_data_writer.writerow(['Network:', cleaned_weather_data['network']])
    weather_data_writer.writerow(['Longitude:', cleaned_weather_data['longitude']])
    weather_data_writer.writerow(['Latitude:', cleaned_weather_data['latitude']])
    weather_data_writer.writerow(['Elevation:', cleaned_weather_data['elevation']])
    weather_data_writer.writerow(
        ['Period of Record:', cleaned_weather_data['start_date'], '-', cleaned_weather_data['end_date']]
    )

    # Write to blank rows
    # This is done to match the format of the original files, which will in
    # turn allow us to use the same function when reading in the cleaned csvs
    weather_data_writer.writerow([])
    weather_data_writer.writerow([])


def write_data_to_csv_file(cleaned_weather_data, file_path):
    with open(file_path, 'w') as cleaned_weather_file:
        weather_data_writer = csv.writer(cleaned_weather_file, delimiter=',')

        # Write the metadata fields
        write_metadata_to_csv(weather_data_writer, cleaned_weather_data)

        # Now, write the names of the columns
        weather_data_writer.writerow(
            ['Date', 'Ref Evapotranspiration', 'Min Temperature', 'Max Temperature', 'Snow Depth', 'Snow Fall', 'Precipitation']
        )

        # Finally, write all of the weather data
        for single_day_weather in cleaned_weather_data['daily_weather_data']:
            weather_data_writer.writerow(
                [
                    single_day_weather['date'],
                    single_day_weather['ref_evapotranspiration'],
                    single_day_weather['min_temperature'],
                    single_day_weather['max_temperature'],
                    single_day_weather['snow_depth'],
                    single_day_weather['snow_fall'],
                    single_day_weather['precipitation']
                ]
            )



def write_side_by_side_data_to_csv_file(weather_data, file_path):
    with open(file_path, 'w') as weather_file:
        weather_data_writer = csv.writer(weather_file, delimiter=',')

        # Write the metadata fields
        write_metadata_to_csv(weather_data_writer, weather_data)

        # Now, write the names of the columns
        weather_data_writer.writerow(
            [
                'first_date',
                'second_date',
                'first_day_evapotranspiration',
                'next_day_evapotranspiration',
                'first_day_min_temp',
                'next_day_min_temp',
                'first_day_max_temp',
                'next_day_max_temp'
            ]
        )

        # Finally, write all of the weather data
        daily_weather = weather_data['daily_weather_data']
        for i in range(0, len(daily_weather) - 1):
            first_date = convert_single_date_string_to_datetime_object(daily_weather[i]['date'])
            second_date = convert_single_date_string_to_datetime_object(daily_weather[i + 1]['date'])
            if (second_date - first_date).days == 1:
                weather_data_writer.writerow(
                    [
                        daily_weather[i]['date'],
                        daily_weather[i + 1]['date'],
                        daily_weather[i]['ref_evapotranspiration'],
                        daily_weather[i + 1]['ref_evapotranspiration'],
                        daily_weather[i]['min_temperature'],
                        daily_weather[i + 1]['min_temperature'],
                        daily_weather[i]['max_temperature'],
                        daily_weather[i + 1]['max_temperature']
                    ]
                )


def write_evapotranspiration_to_csv_file(weather_data, file_path):
    with open(file_path, 'w') as weather_file:
        weather_data_writer = csv.writer(weather_file, delimiter=',')

        # Write the metadata fields
        write_metadata_to_csv(weather_data_writer, weather_data)

        # Now, write the names of the columns
        weather_data_writer.writerow(
            ['first_date', 'second_date', 'first_day_evapotranspiration', 'next_day_evapotranspiration']
        )

        # Finally, write all of the weather data
        daily_weather = weather_data['daily_weather_data']
        for i in range(0, len(daily_weather) - 1):
            first_date = convert_single_date_string_to_datetime_object(daily_weather[i]['date'])
            second_date = convert_single_date_string_to_datetime_object(daily_weather[i + 1]['date'])
            if (second_date - first_date).days == 1:
                weather_data_writer.writerow(
                    [
                        daily_weather[i]['date'],
                        daily_weather[i + 1]['date'],
                        daily_weather[i]['ref_evapotranspiration'],
                        daily_weather[i + 1]['ref_evapotranspiration']
                    ]
                )


def write_min_temp_to_csv_file(weather_data, file_path):
    with open(file_path, 'w') as weather_file:
        weather_data_writer = csv.writer(weather_file, delimiter=',')

        # Write the metadata fields
        write_metadata_to_csv(weather_data_writer, weather_data)

        # Now, write the names of the columns
        weather_data_writer.writerow(
            ['first_date', 'second_date', 'first_day_min_temp', 'next_day_min_temp']
        )

        # Finally, write all of the weather data
        daily_weather = weather_data['daily_weather_data']
        for i in range(0, len(daily_weather) - 1):
            first_date = convert_single_date_string_to_datetime_object(daily_weather[i]['date'])
            second_date = convert_single_date_string_to_datetime_object(daily_weather[i + 1]['date'])
            if (second_date - first_date).days == 1:
                weather_data_writer.writerow(
                    [
                        daily_weather[i]['date'],
                        daily_weather[i + 1]['date'],
                        daily_weather[i]['min_temperature'],
                        daily_weather[i + 1]['min_temperature']
                    ]
                )


def write_max_temp_to_csv_file(weather_data, file_path):
    with open(file_path, 'w') as weather_file:
        weather_data_writer = csv.writer(weather_file, delimiter=',')

        # Write the metadata fields
        write_metadata_to_csv(weather_data_writer, weather_data)

        # Now, write the names of the columns
        weather_data_writer.writerow(
            ['first_date', 'second_date', 'first_day_max_temp', 'next_day_max_temp']
        )

        # Finally, write all of the weather data
        daily_weather = weather_data['daily_weather_data']
        for i in range(0, len(daily_weather) - 1):
            first_date = convert_single_date_string_to_datetime_object(daily_weather[i]['date'])
            second_date = convert_single_date_string_to_datetime_object(daily_weather[i + 1]['date'])
            if (second_date - first_date).days == 1:
                weather_data_writer.writerow(
                    [
                        daily_weather[i]['date'],
                        daily_weather[i + 1]['date'],
                        daily_weather[i]['max_temperature'],
                        daily_weather[i + 1]['max_temperature']
                    ]
                )


def load_dict_from_cleaned_csv_file(file_path):
    return load_dict_from_csv_file(file_path, need_to_clean_data=False)


def load_dict_from_cleaned_txt_file(file_path):
    txt_file = open(file_path, 'r')
    weather_data = ast.literal_eval(txt_file.read())
    txt_file.close()
    return weather_data


def write_data_to_txt_file(cleaned_weather_data, file_path):
    cleaned_weather_file = open(file_path, 'w')
    cleaned_weather_file.write(str(cleaned_weather_data))
    cleaned_weather_file.close()


def clean_data():
    current_directory = os.getcwd()
    input_directory_path = current_directory + '/weather-data-all'
    output_txt_directory = current_directory + '/cleaned_all_top100_txt'
    output_csv_directory = current_directory + '/cleaned_all_top100_csv'
    output_side_by_side_directory = current_directory + '/cleaned_all_side_by_side_csv'
    output_evapotranspiration_directory = current_directory + '/cleaned_all_evapotranspiration_csv'
    output_min_temp_directory = current_directory + '/cleaned_all_min_temp_csv'
    output_max_temp_directory = current_directory + '/cleaned_all_max_temp_csv'

    # Create the output directories if they do not already exist
    if not os.path.exists(output_txt_directory):
        os.mkdir(output_txt_directory)
    if not os.path.exists(output_csv_directory):
        os.mkdir(output_csv_directory)
    if not os.path.exists(output_side_by_side_directory):
        os.mkdir(output_side_by_side_directory)
    if not os.path.exists(output_evapotranspiration_directory):
        os.mkdir(output_evapotranspiration_directory)
    if not os.path.exists(output_min_temp_directory):
        os.mkdir(output_min_temp_directory)
    if not os.path.exists(output_max_temp_directory):
        os.mkdir(output_max_temp_directory)

    # For each of the input files:
    # 1) Obtain the data as a dictionary. In the process of assembling the dictionary, clean the data.
    # 2) Write the cleaned data to a csv file that mirrors the format of the original csv file. If the format
    # is largely the same, the same utilities can be used to load the clean data into a dictionary later.
    # 3) Write the cleaned data to a txt file. The major advantage of a txt file is that we can simply
    # write the string representation of the dictionary. This allows us to load the dictionary in directly
    # without any further parsing next time we would like to use the data.
    # 4) Write the data to a series of three-column csv files
    input_directory = os.fsencode(input_directory_path)
    for file in os.listdir(input_directory):
        file_path = input_directory_path + '/' + os.fsdecode(file)
        weather_data = load_dict_from_csv_file(file_path)

        file_name_suffix = file_path[file_path.rfind('/') + 1:file_path.rfind('.')] + '_cleaned'
        output_txt_file = '{}/{}.{}'.format(
            output_txt_directory, file_name_suffix, 'txt'
        )
        output_csv_file = '{}/{}.{}'.format(
            output_csv_directory, file_name_suffix, 'csv'
        )
        output_csv_file_side_by_side = '{}/{}.{}'.format(
            output_side_by_side_directory, file_name_suffix, 'csv'
        )
        output_csv_file_evapostranspiration = '{}/{}.{}'.format(
            output_evapotranspiration_directory, file_name_suffix, 'csv'
        )
        output_csv_file_min_temp = '{}/{}.{}'.format(
            output_min_temp_directory, file_name_suffix, 'csv'
        )
        output_csv_file_max_temp = '{}/{}.{}'.format(
            output_max_temp_directory, file_name_suffix, 'csv'
        )

        write_data_to_txt_file(weather_data, output_txt_file)
        write_data_to_csv_file(weather_data, output_csv_file)
        write_side_by_side_data_to_csv_file(weather_data, output_csv_file_side_by_side)
        write_evapotranspiration_to_csv_file(weather_data, output_csv_file_evapostranspiration)
        write_min_temp_to_csv_file(weather_data, output_csv_file_min_temp)
        write_max_temp_to_csv_file(weather_data, output_csv_file_max_temp)


if __name__ == '__main__':
    clean_data()
