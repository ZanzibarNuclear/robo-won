import os
import json
import logging
from typing import Dict, List, Optional, Tuple, Union
from enum import Enum

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("forum_moderator")


class ViolationSeverity(Enum):
    NONE = 0
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


class LLMProvider(Enum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    LOCAL = "local"


class ModeratedPost:
    def __init__(
        self,
        post_id: str,
        content: str,
        has_violation: bool,
        severity: ViolationSeverity,
        violation_details: Optional[str] = None,
        violated_rules: Optional[List[str]] = None
    ):
        self.post_id = post_id
        self.content = content
        self.has_violation = has_violation
        self.severity = severity
        self.violation_details = violation_details
        self.violated_rules = violated_rules or []

    def to_dict(self) -> Dict:
        return {
            "post_id": self.post_id,
            "content": self.content,
            "has_violation": self.has_violation,
            "severity": self.severity.name,
            "violation_details": self.violation_details,
            "violated_rules": self.violated_rules
        }


class ForumModerator:
    def __init__(
        self,
        provider: LLMProvider = LLMProvider.OPENAI,
        terms_of_service_file: str = "terms_of_service.txt"
    ):
        self.provider = provider
        self.client = self._setup_client()
        self.terms_of_service = self._load_terms_of_service(
            terms_of_service_file)
        self.system_prompt = self._build_system_prompt()

    def _load_terms_of_service(self, file_path: str) -> str:
        """Load terms of service from a file."""
        try:
            with open(file_path, 'r') as f:
                return f.read()
        except FileNotFoundError:
            logger.warning(f"Terms of service file not found: {file_path}")
            return "No specific terms provided."

    def _build_system_prompt(self) -> str:
        """Build the system prompt using the terms of service."""
        return f"""You are a content moderation assistant for a forum.
Your task is to analyze posts and determine if they violate the forum's terms of service.

FORUM TERMS OF SERVICE:
{self.terms_of_service}

For each post, analyze the content and determine:
1. Whether it violates any terms
2. The severity of the violation (NONE, LOW, MEDIUM, HIGH, CRITICAL)
3. Specific violated rules, if any
4. Brief explanation of the violation

Respond with a JSON object containing these fields:
- has_violation: boolean
- severity: "NONE", "LOW", "MEDIUM", "HIGH", or "CRITICAL"
- violated_rules: array of strings (empty if no violation)
- violation_details: string explanation (null if no violation)

Example response for a violation:
{{
  "has_violation": true,
  "severity": "MEDIUM",
  "violated_rules": ["hate_speech", "personal_attack"],
  "violation_details": "The post contains direct personal attacks and derogatory language targeting specific groups."
}}

Example response for no violation:
{{
  "has_violation": false,
  "severity": "NONE",
  "violated_rules": [],
  "violation_details": null
}}
"""

    def _setup_client(self):
        """Set up the appropriate LLM client based on provider."""
        if self.provider == LLMProvider.OPENAI:
            try:
                from openai import OpenAI
                return OpenAI()
            except ImportError:
                logger.error(
                    "OpenAI package not installed. Run: pip install openai")
                raise
        elif self.provider == LLMProvider.ANTHROPIC:
            try:
                from anthropic import Anthropic
                return Anthropic()
            except ImportError:
                logger.error(
                    "Anthropic package not installed. Run: pip install anthropic")
                raise
        elif self.provider == LLMProvider.LOCAL:
            try:
                # For local models, options include:
                # - Ollama: https://github.com/ollama/ollama
                # - LM Studio: https://lmstudio.ai/
                # This example uses LiteLLM which can route to many backends
                from litellm import completion
                return None  # No specific client needed for litellm
            except ImportError:
                logger.error(
                    "LiteLLM package not installed. Run: pip install litellm")
                raise
        else:
            raise ValueError(f"Unsupported LLM provider: {self.provider}")

    def moderate_post(self, post_id: str, content: str) -> ModeratedPost:
        """Moderate a forum post using the LLM."""
        try:
            response_text = self._get_llm_response(content)
            analysis = self._parse_llm_response(response_text)

            # Create moderated post object
            severity = ViolationSeverity[analysis.get("severity", "NONE")]
            return ModeratedPost(
                post_id=post_id,
                content=content,
                has_violation=analysis.get("has_violation", False),
                severity=severity,
                violation_details=analysis.get("violation_details"),
                violated_rules=analysis.get("violated_rules", [])
            )
        except Exception as e:
            logger.error(f"Error moderating post {post_id}: {str(e)}")
            # Return a default "error" moderation
            return ModeratedPost(
                post_id=post_id,
                content=content,
                has_violation=False,
                severity=ViolationSeverity.NONE,
                violation_details=f"Error during moderation: {str(e)}"
            )

    def _get_llm_response(self, content: str) -> str:
        """Get response from the LLM based on provider."""
        if self.provider == LLMProvider.OPENAI:
            response = self.client.chat.completions.create(
                model="gpt-4o",  # or gpt-3.5-turbo for lower cost
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": f"Post to moderate: {content}"}
                ],
                temperature=0,  # Lower temperature for more consistent results
                response_format={"type": "json_object"}
            )
            return response.choices[0].message.content

        elif self.provider == LLMProvider.ANTHROPIC:
            response = self.client.messages.create(
                model="claude-3-opus-20240229",  # or claude-3-sonnet/haiku for cost/speed balance
                max_tokens=1000,
                temperature=0,
                system=self.system_prompt,
                messages=[
                    {"role": "user", "content": f"Post to moderate: {content}"}
                ]
            )
            return response.content[0].text

        elif self.provider == LLMProvider.LOCAL:
            # Using LiteLLM to interact with a local model (requires litellm)
            from litellm import completion

            # Configure for your local model setup
            # Examples:
            # - For Ollama: "ollama/llama3"
            # - For local server: "http://localhost:8000"
            # - For LM Studio: "lmstudio/model_name"
            MODEL = "ollama/mistral"  # Change to your local model

            response = completion(
                model=MODEL,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": f"Post to moderate: {content}"}
                ],
                temperature=0
            )
            return response.choices[0].message.content

    def _parse_llm_response(self, response_text: str) -> Dict:
        """Parse the LLM response into a structured format."""
        try:
            # Try to parse as JSON
            return json.loads(response_text)
        except json.JSONDecodeError:
            # If not valid JSON, try to extract JSON from text
            import re
            json_match = re.search(
                r'```json\n(.*?)\n```', response_text, re.DOTALL)
            if json_match:
                try:
                    return json.loads(json_match.group(1))
                except json.JSONDecodeError:
                    pass

            # Fallback to default response
            logger.warning(
                f"Failed to parse LLM response as JSON: {response_text[:100]}...")
            return {
                "has_violation": False,
                "severity": "NONE",
                "violated_rules": [],
                "violation_details": "Failed to parse LLM response"
            }


class ForumModeratorBot:
    def __init__(
        self,
        moderator: ForumModerator,
        high_water_mark_file: str = "high_water_mark.txt"
    ):
        self.moderator = moderator
        self.high_water_mark_file = high_water_mark_file
        self.high_water_mark = self._load_high_water_mark()

    def _load_high_water_mark(self) -> str:
        """Load the high water mark from file."""
        try:
            with open(self.high_water_mark_file, 'r') as f:
                return f.read().strip()
        except FileNotFoundError:
            logger.info(
                "No high water mark file found. Starting from beginning.")
            return ""

    def _save_high_water_mark(self, mark: str):
        """Save the high water mark to file."""
        with open(self.high_water_mark_file, 'w') as f:
            f.write(mark)

    def process_posts(self, posts: List[Dict]) -> List[ModeratedPost]:
        """Process a batch of posts."""
        results = []
        latest_id = self.high_water_mark

        for post in posts:
            # Skip posts we've already processed
            if post["id"] <= self.high_water_mark:
                continue

            # Moderate the post
            result = self.moderator.moderate_post(post["id"], post["content"])
            results.append(result)

            # Track the latest post ID
            if post["id"] > latest_id:
                latest_id = post["id"]

        # Update high water mark
        if latest_id != self.high_water_mark:
            self.high_water_mark = latest_id
            self._save_high_water_mark(latest_id)

        return results

    def handle_moderation_results(self, results: List[ModeratedPost]):
        """Handle moderation results (can be customized)."""
        for result in results:
            if result.has_violation:
                if result.severity in [ViolationSeverity.HIGH, ViolationSeverity.CRITICAL]:
                    logger.warning(
                        f"SEVERE VIOLATION in post {result.post_id}: {result.violation_details}")
                    # Here you could implement automatic hiding/removal for severe violations
                elif result.severity == ViolationSeverity.MEDIUM:
                    logger.info(
                        f"MEDIUM VIOLATION in post {result.post_id}: {result.violation_details}")
                    # Queue for human review
                else:
                    logger.info(
                        f"MINOR VIOLATION in post {result.post_id}: {result.violation_details}")
                    # Log but maybe allow with warning
            else:
                logger.debug(f"Post {result.post_id} passed moderation")


# Example usage
if __name__ == "__main__":
    # Sample Terms of Service (should be loaded from a file in practice)
    sample_tos = """
    Forum Rules:
    1. No hate speech or discrimination based on race, gender, religion, etc.
    2. No personal attacks or harassment of other users
    3. No spam or commercial solicitations
    4. No sharing of private information without consent
    5. No explicit sexual content or pornography
    6. No violent threats or incitement
    7. No illegal content or discussion of illegal activities
    8. Respectful language and constructive discussion required
    """

    # Write sample ToS to file for demo
    with open("terms_of_service.txt", "w") as f:
        f.write(sample_tos)

    # Initialize the moderator
    moderator = ForumModerator(
        provider=LLMProvider.OPENAI,  # Change to your preferred provider
        terms_of_service_file="terms_of_service.txt"
    )

    # Initialize the bot
    bot = ForumModeratorBot(moderator)

    # Sample posts to moderate
    sample_posts = [
        {"id": "001", "content": "I really enjoyed the new features in the latest update!"},
        {"id": "002", "content": "You're all idiots for using this garbage software. The developer is a complete moron."},
        {"id": "003", "content": "Does anyone know how to configure the notification settings?"},
        {"id": "004", "content": "CHECK OUT HOT SINGLES IN YOUR AREA: www.scamsite123.com"},
        {"id": "005", "content": "I'm going to find where you live and teach you a lesson for disagreeing with me."}
    ]

    # Process the posts
    results = bot.process_posts(sample_posts)

    # Handle the results
    bot.handle_moderation_results(results)

    # Print detailed results
    print("\nDetailed Moderation Results:")
    for result in results:
        print(f"\nPost ID: {result.post_id}")
        print(f"Content: {result.content}")
        print(f"Violates rules: {result.has_violation}")
        print(f"Severity: {result.severity.name}")
        if result.has_violation:
            print(f"Violated rules: {', '.join(result.violated_rules)}")
            print(f"Details: {result.violation_details}")
        print("-" * 50)
