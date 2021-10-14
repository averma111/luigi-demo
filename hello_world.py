import luigi

class HelloLuigi(luigi.Task):

    def output(self):
        return luigi.LocalTarget('hello_world.txt')

    def run(self):
        with self.output().open('w') as outputfile:
            outputfile.write('Hello Luigi')