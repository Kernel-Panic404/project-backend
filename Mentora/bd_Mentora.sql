CREATE TABLE "usuario" (
  "id" integer PRIMARY KEY,
  "nombre" varchar(100) NOT NULL,
  "apellido" varchar(100) NOT NULL,
  "correo" varchar(150) NOT NULL UNIQUE,
  "password_hash" varchar(255) NOT NULL,
  "activo" boolean DEFAULT true,
  "intentos_fallidos" integer DEFAULT 0,
  "bloqueado_hasta" timestamp,
  "creado_en" timestamp DEFAULT CURRENT_TIMESTAMP,
  "ultimo_acceso" timestamp
);

CREATE TABLE "rol" (
  "id" integer PRIMARY KEY,
  "nombre" varchar(50) NOT NULL UNIQUE
);

CREATE TABLE "usuario_rol" (
  "id" integer PRIMARY KEY,
  "usuario_id" integer NOT NULL,
  "rol_id" integer NOT NULL,
  UNIQUE(usuario_id, rol_id)
);

CREATE TABLE "materia" (
  "id" integer PRIMARY KEY,
  "nombre" varchar(100) NOT NULL,
  "codigo" varchar(20) NOT NULL UNIQUE,
  "descripcion" text
);

CREATE TABLE "disponibilidad_tutor" (
  "id" integer PRIMARY KEY,
  "tutor_id" integer NOT NULL,
  "dia_semana" integer NOT NULL,
  "hora_inicio" time NOT NULL,
  "hora_fin" time NOT NULL,
  "disponible" boolean DEFAULT true,
  CHECK (hora_inicio < hora_fin),
  CHECK (dia_semana BETWEEN 0 AND 6)
);

CREATE TABLE "disponibilidad_excepcion" (
  "id" integer PRIMARY KEY,
  "tutor_id" integer NOT NULL,
  "fecha_excepcion" date NOT NULL,
  "disponible" boolean NOT NULL,
  "motivo" varchar(255),
  UNIQUE(tutor_id, fecha_excepcion)
);

CREATE TABLE "tutoria" (
  "id" integer PRIMARY KEY,
  "materia_id" integer,
  "fecha" date NOT NULL,
  "hora_inicio" time NOT NULL,
  "hora_fin" time NOT NULL,
  "estado" varchar(20) DEFAULT 'agendada',
  "motivo_cancelacion" text,
  "reprogramada_desde_id" integer,
  "reprogramacion_count" integer DEFAULT 0,
  "fecha_limite_cancelacion" timestamp,
  "creado_en" timestamp DEFAULT CURRENT_TIMESTAMP,
  CHECK (reprogramacion_count <= 2)
);

CREATE TABLE "participacion_tutoria" (
  "id" integer PRIMARY KEY,
  "tutoria_id" integer NOT NULL,
  "usuario_id" integer NOT NULL,
  "rol_en_tutoria" varchar(20) NOT NULL CHECK (rol_en_tutoria IN ('estudiante', 'tutor')),
  UNIQUE(tutoria_id, usuario_id, rol_en_tutoria)
);

CREATE TABLE "tutor_materia" (
  "id" integer PRIMARY KEY,
  "tutor_id" integer NOT NULL,
  "materia_id" integer NOT NULL,
  UNIQUE(tutor_id, materia_id)
);

CREATE TABLE "registro_sesion" (
  "id" integer PRIMARY KEY,
  "tutoria_id" integer UNIQUE,
  "calificacion" decimal(5,2),
  "observaciones" text,
  "temas_trabajados" text,
  "creado_en" timestamp DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE "asistencia" (
  "id" integer PRIMARY KEY,
  "tutoria_id" integer NOT NULL,
  "usuario_id" integer NOT NULL,
  "asistio" boolean NOT NULL,
  "observacion" varchar(255),
  UNIQUE(tutoria_id, usuario_id)
);

CREATE TABLE "notificacion" (
  "id" integer PRIMARY KEY,
  "tutoria_id" integer NOT NULL,
  "usuario_id" integer NOT NULL,
  "canal" varchar(20) NOT NULL CHECK (canal IN ('email', 'push', 'ambos')),
  "enviada" boolean DEFAULT false,
  "fecha_envio" timestamp,
  "mensaje" text,
  "intentos_enviados" integer DEFAULT 0,
  "proximo_intento" timestamp,
  "ultimo_error" text
);

CREATE TABLE "cuestionario" (
  "id" integer PRIMARY KEY,
  "profesor_id" integer,
  "materia_id" integer,
  "titulo" varchar(200) NOT NULL,
  "descripcion" text,
  "fecha_limite" date,
  "intentos_permitidos" integer DEFAULT 1,
  "activo" boolean DEFAULT true,
  "creado_en" timestamp DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE "pregunta" (
  "id" integer PRIMARY KEY,
  "cuestionario_id" integer NOT NULL,
  "enunciado" text NOT NULL,
  "tipo" varchar(30) NOT NULL CHECK (tipo IN ('multiple', 'vf', 'abierta')),
  "orden" integer,
  "puntaje_maximo" decimal(5,2)
);

CREATE TABLE "opcion_pregunta" (
  "id" integer PRIMARY KEY,
  "pregunta_id" integer NOT NULL,
  "texto" varchar(255) NOT NULL,
  "es_correcta" boolean DEFAULT false
);

CREATE TABLE "resultado_cuestionario" (
  "id" integer PRIMARY KEY,
  "cuestionario_id" integer NOT NULL,
  "estudiante_id" integer NOT NULL,
  "puntaje_total" decimal(5,2),
  "fecha_realizacion" timestamp DEFAULT CURRENT_TIMESTAMP,
  UNIQUE(cuestionario_id, estudiante_id)
);

CREATE TABLE "respuesta_cuestionario" (
  "id" integer PRIMARY KEY,
  "cuestionario_id" integer,
  "estudiante_id" integer NOT NULL,
  "pregunta_id" integer NOT NULL,
  "respuesta_texto" text,
  "opcion_seleccionada_id" integer,
  "puntaje" decimal(5,2),
  "creado_en" timestamp DEFAULT CURRENT_TIMESTAMP,
  CHECK (
    (tipo_pregunta_abierta() AND respuesta_texto IS NOT NULL) OR
    (opcion_seleccionada_id IS NOT NULL)
  )
);

ALTER TABLE "usuario_rol" ADD FOREIGN KEY ("usuario_id") REFERENCES "usuario" ("id") DEFERRABLE INITIALLY IMMEDIATE;
ALTER TABLE "usuario_rol" ADD FOREIGN KEY ("rol_id") REFERENCES "rol" ("id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "disponibilidad_tutor" ADD FOREIGN KEY ("tutor_id") REFERENCES "usuario" ("id") DEFERRABLE INITIALLY IMMEDIATE;
ALTER TABLE "disponibilidad_excepcion" ADD FOREIGN KEY ("tutor_id") REFERENCES "usuario" ("id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "tutoria" ADD FOREIGN KEY ("materia_id") REFERENCES "materia" ("id") DEFERRABLE INITIALLY IMMEDIATE;
ALTER TABLE "tutoria" ADD FOREIGN KEY ("reprogramada_desde_id") REFERENCES "tutoria" ("id") DEFERRABLE INITIALLY IMMEDIATE;

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

CREATE INDEX idx_usuario_correo ON usuario(correo);
CREATE INDEX idx_usuario_activo ON usuario(activo);
CREATE INDEX idx_tutoria_fecha ON tutoria(fecha);
CREATE INDEX idx_tutoria_estado ON tutoria(estado);
CREATE INDEX idx_participacion_usuario ON participacion_tutoria(usuario_id);
CREATE INDEX idx_participacion_tutoria ON participacion_tutoria(tutoria_id);
CREATE INDEX idx_disponibilidad_tutor ON disponibilidad_tutor(tutor_id, dia_semana);
CREATE INDEX idx_disponibilidad_excepcion_tutor_fecha ON disponibilidad_excepcion(tutor_id, fecha_excepcion);
CREATE INDEX idx_notificacion_pendiente ON notificacion(proximo_intento) WHERE enviada = false;
CREATE INDEX idx_cuestionario_materia ON cuestionario(materia_id);
CREATE INDEX idx_resultado_estudiante ON resultado_cuestionario(estudiante_id);
CREATE INDEX idx_asistencia_tutoria ON asistencia(tutoria_id);
CREATE INDEX idx_registro_sesion_tutoria ON registro_sesion(tutoria_id);