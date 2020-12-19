#!/usr/bin/env python

from time import sleep

from youtubechat import YoutubeLiveChat, get_live_chat_id_for_stream_now

livechat_id = get_live_chat_id_for_stream_now("oauth_creds")
chat_obj = YoutubeLiveChat("oauth_creds", [livechat_id])


# msg in this case is a LiveChatMessage object defined in ytchat.py
def respond(msgs, chatid):
    for msg in msgs:
        print(f"NEW MESSAGE: {msg.published_at} | {msg}")
        #print(msg)
        #msg.delete()
        #chat_obj.send_message("RESPONSE!", chatid)


try:
    chat_obj.start()
    chat_obj.subscribe_chat_message(respond)
    chat_obj.join()

finally:
    chat_obj.stop()
