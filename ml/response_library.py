"""Predefined supportive responses.

The classifier only chooses a category. It never writes text. Every reply below
was written by hand, and each category has several variants so replies don't
feel repetitive.
"""
import random

# One shared list of categories, used by training, prediction and responses.
CATEGORIES = [
    "Academic Stress",
    "Exam Anxiety",
    "Time Management",
    "Low Motivation",
    "Concentration Difficulties",
    "General Emotional Stress",
    "General or Unclassified Concern",
]

NEUTRAL_CATEGORY = "General or Unclassified Concern"

# Action buttons: label + Flask endpoint name (resolved with url_for)
ACTION_PLANNER = {"label": "Open the study planner", "endpoint": "planner.planner"}
ACTION_BREATHING = {"label": "Try a breathing exercise", "endpoint": "activities.activities"}
ACTION_MOOD = {"label": "Record how I feel", "endpoint": "mood.mood_tracker"}
ACTION_JOURNAL = {"label": "Write in my journal", "endpoint": "activities.journaling"}
ACTION_RESOURCES = {"label": "See wellness resources", "endpoint": "resources.resources"}

RESPONSES = {
    "Academic Stress": {
        "messages": [
            "It sounds like there is a lot of academic work on your plate right now, and that can feel heavy. "
            "Try writing everything down in one place, then pick just one small task to start with. "
            "You don't have to finish it all at once.",
            "Feeling under pressure with coursework is really common among students. "
            "One idea: split your work into 'must do this week' and 'can wait', and begin with the smallest item. "
            "Would you like to put your tasks in the study planner?",
            "That sounds like a demanding stretch. It may help to focus on the next single step rather than the whole pile. "
            "Short study blocks with a small break in between can make a big workload feel more manageable.",
            "Thank you for sharing that. When everything feels important, it can help to ask your teacher or a classmate "
            "which parts matter most. Sorting tasks by due date is a gentle way to begin.",
        ],
        "actions": [ACTION_PLANNER, ACTION_BREATHING],
    },
    "Exam Anxiety": {
        "messages": [
            "Feeling nervous before exams is something many students go through. "
            "A short breathing exercise can help you settle before or during study sessions. "
            "Planning small revision sessions across several days can also take some pressure off.",
            "It sounds like the upcoming exams are weighing on you. You could list the topics you need to cover and "
            "tackle one at a time. Rest and regular meals matter too, even in busy exam weeks.",
            "Worry about exams is understandable. Practising with past questions in short sessions can build familiarity, "
            "and taking a few slow breaths when your mind races may help you feel steadier.",
            "That sounds stressful. Try not to compare your preparation with other people's. "
            "A realistic daily revision plan, with breaks and sleep included, is a good place to start.",
        ],
        "actions": [ACTION_BREATHING, ACTION_PLANNER],
    },
    "Time Management": {
        "messages": [
            "It sounds like you have a lot to manage right now. Try listing your assignments and choosing one small "
            "task to start with. You don't need to finish everything at once. "
            "Would you like to organize your tasks in the study planner?",
            "Juggling several deadlines is hard. Putting each task into a planner with a due date can make the "
            "picture clearer. Then you only need to decide what to do today.",
            "When time feels short, it helps to estimate how long each task will really take and pick the most urgent "
            "one first. Even 25 focused minutes is a real start.",
            "Feeling behind is stressful, but it can be improved step by step. Try writing the due dates down, "
            "ordering them, and picking the first small action. The planner can help with that.",
        ],
        "actions": [ACTION_PLANNER, ACTION_MOOD],
    },
    "Low Motivation": {
        "messages": [
            "Losing motivation happens to many students, especially during long stretches of study. "
            "Try making the first step very small, like opening your notes for five minutes. "
            "Starting is often the hardest part.",
            "It sounds like it is hard to get going right now. Rewarding yourself after a small task, or studying "
            "alongside a friend, sometimes helps. Be kind to yourself about it.",
            "Thank you for being honest about that. A small goal for today, such as one page or one problem, may feel "
            "more doable than a big plan. Would you like to add it to the planner?",
            "Low energy for studying can come and go. A short walk, some water, or a quick stretch before you begin "
            "can sometimes help. If this feeling lasts a long time, talking to someone you trust is a good idea.",
        ],
        "actions": [ACTION_PLANNER, ACTION_MOOD, ACTION_JOURNAL],
    },
    "Concentration Difficulties": {
        "messages": [
            "Trouble focusing is frustrating. You could try a short timer, such as 25 minutes of study and a "
            "5 minute break, and keep your phone out of reach while it runs.",
            "It sounds like your mind keeps wandering. Studying one subject at a time in a quiet spot, with a clear "
            "goal for the session, can sometimes help. A few slow breaths before you begin may also help.",
            "Many students find it hard to focus, especially when tired or stressed. "
            "Writing down distracting thoughts on a piece of paper and returning to them later can clear some space.",
            "Thank you for sharing that. Try breaking your study into small chunks, and notice whether sleep, food "
            "or screen time may be affecting you. A grounding exercise can be a gentle reset between sessions.",
        ],
        "actions": [ACTION_BREATHING, ACTION_PLANNER],
    },
    "General Emotional Stress": {
        "messages": [
            "I'm sorry you're feeling this way. It can help to talk with a friend, a family member or a counsellor "
            "you trust. If you would like, a breathing or grounding exercise might help you feel a little calmer right now.",
            "That sounds hard, and your feelings matter. You don't have to handle everything alone. "
            "Writing your thoughts down, or reaching out to someone you trust, can be a good next step.",
            "Thank you for telling me. Feeling overwhelmed is something many people go through at times. "
            "Taking a short break, drinking some water and breathing slowly may help you settle a little.",
            "It sounds like you're carrying a lot. Be gentle with yourself today. Recording how you feel, or talking "
            "to someone you trust, can help. If things feel too heavy for too long, a professional can support you.",
        ],
        "actions": [ACTION_BREATHING, ACTION_JOURNAL, ACTION_RESOURCES],
    },
    NEUTRAL_CATEGORY: {
        "messages": [
            "Thanks for sharing. I'm not sure I understood exactly what you mean, so I don't want to guess. "
            "Could you tell me a bit more, for example whether it is about studies, exams, time, focus or how you feel?",
            "I'm here to listen. I couldn't tell clearly what this is about, so I'd rather not assume. "
            "You can describe it in different words, or try one of the activities below.",
            "Thank you for telling me. My understanding of messages is only approximate, so I may have missed "
            "something. Feel free to add more detail, or explore the tools that might help.",
        ],
        "actions": [ACTION_MOOD, ACTION_BREATHING, ACTION_RESOURCES],
    },
}

DISCLAIMER = (
    "MindMate's reading of your message is only an approximate guess made by a simple program. "
    "It is not an assessment or diagnosis."
)


def has_response(category):
    """True if the category has at least one configured response."""
    entry = RESPONSES.get(category)
    return bool(entry and entry.get("messages"))


def get_response(category, rng=random):
    """Pick a response for a category. Unknown categories get the neutral reply."""
    if not has_response(category):
        category = NEUTRAL_CATEGORY
    entry = RESPONSES[category]
    return {
        "category": category,
        "message": rng.choice(entry["messages"]),
        "actions": list(entry["actions"]),
    }
