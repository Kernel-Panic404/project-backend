CREATE TABLE "usuario" (
  "id" integer PRIMARY KEY,
  "nombre" varchar(100),
  "apellido" varchar(100) NOT NULL,
  "correo" varchar(150) NOT NULL,
  "password_hash" varchar(255) NOT NULL,
  "activo" boolean,
  "creado_en" timestamp
);

CREATE TABLE "rol" (
  "id" integer PRIMARY KEY,
  "nombre" varchar(50) NOT NULL
);

CREATE TABLE "usuario_rol" (
  "id" integer PRIMARY KEY,
  "usuario_id" integer NOT NULL,
  "rol_id" integer NOT NULL
);

CREATE TABLE "materia" (
  "id" integer PRIMARY KEY,
  "nombre" varchar(100) NOT NULL,
  "codigo" varchar(20) NOT NULL,
  "descripcion" text
);

CREATE TABLE "disponibilidad_tutor" (
  "id" integer PRIMARY KEY,
  "tutor_id" integer NOT NULL,
  "dia_semana" varchar(15) NOT NULL,
  "hora_inicio" time NOT NULL,
  "hora_fin" time NOT NULL,
  "disponible" boolean
);

CREATE TABLE "tutoria" (
  "id" integer PRIMARY KEY,
  "materia_id" integer,
  "fecha" date NOT NULL,
  "hora_inicio" time NOT NULL,
  "hora_fin" time NOT NULL,
  "estado" varchar(20),
  "motivo_cancelacion" text,
  "creado_en" timestamp
);

CREATE TABLE "participacion_tutoria" (
  "id" integer PRIMARY KEY,
  "tutoria_id" integer NOT NULL,
  "usuario_id" integer NOT NULL,
  "rol_en_tutoria" varchar(20) NOT NULL
);

CREATE TABLE "tutor_materia" (
  "id" integer PRIMARY KEY,
  "tutor_id" integer NOT NULL,
  "materia_id" integer NOT NULL
);

CREATE TABLE "registro_sesion" (
  "id" integer PRIMARY KEY,
  "tutoria_id" integer,
  "calificacion" decimal(4,2),
  "observaciones" text,
  "temas_trabajados" text,
  "creado_en" timestamp
);

CREATE TABLE "asistencia" (
  "id" integer PRIMARY KEY,
  "tutoria_id" integer NOT NULL,
  "usuario_id" integer NOT NULL,
  "asistio" boolean NOT NULL,
  "observacion" varchar(255)
);

CREATE TABLE "notificacion" (
  "id" integer PRIMARY KEY,
  "tutoria_id" integer NOT NULL,
  "usuario_id" integer NOT NULL,
  "canal" varchar(20) NOT NULL,
  "enviada" boolean,
  "fecha_envio" timestamp,
  "mensaje" text
);

CREATE TABLE "cuestionario" (
  "id" integer PRIMARY KEY,
  "profesor_id" integer,
  "materia_id" integer,
  "titulo" varchar(200) NOT NULL,
  "descripcion" text,
  "activo" boolean,
  "creado_en" timestamp
);

CREATE TABLE "pregunta" (
  "id" integer PRIMARY KEY,
  "cuestionario_id" integer NOT NULL,
  "enunciado" text NOT NULL,
  "tipo" varchar(30) NOT NULL,
  "orden" integer
);

CREATE TABLE "opcion_pregunta" (
  "id" integer PRIMARY KEY,
  "pregunta_id" integer NOT NULL,
  "texto" varchar(255) NOT NULL,
  "es_correcta" boolean
);

CREATE TABLE "resultado_cuestionario" (
  "id" integer PRIMARY KEY,
  "cuestionario_id" integer NOT NULL,
  "estudiante_id" integer NOT NULL,
  "puntaje_total" decimal(5,2),
  "fecha_realizacion" timestamp
);

CREATE TABLE "respuesta_cuestionario" (
  "id" integer PRIMARY KEY,
  "cuestionario_id" integer,
  "estudiante_id" integer NOT NULL,
  "pregunta_id" integer NOT NULL,
  "respuesta_texto" text,
  "opcion_seleccionada_id" integer,
  "puntaje" decimal(4,2),
  "creado_en" timestamp
);

ALTER TABLE "usuario_rol" ADD FOREIGN KEY ("usuario_id") REFERENCES "usuario" ("id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "usuario_rol" ADD FOREIGN KEY ("rol_id") REFERENCES "rol" ("id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "disponibilidad_tutor" ADD FOREIGN KEY ("tutor_id") REFERENCES "usuario" ("id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "tutoria" ADD FOREIGN KEY ("materia_id") REFERENCES "materia" ("id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "participacion_tutoria" ADD FOREIGN KEY ("tutoria_id") REFERENCES "tutoria" ("id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "participacion_tutoria" ADD FOREIGN KEY ("usuario_id") REFERENCES "usuario" ("id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "tutor_materia" ADD FOREIGN KEY ("tutor_id") REFERENCES "usuario" ("id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "tutor_materia" ADD FOREIGN KEY ("materia_id") REFERENCES "materia" ("id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "registro_sesion" ADD FOREIGN KEY ("tutoria_id") REFERENCES "tutoria" ("id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "asistencia" ADD FOREIGN KEY ("tutoria_id") REFERENCES "tutoria" ("id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "asistencia" ADD FOREIGN KEY ("usuario_id") REFERENCES "usuario" ("id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "notificacion" ADD FOREIGN KEY ("tutoria_id") REFERENCES "tutoria" ("id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "notificacion" ADD FOREIGN KEY ("usuario_id") REFERENCES "usuario" ("id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "cuestionario" ADD FOREIGN KEY ("profesor_id") REFERENCES "usuario" ("id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "cuestionario" ADD FOREIGN KEY ("materia_id") REFERENCES "materia" ("id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "pregunta" ADD FOREIGN KEY ("cuestionario_id") REFERENCES "cuestionario" ("id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "opcion_pregunta" ADD FOREIGN KEY ("pregunta_id") REFERENCES "pregunta" ("id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "resultado_cuestionario" ADD FOREIGN KEY ("cuestionario_id") REFERENCES "cuestionario" ("id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "resultado_cuestionario" ADD FOREIGN KEY ("estudiante_id") REFERENCES "usuario" ("id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "respuesta_cuestionario" ADD FOREIGN KEY ("cuestionario_id") REFERENCES "cuestionario" ("id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "respuesta_cuestionario" ADD FOREIGN KEY ("estudiante_id") REFERENCES "usuario" ("id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "respuesta_cuestionario" ADD FOREIGN KEY ("pregunta_id") REFERENCES "pregunta" ("id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "respuesta_cuestionario" ADD FOREIGN KEY ("opcion_seleccionada_id") REFERENCES "opcion_pregunta" ("id") DEFERRABLE INITIALLY IMMEDIATE;
