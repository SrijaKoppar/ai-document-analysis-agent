class Skill:
    def __init__(self, name, description, input_schema, output_schema, func):
        self.name = name
        self.description = description
        self.input_schema = input_schema
        self.output_schema = output_schema
        self.func = func

    def run(self, **kwargs):
        return self.func(**kwargs)