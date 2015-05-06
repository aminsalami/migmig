# Python utils for migmig project



def parse_doc_arguments(arguments):
	options, args, command = {}, {}, None
	for key, value in arguments.items():
		if key[0:2] == "--":
			options[key[2:]] = value
		elif key[0] == "<":
			args[key] = value
		else:
			if value:
				command = key

	return command, args, options

