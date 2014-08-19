import unittest

from pyramid import testing
from ..models import DBSession


class TestBase(unittest.TestCase):

    def setUp(self):
        testing.setUp()

    def test_one(self):
        assert 1 == 1

    def tearDown(self):
        DBSession.remove()
        testing.tearDown()


# import transaction

# # from sqlalchemy import create_engine



# # def baseSetUp(cls):
# #     config = testing.setUp()
# #     engine = create_engine('sqlite://')
# #     DBSession.configure(bind=engine)
# #     Base.metadata.tables['session'].create(checkfirst=True)




#     #     # self.config = baseSetUp(self)

#     # def tearDown(self):
#     #     DBSession.remove()
#     #     testing.tearDown()

#     # def test_one(self):
#     #     import pdb; pdb.set_trace( )
