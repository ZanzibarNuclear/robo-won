import os
import json
from ollama import Client
from prompts import *
from formats import *

os.environ['OLLAMA_HOST'] = 'http://192.168.1.239:11434'

sample_posts = [
    {"id": 1,
     "content": "<p>Oh, now I remember. It was the summer of 2019. I was dreaming about Power Up magazine, and I needed an avatar. There you were, ready to go.</p>"},
    {"id": 2,
     "content": "<p>Oh my, how time flies. Seems like we set up this AI thing just yesterday.</p>"},
    {"id": 3,
     "content": "<p>Sucks to be you.</p>"},
    {"id": 4,
     "content": "<p>Kiss my ass, you piece of crap.</p>"},
    {"id": 5,
     "content": "<p>Fuck you, piece of shit.</p>"},
    {"id": 6,
     "content": "<p>You are a goddam idiot. I could punch you.</p>"},
    {"id": 7,
     "content": "<p>This message is definitely not racist. Are you?</p>"}
]


class ModeratorBotClient:

    def __init__(
        self,
    ):
        self.client = Client()
        self.model = 'qwen3:30b-a3b'

    def ping_ai(self):
        """
        See if the AI is listening. Find out how it's doing.
        """
        print("Let's make sure we can reach our AI agent.")
        try:
            response = self.client.generate(model=self.model)
            print("AI replied at:", response['created_at'])
            return True
        except Exception as e:
            print("AI is not responsive.", e)
            return False

    def prepare_to_classify(self):
        """
        Give instructions to AI about how to classify the language used in social media posts.

        This is meant to be called before post content is sent for evaluation. Can be called
        from time to time, especially if the AI forgets what it's supposed to be doing (e.g., 
        it gets restarted or drifts).
        """
        response = self.client.generate(
            model=self.model, prompt=rating_instructions, stream=False, format=response_format)
        parsed = json.loads(response['response'])
        print(parsed['reply'])

    def evaluate_post(self, post):
        """
        Review the post, assign a rating and provide a (short?) reason.
        """
        content = post["content"]
        response = self.client.generate(
            model=self.model, prompt=content, stream=False, format=rating_format)
        decision = json.loads(response['response'])
        return (decision['rating'], decision['reason'])


def main():
    bot = ModeratorBotClient()
    good = bot.ping_ai()
    if not good:
        print('oh no!!')
        return
    print('Our moderator is available.')

    bot.prepare_to_classify()

    for post in sample_posts:
        answer = bot.evaluate_post(post)
        print(f"Post {post["id"]}: rating {answer}\n")


if __name__ == "__main__":
    main()
