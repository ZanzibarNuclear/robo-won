import os
from ollama import Client

os.environ['OLLAMA_HOST'] = 'http://192.168.1.239:11434'

rating_levels = """
In order of severity, from none to extreme:

**safe** - non-offensive, no swear words, kid-safe, safe for work
**elevated** - light swearing ('hell', 'damn'), mildly offensive, edgy humor
**strong** - regular swear words, forbidden word alternatives (f-, s*, etc.), verbal attacks and insults
**naughty** - forbidden words ('fuck', 'shit', 'cunt', the n-word, other racial slurs), threats of violence, illegal information
"""

terms_of_use = """
1. No personal attacks
2. No threats of violence
3. No illegal information
4. No racist slurs
5. Nothing explicitly sexual or elicit
"""

response_format = {
    "type": "object",
    "properties": {
        "answer": {
            "type": "string"
        }
    },
    "required": [
        "answer"
    ]
}

rating_format = {
    "type": "object",
    "properties": {
        "rating": {
            "type": "string"
        },
        "reason": {
            "type": "string"
        }
    },
    "required": [
        "rating",
        "reason"
    ]
}


class ModeratorBotClient:

    def __init__(
        self,
    ):
        self.client = Client()

    def ping_ai(self):
        """
        See if the AI is listening. Find out how it's doing.
        """
        try:
            response = self.client.generate(
                model='qwen3:30b-a3b', prompt='echo. If you heard that, answer my echo.', stream=False, format=response_format)

            answer = response['response']
            print(answer)
            return answer
        except Exception as e:
            print("AI is not responsive.", e)
            return None

    def prepare_to_classify(self, ratings=rating_levels, terms=terms_of_use):
        """
        Give instructions to AI about how to classify the language used in social media posts.
        This is meant to be called before post content is sent for evaluation. Can be called
        from time to time, especially if the AI forgets what it's supposed to be doing (e.g., 
        it gets restarted or drifts).

        Args:
            classifications: The possible values to choose from and their criteria.
            termsOfUse: A summary of the terms of use that are pertinent to content that a member provides.
        """

        full_prompt = f"""You are a content moderation assistant for the Flux forum,
        where members can post their ideas to share with other members and guest users. Your job is to assign each post a rating by choosing one of the classifications that matches the post content.

        The classifications are:
        {ratings}

        This message is meant to establish the parameters for evaluation. Real posts will follow. As they come into the system, they will be sent to you for rating.

        At this point, I assume you are ready to go. If not, let me know what else you need.
        """

#        Any post that violates the terms of use should receive the worst classification. Here are the terms of use:
#        {terms}

        response = self.client.generate(
            model='qwen3:30b-a3b', prompt=full_prompt, stream=False, format=response_format)
        print(response['response'])

    def evaluate_post(self, post):
        content = post["content"]
        response = self.client.generate(
            model='qwen3:30b-a3b', prompt=content, stream=False, format=rating_format)
        return response

    def chat_w_llm(host=None):
        """
        Chat with an LLM using Ollama.

        Args:
            host (str, optional): The remote Ollama host URL (e.g., 'http://192.168.1.239:11434').
                                If None, it will use the OLLAMA_HOST environment variable or default to localhost.
        """
        # Create a client with the specified host or use environment variable
        if host:
            client = Client(host=host)
        else:
            # Will use OLLAMA_HOST environment variable if set, otherwise default to localhost
            client = Client()

        response = client.generate(
            model='qwen3:30b-a3b', prompt='Why is the sky blue?')
        print(response['response'])


def main():
    bot = ModeratorBotClient()
    good = bot.ping_ai()
    if not good:
        print('oh no!!')
        return
    print('Our moderator is available.')

    bot.prepare_to_classify()
    print('Our moderator is ready to go.')

    sample_post = {"author": {"id": 1, "handle": "the-real-zanzi", "alias": "Zanzi", "avatar": "/media/members/3cd75424-c0e0-4e80-b2da-2644c0047315/avatar.jpeg?v=1746131439384"}, "id": 18, "authorId": 1, "reactionTo": 17,
                   "content": "<p>Oh, now I remember. It was the summer of 2019. I was dreaming about Power Up magazine, and I needed an avatar. Like Zeus, my head split open, and out you popped.</p>", "reactions": 0, "boosts": 0, "views": 0, "postedAt": "2025-05-13T00:37:56.772Z", "updatedAt": "2025-05-13T00:37:56.772Z", "deletedAt": None}
    rating = bot.evaluate_post(sample_post)
    print(rating)


if __name__ == "__main__":
    main()
