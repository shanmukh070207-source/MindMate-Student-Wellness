"""Build the small DEMONSTRATION dataset (data/demo_dataset.csv).

IMPORTANT: this is synthetic demonstration data written for this project. It was
created by combining hand-written sentence cores with short openers and closers.
It is NOT real student data and NOT clinically meaningful. Results measured on it
only show that the pipeline works. For a real project, replace it with a properly
sourced, licensed dataset in the same format (see data/README.md).

The 'group' column marks which hand-written core sentence a row came from, so
the training script can keep all variations of one sentence on the same side of
the train/test split (this prevents data leakage).
"""
import csv
import os
import random

CORES = {
    "Academic Stress": [
        "I have too much academic work",
        "my coursework is overwhelming me",
        "the syllabus is huge and I feel under so much pressure",
        "my professors keep piling on more assignments",
        "I am stressed about my grades dropping this semester",
        "college studies are getting too heavy for me",
        "I feel like I can't keep up with the academic load",
        "the pressure to score well is getting to me",
        "all my subjects are difficult this semester and I'm drowning in work",
        "I am under constant pressure to perform in my courses",
        "my lab reports, projects and classes are exhausting me",
        "the workload in my engineering course is too much",
        "I'm worried that my CGPA is falling",
        "everyone expects top marks from me and it's stressful",
        "I feel buried under so many academic responsibilities",
        "studying for so many subjects at once is draining me",
    ],
    "Exam Anxiety": [
        "I am worried about my upcoming exams",
        "I get very nervous before every exam",
        "my mind goes blank when I sit down for the test",
        "I'm scared I will fail the final exams",
        "I feel panicky thinking about the semester exams next week",
        "exam fear is keeping me awake at night",
        "my hands shake when I enter the exam hall",
        "I'm afraid I won't remember anything during the paper",
        "the thought of the viva makes me anxious",
        "I keep worrying that I'll do badly in the test",
        "I feel sick with nerves before my internal exams",
        "I can't stop thinking about how the exam might go wrong",
        "my heart races whenever I think about the exam results",
        "I am so anxious about the upcoming midterms",
        "exams are close and I'm terrified of failing",
        "I freeze during tests even when I have studied",
    ],
    "Time Management": [
        "I cannot manage all my assignments",
        "I don't know how to organize my study schedule",
        "I always leave things until the last minute",
        "I have too many deadlines and no plan",
        "I keep missing submission dates",
        "I struggle to balance classes, projects and free time",
        "I don't know where to start with all these tasks",
        "my time table is a mess and I'm always running late",
        "I waste hours and then I have no time left to study",
        "I need help planning my week",
        "I can't prioritize what to study first",
        "I never finish my to-do list on time",
        "deadlines are piling up and I can't schedule my work",
        "I don't have a routine and my days feel unorganized",
        "I'm bad at planning and always behind on submissions",
        "how do I fit everything into my day",
    ],
    "Low Motivation": [
        "I have lost motivation to study",
        "I just don't feel like doing anything for college",
        "I have no energy or interest in my studies anymore",
        "I keep procrastinating because I don't care about my subjects",
        "I can't push myself to open my books",
        "I feel lazy and unmotivated all the time",
        "studying feels pointless to me lately",
        "I don't see the point in trying so hard in class",
        "I have zero drive to complete my assignments",
        "I keep putting off studying and I feel stuck",
        "I'm not interested in my course any more",
        "I can't find the will to start working",
        "I feel bored and unmotivated with everything related to college",
        "getting out of bed to attend class feels impossible",
        "I used to be driven but now I can't be bothered",
        "my enthusiasm for studying has completely gone",
    ],
    "Concentration Difficulties": [
        "I am finding it difficult to focus on studying",
        "I can't concentrate on my books for more than a few minutes",
        "my mind keeps wandering when I try to study",
        "I get distracted by my phone all the time while studying",
        "I read the same page again and again without understanding",
        "I find it hard to pay attention in lectures",
        "I can't stay focused during study sessions",
        "my attention drifts away every time I sit down to revise",
        "I zone out in class and miss what the teacher says",
        "I have trouble concentrating on one topic",
        "social media keeps breaking my focus when I study",
        "I sit with my notes but my thoughts are elsewhere",
        "it's hard to keep my concentration while reading",
        "I get easily distracted and can't finish a chapter",
        "I can't focus even when I really want to learn",
        "my brain feels foggy and I can't hold my attention",
    ],
    "General Emotional Stress": [
        "I feel overwhelmed and stressed all the time",
        "I have been feeling really low and anxious lately",
        "I feel so lonely in my hostel",
        "everything feels like too much right now",
        "I'm stressed and I don't even know why",
        "I've been crying a lot and feel emotionally drained",
        "I feel like I have no one to talk to",
        "I am homesick and it's making me sad",
        "I feel tense and on edge most days",
        "my emotions feel out of control and I'm exhausted",
        "I feel sad and stressed about my life in general",
        "I'm struggling with my feelings and feel really down",
        "I can't sleep because my mind is full of worries",
        "I'm having a hard time with my friends and it's upsetting me",
        "I feel anxious and heavy inside without a clear reason",
        "I feel emotionally worn out and need to talk",
    ],
    "General or Unclassified Concern": [
        "hello",
        "I just wanted to talk to someone",
        "what can you do",
        "how does this app work",
        "my roommate is very noisy today",
        "I had a long day",
        "I am not sure how to explain it",
        "can you tell me about this app",
        "the weather is nice today",
        "I'm hungry and thinking about lunch",
        "I went to the library this morning",
        "I don't know what to say",
        "what is the college canteen timing",
        "just checking this out",
        "thanks for being here",
        "I have a question about something else",
    ],
}

# Extra sentence frames with slots, so the vocabulary varies more than the cores
# alone. Each frame is its own group in the train/test split.
SUBJECTS = ["maths", "physics", "my programming course", "data structures", "chemistry",
            "my engineering subjects", "the semester", "my final year", "electronics", "my project work"]

FRAMES = {
    "Academic Stress": [
        "the workload in {s} is too heavy and I feel pressured",
        "I'm stressed about my marks in {s}",
        "there is so much coursework for {s} that I feel overloaded",
        "I feel academic pressure from {s} every single day",
        "my grades in {s} are a big source of stress",
        "the assignments and syllabus for {s} are overwhelming",
    ],
    "Exam Anxiety": [
        "I'm nervous about the {s} exam",
        "I'm scared I will fail the {s} test",
        "the {s} paper is next week and I'm panicking",
        "I get exam fear whenever I think about {s}",
        "I'm afraid my mind will go blank in the {s} exam",
        "I feel anxious about the {s} viva",
    ],
    "Time Management": [
        "I can't plan my time for {s}",
        "I never schedule my {s} work properly and miss deadlines",
        "I don't know how to organize my study timetable for {s}",
        "I'm always late submitting {s} assignments because I manage my time badly",
        "I need a plan to balance {s} with everything else",
        "I keep running out of time to finish {s} tasks",
    ],
    "Low Motivation": [
        "I have no motivation to study {s}",
        "I feel lazy and keep procrastinating on {s}",
        "I've lost interest in {s} and can't start",
        "studying {s} feels pointless and I can't be bothered",
        "I don't feel like doing anything for {s}",
        "I'm unmotivated and drifting in {s}",
    ],
    "Concentration Difficulties": [
        "I can't focus when I study {s}",
        "I get distracted while reading {s}",
        "my mind wanders in the {s} lecture",
        "I can't concentrate on {s} for more than five minutes",
        "my attention keeps slipping when I revise {s}",
        "I find it hard to stay focused on {s}",
    ],
    "General Emotional Stress": [
        "I feel sad and overwhelmed and {s} is not even the problem",
        "I'm feeling very low and lonely at college",
        "I feel anxious and upset and I don't know who to talk to",
        "I'm emotionally drained and want to cry",
        "I feel homesick and stressed out about everything",
        "I feel heavy and worried about my life, not just {s}",
    ],
}

OPENERS = ["", "", "", "Honestly, ", "Lately ", "Right now ", "Hi, ", "I think ", "Please help, ", "Today "]
CLOSERS = ["", "", "", ".", " and it's bothering me.", " these days.", ", not sure what to do.", " lately."]


def build_rows(variants_per_core=10, seed=42):
    rng = random.Random(seed)
    rows, seen = [], set()
    group_id = 0
    for label, cores in CORES.items():
        for core in cores:
            group_id += 1
            count = 0
            attempts = 0
            while count < variants_per_core and attempts < 100:
                attempts += 1
                opener = rng.choice(OPENERS)
                closer = rng.choice(CLOSERS)
                body = core
                # Openers like "Lately " read better when the sentence starts lower-case.
                if opener and not opener.startswith("I") and body[:2] != "I ":
                    body = body[0].lower() + body[1:] if body[0].isupper() and body[:2] != "I'" else body
                text = (opener + body + closer).strip()
                text = text[0].upper() + text[1:]
                if text in seen:
                    continue
                seen.add(text)
                rows.append((text, label, group_id))
                count += 1

    # Slot-based frames: one group per frame
    for label, frames in FRAMES.items():
        for frame in frames:
            group_id += 1
            subjects = rng.sample(SUBJECTS, 8)
            for subject in subjects:
                text = frame.format(s=subject)
                text = rng.choice(OPENERS) + text
                text = text.strip()
                text = text[0].upper() + text[1:]
                if text in seen:
                    continue
                seen.add(text)
                rows.append((text, label, group_id))
    return rows


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(here, "demo_dataset.csv")
    rows = build_rows()
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["text", "label", "group"])
        writer.writerows(rows)
    print(f"Wrote {len(rows)} demonstration rows to {path}")


if __name__ == "__main__":
    main()
