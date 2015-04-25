# python setup file, uses setuptools and easy_install instead of distutils


from setuptools import setup, find_packages

setup(
	# distribution name
	name = "DDM",
	version = "0.1",
	description = "DDM, A distributed download manager",
	long_description = "Nothing yet ...",
	author = "amin",
	author_email = "amin@dotamin.ir",
	url = "ddm.dotamin.ir",
	packages = find_packages(),
	# scripts for running in shells ( in GNU/linux systems )
	# "scripts/migmig" -> /usr/bin
	scripts = ["scripts/migmig"],

	requires = ['setuptools'],
	install_requires = [	
			# 'docopt>=0.6.1', # not needed! i imported this module manually.
			# 'setuptools>=13.0.2'
		]
	)



