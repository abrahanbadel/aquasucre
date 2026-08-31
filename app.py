from flask import Flask, request, redirect, url_for
import os
import psycopg2

app = Flask(__name__)


def obtener_conexion():
    return psycopg2.connect(os.environ["DATABASE_URL"])


# ==========================================
# ESTILOS COMPARTIDOS (solo presentación)
# ==========================================
ESTILOS = """
<style>
    :root {
        --azul: #0b6fb3;
        --azul-oscuro: #084c7d;
        --gris-fondo: #f4f7fa;
        --gris-borde: #dde3ea;
        --texto: #2a2f36;
        --texto-suave: #647082;
        --blanco: #ffffff;
        --sombra: 0 2px 10px rgba(15, 45, 75, 0.08);
    }

    * { box-sizing: border-box; }

    body {
        margin: 0;
        padding: 32px 24px 60px;
        background: var(--gris-fondo);
        color: var(--texto);
        font-family: "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        line-height: 1.5;
    }

    .contenedor {
        max-width: 1100px;
        margin: 0 auto;
    }

    header.marca {
        display: flex;
        align-items: center;
        gap: 14px;
        margin-bottom: 24px;
    }

    header.marca .gota {
        width: 40px;
        height: 40px;
        border-radius: 50%;
        background: linear-gradient(135deg, var(--azul), var(--azul-oscuro));
        flex-shrink: 0;
    }

    h1 {
        margin: 0;
        font-size: 1.6rem;
        color: var(--azul-oscuro);
        letter-spacing: 0.5px;
    }

    h1 small {
        display: block;
        font-size: 0.75rem;
        font-weight: 400;
        color: var(--texto-suave);
        letter-spacing: 0.3px;
    }

    h2 {
        font-size: 1.15rem;
        color: var(--azul-oscuro);
        margin: 0 0 4px;
    }

    h3 {
        font-size: 1rem;
        color: var(--azul-oscuro);
        margin: 0 0 10px;
    }

    p.subtitulo {
        color: var(--texto-suave);
        margin: 0 0 20px;
        max-width: 640px;
    }

    .panel {
        background: var(--blanco);
        border: 1px solid var(--gris-borde);
        border-radius: 12px;
        box-shadow: var(--sombra);
        padding: 22px 24px;
        margin-bottom: 24px;
    }

    .panel-encabezado {
        display: flex;
        justify-content: space-between;
        align-items: baseline;
        margin-bottom: 14px;
        flex-wrap: wrap;
        gap: 8px;
    }

    table {
        width: 100%;
        border-collapse: collapse;
        font-size: 0.92rem;
    }

    thead th {
        text-align: left;
        background: var(--azul-oscuro);
        color: var(--blanco);
        padding: 10px 12px;
        font-weight: 600;
        white-space: nowrap;
    }

    thead th:first-child { border-radius: 8px 0 0 0; }
    thead th:last-child { border-radius: 0 8px 0 0; }

    tbody td {
        padding: 10px 12px;
        border-bottom: 1px solid var(--gris-borde);
        vertical-align: top;
    }

    tbody tr:hover td {
        background: #f0f6fb;
    }

    tbody tr:last-child td {
        border-bottom: none;
    }

    .campo {
        margin: 0 0 10px;
        color: var(--texto);
    }

    .campo strong {
        color: var(--azul-oscuro);
        display: inline-block;
        min-width: 110px;
    }

    form {
        margin-top: 8px;
    }

    select {
        width: 100%;
        max-width: 420px;
        padding: 10px 12px;
        border: 1px solid var(--gris-borde);
        border-radius: 8px;
        font-size: 0.95rem;
        color: var(--texto);
        background: var(--blanco);
    }

    button[type="submit"] {
        margin-top: 16px;
        padding: 10px 22px;
        background: var(--azul);
        color: var(--blanco);
        border: none;
        border-radius: 8px;
        font-size: 0.95rem;
        font-weight: 600;
        cursor: pointer;
        transition: background 0.15s ease;
    }

    button[type="submit"]:hover {
        background: var(--azul-oscuro);
    }

    .volver {
        display: inline-block;
        margin-top: 18px;
        color: var(--azul);
        text-decoration: none;
        font-weight: 600;
    }

    .volver:hover {
        text-decoration: underline;
    }

    footer.pie {
        margin-top: 28px;
        color: var(--texto-suave);
        font-size: 0.85rem;
        text-align: center;
    }

    .panel.error {
        border-color: #e3b8b8;
        background: #fdf3f3;
    }

    .panel.error h2 {
        color: #b23a3a;
    }

    .panel.error p {
        color: #7a2f2f;
        font-family: monospace;
        word-break: break-word;
    }
</style>
"""


@app.route("/")
def inicio():
    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        # ==========================================
        # CONSULTAR ÓRDENES DE TRABAJO
        # ==========================================

        cursor.execute("""
            SELECT
                ot.id_ot,
                ot.id_pqr,
                ot.tipo_servicio,
                ot.descripcion,
                ot.direccion,
                ot.prioridad,
                ot.estado,
                t.nombre
            FROM ordenes_trabajo ot
            LEFT JOIN tecnicos t
                ON ot.id_tecnico = t.id_tecnico
            ORDER BY ot.id_ot DESC
        """)

        ordenes = cursor.fetchall()

        filas_ordenes = ""

        for ot in ordenes:
            tecnico = ot[7] if ot[7] is not None else "Sin asignar"
            estado = ot[6] if ot[6] is not None else "Sin estado"

            filas_ordenes += f"""
            <tr>
                <td>{ot[0]}</td>
                <td>{ot[1]}</td>
                <td>{ot[2]}</td>
                <td>{ot[3]}</td>
                <td>{ot[4]}</td>
                <td>{ot[5]}</td>
                <td>{estado}</td>
                <td>{tecnico}</td>
            </tr>
            """

        # ==========================================
        # CONSULTAR TÉCNICOS
        # ==========================================

        cursor.execute("""
            SELECT
                id_tecnico,
                nombre,
                telefono,
                especialidad,
                estado
            FROM tecnicos
            ORDER BY id_tecnico
        """)

        tecnicos = cursor.fetchall()

        filas_tecnicos = ""

        for tecnico in tecnicos:
            filas_tecnicos += f"""
            <tr>
                <td>{tecnico[0]}</td>
                <td>{tecnico[1]}</td>
                <td>{tecnico[2]}</td>
                <td>{tecnico[3]}</td>
                <td>{tecnico[4]}</td>
            </tr>
            """

        cursor.close()
        conexion.close()

        return f"""
        <!DOCTYPE html>

        <html lang="es">

        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <title>AquaSucre OT</title>
            {ESTILOS}
        </head>

        <body>

            <div class="contenedor">

                <header class="marca">
                    <div class="gota"></div>
                    <h1>AquaSucre
                        <small>Gestión de Órdenes de Trabajo</small>
                    </h1>
                </header>

                <p class="subtitulo">
                    Plataforma para la gestión y seguimiento
                    de órdenes de trabajo.
                </p>

                <section class="panel">
                    <div class="panel-encabezado">
                        <h2>Órdenes de Trabajo</h2>
                    </div>

                    <table>
                        <thead>
                            <tr>
                                <th>OT</th>
                                <th>PQR</th>
                                <th>Servicio</th>
                                <th>Descripción</th>
                                <th>Dirección</th>
                                <th>Prioridad</th>
                                <th>Estado</th>
                                <th>Técnico</th>
                            </tr>
                        </thead>
                        <tbody>
                            {filas_ordenes}
                        </tbody>
                    </table>
                </section>

                <section class="panel">
                    <div class="panel-encabezado">
                        <h2>Técnicos registrados</h2>
                    </div>

                    <table>
                        <thead>
                            <tr>
                                <th>ID</th>
                                <th>Nombre</th>
                                <th>Teléfono</th>
                                <th>Especialidad</th>
                                <th>Estado</th>
                            </tr>
                        </thead>
                        <tbody>
                            {filas_tecnicos}
                        </tbody>
                    </table>
                </section>

                <footer class="pie">
                    AquaSucre OT &middot; Versión 1.2
                </footer>

            </div>

        </body>

        </html>
        """

    except Exception as error:

        return f"""
        <!DOCTYPE html>
        <html lang="es">
        <head>
            <meta charset="UTF-8">
            <title>AquaSucre OT</title>
            {ESTILOS}
        </head>
        <body>
            <div class="contenedor">
                <header class="marca">
                    <div class="gota"></div>
                    <h1>AquaSucre</h1>
                </header>
                <section class="panel error">
                    <h2>Error conectando con la base de datos</h2>
                    <p>{error}</p>
                </section>
            </div>
        </body>
        </html>
        """


@app.route("/asignar/<int:id_ot>")
def asignar(id_ot):

    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        # Consultar la OT seleccionada
        cursor.execute("""
            SELECT
                id_ot,
                id_pqr,
                tipo_servicio,
                descripcion,
                direccion,
                prioridad,
                estado
            FROM ordenes_trabajo
            WHERE id_ot = %s
        """, (id_ot,))

        ot = cursor.fetchone()

        # Consultar técnicos activos
        cursor.execute("""
            SELECT
                id_tecnico,
                nombre,
                especialidad
            FROM tecnicos
            WHERE UPPER(estado) = 'ACTIVO'
            ORDER BY nombre
        """)

        tecnicos = cursor.fetchall()

        cursor.close()
        conexion.close()

        if ot is None:
            return "<h2>Orden de trabajo no encontrada</h2>", 404

        opciones = ""

        for tecnico in tecnicos:
            opciones += f"""
                <option value="{tecnico[0]}">
                    {tecnico[1]} - {tecnico[2]}
                </option>
            """

        return f"""
        <!DOCTYPE html>

        <html lang="es">

        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <title>Asignar OT - AquaSucre</title>
            {ESTILOS}
        </head>

        <body>

            <div class="contenedor">

                <header class="marca">
                    <div class="gota"></div>
                    <h1>AquaSucre
                        <small>Asignar Orden de Trabajo</small>
                    </h1>
                </header>

                <section class="panel">
                    <h3>OT #{ot[0]}</h3>

                    <p class="campo"><strong>PQR:</strong> {ot[1]}</p>
                    <p class="campo"><strong>Servicio:</strong> {ot[2]}</p>
                    <p class="campo"><strong>Descripción:</strong> {ot[3]}</p>
                    <p class="campo"><strong>Dirección:</strong> {ot[4]}</p>
                    <p class="campo"><strong>Prioridad:</strong> {ot[5]}</p>
                    <p class="campo"><strong>Estado:</strong> {ot[6]}</p>
                </section>

                <section class="panel">
                    <h3>Seleccionar técnico</h3>

                    <form method="POST"
                          action="/confirmar-asignacion/{ot[0]}">

                        <select name="id_tecnico" required>

                            <option value="">
                                -- Seleccione un técnico --
                            </option>

                            {opciones}

                        </select>

                        <br>

                        <button type="submit">
                            Confirmar asignación
                        </button>

                    </form>
                </section>

                <a class="volver" href="/">
                    &larr; Volver al Gestor de OT
                </a>

            </div>

        </body>

        </html>
        """

    except Exception as error:

        return f"""
        <!DOCTYPE html>
        <html lang="es">
        <head>
            <meta charset="UTF-8">
            <title>AquaSucre OT</title>
            {ESTILOS}
        </head>
        <body>
            <div class="contenedor">
                <header class="marca">
                    <div class="gota"></div>
                    <h1>AquaSucre</h1>
                </header>
                <section class="panel error">
                    <h2>Error consultando la orden de trabajo</h2>
                    <p>{error}</p>
                </section>
            </div>
        </body>
        </html>
        """

@app.route("/confirmar-asignacion/<int:id_ot>", methods=["POST"])
def confirmar_asignacion(id_ot):

    conexion = None
    cursor = None

    try:
        id_tecnico = request.form.get("id_tecnico")

        if not id_tecnico:
            return "<h2>Debe seleccionar un técnico.</h2>", 400

        conexion = obtener_conexion()
        cursor = conexion.cursor()

        # Verificar que el técnico exista y esté activo
        cursor.execute("""
            SELECT id_tecnico
            FROM tecnicos
            WHERE id_tecnico = %s
              AND UPPER(estado) = 'ACTIVO'
        """, (id_tecnico,))

        tecnico = cursor.fetchone()

        if tecnico is None:
            return "<h2>El técnico seleccionado no existe o no está activo.</h2>", 400

        # Asignar técnico a la orden de trabajo
        cursor.execute("""
            UPDATE ordenes_trabajo
            SET
                id_tecnico = %s,
                estado = 'ASIGNADA',
                fecha_asignacion = CURRENT_TIMESTAMP
            WHERE id_ot = %s
        """, (id_tecnico, id_ot))

        if cursor.rowcount == 0:
            conexion.rollback()
            return "<h2>Orden de trabajo no encontrada.</h2>", 404

        conexion.commit()

        return redirect(url_for("inicio"))

    except Exception as error:

        if conexion:
            conexion.rollback()

        return f"""
        <!DOCTYPE html>
        <html lang="es">
        <head>
            <meta charset="UTF-8">
            <title>AquaSucre OT</title>
            {ESTILOS}
        </head>
        <body>
            <div class="contenedor">
                <header class="marca">
                    <div class="gota"></div>
                    <h1>AquaSucre</h1>
                </header>
                <section class="panel error">
                    <h2>Error realizando la asignación</h2>
                    <p>{error}</p>
                </section>
            </div>
        </body>
        </html>
        """, 500

    finally:

        if cursor:
            cursor.close()

        if conexion:
            conexion.close()
            
if __name__ == "__main__":
    app.run()
