from database.db import filling_table, create_tables, drop_tadles
from views.gui import MainWindow
# drop_tadles()
create_tables()
filling_table()

MainWindow()