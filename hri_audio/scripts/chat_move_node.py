#!/usr/bin/env python3
import re
import os
import openai
import sys
import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from rclpy.duration import Duration
from hri_interfaces.action import JointsPlay

from std_srvs.srv import SetBool
# bool data # e.g. for hardware enabling / disabling
# ---
# bool success   # indicate successful run of triggered service
# string message # informational, e.g. for error messages

from hri_interfaces.srv import TextToSpeech
# string text
# ---
# bool success
# string debug

api_key = os.environ["OPENAI_API_KEY"]

openai.api_key = api_key

class ChatMoveNode2(Node):

    def __init__(self):
        super().__init__('chat_move_node')

        self.playing_move = False

        self.gstt_client = self.create_client(SetBool, 'gstt_service')
        while not self.gstt_client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('gstt_service not available, waiting again...')
        self.gstt_req = SetBool.Request()

        self.gtts_client = self.create_client(TextToSpeech, 'gtts_service')
        while not self.gtts_client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('gtts_service not available, waiting again...')
        self.gtts_req = TextToSpeech.Request()

        self._action_client = ActionClient(self, JointsPlay, 'joints_play')
        self.get_logger().info('chat_move_node initialized')


    def send_gstt_req(self, cmd):
        self.gstt_req.data = cmd
        self.future = self.gstt_client.call_async(self.gstt_req)
        rclpy.spin_until_future_complete(self, self.future)
        return self.future.result()

    def send_gtts_req(self, text):
        self.gtts_req.text = text
        self.future = self.gtts_client.call_async(self.gtts_req)
        rclpy.spin_until_future_complete(self, self.future)
        return self.future.result()

    def get_response(self, messages:list):
        response = openai.ChatCompletion.create(
            model = "gpt-3.5-turbo",
            messages=messages,
            temperature = 1.0 # 0.0 - 2.0
        )
        return response.choices[0].message

    def send_goal(self, path):
        goal_msg = JointsPlay.Goal()
        goal_msg.path = path

        self._action_client.wait_for_server()

        self.get_logger().info('action server available')
        self._send_goal_future = self._action_client.send_goal_async(goal_msg)
        self.get_logger().info('goal sent')
        return self._send_goal_future
        #self._send_goal_future.add_done_callback(self.goal_response_callback)
        #self.get_logger().info('response callback added')

    def goal_response_callback(self, future):
        goal_handle = future.result()

        if not goal_handle.accepted:
            self.get_logger().info('Goal rejected :(')
            return

        self.get_logger().info('Goal accepted :)')
        self.playing_move=True
        self._get_result_future = goal_handle.get_result_async()
        self._get_result_future.add_done_callback(self.get_result_callback)
        return self._get_result_future

    def get_result_callback(self, future):
        result = future.result().result

        if(result.success):
            self.playing_move=False

def main(args=None):
    rclpy.init(args=args)

    chat = ChatMoveNode2()
    start = True;
    messages = [
        {"role": "system", "content": "Sei un robot umanoide chiamato NAO e parli italiano. Ti piacciono i bambini. La tua casa è il laboratorio di robotica del DIMES all'Università della Calabria."}
    ]
    key_words = {"come"}
    key_words_actions = {"oggi": "/home/toto/Gdrive/uni/robocup/robocup_ws/src/hri/hri_moves/moves/hello.txt",
                         "come": "/home/toto/Gdrive/uni/robocup/robocup_ws/src/hri/hri_moves/moves/hello.txt",
                         "robot": "hello.txt"}
    sec_per_word=0.6;

    try:
        while True:
    
                num_words = 0
                key_words_found = []
                key_words_time = []
                playing=False
                lastActionTime=0

                chat.get_logger().info('ready to listen')
                gstt_resp = chat.send_gstt_req(start)
                #print(f"risultato service: {gstt_resp.success}")
                chat.get_logger().info('stt request complete')

                messages.append({"role": "user", "content": gstt_resp.message})
                new_message = chat.get_response(messages=messages)

                reply_text = new_message['content'];
                print("nao reply: ")
                print(reply_text)

                # using regex( findall() )
                # to extract words from string
                words = re.findall(r'\w+', reply_text)
                
                for w in words:
                    num_words += 1
                    w = w.lower()
                    if w in key_words:
                        key_words_found.append(w)
                        key_words_time.append(num_words*sec_per_word)

                #speaking
                gtts_resp = chat.send_gtts_req(reply_text)
                #print(gtts_resp.debug)
                chat.get_logger().info(' tts Request complete')

                clock = chat.get_clock()
                t_start = clock.now().seconds_nanoseconds()[0] #seconds

                for i in range(len(key_words_time)):
                    print(i)
                    t_word = key_words_time[i] + t_start # seconds
                    t_cur = clock.now().seconds_nanoseconds()[0]

                    if(t_cur < t_word):
                        # wait
                        sleep_for = t_word - t_cur
                        chat.get_logger().info(f"waiting next action for: {sleep_for}")
                        chat.get_clock().sleep_for(Duration(seconds=sleep_for))

                        # execute
                        action_path = key_words_actions[key_words_found[i]]
                        t1 = clock.now().seconds_nanoseconds()[0]

                        future_goal = chat.send_goal(action_path)
                        rclpy.spin_until_future_complete(chat, future_goal)
                       # chat.get_logger().info("future_goal ok")
                        future_result = chat.goal_response_callback(future_goal)
                        rclpy.spin_until_future_complete(chat, future_result)
                        #chat.get_logger().info("future_result ok")
                        t2 = clock.now().seconds_nanoseconds()[0]
                        chat.get_logger().info(f"Last action duration: {t2-t1}")

                    
                messages.append(new_message)
                #rclpy.spin_until_future_complete(chat, gtts_resp)

                user_input = input("Premi dopo aver sentito la risposta")

    except KeyboardInterrupt:
        print("A presto!")

    chat.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()