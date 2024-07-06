import pandas as pd

data = [
    {"text": "Generate an image of a sunset over the mountains.", "label": "generate image"},
    {"text": "Can you create a picture of a futuristic city?", "label": "generate image"},
    {"text": "Please make an image of a serene beach.", "label": "generate image"},
    {"text": "I would like to see an image of a bustling marketplace.", "label": "generate image"},
    {"text": "Create an image of a forest in autumn.", "label": "generate image"},
    {"text": "Generate an image of a majestic castle.", "label": "generate image"},
    {"text": "Can you draw a picture of a dragon?", "label": "generate image"},
    {"text": "Make an image of a space station orbiting a planet.", "label": "generate image"},
    {"text": "Please generate a picture of a snowy village.", "label": "generate image"},
    {"text": "Create an image of an underwater coral reef.", "label": "generate image"},
    {"text": "Let's chat about your favorite movies.", "label": "chat"},
    {"text": "Can we have a conversation about travel destinations?", "label": "chat"},
    {"text": "I want to talk about recent technological advancements.", "label": "chat"},
    {"text": "Let's discuss the best practices for healthy living.", "label": "chat"},
    {"text": "Can we chat about the latest trends in fashion?", "label": "chat"},
    {"text": "I'd like to have a discussion about space exploration.", "label": "chat"},
    {"text": "Let's talk about strategies for personal development.", "label": "chat"},
    {"text": "Can we have a conversation about cooking and recipes?", "label": "chat"},
    {"text": "I want to discuss the current events in politics.", "label": "chat"},
    {"text": "Let's chat about the latest sports news.", "label": "chat"},
]

df = pd.DataFrame(data)
df.to_csv('intents.csv', index=False)