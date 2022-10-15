import re
from xmlrpc.client import Boolean
import pyodbc
import pandas as pd


class Menu:
    """
    Clase para Menu de la aplicacion

    Parmetros:
    ----------
        database (str): Nombre de la base de datos
        server (str): Nombre del servidor

    Atributos:
    ----------
        exp (str): Expresion regular para buscar ofertas
        conn (pyodbc.Connection): Conexion a la base de datos
        cursor (pyodbc.Cursor): Cursor para ejecutar queries
        options (dict): Diccionario con las opciones del menu

    Metodos:
    ----------
        mostrar_carrito: Muestra el carrito de compras
        agregar_producto: Agrega un producto al carrito
        mostrar_top_5: Muestra los 5 productos mas caros
        mostrar_top_5_categoria: Muestra los 5 productos mas caros segun categoria
        finalizar_compra: Finaliza la compra
        mostrar_boleta: Muestra la boleta de compra
        mostrar_valor_total: Muestra el valor total de la compra
        buscar_producto: Busca un producto por nombre
        vaciar_carrito: Vaciar el carrito de compras
        eliminar_producto: Elimina un producto del carrito
        salir: Sale de la aplicacion

    """

    def __init__(self, database: str, server: str) -> None:
        """
        Constructor de la clase Menu

        Parametros:
            database (str): Nombre de la base de datos
            server (str): Nombre del servidor

        Retorna:
            None
        """
        self.database = database
        self.server = server
        self.exp = r'(P|p)ague\s\d+\s(L|l)leve\s\d+'
        self.conn = pyodbc.connect(
            'DRIVER={ODBC Driver 17 for SQL Server};SERVER=' + self.server + ';DATABASE=' + self.database + ';Trusted_Connection=yes;')
        self.cursor = self.conn.cursor()
        try:
            self.cursor.execute(
                'CREATE TABLE {}.dbo.productos (prod_id bigint not null primary key, prod_name nvarchar(150), prod_description nvarchar(150), prod_brand nvarchar(150), category nvarchar(150), prod_unit_price int);'.format(self.database))
            data = pd.read_csv('data/ProductosVF2.csv',
                               sep=';', encoding='utf-8')
            df = pd.DataFrame(data)
            df = df.where(pd.notnull(df), None)
            for index, row in df.iterrows():
                self.cursor.execute('INSERT INTO {}.dbo.productos VALUES (?, ?, ?, ?, ?, ?);'.format(self.database),
                                    int(row[0]), row[1], row[2], row[3], row[4], int(row[5]))
            self.cursor.execute(
                'CREATE TABLE {}.dbo.Carrito (prod_id bigint not null primary key, prod_name nvarchar(150), prod_brand nvarchar(150), quantity int)'.format(self.database))
            self.cursor.execute(
                'CREATE TABLE {}.dbo.Boleta (prod_id bigint not null primary key, offer nvarchar(10), total_value int, final_value int);'.format(self.database))
            self.cursor.execute(
                'CREATE TABLE {}.dbo.Oferta (prod_id bigint not null primary key, offer nvarchar(10));'.format(self.database))
            self.cursor.commit()
            self.cursor.execute(
                "SELECT * FROM test_tarea1_inf239.dbo.productos WHERE prod_description LIKE '%Pague%' or prod_description LIKE '%pague%'")
            rows = self.cursor.fetchall()
            rows = [row for row in rows if row is not None]
            new_rows = []
            for row in rows:
                if re.search(self.exp, row[2]) is not None:
                    new_rows.append(row)
            for row in new_rows:
                offer = re.search(self.exp, row[2]).group()
                offer = re.split(r'\s', offer)
                pague = int(offer[1])
                lleve = int(offer[3])
                self.cursor.execute(
                    "INSERT INTO test_tarea1_inf239.dbo.Oferta VALUES (?, ?)", row[0], '{}x{}'.format(lleve, pague))
            self.cursor.commit()
            print(
                """
                Base de datos creada exitosamente
                [ OK ] PRODUCTOS CARGADOS
                [ OK ] TABLAS CREADAS
                [ OK ] OFERTAS CARGADAS
                """
            )
            print(" Bienvenido a la tienda virtual ".center(50, '-'))
        except pyodbc.ProgrammingError:
            print(" Bienvenido/a a la tienda virtual ".center(50, '-'))
        self.options = {
            "1": self.mostrar_carrito,
            "2": self.agregar_producto,
            "3": self.mostrar_top_5,
            "4": self.mostrar_top_5_categoria,
            "5": self.finalizar_compra,
            "6": self.mostrar_boleta,
            "7": self.mostrar_valor_total,
            "8": self.buscar_producto,
            "9": self.vaciar_carrito,
            "10": self.eliminar_producto,
            "11": self.salir
        }

    def display_menu(self) -> None:
        """
        Muestra el menu de la aplicacion

        Parametros:
        ----------
            None

        Retorna:
        ----------
            None
        """
        print("""
        1. Mostrar mi carrito
        2. Agregar productos al carrito
        3. Mostrar Top 5 productos mas caros
        4. Mostrar los 5 productos mas caros segun categoria
        5. Finalizar compra
        6. Mostrar mi boleta
        7. Mostrar valor total
        8. Buscar producto
        9. Vaciar carrito
        10. Eliminar producto del carrito
        11. Salir
        """)

    def run(self) -> None:
        """
        Ejecuta la aplicacion

        Parametros:
        ----------  
           None

        Retorna:
        ----------
            None
        """
        while True:
            self.display_menu()
            choice = input("Ingrese una opcion: ")
            action = self.options.get(choice)
            if action:
                action()
            else:
                print("{0} is not a valid choice".format(choice))

    def mostrar_carrito(self) -> None:
        """
        Muestra el carrito de compras con ofertas aplicadas

        Parametros:
        ----------  
           None

        Retorna:
        ----------
            None
        """
        self.cursor.execute(
            'SELECT * FROM {}.dbo.Carrito;'.format(self.database))
        for row in self.cursor:
            print("ID: {0} | Nombre: {1} | Marca: {2} | Cantidad: {3}".format(
                row[0], row[1], row[2], row[3]))

    def agregar_producto(self) -> None:
        """
        Agrega un producto al carrito de compras

        Parametros:
        ----------  
           None

        Retorna:
        ----------
            None
        """
        prod_id = int(input("Ingrese el ID del producto: "))
        quantity = int(input("Ingrese la cantidad: "))
        # check if id exists carrito
        self.cursor.execute(
            'SELECT * FROM {}.dbo.Carrito WHERE prod_id = ?;'.format(self.database), prod_id)
        row = self.cursor.fetchone()
        if row:
            self.cursor.execute(
                'UPDATE {}.dbo.Carrito SET quantity = quantity + ? WHERE prod_id = ?;'.format(self.database), quantity, prod_id)
            self.cursor.commit()
        else:
            try:
                self.cursor.execute(
                    'SELECT * FROM {}.dbo.productos WHERE prod_id = ?;'.format(self.database), prod_id)
                row = self.cursor.fetchone()
                if row:
                    self.cursor.execute(
                        'INSERT INTO {}.dbo.Carrito VALUES (?, ?, ?, ?);'.format(self.database), row[0], row[1], row[3], quantity)
                else:
                    print("ID no existe")
            except pyodbc.ProgrammingError:
                print("Producto no existe")
        self.cursor.execute(
            'SELECT * FROM {}.dbo.Oferta WHERE prod_id = ?;'.format(self.database), prod_id)
        row = self.cursor.fetchone()
        if row:
            self.cursor.execute(
                'UPDATE {}.dbo.Oferta SET offer = ? WHERE prod_id = ?;'.format(self.database), row[1], prod_id)
        self.cursor.commit()

    def mostrar_top_5(self) -> None:
        """
        Muestra los 5 productos mas caros

        Parametros:
        ----------  
           None

        Retorna:
        ----------
            None
        """
        self.cursor.execute(
            'SELECT TOP 5 * FROM {}.dbo.productos ORDER BY prod_unit_price DESC;'.format(self.database))
        for row in self.cursor:
            print("ID: {0} | Nombre: {1} | Descripcion: {2} | Marca: {3} | Categoria: {4} | Precio: ${5}".format(
                row[0], row[1], row[2], row[3], row[4], row[5]))

    def mostrar_top_5_categoria(self) -> None:
        """
        Muestra los 5 productos mas caros por categoria

        Parametros:
        ----------  
           None

        Retorna:
        ----------
            None
        """
        category = input("Ingrese la categoria: ")
        self.cursor.execute(
            'SELECT TOP 5 * FROM {}.dbo.productos WHERE category = ? ORDER BY prod_unit_price DESC;'.format(self.database), category)
        for row in self.cursor:
            print("ID: {0} | Nombre: {1} | Descripcion: {2} | Marca: {3} | Categoria: {4} | Precio: ${5}".format(
                row[0], row[1], row[2], row[3], row[4], row[5]))

    def finalizar_compra(self) -> None:
        """
        Finaliza la compra y genera un boleta a partir del carrito actual

        Parametros:
        ----------  
           None

        Retorna:
        ----------
            None
        """
        self.mostrar_boleta()
        self.salir()

    def mostrar_boleta(self) -> None:
        """
        Muestra la boleta al usuario, con las ofertas aplicadas

        Parametros:
        ----------  
           None

        Retorna:
        ----------
            None
        """
        self.cursor.execute('DELETE FROM {}.dbo.Boleta'.format(self.database))
        self.cursor.execute(
            'SELECT * FROM {}.dbo.Carrito;'.format(self.database))
        data = self.cursor.fetchall()
        for carrito_row in data:
            self.cursor.execute(
                'SELECT * FROM {}.dbo.productos WHERE prod_id = ?;'.format(self.database), carrito_row[0])
            total_price = self.cursor.fetchone()[5] * carrito_row[3]
            self.cursor.execute(
                'SELECT * FROM {}.dbo.Oferta WHERE prod_id = ?;'.format(self.database), carrito_row[0])
            oferta_row = self.cursor.fetchone()
            if not oferta_row:
                oferta_row = (carrito_row[0], '1x1')
            lleve = int(oferta_row[1].split('x')[0])
            pague = int(oferta_row[1].split('x')[1])
            if pague != 0:
                self.cursor.execute(
                    'SELECT * FROM {}.dbo.productos WHERE prod_id = ?;'.format(self.database), carrito_row[0])
                final_price = ((int(carrito_row[3] / lleve) * pague) + (
                    carrito_row[3] % lleve)) * self.cursor.fetchone()[5]
            else:
                final_price = 0
            self.cursor.execute(
                'INSERT INTO {}.dbo.Boleta VALUES (?, ?, ?, ?);'.format(self.database), carrito_row[0], oferta_row[1], total_price, final_price)
            self.cursor.commit()
        self.cursor.execute(
            'SELECT * FROM {}.dbo.Boleta'.format(self.database))
        for row in self.cursor:
            print("ID: {0} | Oferta: {1} | Total: {2} | Final: {3}".format(
                row[0], row[1], row[2], row[3]))

    def mostrar_valor_total(self) -> None:
        """
        Muestra el valor total apartir de la boleta

        Parametros:
        ----------  
           None

        Retorna:
        ----------
            None
        """
        self.cursor.execute(
            'SELECT SUM(final_value) FROM {}.dbo.Boleta'.format(self.database))
        row = self.cursor.fetchone()
        if row[0]:
            print("Valor total: ${}".format(row[0]))
        else:
            print("Valor total: $0")

    def buscar_producto(self) -> None:
        """
        Busca un producto por id

        Parametros:
        ----------
        None

        """
        while True:
            try:
                prod_id = int(input("Ingrese el ID del producto: "))
                break

            except KeyboardInterrupt:
                self.salir()

            except:
                print("ID no valido")

        self.cursor.execute(
            'SELECT * FROM {}.dbo.productos WHERE prod_id = ?;'.format(self.database), prod_id)
        row = self.cursor.fetchone()
        if row:
            print('ID: {0} | Nombre: {1} | Descripcion: {2} | Marca: {3} | Categoria: {4} | Precio: ${5}'.format(
                row[0], row[1], row[2], row[3], row[4], row[5]))
        else:
            print("Producto no encontrado")

    def vaciar_carrito(self) -> None:
        """
        Vaciar el carrito de compras

        Parametros:
        ----------
            None

        Retorno:
        ----------
            None
        """
        self.cursor.execute(
            'DELETE FROM {}.dbo.Carrito;'.format(self.database))
        self.cursor.commit()

    def eliminar_producto(self) -> None:
        """"
        Eliminar el producto del carrito por el id

        Parametros:
        ----------
           None

        Retorno:
        ----------
           None

        """
        while True:
            try:
                prod_id = int(input("Ingrese el ID del producto: "))
                break

            except KeyboardInterrupt:
                self.salir()

            except:
                print("ID no valido")

        try:
            select = self.cursor.execute(
                'SELECT * FROM {}.dbo.Carrito WHERE prod_id = ?;'.format(self.database), prod_id)
            print("Se ha eliminado el producto: {}".format(select[1]))
            self.cursor.execute(
                'DELETE FROM {}.dbo.Carrito WHERE prod_id = ?;'.format(self.database), prod_id)
            self.cursor.commit()
        except:
            print("Producto no encontrado. Verifique el ID")

    def salir(self) -> None:
        """
        Cierra la conexion con la base de datos

        Parametros:
        ----------
            None

        Retorna:
        ----------
            None
        """
        print("Gracias por su visita")
        exit()
