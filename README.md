# MindMate – Student Mental Wellness Companion

A web-based student wellness application that brings academic planning, mood tracking, personal journaling, and supportive wellness activities together in one place.

MindMate is designed to help students organize their academic responsibilities, reflect on their emotions, and develop healthier daily routines through a simple and accessible interface.

> **Project Type:** Academic / Student Project
> **Backend:** Python and Flask
> **Frontend:** HTML, CSS, JavaScript, and Jinja templates
> **Database:** SQLite
> **Machine Learning:** Scikit-learn

---
## Live Demo

**Live Application:** https://mindmate-student-wellness.onrender.com/

**GitHub Repository:**

**Source Code:** https://github.com/shanmukh070207-source/MindMate-Student-Wellness

This project was developed as an academic software project to explore web application development, database integration, machine learning, data visualization, and student-focused wellness tools.

---

## Overview

College students often have to manage assignments, examinations, deadlines, personal responsibilities, and emotional stress simultaneously.

MindMate is a student-focused web application that combines academic organization with simple wellness tools. Rather than treating productivity and well-being as completely separate activities, the application provides a shared space where students can manage their work and reflect on how they are feeling.

The application includes a study planner, mood tracker, personal journal, supportive chatbot, guided wellness activities, and a dashboard that presents useful summaries of recorded information.

MindMate is an educational software project demonstrating the integration of web development, database management, data visualization, and machine learning.

## Problem Statement

Students may find it difficult to maintain an organized study schedule while also paying attention to their emotional well-being.

Common challenges include:

* Difficulty organizing assignments and academic deadlines.
* Lack of a consistent habit of tracking moods.
* Limited opportunities for private self-reflection.
* Difficulty identifying patterns in personal routines.
* Need for accessible, simple activities during stressful study periods.

MindMate addresses these challenges by bringing academic planning and basic wellness activities into a single web application.

## Objectives

The main objectives of MindMate are:

1. To provide students with a centralized academic task management system.
2. To encourage regular mood tracking and personal reflection.
3. To offer a supportive, response-based chatbot.
4. To provide simple guided breathing and grounding activities.
5. To present useful summaries through a personalized dashboard.
6. To demonstrate the practical use of Flask, SQLite, machine learning, and data visualization.
7. To provide a modular application that can be extended with additional features.

---

## Features

### 1. Personalized Dashboard

The dashboard brings important information together in one place.

Depending on the available records and implemented dashboard components, it can present summaries of academic tasks, mood entries, and other tracked information.

**Purpose:** Help students quickly understand their current activity without navigating through every section individually.

### 2. Study Planner

The study planner helps students organize academic responsibilities.

Its task-management functionality includes:

* Adding tasks.
* Recording task descriptions.
* Organizing tasks by subject.
* Setting due dates.
* Editing existing tasks.
* Marking tasks as completed.
* Reopening completed tasks.
* Deleting tasks.
* Filtering and sorting tasks.

**Purpose:** Make it easier to organize assignments, revision sessions, projects, and other academic activities.

### 3. Mood Tracker

The mood tracker allows students to record how they feel.

The supported mood categories are:

* Very Good
* Good
* Okay
* Stressed
* Low

Students can also add optional notes and review their mood history.

**Purpose:** Encourage emotional awareness and personal reflection over time.

### 4. Personal Journal

The journal provides a space for recording personal reflections and thoughts.

Journal functionality includes creating entries, viewing previous entries, editing existing entries, and deleting entries.

Journal records are associated with the logged-in user.

**Purpose:** Encourage regular reflection and provide a private space for organizing personal thoughts.

### 5. Supportive Chatbot

MindMate includes a machine-learning-based text classification component that helps select supportive responses to user messages.

The chatbot uses a trained text-processing pipeline and a predefined response library.

Its response process includes:

1. Receiving a user's message.
2. Processing the text.
3. Predicting a response category using the trained classifier.
4. Checking the prediction confidence.
5. Selecting a suitable predefined response.
6. Using a fallback response when the prediction is not sufficiently confident.

A separate phrase-based safety check is also included.

**Important:** The chatbot is an educational prototype. It does not diagnose medical conditions, replace professional support, or reliably detect every crisis situation.

### 6. Guided Breathing

The breathing activity provides a simple guided exercise that students can follow during a study break or a stressful moment.

**Purpose:** Encourage short pauses and mindful breathing.

### 7. Five-Senses Grounding

The grounding activity guides users through a five-senses exercise to help them focus on their immediate surroundings.

**Purpose:** Provide a simple self-guided grounding activity.

### 8. Wellness Resources

The application includes a section for wellness-related resources intended to help students explore additional information and support options.

### 9. Data Visualization

MindMate uses Pandas and Matplotlib to process recorded information and generate visual summaries.

These visualizations help make the available dashboard information easier to interpret.

### 10. User Accounts

The application includes registration and login functionality.

User-specific records are associated with the relevant account so that the application can retrieve the appropriate tasks, mood entries, and journal records.

---


## Technology Stack

| Technology   | Purpose                                    |
| ------------ | ------------------------------------------ |
| Python       | Application logic and backend programming  |
| Flask        | Web application framework                  |
| HTML5        | Page structure                             |
| CSS3         | Styling and layout                         |
| JavaScript   | Client-side interactions                   |
| Jinja        | Dynamic HTML templates                     |
| SQLite       | Local relational database                  |
| Scikit-learn | Machine learning and text classification   |
| Pandas       | Data processing and analysis               |
| Matplotlib   | Charts and visualizations                  |
| Joblib       | Saving and loading the trained ML pipeline |
| Pytest       | Automated testing, where configured        |

## Machine Learning Approach

The chatbot uses a traditional machine learning classification approach rather than a generative language model.

The training pipeline is implemented using Scikit-learn.

### Workflow

1. Prepare labelled text examples.
2. Convert the text into numerical features using TF-IDF.
3. Train a Logistic Regression classifier.
4. Evaluate the trained model using the available evaluation process.
5. Save the fitted pipeline using Joblib.
6. Load the saved pipeline when the application needs to classify a message.
7. Use the predicted category to select a predefined response.

### Main ML files

* `ml/train_model.py` — training workflow.
* `ml/predict.py` — prediction functionality.
* `ml/response_library.py` — predefined chatbot responses.
* `ml/safety.py` — phrase-based safety check.
* `ml/model/` — saved model and associated metrics, when present.
* `data/` — demonstration and training data.

The classifier is intended to demonstrate a practical machine learning workflow. Its predictions and responses are limited by the quality and coverage of the training examples.

It should not be interpreted as a clinically validated mental-health model.

---

## System Architecture

MindMate follows a modular web application architecture.

```text
                 Student / User
                       |
                       v
             HTML, CSS, JavaScript
                       |
                       v
                Flask Application
                       |
          +------------+-------------+
          |            |             |
          v            v             v
      User Routes   Task Routes   Wellness Routes
          |            |             |
          +------------+-------------+
                       |
          +------------+-------------+
          |            |             |
          v            v             v
       SQLite       ML Pipeline    Data Processing
      Database      Chatbot        Pandas/Matplotlib
          |            |             |
          +------------+-------------+
                       |
                       v
              Rendered Web Pages
```

The exact runtime flow depends on the selected route and feature.

---

## Project Structure

```text
MindMate/
│
├── app.py
├── config.py
├── charts.py
├── requirements.txt
├── requirements-dev.txt
├── .env.example
├── .gitignore
├── README.md
├── PROJECT_GUIDE.md
│
├── routes/
│   └── Application route modules
│
├── templates/
│   └── HTML and Jinja templates
│
├── static/
│   ├── css/
│   └── js/
│
├── database/
│   └── Database-related modules
│
├── instance/
│   └── Local application data
│
├── ml/
│   ├── train_model.py
│   ├── predict.py
│   ├── response_library.py
│   ├── safety.py
│   └── model/
│
├── data/
│   ├── demo_dataset.csv
│   └── generate_demo_dataset.py
│
├── tests/
│   └── Automated tests
│
└── docs/
    └── screenshots/
```

The names and contents of individual modules may differ slightly depending on the current project version.

---

## Training the Machine Learning Model

If you need to generate or retrain the chatbot classifier, activate your virtual environment and run:

```bash
python -m ml.train_model
```

The script should train the configured text classification pipeline and save the resulting model to the location expected by the application.

Check the training output and generated model files before starting the application.

Training results depend on the dataset and evaluation method used by the current implementation.

---

## Security and Privacy

MindMate includes security-related implementation measures such as password hashing, parameterized database queries, user-specific record access, and CSRF protection where configured.

The exact protections available depend on the current implementation and configuration.

For safe use:

* Never commit passwords, secret keys, or credentials.
* Do not upload a personal SQLite database to a public repository.
* Use fictional information in screenshots and demonstrations.
* Avoid entering sensitive personal or health information into a demonstration deployment.
* Use HTTPS and secure session-cookie settings in a hosted environment.
* Review database persistence and backup requirements before deploying for long-term use.

The project is an educational prototype and has not been presented as a production-grade mental-health service.

---

## Limitations

The current project has several limitations:

* The chatbot relies on a predefined response library and a traditional text classifier.
* Chatbot performance depends on the coverage and quality of the training data.
* The phrase-based safety check cannot reliably detect every emergency or crisis.
* The application does not diagnose mental-health conditions.
* SQLite persistence requires appropriate configuration when hosted on a platform with an ephemeral filesystem.
* Dashboard visualizations are limited to the data collected by the application.
* A public demonstration deployment may have resource and availability limitations.

---

## Future Enhancements

Possible improvements include:

* Persistent managed database support for deployment.
* More extensive automated testing.
* Better model evaluation using suitable test data.
* Improved accessibility and mobile responsiveness.
* Additional dashboard insights and progress summaries.
* Configurable study reminders.
* Expanded wellness resources.
* More comprehensive error handling and monitoring.
* Stronger privacy controls and production deployment safeguards.

These are potential future improvements and should not be interpreted as features already implemented.

---

## Disclaimer

MindMate is an educational project intended to support academic organization, self-reflection, and general wellness activities.

It is not a substitute for professional mental-health care, medical advice, diagnosis, or emergency assistance. Users experiencing a mental-health emergency should contact appropriate local emergency services or a qualified professional.

---

**MindMate — Organize your studies. Reflect on your day. Make time for yourself.**

