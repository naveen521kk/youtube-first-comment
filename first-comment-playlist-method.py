import os
import googleapiclient.discovery
import google_auth_oauthlib.flow
import googleapiclient.errors
import time
from datetime import datetime
from pytz import timezone


def current_time():
    return datetime.now(timezone('EST'))


def get_latest_video_playlist(youtube, playlist_id):
    # get first 50 videos and sort by published datetime.
    # the google format for datetime is: 2019-12-14T20:59:57.000Z
    request = youtube.playlistItems().list(
        part="snippet",
        playlistId=playlist_id,
        maxResults=50
    )
    response = request.execute()
    list_videos = response['items']
    list_videos_sorted = sorted(list_videos, key=lambda video: datetime.strptime(video['snippet']['publishedAt'],
                                                                                 '%Y-%m-%dT%H:%M:%S.%fZ'),
                                reverse=True)
    return list_videos_sorted[0]


def get_latest_video_search(youtube, channel_id):
    request = youtube.search().list(
        part="snippet",
        channelId=channel_id,
        maxResults=50,
        order="date",
        type="video"
    )
    response = request.execute()
    list_videos = response['items']
    return list_videos[0]


def insert_top_level_comment(youtube, video_id, comment_text):
    request = youtube.commentThreads().insert(
        part="snippet",
        body={
            "snippet": {
                "videoId": video_id,
                "topLevelComment": {
                    "snippet": {
                        "textOriginal": comment_text
                    }
                }
            }
        }
    )
    return request.execute()


def main():
    # Disable OAuthlib's HTTPS verification when running locally.
    # *DO NOT* leave this option enabled in production.
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

    api_service_name = "youtube"
    api_version = "v3"
    client_secrets_file = "client_secret_22372764053-9deei2ifedbr6fpqk355b3jplp66kute.apps.googleusercontent.com.json"

    scopes = ['https://www.googleapis.com/auth/youtube.force-ssl']

    # Get credentials and create an API client
    flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(client_secrets_file, scopes)
    credentials = flow.run_console()
    youtube = googleapiclient.discovery.build(api_service_name, api_version, credentials=credentials)

    # Beast's youtube uploads playlist
    beast_channel = "UCX6OQ3DkcsbYNE6H8uQQuVA"
    beast_uploads = "UUX6OQ3DkcsbYNE6H8uQQuVA"
    mtang_work_test_channel = "UCVRGPeJfJPFG7ss33iTFDmQ"
    mtang_work_test_uploads = "UUVRGPeJfJPFG7ss33iTFDmQ"

    ############################### SEARCH METHOD ###############################
    starting_latest_video = get_latest_video_search(youtube, mtang_work_test_channel)

    # starting video
    starting_video_id = starting_latest_video['id']['videoId']
    latest_video_id = starting_latest_video['id']['videoId']
    latest_video_title = starting_latest_video['snippet']['title']
    print(current_time(), latest_video_id, latest_video_title)

    while (latest_video_id == starting_video_id):
        # how long to wait for. default = 1 second
        # TODO: test 0.2 seconds for rate limiting
        time.sleep(2)

        response = get_latest_video_search(youtube, mtang_work_test_channel)
        latest_video_id = response['id']['videoId']
        latest_video_title = response['snippet']['title']

        print(current_time(), latest_video_id, latest_video_title)

    # as soon as the latest video is not equal to the starting video (aka, new upload)
    # insert a new top-level comment into the new video
    comment_text = "Honestly I doubt this comment will be one out of the ten newest comments. But if it is, that would be a miracle"
    response = insert_top_level_comment(youtube, latest_video_id, comment_text)
    print(response)


if __name__ == "__main__":
    main()
