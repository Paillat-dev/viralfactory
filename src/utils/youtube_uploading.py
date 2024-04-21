import random
import time
from http import client

import google.oauth2.credentials
import httplib2
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload

httplib2.RETRIES = 1

MAX_RETRIES = 10

RETRIABLE_EXCEPTIONS = (
    httplib2.HttpLib2Error,
    IOError,
    client.NotConnected,
    client.IncompleteRead,
    client.ImproperConnectionState,
    client.CannotSendRequest,
    client.CannotSendHeader,
    client.ResponseNotReady,
    client.BadStatusLine,
)

RETRIABLE_STATUS_CODES = [500, 502, 503, 504]

CLIENT_SECRETS_FILE = ""

SCOPES = ["https://www.googleapis.com/auth/youtube"]
API_SERVICE_NAME = "youtube"
API_VERSION = "v3"

VALID_PRIVACY_STATUSES = ("public", "private", "unlisted")


def get_youtube(oauth_credentials: dict):
    oauth_credentials = google.oauth2.credentials.Credentials(
        token=oauth_credentials["token"],
        refresh_token=oauth_credentials["refresh_token"],
        token_uri=oauth_credentials["token_uri"],
        client_id=oauth_credentials["client_id"],
        client_secret=oauth_credentials["client_secret"],
        scopes=oauth_credentials["scopes"],
    )
    return build(API_SERVICE_NAME, API_VERSION, credentials=oauth_credentials)


def upload(oauth_credentials, options):
    youtube = get_youtube(oauth_credentials)
    tags = None
    if options.get("keywords"):
        tags = options["keywords"].split(",")

    body = dict(
        snippet=dict(
            title=options["title"],
            description=options["description"],
            tags=tags,
            categoryId=options["category"],
            defaultLanguage="en",
        ),
        status=dict(
            privacyStatus=options["privacyStatus"], selfDeclaredMadeForKids=False
        ),
    )

    # Call the API's videos.insert method to create and upload the video.
    insert_request = youtube.videos().insert(
        part=",".join(body.keys()),
        body=body,
        media_body=MediaFileUpload(options["file"], chunksize=-1, resumable=True),
    )

    videoid = resumable_upload(insert_request)
    return videoid


def resumable_upload(request):
    response = None
    error = None
    retry = 0
    while response is None:
        try:
            print("Uploading file...")
            status, response = request.next_chunk()
            if response is not None:
                if "id" in response:
                    print('Video id "%s" was successfully uploaded.' % response["id"])
                    return response["id"]
                else:
                    exit("The upload failed with an unexpected response: %s" % response)
        except HttpError as e:
            if e.resp.status in RETRIABLE_STATUS_CODES:
                error = "A retriable HTTP error %d occurred:\n%s" % (
                    e.resp.status,
                    e.content,
                )
            else:
                raise
        except RETRIABLE_EXCEPTIONS as e:
            error = "A retriable error occurred: %s" % e

        if error is not None:
            print(error)
            retry += 1
            if retry > MAX_RETRIES:
                exit("No longer attempting to retry.")

            max_sleep = 2**retry
            sleep_seconds = random.random() * max_sleep
            print("Sleeping %f seconds and then retrying..." % sleep_seconds)
            time.sleep(sleep_seconds)


def upload_thumbnail(video_id, path, oauth_credentials):
    youtube = get_youtube(oauth_credentials)
    youtube.thumbnails().set(  # type: ignore
        videoId=video_id, media_body=path
    ).execute()
