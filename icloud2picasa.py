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
    Support syncing new things in Picasa to photo stream.

'''

#import gdata.photos.service
#import gdata.media

__app_name___ = 'iCloud2Picasa'

def get_saved_variables():
    '''Tries to read a pickled hash from disk. Will return the hash or None.'''
    pass

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

    print(variables)

def login(variables):
    '''To do: Takes the hash where it will extract the username and OAuth token.
    If token is invalid (or doesn't exist), will ask the user to login so a
    valid token can be generated and added to the hash.
    Returns a valid gdclient.'''

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
    #Download list of photos from picasa
    #If this fails, should create the album
    album_url = '/data/feed/api/user/{0}/albumid/{1}'.format(variables['username'], variables['picasaalbum'])
    try:
        photos = client.GetFeed(album_url + '?kind=photo')
    except GooglePhotosException:
        #Try creating the album first
        album_entry = client.InsertAlbum(variables['picasaalbum'], 'This is where pictures taken from your phone ends up.', access='private', commenting_enabled='false')
        #And retry
        photos = client.GetFeed(album_url + '?kind=photo')
        
    picasa_photos = photos.entry
    for photo in photos.entry:
        print 'Photo title:', photo.title.text

    #Get list of photos in photo stream folder
    pass
    #Create two delta lists, one to upload and one to download.
    files_to_upload = ()
    photos_to_download = ()

    #Upload
    #Remove extension (last 4 chards) for title. Use empty description.
    for filename in files_to_upload:
        photo = gd_client.InsertPhotoSimple(album_url, filename[:-4], '', filename, keywords = 'icloud,')
        #Add any necessary metadata here.

    #Download
    for photo in photos_to_download:
        url = photo.GetMediaURL()
        #Download url to specified directory
        pass
    

if __name__ == '__main__':
    #Read login info and other variables from disk
    variables = get_saved_variables()
    #Ask user for missing data
    variables = add_missing_variables(variables)
    #Login
    client = login(variables)
    #Sync
    sync(client, variables)
