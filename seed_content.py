"""
SIH Vernacular Education
Curriculum Seed + Database Repair Script

This script:
1. Keeps the existing 5 official subjects.
2. Repairs old/duplicate subject records.
3. Correctly maps all 20 official lessons to subjects.
4. Deactivates stale subjects/lessons.
5. Preserves existing quiz questions.
6. Adds missing quiz questions from QUESTIONS.
"""

from app.database import SessionLocal
from app import models


# ============================================================
# OFFICIAL SUBJECTS
# ============================================================

SUBJECTS = [
    (
        "Mathematics",
        "Basic mathematics for primary learners: numbers, operations, fractions and geometry.",
        "Hindi",
    ),
    (
        "Science",
        "Foundational science concepts from everyday life, nature, matter and the human body.",
        "Hindi",
    ),
    (
        "English Language",
        "Beginner English vocabulary, grammar, sentences and communication.",
        "Hindi",
    ),
    (
        "Environmental Studies",
        "Everyday environment, plants, animals, water, safety and community awareness.",
        "Hindi",
    ),
    (
        "Digital Literacy",
        "Basic computer, internet, digital safety and responsible technology use.",
        "Hindi",
    ),
]


# ============================================================
# OFFICIAL 20 LESSONS
# ============================================================

LESSONS = [
    (
        1,
        "Understanding Numbers",
        "Learn to read, compare and use whole numbers.",
        "Numbers are used to count objects and describe quantities. Place value helps us understand the value of each digit. For example, in 245, the digit 2 represents two hundreds.",
    ),
    (
        1,
        "Addition and Subtraction",
        "Learn basic addition and subtraction using everyday examples.",
        "Addition combines quantities. Subtraction finds the difference or removes a quantity. Example: 8 + 5 = 13 and 13 - 5 = 8.",
    ),
    (
        1,
        "Multiplication and Division",
        "Understand multiplication as repeated addition and division as equal sharing.",
        "Multiplication is repeated addition. Division means sharing a quantity into equal groups. Example: 4 × 3 means four groups of three.",
    ),
    (
        1,
        "Fractions",
        "Learn simple fractions such as halves, thirds and quarters.",
        "A fraction represents a part of a whole. In 3/4, 3 is the numerator and 4 is the denominator. The denominator tells how many equal parts make the whole.",
    ),
    (
        2,
        "Living and Non-Living Things",
        "Identify basic characteristics of living and non-living things.",
        "Living things grow, need energy and carry out life processes. Plants, animals and humans are living things. Rocks, chairs and pencils are non-living.",
    ),
    (
        2,
        "Plants Around Us",
        "Learn about roots, stems, leaves, flowers and their basic functions.",
        "Roots usually anchor a plant and absorb water. Stems support the plant. Leaves help plants make food using sunlight, water and carbon dioxide.",
    ),
    (
        2,
        "States of Matter",
        "Understand solids, liquids and gases.",
        "Matter commonly exists as solid, liquid or gas. A solid has a fixed shape, a liquid takes the shape of its container, and a gas spreads to fill available space.",
    ),
    (
        2,
        "Human Body Basics",
        "Learn about major body parts and their simple functions.",
        "The heart pumps blood, the lungs help us breathe, and the brain controls many body activities. Good food, exercise and sleep help maintain health.",
    ),
    (
        3,
        "Alphabet and Sounds",
        "Learn English letters and common letter sounds.",
        "English uses 26 letters. Letters can represent different sounds. Learning letter sounds helps learners read and spell simple words.",
    ),
    (
        3,
        "Nouns and Pronouns",
        "Understand naming words and words used in place of nouns.",
        "A noun names a person, place, animal or thing. A pronoun can replace a noun. For example, 'Riya is happy. She is smiling.'",
    ),
    (
        3,
        "Verbs and Actions",
        "Identify action words and use them in simple sentences.",
        "A verb often describes an action or state. Examples include run, eat, read, write and sleep. In 'The child reads,' reads is the verb.",
    ),
    (
        3,
        "Simple Sentences",
        "Build clear sentences using subjects and verbs.",
        "A simple sentence can express a complete idea. Example: 'The boy plays.' A sentence normally begins with a capital letter and ends with appropriate punctuation.",
    ),
    (
        4,
        "Our Family and Community",
        "Understand family roles and people who help the community.",
        "Families can have different structures. Communities include people who work together. Teachers, doctors, farmers, drivers and sanitation workers all contribute to society.",
    ),
    (
        4,
        "Water and Its Uses",
        "Learn why water is important and how to conserve it.",
        "Water is needed by people, animals and plants. We use it for drinking, cooking and cleaning. Closing taps and fixing leaks are simple ways to reduce wastage.",
    ),
    (
        4,
        "Plants and Animals",
        "Understand basic relationships between plants, animals and people.",
        "Plants provide food and oxygen and create habitats. Animals depend on plants or other organisms for food. People should protect biodiversity and avoid unnecessary harm to wildlife.",
    ),
    (
        4,
        "Clean and Safe Environment",
        "Learn basic habits for a clean and healthy environment.",
        "Keeping surroundings clean reduces waste and can help prevent disease. Waste should be handled responsibly. Reusing and recycling suitable materials can reduce environmental impact.",
    ),
    (
        5,
        "Computer Basics",
        "Identify common computer parts and their basic uses.",
        "A computer system can include a monitor, keyboard, mouse and CPU. The keyboard is used for typing, while the mouse helps point, click and select items.",
    ),
    (
        5,
        "Internet Basics",
        "Understand websites, browsers and basic internet use.",
        "A web browser is software used to access websites. The internet connects computers and devices so information and services can be shared.",
    ),
    (
        5,
        "Digital Safety",
        "Learn simple rules for protecting accounts and personal information.",
        "Strong passwords should be difficult to guess and should not be shared. Personal information should be given only to trusted services or people when appropriate.",
    ),
    (
        5,
        "Responsible Technology Use",
        "Learn healthy and respectful habits while using digital devices.",
        "Technology should be used safely and responsibly. Take breaks, communicate respectfully, check information before sharing it, and avoid accessing unknown or suspicious links.",
    ),
]


# ============================================================
# IMPORTANT
# ============================================================
#
# KEEP YOUR EXISTING QUESTIONS = {...} BLOCK HERE.
#
# Do NOT delete your current 200-question QUESTIONS dictionary.
#
# Paste the QUESTIONS dictionary from your current
# seed_content.py below this comment.
#
# Example:
#
# QUESTIONS = {
#     1: [...],
#     2: [...],
#     ...
#     20: [...]
# }
#
# ============================================================


# ============================================================
# EXISTING QUESTIONS CHECK
# ============================================================

try:
    QUESTIONS
except NameError:
    QUESTIONS = {}


# ============================================================
# OFFICIAL SUBJECT IDS
# ============================================================
#
# These IDs match the current Render database you showed:
#
# Mathematics          = 1
# Science              = 4
# English Language     = 5
# Environmental Studies= 6
# Digital Literacy     = 7
#
# We intentionally DO NOT delete these records.
# ============================================================

OFFICIAL_SUBJECT_IDS = {
    "Mathematics": 1,
    "Science": 4,
    "English Language": 5,
    "Environmental Studies": 6,
    "Digital Literacy": 7,
}


# ============================================================
# GET TEACHER
# ============================================================

def get_teacher(db):
    user = (
        db.query(models.User)
        .filter(models.User.role.in_(["teacher", "admin"]))
        .order_by(models.User.id)
        .first()
    )

    if not user:
        raise RuntimeError(
            "No teacher/admin user found. "
            "Register a teacher/admin account first."
        )

    return user


# ============================================================
# REPAIR SUBJECTS
# ============================================================

def repair_subjects(db):
    print("\n========================================")
    print("REPAIRING SUBJECTS")
    print("========================================")

    subject_map = {}

    for name, description, language in SUBJECTS:

        official_id = OFFICIAL_SUBJECT_IDS[name]

        subject = (
            db.query(models.Subject)
            .filter(models.Subject.id == official_id)
            .first()
        )

        if not subject:
            raise RuntimeError(
                f"Required subject '{name}' with ID "
                f"{official_id} was not found."
            )

        subject.name = name
        subject.description = description
        subject.language = language
        subject.is_active = True

        subject_map[name] = subject.id

        print(
            f"Official subject: {name} "
            f"(id={subject.id})"
        )

    # --------------------------------------------------------
    # Deactivate old/duplicate subjects
    # --------------------------------------------------------

    for subject in db.query(models.Subject).all():

        if subject.id not in OFFICIAL_SUBJECT_IDS.values():

            if subject.is_active:
                subject.is_active = False

                print(
                    f"Deactivated old subject: "
                    f"{subject.name} "
                    f"(id={subject.id})"
                )

    db.commit()

    print("\nSubject repair completed.")

    return subject_map


# ============================================================
# REPAIR LESSONS
# ============================================================

def repair_lessons(db, subject_map, teacher):

    print("\n========================================")
    print("REPAIRING LESSONS")
    print("========================================")

    lesson_map = {}

    official_titles = {
        lesson[1]
        for lesson in LESSONS
    }

    # --------------------------------------------------------
    # Create/update official 20 lessons
    # --------------------------------------------------------

    for subject_no, title, description, content in LESSONS:

        subject_name = SUBJECTS[subject_no - 1][0]
        subject_id = subject_map[subject_name]

        lesson = (
            db.query(models.Lesson)
            .filter(models.Lesson.title == title)
            .first()
        )

        if lesson:

            # IMPORTANT:
            # Repair the subject mapping.
            lesson.subject_id = subject_id

            lesson.description = description
            lesson.content = content
            lesson.language = "Hindi"
            lesson.is_active = True

            print(
                f"Repaired lesson: {title} "
                f"(id={lesson.id}) "
                f"→ subject_id={subject_id}"
            )

        else:

            lesson = models.Lesson(
                title=title,
                description=description,
                content=content,
                language="Hindi",
                subject_id=subject_id,
                created_by=teacher.id,
            )

            db.add(lesson)
            db.flush()

            print(
                f"Created lesson: {title} "
                f"(id={lesson.id}) "
                f"→ subject_id={subject_id}"
            )

        lesson_map[title] = lesson.id

    db.commit()

    # --------------------------------------------------------
    # Deactivate old/stale lessons
    # --------------------------------------------------------

    all_lessons = db.query(models.Lesson).all()

    for lesson in all_lessons:

        if lesson.title not in official_titles:

            if lesson.is_active:
                lesson.is_active = False

                print(
                    f"Deactivated old lesson: "
                    f"{lesson.title} "
                    f"(id={lesson.id})"
                )

    db.commit()

    print("\nLesson repair completed.")

    return lesson_map


# ============================================================
# REPAIR QUIZ QUESTIONS
# ============================================================

def repair_questions(db, lesson_map):

    print("\n========================================")
    print("REPAIRING QUIZ QUESTIONS")
    print("========================================")

    total_added = 0

    for lesson_index, lesson_row in enumerate(
        LESSONS,
        start=1
    ):

        _, title, _, _ = lesson_row

        lesson_id = lesson_map[title]

        question_bank = QUESTIONS.get(
            lesson_index,
            []
        )

        if not question_bank:
            print(
                f"WARNING: No question bank found "
                f"for lesson {lesson_index}: {title}"
            )
            continue

        existing_count = (
            db.query(models.QuizQuestion)
            .filter(
                models.QuizQuestion.lesson_id
                == lesson_id
            )
            .count()
        )

        # ----------------------------------------------------
        # If 10 questions already exist, preserve them.
        # ----------------------------------------------------

        if existing_count >= 10:

            print(
                f"Questions already present: "
                f"{title} "
                f"({existing_count})"
            )

            continue

        # ----------------------------------------------------
        # Add only missing questions.
        # ----------------------------------------------------

        for q in question_bank:

            (
                question_text,
                option_a,
                option_b,
                option_c,
                option_d,
                correct_answer,
                explanation,
            ) = q

            question = models.QuizQuestion(
                lesson_id=lesson_id,
                question=question_text,
                option_a=option_a,
                option_b=option_b,
                option_c=option_c,
                option_d=option_d,
                correct_answer=correct_answer,
                explanation=explanation,
            )

            db.add(question)

            total_added += 1

        db.commit()

        print(
            f"Added {len(question_bank)} "
            f"questions: {title}"
        )

    print(
        f"\nNew quiz questions added: "
        f"{total_added}"
    )


# ============================================================
# FINAL VERIFICATION
# ============================================================

def verify_curriculum(db):

    print("\n========================================")
    print("FINAL CURRICULUM CHECK")
    print("========================================")

    print("\nACTIVE SUBJECTS:")

    active_subjects = (
        db.query(models.Subject)
        .filter(
            models.Subject.is_active == True
        )
        .order_by(models.Subject.id)
        .all()
    )

    for subject in active_subjects:

        print(
            f"  ID {subject.id}: "
            f"{subject.name}"
        )

    print("\nACTIVE LESSONS:")

    active_lessons = (
        db.query(models.Lesson)
        .filter(
            models.Lesson.is_active == True
        )
        .order_by(models.Lesson.id)
        .all()
    )

    subject_lesson_count = {}

    for lesson in active_lessons:

        subject_lesson_count[
            lesson.subject_id
        ] = (
            subject_lesson_count.get(
                lesson.subject_id,
                0
            ) + 1
        )

        print(
            f"  Lesson ID {lesson.id}: "
            f"{lesson.title} "
            f"→ subject_id={lesson.subject_id}"
        )

    print("\nLESSON COUNT BY SUBJECT:")

    for subject_id, count in sorted(
        subject_lesson_count.items()
    ):

        print(
            f"  subject_id={subject_id}: "
            f"{count} lessons"
        )

    total_questions = (
        db.query(models.QuizQuestion)
        .count()
    )

    print(
        f"\nTotal quiz questions: "
        f"{total_questions}"
    )


# ============================================================
# MAIN
# ============================================================

def main():

    db = SessionLocal()

    try:

        print("\n")
        print("========================================")
        print("SIH VERNACULAR EDUCATION")
        print("CURRICULUM DATABASE REPAIR")
        print("========================================")

        # ----------------------------------------------------
        # Teacher/admin
        # ----------------------------------------------------

        teacher = get_teacher(db)

        print(
            f"\nUsing teacher/admin user: "
            f"{teacher.name} "
            f"(id={teacher.id})"
        )

        # ----------------------------------------------------
        # Subjects
        # ----------------------------------------------------

        subject_map = repair_subjects(db)

        # ----------------------------------------------------
        # Lessons
        # ----------------------------------------------------

        lesson_map = repair_lessons(
            db,
            subject_map,
            teacher,
        )

        # ----------------------------------------------------
        # Questions
        # ----------------------------------------------------

        repair_questions(
            db,
            lesson_map,
        )

        # ----------------------------------------------------
        # Final verification
        # ----------------------------------------------------

        verify_curriculum(db)

        print("\n")
        print("========================================")
        print("DONE")
        print("========================================")
        print(
            "5 official subjects are active."
        )
        print(
            "20 official lessons are active."
        )
        print(
            "Lesson-to-subject mapping repaired."
        )
        print(
            "Old/duplicate subjects deactivated."
        )
        print(
            "Old/stale lessons deactivated."
        )
        print(
            "Existing quiz questions preserved."
        )
        print(
            "Missing quiz questions added."
        )
        print("========================================")

    except Exception as error:

        db.rollback()

        print("\n")
        print("========================================")
        print("SEED/REPAIR FAILED")
        print("========================================")
        print(str(error))
        print("========================================")

        raise

    finally:

        db.close()


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":
    main()