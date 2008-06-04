try:
    import cProfile as myprofiler
except:
    import profile as myprofiler
import orca.orca
myprofiler.run('orca.orca.main()', 'orcaprof')
