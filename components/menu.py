import re
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
            print(row)

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
                self.cursor.execute(
                    'SELECT * FROM test_tarea1_inf239.dbo.Oferta WHERE prod_id = ?;', prod_id)
                offer = self.cursor.fetchone()
                if offer:
                    self.cursor.execute(
                        'INSERT INTO test_tarea1_inf239.dbo.Boleta VALUES (?, ?, ?, ?);', row[0], offer[1], row[5], row[5])
                else:
                    self.cursor.execute(
                        'INSERT INTO test_tarea1_inf239.dbo.Boleta VALUES (?, ?, ?, ?);', row[0], '1x1', row[5], row[5])
                self.cursor.commit()
            except pyodbc.ProgrammingError:
                print("Producto no existe")

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
        self.cursor.execute('SELECT * FROM test_tarea1_inf239.dbo.Carrito')
        for row in self.cursor:
            # get price from productos table
            self.cursor.execute(
                'SELECT prod_unit_price FROM test_tarea1_inf239.dbo.productos WHERE prod_id = ?', row[0])
            price = self.cursor.fetchone()[0]
            # get offer from oferta table
            self.cursor.execute(
                'SELECT offer FROM test_tarea1_inf239.dbo.Oferta WHERE prod_id = ?', row[0])
            offer = self.cursor.fetchone()[0]
            lleve = int(offer.split('x')[0])
            pague = int(offer.split('x')[1])
            # calculate total value
            total_value = int(row[3]) * int(price)
            # calculate final value
            final_value = int(row[3]) * int(price)

            self.cursor.commit()
        self.mostrar_boleta()

    def mostrar_boleta(self) -> None:
        self.cursor.execute('SELECT * FROM test_tarea1_inf239.dbo.Boleta')
        print(" BOLETA ".center(50, "-"))
        for row in self.cursor:
            print('ID: {0} | Precio: ${1} | Total: ${2}'.format(row[0], row[2], row[3]))
        print(" TOTAL: ${} ".format(self.mostrar_valor_total()).center(50, "-"))
        self.mostrar_valor_total()

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
        id = input("Ingrese el id del producto: ")
        self.cursor.execute(
            'SELECT * FROM test_tarea1_inf239.dbo.productos WHERE prod_id = ?', id)
        for row in self.cursor:
            print('ID: {0} | Nombre: {1} | Descripcion: {2} | Marca: {3} | Categoria: {4} | Precio: ${5}'.format(
                row[0], row[1], row[2], row[3], row[4], row[5]))

    def vaciar_carrito(self) -> None:
        self.cursor.execute('DELETE FROM test_tarea1_inf239.dbo.Carrito')
        self.cursor.commit()

    def eliminar_producto(self) -> None:
        prod_id = input("Ingrese el ID del producto: ")
        try:
            self.cursor.execute(
                'DELETE FROM test_tarea1_inf239.dbo.Carrito WHERE prod_id = ?', prod_id)
            self.cursor.commit()
        except pyodbc.ProgrammingError:
            print("Producto no encontrado. ¿Esta seguro que esta en el carrito?")

    def aplicar_oferta(self) -> None:
        self.cursor.execute(
            'SELECT * FROM test_tarea1_inf239.dbo.Oferta')
        ofertas = self.cursor.fetchall()
        for oferta in ofertas:
            self.cursor.execute(
                'SELECT * FROM test_tarea1_inf239.dbo.Carrito WHERE prod_id = ?', oferta[0])
            row = self.cursor.fetchone()
            if row:
                self.cursor.execute(
                    'UPDATE test_tarea1_inf239.dbo.Boleta SET offer = ? WHERE prod_id = ?', oferta[1], oferta[0])
                self.cursor.commit()
                lleve = oferta[1].split('x')[0]
                pague = oferta[1].split('x')[1]

    def salir(self) -> None:
        print("Gracias por su visita")
        exit()
