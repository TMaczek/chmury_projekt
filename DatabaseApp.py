from neo4j import GraphDatabase
import logging
from neo4j.exceptions import ServiceUnavailable


class DatabaseApp:

    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        # Don't forget to close the driver connection when you are finished with it
        self.driver.close()

    def add_generic(self, character_name, node_type):
        with self.driver.session(database="neo4j") as session:
            result = session.execute_write(self._add_and_return, character_name, node_type)
            for row in result:
                print("Added  {node} : {p}".format(p=row['p'], node=node_type))

    @staticmethod
    def _add_and_return(tx, character_name, node_type):
        query = (
         "CREATE (p: " + node_type + " { name: $character_name }) "
         "RETURN p"
        )
        result = tx.run(query, character_name=character_name)
        try:
            return [{"p": row["p"]["name"]} for row in result]
        except ServiceUnavailable as exception:
            logging.error("{query} raised an error: \n {exception}".format(
                query=query, exception=exception))
            raise

    def add_episode(self, name, season, number, overall):
        with self.driver.session(database="neo4j") as session:
            result = session.execute_write(self._add_and_return_episode, name, season, number, overall)
            for row in result:
                print("Added episode: {p}".format(p=row['p']))

    @staticmethod
    def _add_and_return_episode(tx, name, season, number, overall):
        query = (
         "CREATE (p: Episode { name: $name, season: $season, number: $number, overall: $overall }) "
         "RETURN p"
        )
        result = tx.run(query, name=name, season=season, number=number, overall=overall)
        try:
            return [{"p": row["p"]["name"]} for row in result]
        except ServiceUnavailable as exception:
            logging.error("{query} raised an error: \n {exception}".format(
                query=query, exception=exception))
            raise

    def add_characters(self, *character_names):
        for character_name in character_names:
            self.add_generic(character_name, "Character")

    def add_groups(self, *group_names):
        for group_name in group_names:
            self.add_generic(group_name, "Group")

    def add_writers(self, *writer_names):
        for writer_name in writer_names:
            self.add_generic(writer_name, "Writer")

    def delete_by_name(self, name):
        with self.driver.session(database="neo4j") as session:
            result = session.execute_write(self._delete_by_name, name)

    @staticmethod
    def _delete_by_name(tx, name):
        query = (
            "MATCH (n {name: $name}) DETACH DELETE n "
        )
        result = tx.run(query, name=name)

    def delete_relation_between(self, a, b):
        with self.driver.session(database="neo4j") as session:
            result = session.execute_write(self._delete_relation_between, a, b)

    @staticmethod
    def _delete_relation_between(tx, a, b):
        query = (
            "MATCH (a)-[r]-(b) WHERE a.name=$a and b.name=$b DELETE r  "
        )
        result = tx.run(query, a=a, b=b)

    def delete_everything(self):
        with self.driver.session(database="neo4j") as session:
            result = session.execute_write(self._delete_everything)
            print("Database cleaned, it should be empty now")

    @staticmethod
    def _delete_everything(tx):
        query = (
            "MATCH (n) OPTIONAL MATCH (n)-[r]-() DELETE n, r"
        )
        tx.run(query)

    def add_generic_relation(self, from_where, to_where, what_kind, from_node, to_node):
        with self.driver.session(database="neo4j") as session:
            result = session.execute_write(
                self._add_and_return_generic_relation, from_where, to_where, what_kind, from_node, to_node)
        for row in result:
            print("Added : {a} - {rel} -> {b}".format(a=row['a'], b=row['b'], rel=what_kind))

    @staticmethod
    def _add_and_return_generic_relation(tx, from_where, to_where, what_kind, from_node, to_node):
        query = (
            "MATCH (a:" + from_node + ") WHERE a.name=$from_where  "
            "MATCH (b:" + to_node + ") WHERE b.name=$to_where "
            "CREATE (a)-[:" + what_kind + "]->(b) "
            "RETURN a, b"
           )
        result = tx.run(query, from_where=from_where, to_where=to_where)
        try:
            return [{"a": row["a"]["name"], "b": row["b"]["name"]} for row in result]
        except ServiceUnavailable as exception:
            logging.error("{query} raised an error: \n {exception}".format(
                query=query, exception=exception))
            raise

    def add_wrote(self, episode,  *writers):
        for writer in writers:
            self.add_generic_relation(writer, episode, "WROTE", "Writer", "Episode")

    def add_appeared(self, episode, *characters, ):
        for character in characters:
            self.add_generic_relation(character, episode, "APPEARED_IN", "Character", "Episode")

    def add_belongs_to(self, group, *characters):
        for character in characters:
            self.add_generic_relation(character, group, "BELONGS_TO", "Character", "Group")

    def add_fusion_of(self, fusion, *characters):
        for character in characters:
            self.add_generic_relation(fusion, character, "FUSION_OF", "Character", "Character")

    # def find_person(self, person_name):
    #     with self.driver.session(database="neo4j") as session:
    #         result = session.execute_read(self._find_and_return_person, person_name)
    #         for row in result:
    #             print("Found person: {row}".format(row=row))

    # @staticmethod
    # def _find_and_return_person(tx, person_name):
    #     query = (
    #         "MATCH (p:Person) "
    #         "WHERE p.name = $person_name "
    #         "RETURN p.name AS name"
    #     )
    #     result = tx.run(query, person_name=person_name)
    #     return [row["name"] for row in result]

    def find_characters_episodes(self, character_name):
        with self.driver.session(database="neo4j") as session:
            result = session.execute_read(self._find_and_return_characters_episodes, character_name)
            return result
            # for row in result:
            #     print("Found episode: {row}".format(row=row['name']))

    @staticmethod
    def _find_and_return_characters_episodes(tx, character_name):
        query = (
            "MATCH (c:Character) -[r:APPEARED_IN] -> (e:Episode) WHERE c.name=$character_name RETURN e as name "
        )
        result = tx.run(query, character_name=character_name)
        return [row["name"] for row in result]


    def add_series_data(self):
        self.add_characters("Steven", "Garnet", "Amethyst", "Pearl", "Lars", "Sadie", "Lion",
                            "Opal", "Sugilite", "Greg", "Connie", "Ruby", "Sapphire", "Jasper",
                            "Peridot", "Lapis", "Sardonyx", "Stevonnie", "Yellow Diamond",
                            "Blue Diamond")

        self.add_writers("Joe Johnston", "Jeff Liu", "Lamar Abrams", "Aleth Romanillos", "Raven Molisee",
                         "Paul Villeco", "Hillary Florido", "Jesse Zuko", "Colin Howard", "Takafumi Hori",
                         "Katie Mitroff")

        self.add_fusion_of("Stevonnie", "Steven", "Connie")
        self.add_fusion_of("Garnet", "Ruby", "Sapphire")
        self.add_fusion_of("Opal", "Pearl", "Amethyst")
        self.add_fusion_of("Sugilite", "Garnet", "Amethyst")
        self.add_fusion_of("Sardonyx", "Pearl", "Garnet")

        self.add_groups("Crystal Gems", "Beach City", "Homeworld")
        self.add_belongs_to("Crystal Gems", "Steven", "Garnet", "Amethyst", "Pearl")
        self.add_belongs_to("Beach City", "Steven", "Greg", "Lars", "Sadie")
        self.add_belongs_to("Homeworld", "Yellow Diamond", "Blue Diamond", "Jasper", "Peridot", "Lapis")

        self.add_episode("Gem Glow", 1, 1, 1)
        self.add_appeared("Gem Glow", "Steven", "Garnet", "Amethyst", "Pearl", "Lars", "Sadie")
        self.add_wrote("Gem Glow", "Joe Johnston", "Jeff Liu")

        self.add_episode("Steven's Lion", 1, 10, 10)
        self.add_appeared("Steven's Lion", "Steven", "Garnet", "Amethyst", "Pearl", "Lion")
        self.add_wrote("Steven's Lion", "Lamar Abrams", "Aleth Romanillos")

        self.add_episode("Lion 2: The Movie", 1, 17, 17)
        self.add_appeared("Lion 2: The Movie", "Steven", "Garnet", "Amethyst", "Pearl", "Lion", "Connie")
        self.add_wrote("Lion 2: The Movie", "Joe Johnston", "Jeff Liu")

        self.add_episode("Giant Woman", 1, 12, 12)
        self.add_appeared("Giant Woman", "Steven", "Garnet", "Amethyst", "Pearl", "Opal")
        self.add_wrote("Giant Woman", "Joe Johnston", "Jeff Liu")

        self.add_episode("Coach Steven", 1, 20, 20)
        self.add_appeared("Coach Steven", "Steven", "Garnet", "Amethyst", "Pearl", "Sugilite", "Greg", "Lars", "Sadie")
        self.add_wrote("Coach Steven", "Raven Molisee", "Paul Villeco")

        self.add_episode("Cry for Help", 2, 11, 63)
        self.add_appeared("Cry for Help", "Steven", "Garnet", "Amethyst", "Pearl", "Sugilite", "Sardonyx")
        self.add_wrote("Cry for Help", "Joe Johnston", "Jeff Liu")

        self.add_episode("Gem Drill", 3, 2, 80)
        self.add_appeared("Gem Drill", "Steven", "Peridot")
        self.add_wrote("Gem Drill", "Raven Molisee", "Paul Villeco")

        self.add_episode("Barn Mates", 3, 4, 82)
        self.add_appeared("Barn Mates", "Steven", "Peridot", "Lapis")
        self.add_wrote("Barn Mates", "Hillary Florido", "Jesse Zuko")

        self.add_episode("Mr. Greg", 3, 8, 86)
        self.add_appeared("Mr. Greg", "Steven", "Greg", "Pearl")
        self.add_wrote("Mr. Greg", "Joe Johnston", "Jeff Liu")

        self.add_episode("Mindful Education", 4, 4, 107)
        self.add_appeared("Mindful Education", "Steven", "Connie", "Garnet", "Stevonnie", "Pearl")
        self.add_wrote("Mindful Education", "Colin Howard", "Jeff Liu", "Takafumi Hori")

        self.add_episode("Lion 4: Alternate Ending", 4, 21, 124)
        self.add_appeared("Lion 4: Alternate Ending", "Steven", "Lion", "Greg")
        self.add_wrote("Lion 4: Alternate Ending", "Hillary Florido", "Paul Villeco")

        self.add_episode("The Trial", 5, 2, 130)
        self.add_appeared("The Trial", "Steven", "Lars", "Yellow Diamond", "Blue Diamond")
        self.add_wrote("The Trial", "Katie Mitroff", "Paul Villeco")

        self.add_episode("Escapism", 5, 28, 156)
        self.add_appeared("Escapism", "Steven", "Connie", "Stevonnie", "Lion")
        self.add_wrote("Escapism", "Joe Johnston", "Jeff Liu")
