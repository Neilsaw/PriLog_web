import pstats
import cProfile

import pyximport
pyximport.install()

import app

cProfile.runctx("app.analyze_movie('movie/testa.mp4')", globals(), locals(), "Profile.prof")

s = pstats.Stats("Profile.prof")
s.strip_dirs().sort_stats("time").print_stats()