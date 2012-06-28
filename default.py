# -*- coding: utf-8 -*-
'''
    @document   : default.py
    @package    : MyPlex XBMC add-on
    @author     : Rick Crook
    @copyright  : 2012, Rick Crook 
    @thanks     : to Zsolt Torok for his example SoundCloud add-on
    @version    : 0.1.1

    @license    : Gnu General Public License - see LICENSE.TXT
    @description: myPlex XBMC add-on
''' 
'''
This file is part of XBMC MyPlex Plugin.

XBMC MyPlex Plugin is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

XBMC MyPlex Plugin is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with XBMC MyPlex Plugin.  If not, see <http://www.gnu.org/licenses/>.

'''
import sys
import xbmc, xbmcgui, xbmcplugin, xbmcaddon
import myplex.client as myplex
import urllib

# plugin related constants
PLUGIN_URL = u'plugin://video/myplex-xbmc/'
PLUGIN_ID = u'plugin.video.myplex-xbmc'
ADDON = xbmcaddon.Addon(id=PLUGIN_ID)
LANGUAGE = ADDON.getLocalizedString

# XBMC plugin modes
MODE_VIDEO_PLAY = 15
MODE_USERS_VIDEOS = 29
MODE_USERS_SECTIONS = 30
MODE_USERS_SERVERS = 31
MODE_DIRECTORY = 3
MODE_PLAYLISTS = 2

# Parameter keys
PARAMETER_KEY_OFFSET = u'offset'
PARAMETER_KEY_LIMIT = u'limit'
PARAMETER_KEY_MODE = u'mode'
PARAMETER_KEY_URL = u'url'
PARAMETER_KEY_PERMALINK = u'permalink'
PARAMETER_KEY_TOKEN = u'token'
PARAMETER_KEY_SERVER = u'server'
PARAMETER_KEY_HOST = u'host'
PARAMETER_KEY_PORT = u'port'

# Plugin settings
SETTING_USERNAME = u'username'
SETTING_PASSWORD = u'password'
# @feature: add offset and quality features

def _parameters_string_to_dict(parameters):
    ''' Convert parameters encoded in a URL to a dict. '''
    paramDict = {}
    if parameters:
        paramPairs = parameters[1:].split("&")
        for paramsPair in paramPairs:
            paramSplits = paramsPair.split('=')
            if (len(paramSplits)) == 2:
                paramDict[paramSplits[0]] = paramSplits[1]
    return paramDict

loginerror = False
params = _parameters_string_to_dict(sys.argv[2])
url = urllib.unquote_plus(params.get(PARAMETER_KEY_URL, ""))
permalink = urllib.unquote_plus(params.get(PARAMETER_KEY_PERMALINK,""))
name = urllib.unquote_plus(params.get("name", ""))
mode = int(params.get(PARAMETER_KEY_MODE, "0"))
nexturl = params.get("nexturl","")
query = urllib.unquote_plus(params.get("q", ""))
token = urllib.unquote_plus(params.get(PARAMETER_KEY_TOKEN,""))
server = urllib.unquote_plus(params.get(PARAMETER_KEY_SERVER,""))

handle = int(sys.argv[1])

username = xbmcplugin.getSetting(handle, SETTING_USERNAME)
password = xbmcplugin.getSetting(handle, SETTING_PASSWORD)

myplex_client = myplex.MyPlexClient(username,password,token)

if (not myplex_client.login):
  msg = LANGUAGE(32) + ':' + myplex_client.loginerror
  xbmc.executebuiltin("Notification(%s,%s,%i)" % (LANGUAGE(31), msg, 5000))
  ADDON.openSettings()

def addDirectoryItem(name, label2='', infoType="Video", infoLabels={}, isFolder=True, parameters={}, url=""):
    ''' Add a list item to the XBMC UI.'''
    li = xbmcgui.ListItem(name, label2)
    if not infoLabels:
        infoLabels = {"Title": name }

    li.setInfo(infoType, infoLabels)
    if url=="":
        url = sys.argv[0] + '?' + urllib.urlencode(parameters) 
    else:
        #activities next url
        url = sys.argv[0] + '?' + urllib.urlencode(parameters) + '&' + "nexturl=" + url
    return xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=url, listitem=li, isFolder=isFolder)
           
def showDirectory(directory, parameters={}):
  ''' Show a list as an XBMC directory
  '''  
  # Create directory
  for dir in directory:
    # @refactor move creation of listitem to new function
    dirTitle = dir['title']
    dirURL = dir[myplex._URL]
    dirToken = dir[myplex._TOKEN]
    
    li = xbmcgui.ListItem(label=dirTitle)
    # add meta data to ListItem
    infoLabels = {"Title": dirTitle }
    infoType = 'Video'
    li.setInfo(infoType, infoLabels)
    
    if (dir[myplex._PLAYABLE]):
      nextMode = MODE_VIDEO_PLAY
      li.setProperty("IsPlayable", "true")
    else:
      nextMode = MODE_DIRECTORY
      
    dirParameters = {PARAMETER_KEY_MODE: nextMode, PARAMETER_KEY_URL: PLUGIN_URL + "directory/" + dirTitle.encode('ascii', 'ignore'), PARAMETER_KEY_PERMALINK: dirURL, PARAMETER_KEY_TOKEN: dirToken}
    url = sys.argv[0] + '?' + urllib.urlencode(dirParameters)
    ok = xbmcplugin.addDirectoryItem(handle, url=url, listitem=li, isFolder=dir[myplex._FOLDER])
  return xbmcplugin.endOfDirectory(handle=handle, succeeded=True)
  
def show_videos(videos, parameters={}):
    ''' Show a list of tracks.  '''
    xbmcplugin.setContent(handle, "movies")
    for video in videos:
        # @feature: add thumbnail and fan art
        # 
        li = xbmcgui.ListItem(label=video[myplex.VIDEO_TITLE])
        properties = {'studio': video['studio'],
        'mpaa': video['contentRating'],
        'plot': video['summary'],
        'rating': video['rating'],
        'year': video['year'],
        'duration': video['duration'],
        'premieried': video['originallyAvailableAt'],
        #'bitrate',
        #'width',
        #'height',
        #'aspectRatio',
        #'audioChannels',
        #'audioCodec',
        #'videoCodec',
        #'videoResolution',
        #'container',
        #'videoFrameRate',
        #'optimizedForStreaming'
        'size': video['size']}
        
        li.setInfo( type='video', infoLabels=properties )
        li.setProperty("IsPlayable", "true")
        videoid = str(video[myplex.VIDEO_STREAM_URL])
        video_parameters = {PARAMETER_KEY_MODE: MODE_VIDEO_PLAY, PARAMETER_KEY_URL: PLUGIN_URL + "videos/" + videoid, "permalink": videoid}
        url = sys.argv[0] + '?' + urllib.urlencode(video_parameters)
        ok = xbmcplugin.addDirectoryItem(handle, url=url, listitem=li, isFolder=False)
    xbmcplugin.endOfDirectory(handle=handle, succeeded=True)

def show_sections(sections, parameters={}):
    ''' Show a list of sections    '''
    for section in sections:
        section_title = section[myplex._TITLE]
        section_url = section[myplex._URL]
        section_token = section[myplex._TOKEN]
        section_host = section[myplex._SERVER]
        li = xbmcgui.ListItem(label=section_title)
        section_parameters = {PARAMETER_KEY_MODE: MODE_DIRECTORY, PARAMETER_KEY_URL: PLUGIN_URL + "sections/" + section_title, PARAMETER_KEY_HOST: section_host, PARAMETER_KEY_PERMALINK: section_url, PARAMETER_KEY_TOKEN: section_token}
        url = sys.argv[0] + '?' + urllib.urlencode(section_parameters)
        ok = xbmcplugin.addDirectoryItem(handle, url=url, listitem=li, isFolder=True)
    xbmcplugin.endOfDirectory(handle=handle, succeeded=True)    

def show_servers(servers, parameters={}):
    ''' Show a list of servers.     '''
    for server in servers:
        server_title = server[myplex._TITLE]
        server_url = server[myplex._URL]
        server_token = server[myplex._TOKEN]
        li = xbmcgui.ListItem(label=server_title)
        server_parameters = {PARAMETER_KEY_MODE: MODE_USERS_SECTIONS, PARAMETER_KEY_URL: PLUGIN_URL + "servers/" + server_title, PARAMETER_KEY_PERMALINK: server_url, PARAMETER_KEY_TOKEN: server_token}
        url = sys.argv[0] + '?' + urllib.urlencode(server_parameters)
        ok = xbmcplugin.addDirectoryItem(handle, url=url, listitem=li, isFolder=True)
    xbmcplugin.endOfDirectory(handle=handle, succeeded=True) 

def play_video(id):
    ''' Start to stream the video with the given id. '''
    li = xbmcgui.ListItem(label='TestTitle', path=id)
    # @feature: Decorate ListItem with metadata
    # @feature: Add offset and quality parameters to URL from settings
    xbmcplugin.setResolvedUrl(handle=int(sys.argv[1]), succeeded=True, listitem=li)

def show_root_menu():
    ''' Show the plugin root menu. '''
    addDirectoryItem(name=LANGUAGE(10), parameters={PARAMETER_KEY_URL: PLUGIN_URL + 'servers', PARAMETER_KEY_MODE: MODE_USERS_SERVERS, PARAMETER_KEY_TOKEN: token}, isFolder=True)
    addDirectoryItem(name=LANGUAGE(11), parameters={PARAMETER_KEY_URL: PLUGIN_URL + 'playlists', PARAMETER_KEY_MODE: MODE_PLAYLISTS, PARAMETER_KEY_TOKEN: token}, isFolder=True)
    xbmcplugin.endOfDirectory(handle=handle, succeeded=True)
##################################################################

# Depending on the mode, call the appropriate function to build the UI.
if not sys.argv[ 2 ] or not url:
    ok = show_root_menu()
elif mode == MODE_DIRECTORY:
    directory = myplex_client.getList(permalink)
    ok = showDirectory(parameters={PARAMETER_KEY_MODE: mode, PARAMETER_KEY_URL: url}, directory=directory)
elif mode == MODE_USERS_VIDEOS:
    xbmc.executebuiltin("XBMC.ActivateWindow(VideoLibrary,%s,return)" % PLUGIN_URL)
    videos = myplex_client.get_videos(permalink)
    ok = show_videos(parameters={PARAMETER_KEY_MODE: mode, PARAMETER_KEY_URL: url}, videos=videos)
elif mode == MODE_USERS_SECTIONS:
    server = str(url).partition('servers/')[2]
    sections = myplex_client.get_sections(server)
    ok = show_sections(parameters={PARAMETER_KEY_MODE: mode, PARAMETER_KEY_URL: url}, sections=sections)
elif mode == MODE_USERS_SERVERS:
    servers = myplex_client.get_servers()
    ok = show_servers(parameters={PARAMETER_KEY_MODE: mode, PARAMETER_KEY_URL: url}, servers=servers)
elif mode == MODE_PLAYLISTS:
    playlist = myplex_client.getPlayLists()
    ok = showDirectory(parameters={PARAMETER_KEY_MODE: mode, PARAMETER_KEY_URL: url}, directory=playlist)
elif mode == MODE_VIDEO_PLAY:
    play_video(permalink)
    