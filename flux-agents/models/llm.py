import json
from ollama import Client
from .prompts import *
from .formats import *
from string import Template
from config.settings import LLM_MODEL
from datetime import datetime
from utils.logger import logger


class ModeratorBotClient:

    def __init__(
        self,
    ):
        self.client = Client()
        self.model = LLM_MODEL or "gemma3:latest"  # include a default
        # might be better to raise an exception if no model specified;
        # then again, we have ping to make sure the model loads and runs

        logger.info("model_requested", model=self.model)

    def ping_ai(self):
        """
        See if the AI is listening. Find out how it's doing.
        """
        logger.info(
            "pinging_ai", message="Let's make sure we can reach our AI agent.")
        try:
            response = self.client.generate(model=self.model)
            time_of_response = datetime.fromisoformat(
                response['created_at']).strftime("%Y-%m-%d %H:%M:%S")
            logger.info("ai_responded", timestamp=time_of_response)
            return True
        except Exception as e:
            logger.error("ai_not_responsive", error=str(e))
            return False

    def prepare_to_classify(self):
        """
        Give instructions to AI about how to classify the language used in social media posts.

        This is meant to be called before post content is sent for evaluation. Can be called
        from time to time, especially if the AI forgets what it's supposed to be doing (e.g., 
        it gets restarted or drifts).
        """
        # NOTE: preparing the model for a batch of posts did not work as well
        # as providing instructions every time
        response = self.client.generate(
            model=self.model, prompt=rating_instructions, stream=False, format=response_format)
        parsed = json.loads(response['response'])
        logger.info("ai_prepared", reply=parsed['reply'])

    def evaluate_post(self, post):
        """
        Review the post, assign a rating and provide a (short?) reason.
        """
        # set up prompt
        content = post["content"]
        prompt = Template(assign_rating_level)
        full_prompt = prompt.substitute(content=content)

        # make the call to AI
        response = self.client.generate(
            model=self.model, prompt=full_prompt, stream=False, format=rating_format, options={"temperature": 0})

        # process response
        decision = json.loads(response['response'])
        return (decision['rating'], decision['reason'])


sample_posts = [
    {"id": 2,
     "content": "<p>Time flies. Seems like we started using AI just yesterday.</p>"},
    {"id": 3,
     "content": "<p>Sucks to be you.</p>"},
    {"id": 4,
     "content": "<p>You are an idiot.</p>"},
    {"id": 5,
     "content": "<p>What do you have against my hat? Kiss my ass!</p>"},
    {"id": 6,
     "content": "<p>Fuck you, piece of shit.</p>"},
    {"id": 7,
     "content": "<p>I will blow up the power plant if they don't shut it down.</p>"},
    {"id": 8,
     "content": "<p>This message is definitely not racist. Are you?</p>"}
]


def main():
    # os.environ['OLLAMA_HOST'] = 'http://<ip address>:11434'
    bot = ModeratorBotClient()
    made_contact = bot.ping_ai()
    if not made_contact:
        logger.error("ai_connection_failed", message="oh no!!")
        return
    logger.info("moderator_available", message="Our moderator is available.")

    # include instructions with each post
    for post in sample_posts:
        answer = bot.evaluate_post(post)
        logger.info("post_evaluated",
                    post_id=post["id"], rating=answer[0], reason=answer[1])


if __name__ == "__main__":
    main()
