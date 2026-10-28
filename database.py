import json
import sqlite3
from workflow import JobReview, ReviewStatus
from scoring import calculate_reviewed_score
from criteria import CAREER_CRITERIA


DATABASE_NAME = "job_tracker.db"

def get_connection():
    connection = sqlite3.connect(DATABASE_NAME)
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def initialize_database():
    conn = get_connection()
    cursor = conn.cursor()

    # Create jobs table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,

            company TEXT,
            role TEXT,
            location TEXT,

            original_job_description TEXT NOT NULL,

            ai_career_score REAL NOT NULL,
            reviewed_career_score REAL NOT NULL,

            status TEXT NOT NULL,

            created_at TIMESTAMP
                DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Create assessments table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS assessments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,

            job_id INTEGER NOT NULL,

            criterion TEXT NOT NULL,

            ai_score INTEGER NOT NULL,
            evidence TEXT,
            confidence REAL NOT NULL,

            FOREIGN KEY (job_id)
                REFERENCES jobs(id)
                ON DELETE CASCADE
        )
    ''')

    # Create reviews table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS human_overrides (
            id INTEGER PRIMARY KEY AUTOINCREMENT,

            job_id INTEGER NOT NULL,

            criterion TEXT NOT NULL,

            original_score INTEGER NOT NULL,
            human_score INTEGER NOT NULL,

            reason TEXT NOT NULL,

            is_active INTEGER NOT NULL
                DEFAULT 1,

            created_at TIMESTAMP
                DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (job_id)
                REFERENCES jobs(id)
                ON DELETE CASCADE
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS workflow_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,

            job_id INTEGER NOT NULL,

            event TEXT NOT NULL,
            details TEXT,

            created_at TIMESTAMP
                DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (job_id)
                REFERENCES jobs(id)
                ON DELETE CASCADE
        )
    ''')

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS missing_information (
            id INTEGER PRIMARY KEY AUTOINCREMENT,

            job_id INTEGER NOT NULL,

            item TEXT NOT NULL,

            created_at TIMESTAMP
                DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (job_id)
                REFERENCES jobs(id)
                ON DELETE CASCADE
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ai_runs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,

            job_id INTEGER,

            run_type TEXT NOT NULL,

            model_name TEXT NOT NULL,
            prompt_version TEXT NOT NULL,
            rubric_version TEXT,

            status TEXT NOT NULL,

            latency_seconds REAL,

            error_message TEXT,

            created_at TIMESTAMP
                DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (job_id)
                REFERENCES jobs(id)
                ON DELETE CASCADE
        )
    """)


def save_approved_job(review: JobReview, original_job_description: str) -> int:

    if review.status != ReviewStatus.APPROVED:
        raise PermissionError("Only approved jobs can be saved.")

    reviewed_score = calculate_reviewed_score(review)

    connection = get_connection()
    try:
        cursor = connection.cursor()

        # Start transaction
        connection.execute("BEGIN")

        # -------------------------
        # 1. Save job
        # -------------------------

        cursor.execute('''
            INSERT INTO jobs (
                company,
                role,
                location,
                original_job_description,
                ai_career_score,
                reviewed_career_score,
                status
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            review.job.company,
            review.job.role,
            review.job.location,
            original_job_description,
            review.career_score,
            reviewed_score,
            review.status.value
        ))

        job_id = cursor.lastrowid


        # -------------------------
        # 2. Save AI assessments
        # -------------------------


        for criterion_name in CAREER_CRITERIA:
            result = getattr(review.assessment, criterion_name)

            cursor.execute('''
                INSERT INTO assessments (
                    job_id,
                    criterion,
                    ai_score,
                    evidence,
                    confidence
                )
                VALUES (?, ?, ?, ?, ?)
            ''', (
                job_id,
                criterion_name,
                result.score,
                json.dumps(result.evidence, ensure_ascii=False),
                result.confidence
            ))


        # -------------------------
        # 3. Save override history
        # -------------------------
        for override in review.overrides:
            cursor.execute('''
                INSERT INTO human_overrides (
                    job_id,
                    criterion,
                    original_score,
                    human_score,
                    reason,
                    is_active
                )
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                job_id,
                override.criterion,
                override.original_score,
                override.human_score,
                override.reason,
                int(override.is_active)
            ))


        # -------------------------
        # Save Missing Information
        # -------------------------


        for item in (
            review.assessment.missing_information
        ):

            cursor.execute(
                """
                INSERT INTO missing_information (
                    job_id,
                    item
                )
                VALUES (?, ?)
                """,
                (
                    job_id,
                    item
                )
            )


        for ai_run in review.ai_runs:

            cursor.execute(
                """
                INSERT INTO ai_runs (
                    job_id,
                    run_type,
                    model_name,
                    prompt_version,
                    rubric_version,
                    status,
                    latency_seconds,
                    error_message
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        job_id,
                        ai_run.run_type,
                        ai_run.model_name,
                        ai_run.prompt_version,
                        ai_run.rubric_version,
                        ai_run.status,
                        ai_run.latency_seconds,
                        ai_run.error_message
                    )
            )


        # -------------------------
        # 4. Save workflow log
        # -------------------------

        cursor.execute('''
            INSERT INTO workflow_logs (
                job_id,
                event,
                details
            )
            VALUES (?, ?, ?)
        ''', (
            job_id,
            "Job Approved",
            f"Job approved with reviewed score: {reviewed_score}"
        ))


     # Everything succeeded
        connection.commit()
        return job_id

    except Exception as e:
        # Something failed
        connection.rollback()
        raise

    finally:
        connection.close()

def get_all_jobs():
    connection = get_connection()
    connection.row_factory = sqlite3.Row

    try:
        cursor = connection.cursor()

        cursor.execute("""
            SELECT
                id,
                company,
                role,
                location,
                ai_career_score,
                reviewed_career_score,
                status,
                created_at
            FROM jobs
            ORDER BY id DESC
        """)

        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    finally:
        connection.close()

def get_job_assessments(job_id: int):
    connection = get_connection()
    connection.row_factory = sqlite3.Row

    try:
        cursor = connection.cursor()

        cursor.execute("""
            SELECT
                criterion,
                ai_score,
                evidence,
                confidence
            FROM assessments
            WHERE job_id = ?
        """, (job_id,))

        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    finally:
        connection.close()

def get_job_overrides(job_id: int):
    connection = get_connection()
    connection.row_factory = sqlite3.Row

    try:
        cursor = connection.cursor()

        cursor.execute("""
            SELECT
                criterion,
                original_score,
                human_score,
                reason,
                is_active,
                created_at
            FROM human_overrides
            WHERE job_id = ?
            ORDER BY created_at DESC
        """, (job_id,))

        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    finally:
        connection.close()

def get_job_by_id(job_id:int):
    connection = get_connection()
    connection.row_factory = sqlite3.Row

    try:

        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT
                *
            FROM jobs
            WHERE id = ?
            """,
            (job_id,)
        )

        row = cursor.fetchone()

        if row is None:
            return None

        return dict(row)
    finally:
        connection.close()

def get_job_missing_information(job_id: int):

    connection = get_connection()
    connection.row_factory = sqlite3.Row

    try:

        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT
                item
            FROM missing_information
            WHERE job_id = ?
            ORDER BY id
            """,
            (job_id,)
        )

        rows = cursor.fetchall()

        return [
            row["item"]
            for row in rows
        ]

    finally:

        connection.close()

def get_effective_assessment_scores(job_id: int):

    assessments = get_job_assessments(job_id)

    overrides = get_job_overrides(job_id)

    scores = {
        item["criterion"]:
            item["ai_score"]
            for item in assessments
    }

    for override in overrides:

        if override["is_active"]:
            scores[override["criterion"]] = override["human_score"]

    return scores


def get_job_ai_runs(job_id:int):

    connection = get_connection()
    connection.row_factory = sqlite3.Row

    try:

        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT
                run_type,
                model_name,
                prompt_version,
                rubric_version,
                status,
                latency_seconds,
                error_message,
                created_at
            FROM ai_runs
            WHERE job_id = ?
            ORDER BY id
            """,
            (job_id,)
        )

        rows = cursor.fetchall()

        return [
            dict(row)
            for row in rows
        ]

    finally:
        connection.close()

def get_override_statistics():

    connection = get_connection()
    connection.row_factory = sqlite3.Row

    try:

        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT
                criterion,
                COUNT (*) AS override_count
            FROM human_overrides
            GROUP BY criterion
            ORDER BY override_count DESC
            """
        )

        rows = cursor.fetchall()

        return [
            dict(row)
            for row in rows
        ]

    finally:

        connection.close()

def get_override_direction_statistics():

    connection = get_connection()
    connection.row_factory = sqlite3.Row

    try:

        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT
                criterion,
                SUM(
                    CASE
                        WHEN human_score < original_score
                        THEN 1
                        ELSE 0
                    END
                ) AS lowered,

                SUM(
                    CASE
                        WHEN human_score > original_score
                        THEN 1
                        ELSE 0
                    END
                ) AS raised

                FROM human_overrides
                GROUP BY criterion
                ORDER BY criterion
            """
        )

        rows = cursor.fetchall()

        return [
            dict(row)
            for row in rows
        ]
    finally:
        connection.close()


def get_evaluation_summary():

    connection = get_connection()
    connection.row_factory = sqlite3.Row

    try:

        cursor = connection.cursor()

        total_jobs = cursor.execute(
            """
            SELECT COUNT (*)
            FROM jobs
            """
        ).fetchone()[0]


        total_assessments = cursor.execute(
            """
            SELECT COUNT (*)
            FROM assessments
            """
        ).fetchone()[0]

        total_overrides = cursor.execute(
            """
            SELECT COUNT (*)
            FROM human_overrides
            """
        ).fetchone()[0]

        return {
            "total_jobs":
                total_jobs,

            "total_assessments":
                total_assessments,

            "total_override_events":
                total_overrides
        }
    finally:

        connection.close()

def get_active_override_count():

    connection = get_connection()

    try:

        cursor = connection.cursor()

        result = cursor.execute(
            """
            SELECT COUNT(*)
            FROM human_overrides
            WHERE is_active = 1
            """
        ).fetchone()

        return result[0]

    finally:
        connection.close()