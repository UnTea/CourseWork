-- 1 Задание --
CREATE TABLE IF NOT EXISTS Discipline(
    id              serial  NOT NULL PRIMARY KEY,
    totalHours      integer NOT NULL,
    disciplineType  text    NOT NULL,
    creditType      text    NOT NULL,
    disciplineName  text    NOT NULL
);

CREATE TABLE IF NOT EXISTS Brigade(
    id                  serial  NOT NULL PRIMARY KEY,
    yearOfAdmission     date    NOT NULL,
    brigadeSize         integer NOT NULL,
    courseCode          text    NOT NULL,
    brigadeCode         text    NOT NULL,
    dateOfAccreditation date
);

CREATE TABLE IF NOT EXISTS Classroom(
    id              serial  NOT NULL PRIMARY KEY,
    brigade         integer NOT NULL,
    status          text    NOT NULL,
    classroomNumber text    NOT NULL,
    numberOfPeople  integer    NOT NULL,

    CONSTRAINT fk_4
        FOREIGN KEY (brigade)
        REFERENCES Brigade(id)
);

CREATE TABLE IF NOT EXISTS Teacher(
    id              serial  NOT NULL PRIMARY KEY,
    pairType        text    NOT NULL,
    totalWorkHours  integer NOT NULL,
    Firstname       text    NOT NULL,
    Surname         text    NOT NULL,
    Lastname        text    NOT NULL,
    classroom       integer NOT NULL,
    discipline      integer NOT NULL,
    brigade         integer NOT NULL,

    CONSTRAINT fk_1
		FOREIGN KEY (brigade)
        REFERENCES Brigade(id),

    CONSTRAINT fk_2
		FOREIGN KEY (classroom)
        REFERENCES Classroom(id),

    CONSTRAINT fk_3
		FOREIGN KEY (discipline)
		REFERENCES Discipline(id)
);

-- 2 a --
SELECT DISTINCT Teacher.firstName, Classroom.classroomNumber,
	CASE
		WHEN status = 'Занята'
		THEN 'Аудитория свободна'
		ELSE 'Аудитория занята'
	END
FROM Teacher LEFT JOIN
	Classroom ON Teacher.classroom = Classroom.id;

-- 2 b --
DROP VIEW IF EXISTS View_Classroom;

CREATE OR REPLACE VIEW View_Classroom AS
	SELECT Classroom.id, Classroom.classroomNumber, Classroom.numberOfPeople,
	        Concat_Brigade(Brigade.brigadeSize, Brigade.brigadeCode)
	        AS brigadeName
	        FROM Classroom
	            RIGHT JOIN Brigade ON Brigade.id = ANY(SELECT classroom FROM Teacher WHERE Teacher.classroom = Classroom.id);

SELECT classroomNumber, numberOfPeople, bn from View_Classroom
                GROUP BY (id, classroomNumber, numberOfPeople, bn)
                    ORDER BY classroomNumber DESC;

-- 2 c --
-- корреллированный select  --
SELECT disciplineName, creditType, (SELECT Surname FROM Teacher tchr WHERE dscpln.id = tchr.discipline ) FROM Discipline dscpln;
-- некорреллированный select --
SELECT brigadeCode, brigadeSize, (SELECT AVG(brigadeSize) FROM Brigade ) AS avg_Size FROM Brigade;
-- корреллированный from --
SELECT * FROM (SELECT Firstname, Surname, Lastname, totalWorkHours FROM Teacher RIGHT JOIN Classroom clssrm ON classroom = clssrm.id WHERE classroom = (SELECT id FROM Classroom WHERE classroomNumber LIKE clssrm.classroomNumber)) AS tchrclssrm;
-- некорреллированный from --
SELECT yearOfAdmission, brigadeCode FROM (SELECT * FROM  Brigade) AS brgd WHERE EXTRACT(year FROM (NOW() - yearOfAdmission)) < 4;
-- корреллированный where --
SELECT disciplineType, totalHours FROM Discipline LEFT JOIN Teacher tchr ON discipline = tchr.id WHERE disciplineType = (SELECT disciplineType FROM Discipline WHERE id = tchr.discipline);
-- некорреллированный where --
SELECT * FROM Classroom WHERE id = ANY(SELECT id FROM Brigade WHERE numberOfPeople > 10);
SELECT brigadeCode, courseCode, brigadeSize FROM Brigade WHERE brigadeSize = ANY(SELECT brigadeSize FROM Brigade WHERE brigadeSize < 30);
SELECT creditType, totalHours FROM Discipline LEFT JOIN Teacher tchr ON discipline = tchr.id WHERE creditType = (SELECT creditType FROM Discipline WHERE creditType LIKE 'Зачёт');

-- 2 d --
SELECT Concat_Brigade(brigadeSize, brigadeCode)
    FROM Brigade JOIN Classroom ON Brigade.id = Classroom.brigade
            GROUP BY Brigade.id HAVING MIN(yearOfAdmission) > '2018-02-16';

-- 2 e --
SELECT * FROM Teacher
WHERE brigade =
    ANY(SELECT id FROM Brigade as brgd WHERE brigade = brgd.id);

-- 3 Задание --
CREATE INDEX IF NOT EXISTS DisciplineIndex ON Discipline(totalHours);
CREATE INDEX IF NOT EXISTS BrigadeIndex    ON Brigade(brigadeSize);
CREATE INDEX IF NOT EXISTS ClassroomIndex  ON Classroom(classroomNumber);
CREATE INDEX IF NOT EXISTS TeacherIndex    ON Teacher(totalWorkHours);

-- 4 Задание --
CREATE OR REPLACE FUNCTION Set_Hours()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    IF (TG_OP = 'DELETE') THEN
        UPDATE Discipline SET totalHours = totalHours - 48
        WHERE id = OLD.discipline;
        RETURN OLD;
    ELSIF (TG_OP = 'INSERT') THEN
        UPDATE Discipline SET totalHours = totalHours + 48
        WHERE id = NEW.discipline;
        RETURN NEW;
    ELSIF (TG_OP = 'UPDATE') AND (NEW.totalWorkHours != OLD.totalWorkHours) THEN
        UPDATE Discipline SET totalHours = totalHours + 48
        WHERE id = NEW.discipline;
        UPDATE Discipline SET totalHours = totalHours - 48
        WHERE id = OLD.discipline;
        RETURN NEW;
    END IF;
    RETURN NULL;
END;
$$;

DROP TRIGGER IF EXISTS Update_TotalWorkHours on Teacher;
CREATE TRIGGER Update_TotalWorkHours
    BEFORE INSERT OR UPDATE OR DELETE ON Teacher
    FOR EACH ROW EXECUTE PROCEDURE Set_Hours();

-- 5 Задание --
-- Brigade --
CREATE OR REPLACE PROCEDURE Add_Brigade(yearOfAdmission_ date,
                                        brigadeSize_ integer,
                                        courseCode_ text,
                                        brigadeCode_ text)
LANGUAGE sql
AS $$
	INSERT INTO Brigade(yearOfAdmission,
						brigadeSize,
						courseCode,
						brigadeCode)
	VALUES (yearOfAdmission_,
            brigadeSize_,
            courseCode_,
            brigadeCode_);
$$;

CREATE OR REPLACE PROCEDURE Change_Brigade(id_ integer,
                                yearOfAdmission_ date,
                                brigadeSize_ integer,
                                courseCode_ text,
                                brigadeCode_ text)
LANGUAGE sql
AS $$
	UPDATE Brigade
	SET (yearOfAdmission, brigadeSize, courseCode, brigadeCode) =
		(yearOfAdmission_, brigadeSize_, courseCode_, brigadeCode_)
	WHERE id = id_;
$$;

CREATE OR REPLACE PROCEDURE Delete_Brigade(id_ integer)
LANGUAGE sql
AS $$
	DELETE FROM Brigade WHERE id=id_;
$$;

-- Discipline --
CREATE OR REPLACE PROCEDURE Add_Discipline(totalHours_ integer,
                                           disciplineType_ text,
                                           creditType_ text,
                                           disciplineName_ text)
LANGUAGE sql
AS $$
	INSERT INTO Discipline(totalHours,
	                       disciplineType,
	                       creditType,
	                       disciplineName)
	VALUES (totalHours_,
	        disciplineType_,
	        creditType_,
	        disciplineName_);
$$;

CREATE OR REPLACE PROCEDURE Change_Discipline(id_ integer,
                                              totalHours_ integer,
                                              disciplineType_ text,
                                              creditType_ text,
                                              disciplineName_ text)
LANGUAGE sql
AS $$
	UPDATE Discipline
	SET (totalHours, disciplineType, creditType, disciplineName) =
		(totalHours_, disciplineType_, creditType_, disciplineName_)
	WHERE id = id_;
$$;

CREATE OR REPLACE PROCEDURE Delete_Discipline(id_ integer)
LANGUAGE sql
AS $$
	DELETE FROM Discipline WHERE id=id_;
$$;

-- Classroom --
CREATE OR REPLACE PROCEDURE Add_Classroom(brigade_ integer,
                                          status_ text,
                                          classroomNumber_ text,
                                          numberOfPeople_ integer)
LANGUAGE sql
AS $$
	INSERT INTO Classroom(brigade,
						  status,
						  classroomNumber,
						  numberOfPeople)
	VALUES (brigade_,
	        status_,
	        classroomNumber_,
	        numberOfPeople_);
$$;

CREATE OR REPLACE PROCEDURE Change_Classroom(id_ integer,
                                             brigade_ integer,
                                             status_ text,
                                             classroomNumber_ text,
                                             numberOfPeople_ integer)
LANGUAGE sql
AS $$
	UPDATE Classroom
	SET (brigade, status, classroomNumber, numberOfPeople) =
		(brigade_, status_, classroomNumber_, numberOfPeople_)
	WHERE id = id_;
$$;

CREATE OR REPLACE PROCEDURE Delete_Classroom(id_ integer)
LANGUAGE sql
AS $$
	DELETE FROM Classroom WHERE id = id_;
$$;

-- Teacher --
CREATE OR REPLACE PROCEDURE Add_Teacher(pairType_ text,
                                        totalWorkHours_ integer,
                                        Firstname_ text,
                                        Surname_ text,
                                        Lastname_ text,
                                        classroom_ integer,
                                        discipline_ integer,
                                        brigade_ integer)
LANGUAGE sql
AS $$
	INSERT INTO Teacher(pairType,
						totalWorkHours,
						Firstname,
						Surname,
						Lastname,
						classroom,
						discipline,
						brigade)

	VALUES (pairType_,
	        totalWorkHours_,
	        Firstname_,
	        Surname_,
	        Lastname_,
	        classroom_,
	        discipline_,
	        brigade_);
$$;

CREATE OR REPLACE PROCEDURE Change_Teacher(id_ integer,
                                pairType_ text,
                                totalWorkHours_ integer,
                                Firstname_ text,
                                Surname_ text,
                                Lastname_ text,
                                classroom_ integer,
                                discipline_ integer,
                                brigade_ integer)
LANGUAGE sql
AS $$
	UPDATE Teacher
	SET (pairType, totalWorkHours, Firstname, Surname, Lastname, classroom, discipline, brigade) =
		(pairType_, totalWorkHours_, Firstname_, Surname_, Lastname_, classroom_, discipline_, brigade_)
	WHERE id = id_;
$$;

CREATE OR REPLACE PROCEDURE Delete_Teacher(id_ integer)
LANGUAGE sql
AS $$
	DELETE FROM Teacher WHERE id = id_;
$$;

-- 6 Задание --
CREATE OR REPLACE PROCEDURE Update_Brigade_Date()
LANGUAGE plpgsql
AS $$
DECLARE MaxStudents integer;
BEGIN
    START TRANSACTION;
    SELECT MAX(brigadeSize) INTO MaxStudents FROM Brigade;

    UPDATE Brigade
        SET brigadeSize = Max(classroomNumber)
        FROM Classroom
        WHERE Classroom.brigade = Brigade.id;

    IF (MaxStudents > 30) THEN
        ROLLBACK ;
    ELSE
        COMMIT;
    END IF;
END;
$$;

-- 7 Задание --
CREATE OR REPLACE PROCEDURE Renewal()
LANGUAGE plpgsql
AS $$
DECLARE __cursor CURSOR FOR SELECT * FROM Brigade;
BEGIN
    OPEN __cursor;
    LOOP
        MOVE FORWARD 1 FROM __cursor;
        EXIT WHEN NOT found;

        UPDATE Brigade
            SET dateOfAccreditation = '2018-08-24'
            WHERE CURRENT OF __cursor;
    END LOOP;
    CLOSE __cursor;
END;
$$;

-- 8 Задание --
CREATE OR REPLACE FUNCTION Concat_Brigade(brigadeSize integer, brigadeCode text)
RETURNS text
LANGUAGE SQL
AS $$
    SELECT concat(brigadeCode, ', ', brigadeSize);
$$;

CREATE OR REPLACE FUNCTION Receipt_Date()
RETURNS TABLE(id integer, yearOfAdmission date)
LANGUAGE SQL
as $$
    select id, yearOfAdmission from Brigade;
$$;

-- 9 Задание --
CREATE ROLE readonly;
GRANT USAGE ON SCHEMA public TO readonly;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO readonly;
GRANT CONNECT ON DATABASE coursework TO readonly;
GRANT CONNECT ON DATABASE postgres TO readonly;
CREATE USER readuser WITH PASSWORD 'read';
GRANT readonly TO readuser;

CREATE ROLE readwrite;
GRANT USAGE ON SCHEMA public TO readwrite;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO readwrite;
GRANT CONNECT ON DATABASE coursework TO readwrite;
GRANT CONNECT ON DATABASE postgres TO readwrite;
CREATE USER readwrite WITH PASSWORD 'readwrite';
GRANT readwrite TO readwriteuser;