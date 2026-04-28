from database.db import filling_table, create_tables
from views.gui import MainWindow
from utils.api import get_requests
create_tables()
# filling_table()
get_requests()
# MainWindow()