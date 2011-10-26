'''
This script synchronizes Apple photo stream with Google Picasa web albums.
The windows application for photo stream will download new photos taken on iOS
devices into a "Photo stream" folder. If you place photos in a specified
"Upload" folder, then photo stream will sync that to all connected iOS devices
(and also add it to you photo stream folder on the same machine).

The goal with this script is to upload newly synced photos in the photo stream
folder to a specified folder (by default, 'Instant Upload' to match Android) on
Picasa Web albums. If it does not exist, it should be created.

Things I might add:
    Support syncing new things in Picasa to photo stream. Code for this has already been written. But it needs some mroe work.

'''

import pickle
import urllib
import os, re
import gdata.photos.service

__app_name___ = 'iCloud2Picasa'
__save_file__ = 'variables.txt'
__tag__ = 'icloud'
__jpg_finder__ = re.compile('^(.*)\.[jJ][pP][eE]?[gG]$')

def main():
    #Read login info and other variables from disk
    variables = get_saved_variables()
    #Ask user for missing data
    variables = add_missing_variables(variables)
    #Login
    client = login(variables)
    #Sync
    sync(client, variables)
    #Save variables
    save_variables(variables)

def get_saved_variables():
    '''Tries to read a pickled hash from disk. Will return the hash or None.'''
    variables = None
    try:
        with open(__save_file__, 'r') as f:
            variables = pickle.load(f)
    except IOError:
        print 'No save file found, will create it later...'
    return variables
    
def save_variables(variables):
    '''Saves variables to disk'''
    with open(__save_file__, 'w') as f:
        pickle.dump(variables, f)

def add_missing_variables(variables = None):
    '''If variables is None, then will ask for all variables.
    Otherwise, only ask for missing ones.
    Variables should be a hash of username, token, stream folder, upload
    folder, etc...'''
    
    if variables is None:
        variables = {}

    if 'username' not in  variables:
        variables['username'] = raw_input('Username: ')

    if 'password' not in  variables:
        variables['password'] = raw_input('Password: ')
    
    if 'photostreamfolder' not in variables:
        variables['photostreamfolder'] = raw_input('Photo Stream folder: ')

    if 'uploadfolder' not in variables:
                variables['uploadfolder'] = raw_input('Photo Stream upload folder: ')
    
    if 'picasaalbum' not in variables:
        variables['picasaalbum'] = raw_input('Name of Picasa album to use: ')

    return variables

def login(variables):
    '''To do: Takes the hash where it will extract the username and OAuth token.
    If token is invalid (or doesn't exist), will ask the user to login so a
    valid token can be generated and added to the hash.
    Returns a valid gdclient.'''
    print("Logging in...")
    client = gdata.photos.service.PhotosService()
    client.ClientLogin(variables['username'], variables['password'])

    return client

def sync(client, variables):
    '''Takes a valid client to access data with and a variables hash where
    folders are specified.
    This function will then download a list of recent photos and compare to the
    photos in the photo stream folder. Any new photos in the photo stream
    folder is then uploaded to Picasa. New photos in Picasa are downloaded to
    the upload folder.'''
    #First acquire the id of the album
    #If this fails, weshould create the album
    album_id = ''
    albums = client.GetUserFeed()
    print("Getting album list from Picasa...")
    for album in albums.entry:
        if album.title.text == variables['picasaalbum']:
            album_id = album.gphoto_id.text
            break
            
    if album_id == '':
        print("Creating Picasa album since it could not be found...")
        album = client.InsertAlbum(variables['picasaalbum'], 'This is where pictures taken from your phone ends up.', access='private', commenting_enabled='false')
        album_id = album.gphoto_id.text
    
    #Download list of photos from picasa
    print("Downloading photo list from Picasa...")
    album_url = '/data/feed/api/user/{0}/albumid/{1}'.format(variables['username'], album_id)
    photos = client.GetFeed(album_url + '?kind=photo')
        
    picasa_photos = photos.entry

    #Upload
    files_to_upload = []
    picasa_titles = [photo.title.text for photo in picasa_photos]
    print("Determining which photos to upload...")
    #Get list of photos in photo stream folder
    for (filepath, filename) in locate(variables['photostreamfolder']):
        match = __jpg_finder__.match(filename)
        name = match.group(1)
        if (filename not in picasa_titles) and (name not in picasa_titles):
            files_to_upload.append(filepath)
            
    #Use empty description.
    print("Uploading files...")
    for filepath in files_to_upload:
        (path, filename) = os.path.split(filepath)
        print 'Uploading: ' + filename
        photo = client.InsertPhotoSimple(album_url, filename, '', filepath, keywords = [__tag__])
        #Add any necessary metadata here.

    #Download
	'''
	photos_to_download = []
    print("Determining which photos to download...")
    for photo in picasa_photos:
        #If the photo does not have the icloud tag, then we should download it.
        if str(photo.media.keywords.text).find(__tag__) == -1:
            photos_to_download.append(photo)
			
    print("Downloading files...")
    for photo in photos_to_download:
        url = photo.GetMediaURL()
        filename = photo.title.text
        #match = __jpg_finder__.match(filename)
        #if match is None or match.group(0) is None:
        #    filename += ".jpg"
        #Download url to specified directory
        print "Downloading: " + url + " to: " + os.path.join(variables['uploadfolder'], filename)
        try:
            #with open(os.path.join(variables['uploadfolder'], filename), 'w') as f:
            #    f.write(urllib.urlopen(url).read())

            #Add the icloud tag to the photo
            if not photo.media.keywords:
                photo.media.keywords = gdata.media.Keywords()

            if not photo.media.keywords.text:
                photo.media.keywords.text = __tag__
            else:
                photo.media.keywords.text = __tag__ + ', ' + photo.media.keywords.text

            client.UpdatePhotoMetadata(photo)
        except IOError:
            print 'Could not save file! ' + filename
	'''
        
def locate(root):
    '''Locate all files matching supplied filename pattern in and below
    supplied root directory.'''
    for path, dirs, files in os.walk(os.path.abspath(root)):
        for match in [__jpg_finder__.match(file) for file in files]:
            if match is not None:
                filename = match.group(0)
                yield (os.path.join(path, filename), filename)

if __name__ == '__main__':
    main()