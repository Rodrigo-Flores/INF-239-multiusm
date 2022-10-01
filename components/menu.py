import re
from select import select
import pyodbc


class Menu:
    def __init__(self):
        self.conn = pyodbc.connect(
            'Driver={SQL Server};Server=LAPTOP-A43RI4HS\SQLEXPRESS;Database=test_tarea1_inf239;Trusted_Connection=yes;')
        self.cursor = self.conn.cursor()
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
        try:
            self.cursor.execute(
                'CREATE TABLE test_tarea1_inf239.dbo.Carrito (prod_id int, prod_name nvarchar(150), prod_brand nvarchar(150), quantity int)')
            self.cursor.execute(
                'CREATE TABLE test_tarea1_inf239.dbo.Boleta (prod_id int, offer nvarchar(10), total_value int, final_value int)')
            self.cursor.execute(
                'CREATE TABLE test_tarea1_inf239.dbo.Oferta (prod_id int, offer nvarchar(10)) DEFAULT ?', '1x1')
            self.cursor.commit()
        except pyodbc.ProgrammingError:
            print("Tables already exist")

    def display_menu(self):
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

    def run(self):
        while True:
            self.display_menu()
            choice = input("Ingrese una opcion: ")
            action = self.options.get(choice)
            if action:
                action()
            else:
                print("{0} is not a valid choice".format(choice))

    def mostrar_carrito(self) -> None:
        self.cursor.execute('SELECT * FROM test_tarea1_inf239.dbo.Carrito')
        for row in self.cursor:
            print("ID: {0} | Nombre: {1} | Marca: {2} | Cantidad: {3}".format(
                row[0], row[1], row[2], row[3]))

    def agregar_producto(self) -> None:
        prod_id = input("Ingrese el ID del producto: ")
        quantity = input("Ingrese la cantidad: ")
        # check if id exists carrito
        self.cursor.execute(
            'SELECT * FROM test_tarea1_inf239.dbo.Carrito WHERE prod_id = ?;', prod_id)
        row = self.cursor.fetchone()
        if row:
            self.cursor.execute(
                'UPDATE test_tarea1_inf239.dbo.Carrito SET quantity = quantity + ? WHERE prod_id = ?;', quantity, prod_id)
            self.cursor.commit()
        else:
            try:
                self.cursor.execute(
                    'SELECT * FROM test_tarea1_inf239.dbo.productos WHERE prod_id = ?;', prod_id)
                row = self.cursor.fetchone()
                self.cursor.execute(
                    'INSERT INTO test_tarea1_inf239.dbo.Carrito VALUES (?, ?, ?, ?);', row[0], row[1], row[3], quantity)
            except pyodbc.ProgrammingError:
                print("Producto no existe")
        self.cursor.execute(
            'SELECT * FROM test_tarea1_inf239.dbo.Oferta WHERE prod_id = ?;', prod_id)
        row = self.cursor.fetchone()
        if row:
            self.cursor.execute(
                'UPDATE test_tarea1_inf239.dbo.Oferta SET offer = ? WHERE prod_id = ?;', row[1], prod_id)
        self.cursor.commit()

    def mostrar_top_5(self) -> None:
        self.cursor.execute(
            'SELECT TOP 5 * FROM test_tarea1_inf239.dbo.productos ORDER BY prod_unit_price DESC;')
        for row in self.cursor:
            print("ID: {0} | Nombre: {1} | Descripcion: {2} | Marca: {3} | Categoria: {4} | Precio: ${5}".format(
                row[0], row[1], row[2], row[3], row[4], row[5]))

    def mostrar_top_5_categoria(self) -> None:
        category = input("Ingrese la categoria: ")
        self.cursor.execute(
            'SELECT TOP 5 * FROM test_tarea1_inf239.dbo.productos WHERE category = ? ORDER BY prod_unit_price DESC;', category)
        for row in self.cursor:
            print("ID: {0} | Nombre: {1} | Descripcion: {2} | Marca: {3} | Categoria: {4} | Precio: ${5}".format(
                row[0], row[1], row[2], row[3], row[4], row[5]))

    def finalizar_compra(self) -> None:
        self.mostrar_boleta()

    def mostrar_boleta(self) -> None:
        self.cursor.execute('DELETE FROM test_tarea1_inf239.dbo.Boleta')
        self.cursor.execute('SELECT * FROM test_tarea1_inf239.dbo.Carrito;')
        data = self.cursor.fetchall()
        for carrito_row in data:
            self.cursor.execute(
                'SELECT * FROM test_tarea1_inf239.dbo.productos WHERE prod_id = ?;', carrito_row[0])
            total_price = self.cursor.fetchone()[5] * carrito_row[3]
            self.cursor.execute(
                'SELECT * FROM test_tarea1_inf239.dbo.Oferta WHERE prod_id = ?;', carrito_row[0])
            oferta_row = self.cursor.fetchone()
            if not oferta_row:
                oferta_row = (carrito_row[0], '1x1')
            lleve = int(oferta_row[1].split('x')[0])
            pague = int(oferta_row[1].split('x')[1])
            if pague != 0:
                self.cursor.execute(
                    'SELECT * FROM test_tarea1_inf239.dbo.productos WHERE prod_id = ?;', carrito_row[0])
                final_price = ((int(carrito_row[3] / lleve) * pague) + (
                    carrito_row[3] % lleve)) * self.cursor.fetchone()[5]
            else:
                final_price = 0
            self.cursor.execute(
                'INSERT INTO test_tarea1_inf239.dbo.Boleta VALUES (?, ?, ?, ?);', carrito_row[0], oferta_row[1], total_price, final_price)
            self.cursor.commit()
        self.cursor.execute(
            'SELECT * FROM test_tarea1_inf239.dbo.Boleta')
        for row in self.cursor:
            print("ID: {0} | Oferta: {1} | Total: {2} | Final: {3}".format(
                row[0], row[1], row[2], row[3]))

    def mostrar_valor_total(self, text=False) -> None or int:
        self.cursor.execute(
            'SELECT SUM(final_value) FROM test_tarea1_inf239.dbo.Boleta')
        if text:
            for row in self.cursor:
                print("Total: {0}".format(row[0]))
        else:
            for row in self.cursor:
                return row[0]

    def buscar_producto(self) -> None:
        prod_id = input("Ingrese el id del producto: ")
        self.cursor.execute(
            'SELECT * FROM test_tarea1_inf239.dbo.productos WHERE prod_id = ?', prod_id)
        for row in self.cursor:
            print('ID: {0} | Nombre: {1} | Descripcion: {2} | Marca: {3} | Categoria: {4} | Precio: ${5}'.format(
                row[0], row[1], row[2], row[3], row[4], row[5]))

    def vaciar_carrito(self) -> None:
        self.cursor.execute('DELETE FROM test_tarea1_inf239.dbo.Carrito')
        self.cursor.commit()

    def eliminar_producto(self) -> None:
        prod_id = input("Ingrese el ID del producto: ")
        try:
            select = self.cursor.execute(
                'SELECT * FROM test_tarea1_inf239.dbo.Carrito WHERE prod_id = ?', prod_id)
            print("Se ha eliminado el producto: {}".format(select[1]))
            self.cursor.execute(
                'DELETE FROM test_tarea1_inf239.dbo.Carrito WHERE prod_id = ?', prod_id)
            self.cursor.commit()
        except pyodbc.ProgrammingError:
            print("Producto no encontrado. ¿Esta seguro que esta en el carrito?")

    def salir(self) -> None:
        print("Gracias por su visita")
        exit()
