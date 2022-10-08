delete from test_tarea1_inf239.dbo.Boleta;
delete from test_tarea1_inf239.dbo.Carrito;
delete from test_tarea1_inf239.dbo.Oferta;
delete from test_tarea1_inf239.dbo.productos;

select * from test_tarea1_inf239.dbo.Oferta;
select * from test_tarea1_inf239.dbo.Boleta;
select * from test_tarea1_inf239.dbo.Carrito;
select * from test_tarea1_inf239.dbo.productos;

drop table test_tarea1_inf239.dbo.Boleta;
drop table test_tarea1_inf239.dbo.Carrito;
drop table test_tarea1_inf239.dbo.Oferta;
drop table test_tarea1_inf239.dbo.productos;

/* PRODUCTO REPETIDO AL ELIMINAR */

select * from test_tarea1_inf239.dbo.productos where prod_name = 'Agua Cristal';

select prod_name,count(*) from test_tarea1_inf239.dbo.productos group by prod_name;