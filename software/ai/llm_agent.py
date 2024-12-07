# Local LLM Agent with Multiple Personalities

from transformers import pipeline

class LLM_Agent:
    def __init__(self):
        self.personalities = {
            "Delta": "I am Delta, focused and precise, guiding the ROV.",
            "Echo": "Hi, I'm Echo, your enthusiastic communicator.",
            "Kai": "Hello, I’m Kai, ensuring your safety.",
            "Nix": "Hey, I’m Nix, let’s explore the unknown!"
        }
        self.active_personality = "Delta"
        self.model = pipeline("text-generation", model="gpt2")

    def switch_personality(self, name):
        if name in self.personalities:
            self.active_personality = name
            return f"Switched to {name}'s personality."
        else:
            return f"Personality {name} not found."

    def respond(self, input_text):
        context = self.personalities[self.active_personality]
        prompt = f"{context}
User: {input_text}
{self.active_personality}:"
        response = self.model(prompt, max_length=50, num_return_sequences=1)
        return response[0]['generated_text']

# Example usage
# agent = LLM_Agent()
# print(agent.switch_personality("Kai"))
# print(agent.respond("How deep are we?"))
