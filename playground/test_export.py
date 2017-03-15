from slither.service import Service
from slither.export import TcxExport


s = Service()
a = s.list_activities()[1]
e = TcxExport()
tcx = e.dump(a)
print(tcx)