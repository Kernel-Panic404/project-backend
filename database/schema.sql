-- ============================================================
-- SCRUM-16: Database model for tutor availability and subjects
-- AUTHOR: Alexander Mosquera
-- DATE: 2026-07-01
-- NOTE: These tables ALREADY EXIST in Django.
--       This file is for DOCUMENTATION purposes only.
-- ============================================================

-- ============================================================
-- EXISTING TABLE: disponibilidad_tutor
-- MODEL: TutorAvailability (tutorias/models.py)
-- ============================================================
-- Fields:
-- - id (PK)
-- - tutor_id (FK -> usuarios)
-- - day_of_week (INTEGER, 1-7)
-- - start_time (TIME)
-- - end_time (TIME)
-- - max_capacity (INTEGER, DEFAULT 5)
-- - available_slots (INTEGER, DEFAULT 5)
-- - is_active (BOOLEAN, DEFAULT TRUE)
-- - created_at (TIMESTAMP)
-- - updated_at (TIMESTAMP)
-- ============================================================

-- ============================================================
-- EXISTING TABLE: tutor_materia
-- MODEL: TutorSubject (tutorias/models.py)
-- ============================================================
-- Fields:
-- - id (PK)
-- - tutor_id (FK -> usuarios)
-- - subject_id (FK -> materias)
-- - experience_level (VARCHAR)
-- - is_active (BOOLEAN, DEFAULT TRUE)
-- - created_at (TIMESTAMP)
-- ============================================================

-- ============================================================
-- REFERENCE VIEW (for quick queries)
-- ============================================================
CREATE OR REPLACE VIEW vw_complete_availability AS
SELECT 
    ta.id,
    ta.tutor_id,
    u.nombre as tutor_first_name,
    u.apellido as tutor_last_name,
    ta.day_of_week,
    ta.start_time,
    ta.end_time,
    ta.max_capacity,
    ta.available_slots,
    ta.is_active,
    ts.subject_id,
    m.nombre as subject_name
FROM disponibilidad_tutor ta
JOIN usuarios u ON ta.tutor_id = u.id
JOIN tutor_materia ts ON ta.tutor_id = ts.tutor_id
JOIN materias m ON ts.subject_id = m.id
WHERE ta.is_active = TRUE AND ts.is_active = TRUE;