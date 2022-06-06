import json
import urllib.request


def parse_json(json_data):

    # list_keys=['Title', 'Year', 'Rated', 'Released', 'Runtime', 'Genre',
    # 'Director', 'Writer', 'Actors', 'Plot', 'Language', 'Country',
    # 'Awards', 'Ratings', 'Metascore', 'imdbRating', 'imdbVotes', 'imdbID']

    output = ''
    output += 'IMDB: '+urllib.parse.urljoin('https://www.imdb.com/title/', json_data['imdbID'])+'\n'

    information = {
        'Title': 'Titolo originale',
        'Country': 'Paese di produzione',
        'Genre': 'Genere',
        'Year': 'Anno',
        'Runtime': 'Durata',
        'Director': 'Regia',
        'Actors': 'Cast',
        # 'Plot':'Trama'
    }

    for k in information.keys():
        if k in list(json_data.keys()):
            output += f'{information[k]}: {json_data[k]}\n'
    return output


def get_json_data_from_url(url):
    uh = urllib.request.urlopen(url)
    data = uh.read()
    json_data = json.loads(data)
    return json_data


def save_poster(json_data, filename):
    title = json_data['Title']
    poster_url = json_data['Poster']
    # Splits the poster url by '.' and picks up the last string as file extension
    poster_file_extension = poster_url.split('.')[-1]
    # Reads the image file from web
    poster_data = urllib.request.urlopen(poster_url).read()

    # Creates new directory if the directory does not exist. Otherwise, just use the existing path.
    # if not os.path.isdir(savelocation):
    #    os.mkdir(savelocation)

    # replace extension
    filename = filename+'_POSTER'+'.'+poster_file_extension
    with open(filename, 'wb') as my_file:
        my_file.write(poster_data)


def get_description_omdb(omdbapi, title, year, filename, download_poster=True):
    print(f'Retrieving the data of "{title}" ({year}) now... ')

    try:

        serviceurl = 'http://www.omdbapi.com/?'

        params = urllib.parse.urlencode({'apikey': omdbapi, 't': title, 'y': year})
        url = serviceurl + params
        print(url)

        json_data = get_json_data_from_url(url)

        if json_data['Response'] == 'True':
            # Asks user whether to download the poster of the movie
            if json_data['Poster'] != 'N/A' and download_poster is True:
                save_poster(json_data, filename)
            return parse_json(json_data)

        else:

            print("Error encountered: ", json_data['Error'])
            imdb_id = input("Try again by entering the specific IMDB ID: ")

            params = urllib.parse.urlencode({'apikey': omdbapi, 'i': imdb_id})
            url = serviceurl + params
            print(url)

            json_data = get_json_data_from_url(url)

            if json_data['Response'] == 'True':
                if json_data['Poster'] != 'N/A' and download_poster is True:
                    save_poster(json_data, filename)
                return parse_json(json_data)
            else:
                print("Error encountered: ", json_data['Error'])
                print("Skipping to next one, fix manually later...")
                return ''

    except urllib.error.URLError as error:
        print(f"ERROR: {error.reason}")
        return ''
