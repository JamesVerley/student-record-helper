-- =============================

-- teacher able to get all:
    -- the subject_periods given a particular subject
    SELECT * FROM "subject_periods" WHERE subject_id = ?;

    -- subjects they are assigned to
    
    -- subjects for a particular year level
    -- criteria for a particular subject
    -- sessions taught so far
    -- grades given a particular session
    -- students for a given yearlevel
    -- students for a given subject
    -- yearlevels for a given year
    -- other teachers firstname, lastname and email

-- teacher able to add, update and remove:
    -- subject records (deleting also deletes subject records)
    -- criteria to subject records
    -- session records (deleting will also remove all relevant grade records)
    -- grade records
    -- year level records
    -- student records

